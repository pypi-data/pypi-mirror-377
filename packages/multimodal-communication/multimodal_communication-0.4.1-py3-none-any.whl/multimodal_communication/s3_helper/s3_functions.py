import os
import pandas as pd
import polars as pl
import json
import pickle as pkl
import warnings
import boto3
from botocore.exceptions import ClientError
from typing import Union, Optional
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")


class S3CloudHelper:
    def __init__(
        self,
        obj: Union[pd.DataFrame, pl.DataFrame, dict, str, None] = None,
        path: str = None,
        region_name: str = AWS_REGION,
    ):
        if obj is not None and path is not None:
            raise ValueError(
                "Only one of 'obj' or 'path' should be provided, not both."
            )

        self.obj = obj
        self.path = path

        self.s3_client = boto3.client(
            "s3",
            region_name=region_name,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

    def _infer_file_type(self, file_name: str) -> Optional[str]:
        ext = os.path.splitext(file_name)[1].lower()
        return {
            ".csv": "csv",
            ".json": "json",
            ".pkl": "pickle",
            ".pickle": "pickle",
            ".parquet": "parquet",
            ".pq": "parquet",
            ".txt": "txt",
            "": None,
        }.get(ext, None)

    def upload_to_s3(
        self,
        bucket_name: str,
        file_name: str,
        file_type: str = None,
    ):
        if file_type is None:
            file_type = self._infer_file_type(file_name)
            if file_type is None:
                raise ValueError(f"Cannot infer file_type from filename: {file_name}")

        if self.path:
            self.s3_client.upload_file(self.path, bucket_name, file_name)
            return

        if self.obj is not None:
            buffer = BytesIO()

            if file_type == "csv":
                if isinstance(self.obj, pd.DataFrame):
                    self.obj.to_csv(buffer, index=False)
                elif isinstance(self.obj, pl.DataFrame):
                    buffer.write(self.obj.write_csv().encode("utf-8"))
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name)

            elif file_type == "parquet":
                if isinstance(self.obj, pd.DataFrame):
                    self.obj.to_parquet(buffer, index=False)
                elif isinstance(self.obj, pl.DataFrame):
                    self.obj.write_parquet(buffer)
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name)

            elif file_type == "json":
                json_str = json.dumps(self.obj, indent=2)
                self.s3_client.put_object(
                    Body=json_str.encode("utf-8"), Bucket=bucket_name, Key=file_name
                )

            elif file_type in ("pickle", "pkl"):
                pkl.dump(self.obj, buffer)
                buffer.seek(0)
                self.s3_client.upload_fileobj(buffer, bucket_name, file_name)

            elif file_type == "txt":
                self.s3_client.put_object(
                    Body=self.obj.encode("utf-8"), Bucket=bucket_name, Key=file_name
                )
            else:
                raise ValueError(f"Unsupported file type {file_type}")

    def download_from_s3(
        self,
        s3_filepath: str,
        file_type: str = None,
        use_polars: bool = False,
    ):
        if s3_filepath.startswith("s3://"):
            s3_filepath = s3_filepath[5:]

        bucket_name, *blob_path = s3_filepath.split("/", 1)
        blob_path = blob_path[0]

        is_prefix = not any(
            blob_path.endswith(ext)
            for ext in [".csv", ".parquet", ".json", ".pkl", ".pickle", ".txt"]
        )

        if is_prefix:
            files = self.list_files(bucket=bucket_name, prefix=blob_path)
            if not files:
                return pl.DataFrame() if use_polars else pd.DataFrame()

            if use_polars:
                if file_type == "csv":
                    return pl.scan_csv(files)
                elif file_type == "parquet":
                    return pl.scan_parquet(files)
            else:
                raise ValueError("Lazy multi-file read only supported with Polars.")
        else:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=blob_path)
            data = response["Body"].read()
            buffer = BytesIO(data)

            if file_type is None:
                file_type = self._infer_file_type(blob_path)

            if file_type == "csv":
                return pl.read_csv(buffer) if use_polars else pd.read_csv(buffer)
            elif file_type == "parquet":
                return (
                    pl.read_parquet(buffer) if use_polars else pd.read_parquet(buffer)
                )
            elif file_type == "json":
                return json.loads(data.decode("utf-8"))
            elif file_type in ("pickle", "pkl"):
                return pkl.loads(data)
            elif file_type == "txt":
                return data.decode("utf-8")

    def delete_from_s3(self, bucket_name: str, file_name: str) -> bool:
        try:
            if file_name.endswith("/"):
                paginator = self.s3_client.get_paginator("list_objects_v2")
                pages = paginator.paginate(Bucket=bucket_name, Prefix=file_name)
                objects_to_delete = [
                    {"Key": obj["Key"]}
                    for page in pages
                    for obj in page.get("Contents", [])
                ]
                if objects_to_delete:
                    for i in range(0, len(objects_to_delete), 1000):
                        batch = objects_to_delete[i : i + 1000]
                        self.s3_client.delete_objects(
                            Bucket=bucket_name, Delete={"Objects": batch, "Quiet": True}
                        )
                    return True
                return False
            else:
                self.s3_client.delete_object(Bucket=bucket_name, Key=file_name)
                return True
        except ClientError as e:
            warnings.warn(f"Failed to delete: {file_name}: {e}")
            return False

    def list_files(self, bucket: str, prefix: str) -> list[str]:
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return [
                f"s3://{bucket}/{obj['Key']}"
                for obj in response.get("Contents", [])
                if not obj["Key"].endswith("/")
            ]
        except ClientError as e:
            warnings.warn(
                f"Failed to list files in bucket '{bucket}' with prefix '{prefix}': {e}"
            )
            return []
