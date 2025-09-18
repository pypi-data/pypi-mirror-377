import os
from dotenv import load_dotenv
from typing import Optional, Union

import numpy as np
import pandas as pd
import polars as pl
from deltalake import DeltaTable, write_deltalake
from deltalake.exceptions import TableNotFoundError



# Load environment variables
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")


class DeltaTableHelper:
    def __init__(self, region_name: str = AWS_REGION):
        self.region_name = region_name

    def _resolve_path(self, bucket_or_path: str, table_name: Optional[str] = None, local:bool=False):
        """
        Resolves a path for DeltaTable operations.
        - Local path: just returns it
        - S3 path: returns s3://bucket/key and storage_options
        """
        if local:
            # local filesystem
            return bucket_or_path, None
        else:
            if table_name is None:
                raise ValueError("Must provide key when using S3 bucket")
            s3_path = f"s3://{bucket_or_path}/{table_name}"
            return s3_path, {"AWS_REGION": self.region_name}

    def _fix_null_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        new_dtypes = {}
        for col in df.columns:
            if df[col].isna().all():
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    new_dtypes[col] = "datetime64[ns]"
                else:
                    new_dtypes[col] = np.float64
        if new_dtypes:
            df = df.astype(new_dtypes)
        return df

    def upload_delta(
        self,
        bucket_or_path: str,
        key: Optional[str],
        df: Union[pd.DataFrame, pl.DataFrame],
        partition_by: Optional[list[str]] = None,
    ):
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()
        df = self._fix_null_columns(df)

        path, storage_options = self._resolve_path(bucket_or_path, key)
        write_deltalake(
            path,
            df,
            mode="overwrite",
            partition_by=partition_by,
            storage_options=storage_options,
        )

    def download_delta(
        self,
        bucket_or_path: str,
        key: Optional[str] = None,
        use_polars: bool = False,
    ):
        path, storage_options = self._resolve_path(bucket_or_path, key)
        dt = DeltaTable(path, storage_options=storage_options)
        df = dt.to_pandas()
        return pl.from_pandas(df) if use_polars else df

    def upsert_delta(
        self,
        bucket_or_path: str,
        table_name: Optional[str] = None,
        new_data: Union[pd.DataFrame, pl.DataFrame] = None,
        partition_by: Optional[list[str]] = None,
        drop_duplicates_by: list[str] | None = None,
    ):
        """
        Upsert new_data into an existing Delta table or create a new one.
        
        Args:
            bucket_or_path: local path OR S3 bucket name
            key: S3 key (ignored if using local path)
            new_data: pandas or polars DataFrame to merge in
            partition_by: optional partition columns
            drop_duplicates_by: columns to deduplicate on (defaults to all)
        """
        if isinstance(new_data, pl.DataFrame):
            new_data = new_data.to_pandas()

        path, storage_options = self._resolve_path(bucket_or_path, table_name)

        # Validate partition columns
        if partition_by:
            missing = [c for c in partition_by if c not in new_data.columns]
            if missing:
                raise ValueError(f"Partition columns missing from new_data: {missing}")

        # If table exists, merge
        if self._delta_table_exists(path, storage_options):
            dt = DeltaTable(path, storage_options=storage_options)
            existing_df = dt.to_pandas()
            combined_df = pd.concat([existing_df, new_data], ignore_index=True)

            if drop_duplicates_by:
                combined_df = combined_df.drop_duplicates(
                    subset=drop_duplicates_by, keep="last"
                )
            else:
                combined_df = combined_df.drop_duplicates(keep="last")

            combined_df = self._fix_null_columns(combined_df).reset_index(drop=True)
            write_deltalake(
                path,
                combined_df,
                mode="overwrite",
                partition_by=partition_by,
                storage_options=storage_options,
            )
        else:
            # New table
            new_data = self._fix_null_columns(new_data)
            write_deltalake(
                path,
                new_data,
                mode="overwrite",
                partition_by=partition_by,
                storage_options=storage_options,
            )


    def _delta_table_exists(self, path: str, storage_options: Optional[dict] = None) -> bool:
        """
        Checks if a DeltaTable exists at the given path.
        """
        try:
            DeltaTable(path, storage_options=storage_options)
            return True
        except (FileNotFoundError, TableNotFoundError, OSError):
            return False
