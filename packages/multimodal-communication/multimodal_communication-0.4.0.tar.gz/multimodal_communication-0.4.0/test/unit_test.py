import io
import json
import pickle
import pytest
import pandas as pd
import polars as pl
from unittest.mock import MagicMock
from multimodal_communication import S3CloudHelper, DeltaTableHelper  # adjust path

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def mock_s3_client():
    """Fixture that returns a mocked boto3 S3 client."""
    return MagicMock()

@pytest.fixture
def helper_with_mock_s3(mock_s3_client):
    """S3CloudHelper wired to a mocked S3 client."""
    helper = S3CloudHelper(obj=None)
    helper.s3_client = mock_s3_client
    return helper

@pytest.fixture
def delta_helper(tmp_path):
    """DeltaTableHelper writing to a temporary local directory instead of S3."""
    # Replace bucket/key with local path for tests
    helper = DeltaTableHelper(region_name="us-east-1")
    helper.local_base = tmp_path  # monkeypatch attribute for local writing
    return helper

# -----------------------------
# S3CloudHelper Tests
# -----------------------------
class TestS3CloudHelper:
    def test_infer_file_type(self, helper_with_mock_s3):
        assert helper_with_mock_s3._infer_file_type("file.csv") == "csv"
        assert helper_with_mock_s3._infer_file_type("file.parquet") == "parquet"
        assert helper_with_mock_s3._infer_file_type("file.json") == "json"
        assert helper_with_mock_s3._infer_file_type("file.pkl") == "pickle"
        assert helper_with_mock_s3._infer_file_type("file.txt") == "txt"
        assert helper_with_mock_s3._infer_file_type("file.unknown") is None

    def test_upload_csv_pandas(self, helper_with_mock_s3, mock_s3_client):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        helper_with_mock_s3.obj = df
        helper_with_mock_s3.upload_to_s3("test-bucket", "test.csv")
        assert mock_s3_client.upload_fileobj.called

    def test_upload_json_dict(self, helper_with_mock_s3, mock_s3_client):
        data = {"x": 123}
        helper_with_mock_s3.obj = data
        helper_with_mock_s3.upload_to_s3("test-bucket", "data.json")
        mock_s3_client.put_object.assert_called_once()
        _, kwargs = mock_s3_client.put_object.call_args
        assert json.loads(kwargs["Body"].decode()) == data

    def test_upload_pickle(self, helper_with_mock_s3, mock_s3_client):
        obj = {"a": [1, 2, 3]}
        helper_with_mock_s3.obj = obj
        helper_with_mock_s3.upload_to_s3("bucket", "obj.pkl")
        assert mock_s3_client.upload_fileobj.called

    def test_upload_txt(self, helper_with_mock_s3, mock_s3_client):
        helper_with_mock_s3.obj = "hello world"
        helper_with_mock_s3.upload_to_s3("bucket", "file.txt")
        mock_s3_client.put_object.assert_called_once()
        _, kwargs = mock_s3_client.put_object.call_args
        assert kwargs["Body"].decode() == "hello world"

    def test_download_csv(self, helper_with_mock_s3, mock_s3_client):
        csv_bytes = b"a,b\n1,2\n3,4\n"
        mock_s3_client.get_object.return_value = {"Body": io.BytesIO(csv_bytes)}
        df = helper_with_mock_s3.download_from_s3("s3://bucket/test.csv", file_type="csv")
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["a", "b"]
        assert df.to_dict(orient="list") == {"a": [1, 3], "b": [2, 4]}

    def test_download_json(self, helper_with_mock_s3, mock_s3_client):
        json_data = {"a": 1}
        mock_s3_client.get_object.return_value = {
            "Body": io.BytesIO(json.dumps(json_data).encode("utf-8"))
        }
        result = helper_with_mock_s3.download_from_s3("s3://bucket/data.json")
        assert result == json_data

    def test_download_pickle(self, helper_with_mock_s3, mock_s3_client):
        obj = {"foo": "bar"}
        pickled = pickle.dumps(obj)
        mock_s3_client.get_object.return_value = {"Body": io.BytesIO(pickled)}
        result = helper_with_mock_s3.download_from_s3("s3://bucket/file.pkl")
        assert result == obj

    def test_delete_single_file(self, helper_with_mock_s3, mock_s3_client):
        mock_s3_client.delete_object.return_value = {}
        success = helper_with_mock_s3.delete_from_s3("bucket", "file.txt")
        assert success is True
        mock_s3_client.delete_object.assert_called_once()

    def test_list_files(self, helper_with_mock_s3, mock_s3_client):
        mock_s3_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "file1.csv"}, {"Key": "folder/"}]
        }
        files = helper_with_mock_s3.list_files("bucket", "prefix/")
        assert files == ["s3://bucket/file1.csv"]

# -----------------------------
# DeltaTableHelper Tests
# -----------------------------

@pytest.fixture
def delta_fixture():
    """Fixture that returns a DeltaTableHelper instance."""
    return DeltaTableHelper(region_name="us-east-1")


def test_upload_and_download_delta(delta_fixture, tmp_path):
    """Test uploading and downloading a delta table locally."""
    df = pd.DataFrame({"id": [1, 2], "val": ["a", "b"]})
    delta_path = str(tmp_path / "test_delta")

    # Upload
    delta_fixture.upload_delta(bucket_or_path=delta_path, key=None, df=df)

    # Download
    df_out = delta_fixture.download_delta(delta_path)

    pd.testing.assert_frame_equal(df, df_out)


def test_upload_and_download_delta_polars(delta_fixture, tmp_path):
    """Test uploading and downloading using a Polars DataFrame."""
    df = pl.DataFrame({"id": [1, 2], "val": ["a", "b"]})
    delta_path = str(tmp_path / "test_delta_polars")

    # Upload
    delta_fixture.upload_delta(bucket_or_path=delta_path, key=None, df=df)

    # Download as Polars
    df_out = delta_fixture.download_delta(delta_path, use_polars=True)

    assert isinstance(df_out, pl.DataFrame)
    assert df_out.to_pandas().equals(df.to_pandas())


def test_upsert_delta(delta_fixture, tmp_path):
    """Test upserting new data into an existing delta table."""
    # Initial table
    df1 = pd.DataFrame({"id": [1, 2], "val": ["a", "b"]})
    delta_path = str(tmp_path / "test_delta_upsert")

    delta_fixture.upload_delta(bucket_or_path=delta_path, key=None, df=df1)

    # New data to upsert
    df2 = pd.DataFrame({"id": [2, 3], "val": ["B_new", "c"]})

    # Provide merge_condition for the upsert
    delta_fixture.upsert_delta(bucket_or_path=str(delta_path), new_data=df2, drop_duplicates_by=['id'])

    # Expected result
    df_expected = pd.DataFrame({"id": [1, 2, 3], "val": ["a", "B_new", "c"]})

    df_out = delta_fixture.download_delta(delta_path)
    pd.testing.assert_frame_equal(
        df_out.sort_values("id").reset_index(drop=True),
        df_expected.sort_values("id").reset_index(drop=True)
    )



def test_upsert_delta_polars(delta_helper, tmp_path):
    """Test upserting with Polars DataFrame."""
    df1 = pl.DataFrame({"id": [1, 2], "val": ["a", "b"]})
    delta_path = str(tmp_path / "test_delta_upsert_polars")

    delta_helper.upload_delta(bucket_or_path=delta_path, key=None, df=df1)

    df2 = pl.DataFrame({"id": [2, 3], "val": ["B_new", "c"]})

    delta_helper.upsert_delta(bucket_or_path=str(delta_path), new_data=df2, drop_duplicates_by=['id'])


    df_expected = pd.DataFrame({"id": [1, 2, 3], "val": ["a", "B_new", "c"]})
    df_out = delta_helper.download_delta(delta_path)

    pd.testing.assert_frame_equal(
        df_out.sort_values("id").reset_index(drop=True),
        df_expected.sort_values("id").reset_index(drop=True)
    )
