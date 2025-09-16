import pytest
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

from dfdrift.storages import GcsStorage


class TestGcsStorage:
    def test_init_with_bucket_argument(self):
        """Test GcsStorage initialization with bucket argument"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client') as mock_import:
            mock_client = Mock()
            mock_import.return_value = mock_client
            
            storage = GcsStorage(bucket="test-bucket", prefix="test-prefix")
            
            assert storage.bucket == "test-bucket"
            assert storage.prefix == "test-prefix/"
            assert storage.schema_blob_name == "test-prefix/schemas.json"
            assert storage.client == mock_client

    def test_init_with_env_bucket(self):
        """Test GcsStorage initialization with environment variable bucket"""
        with patch.dict(os.environ, {'DFDRIFT_GCS_BUCKET': 'env-bucket', 'DFDRIFT_GCS_PREFIX': 'env-prefix'}):
            with patch('dfdrift.storages.GcsStorage._import_gcs_client') as mock_import:
                mock_client = Mock()
                mock_import.return_value = mock_client
                
                storage = GcsStorage()
                
                assert storage.bucket == "env-bucket"
                assert storage.prefix == "env-prefix/"

    def test_init_no_bucket_raises_error(self):
        """Test GcsStorage raises error when no bucket provided"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                GcsStorage()
            
            assert "GCS bucket must be provided either as argument or DFDRIFT_GCS_BUCKET environment variable" in str(exc_info.value)

    def test_init_missing_gcs_package_raises_import_error(self):
        """Test GcsStorage raises ImportError when google-cloud-storage not installed"""
        # Create a mock that raises ImportError when called
        def mock_import_gcs_client(self):
            raise ImportError("google-cloud-storage package is required for GcsStorage. Install with: pip install dfdrift[gcs]")
        
        with patch.object(GcsStorage, '_import_gcs_client', mock_import_gcs_client):
            with pytest.raises(ImportError) as exc_info:
                GcsStorage(bucket="test-bucket")
            
            assert "google-cloud-storage package is required" in str(exc_info.value)

    def test_prefix_normalization(self):
        """Test prefix normalization (remove leading slash, add trailing slash)"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client'):
            # Test with leading slash
            storage1 = GcsStorage(bucket="test", prefix="/my-prefix")
            assert storage1.prefix == "my-prefix/"
            
            # Test without trailing slash
            storage2 = GcsStorage(bucket="test", prefix="my-prefix")
            assert storage2.prefix == "my-prefix/"
            
            # Test with both
            storage3 = GcsStorage(bucket="test", prefix="/my-prefix/")
            assert storage3.prefix == "my-prefix/"

    def test_save_schema_success(self):
        """Test successful schema saving to GCS"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client') as mock_import:
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()
            
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_import.return_value = mock_client
            
            storage = GcsStorage(bucket="test-bucket")
            
            # Mock load_schemas to return existing data
            with patch.object(storage, 'load_schemas', return_value={"existing": "schema"}):
                test_schema = {"columns": {"name": {"dtype": "object"}}, "shape": [3, 1]}
                storage.save_schema("test.py:10", test_schema)
            
            # Verify GCS calls
            mock_client.bucket.assert_called_with("test-bucket")
            mock_bucket.blob.assert_called_with("dfdrift/schemas.json")
            mock_blob.upload_from_string.assert_called_once()
            
            # Check uploaded content
            uploaded_content = mock_blob.upload_from_string.call_args[0][0]
            uploaded_data = json.loads(uploaded_content)
            assert "existing" in uploaded_data
            assert "test.py:10" in uploaded_data
            assert uploaded_data["test.py:10"] == test_schema

    def test_save_schema_error_handling(self):
        """Test error handling during schema save"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client') as mock_import:
            mock_client = Mock()
            mock_client.bucket.side_effect = Exception("GCS error")
            mock_import.return_value = mock_client
            
            storage = GcsStorage(bucket="test-bucket")
            
            with pytest.raises(RuntimeError) as exc_info:
                storage.save_schema("test.py:10", {})
            
            assert "Failed to save schema to GCS" in str(exc_info.value)

    def test_load_schemas_success(self):
        """Test successful schema loading from GCS"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client') as mock_import:
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()
            
            test_schemas = {
                "test1.py:10": {"columns": {"col1": {"dtype": "int64"}}, "shape": [5, 1]},
                "test2.py:20": {"columns": {"col2": {"dtype": "object"}}, "shape": [3, 1]}
            }
            
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.exists.return_value = True
            mock_blob.download_as_text.return_value = json.dumps(test_schemas)
            mock_import.return_value = mock_client
            
            storage = GcsStorage(bucket="test-bucket")
            schemas = storage.load_schemas()
            
            assert schemas == test_schemas
            mock_client.bucket.assert_called_with("test-bucket")
            mock_bucket.blob.assert_called_with("dfdrift/schemas.json")

    def test_load_schemas_file_not_exists(self):
        """Test loading schemas when file doesn't exist"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client') as mock_import:
            mock_client = Mock()
            mock_bucket = Mock()
            mock_blob = Mock()
            
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            mock_blob.exists.return_value = False
            mock_import.return_value = mock_client
            
            storage = GcsStorage(bucket="test-bucket")
            schemas = storage.load_schemas()
            
            assert schemas == {}

    def test_load_schemas_error_handling(self):
        """Test error handling during schema load"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client') as mock_import:
            mock_client = Mock()
            mock_client.bucket.side_effect = Exception("GCS error")
            mock_import.return_value = mock_client
            
            storage = GcsStorage(bucket="test-bucket")
            schemas = storage.load_schemas()
            
            # Should return empty dict on error
            assert schemas == {}

    def test_custom_prefix_in_blob_name(self):
        """Test custom prefix is used in blob name"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client'):
            storage = GcsStorage(bucket="test-bucket", prefix="custom/path")
            assert storage.schema_blob_name == "custom/path/schemas.json"

    def test_default_prefix(self):
        """Test default prefix is 'dfdrift'"""
        with patch('dfdrift.storages.GcsStorage._import_gcs_client'):
            storage = GcsStorage(bucket="test-bucket")
            assert storage.prefix == "dfdrift/"
            assert storage.schema_blob_name == "dfdrift/schemas.json"