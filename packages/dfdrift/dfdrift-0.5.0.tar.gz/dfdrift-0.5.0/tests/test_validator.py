import pytest
import pandas as pd
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from io import StringIO
import sys

from dfdrift.validator import DfValidator
from dfdrift.storages import LocalFileStorage
from dfdrift.alerters import StderrAlerter


class TestLocalFileStorage:
    def test_init_default_path(self):
        storage = LocalFileStorage()
        assert storage.storage_path.name == ".dfdrift_schemas"
        assert storage.schema_file.name == "schemas.json"

    def test_init_custom_path(self):
        storage = LocalFileStorage("custom_path")
        assert storage.storage_path.name == "custom_path"
        assert storage.schema_file.name == "schemas.json"

    def test_save_and_load_schema(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            schema = {
                "columns": {"col1": {"dtype": "int64", "null_count": 0, "total_count": 5}},
                "shape": [5, 1]
            }
            location_key = "test_file.py:10"
            
            storage.save_schema(location_key, schema)
            loaded_schemas = storage.load_schemas()
            
            assert location_key in loaded_schemas
            assert loaded_schemas[location_key] == schema

    def test_load_empty_schemas(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            schemas = storage.load_schemas()
            assert schemas == {}


class TestStderrAlerter:
    def test_alert_output(self):
        alerter = StderrAlerter()
        old_schema = {"columns": {"a": {"dtype": "int64"}}, "shape": [1, 1]}
        new_schema = {"columns": {"a": {"dtype": "object"}}, "shape": [1, 1]}
        
        captured_output = StringIO()
        with patch('sys.stderr', captured_output):
            alerter.alert("Test message", "test.py:10", old_schema, new_schema)
        
        output = captured_output.getvalue()
        assert "WARNING: Test message" in output
        assert "Location: test.py:10" in output


class TestDfValidator:
    def test_init_default(self):
        validator = DfValidator()
        assert isinstance(validator.storage, LocalFileStorage)
        assert isinstance(validator.alerter, StderrAlerter)

    def test_get_dataframe_schema(self):
        validator = DfValidator()
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', None],
            'age': [25, 30, 35],
            'score': [85.5, 92.0, 78.5]
        })
        
        schema = validator._get_dataframe_schema(df)
        
        # Only validate column structure, not shape
        assert "name" in schema["columns"]
        assert "age" in schema["columns"]
        assert "score" in schema["columns"]
        assert schema["columns"]["name"]["dtype"] == "object"
        assert schema["columns"]["age"]["dtype"] == "int64"
        assert schema["columns"]["score"]["dtype"] == "float64"
        
    def test_schemas_equal(self):
        validator = DfValidator()
        schema1 = {"columns": {"a": {"dtype": "int64", "null_count": 0, "total_count": 10}}, "shape": [10, 1]}
        schema2 = {"columns": {"a": {"dtype": "int64", "null_count": 1, "total_count": 20}}, "shape": [20, 1]}
        schema3 = {"columns": {"a": {"dtype": "object", "null_count": 0, "total_count": 10}}, "shape": [10, 1]}
        
        # Same dtype, different shape/counts -> should be equal
        assert validator._schemas_equal(schema1, schema2) is True
        # Different dtype -> should be different
        assert validator._schemas_equal(schema1, schema3) is False

    def test_get_schema_differences(self):
        validator = DfValidator()
        old_schema = {
            "columns": {
                "name": {"dtype": "object"},
                "age": {"dtype": "int64"},
                "removed_col": {"dtype": "float64"}
            },
            "shape": [3, 3]
        }
        new_schema = {
            "columns": {
                "name": {"dtype": "object"},
                "age": {"dtype": "object"},  # dtype changed
                "new_col": {"dtype": "int64"}  # added column
            },
            "shape": [4, 3]  # shape changed (but should be ignored)
        }
        
        differences = validator._get_schema_differences(old_schema, new_schema)
        
        assert "Added columns: ['new_col']" in differences
        assert "Removed columns: ['removed_col']" in differences
        assert "Column 'age' dtype changed: int64 → object" in differences
        # Shape changes should NOT be reported
        assert "Shape changed" not in differences

    def test_validate_new_schema(self):
        storage = Mock()
        alerter = Mock()
        storage.load_schemas.return_value = {}
        
        validator = DfValidator(storage=storage, alerter=alerter)
        df = pd.DataFrame({'col': [1, 2, 3]})
        
        with patch('inspect.currentframe') as mock_frame:
            mock_caller = Mock()
            mock_caller.f_code.co_filename = "test.py"
            mock_caller.f_lineno = 10
            mock_frame.return_value.f_back = mock_caller
            
            validator.validate(df)
        
        storage.save_schema.assert_called_once()
        alerter.alert.assert_not_called()

    def test_validate_schema_changed(self):
        old_schema = {"columns": {"col": {"dtype": "int64"}}, "shape": [3, 1]}
        storage = Mock()
        alerter = Mock()
        storage.load_schemas.return_value = {"test.py:10": old_schema}
        
        validator = DfValidator(storage=storage, alerter=alerter)
        df = pd.DataFrame({'col': ['a', 'b', 'c']})  # dtype changed to object
        
        with patch('inspect.currentframe') as mock_frame:
            mock_caller = Mock()
            mock_caller.f_code.co_filename = "test.py"
            mock_caller.f_lineno = 10
            mock_frame.return_value.f_back = mock_caller
            
            validator.validate(df)
        
        storage.save_schema.assert_called_once()
        alerter.alert.assert_called_once()

    def test_validate_schema_unchanged(self):
        schema = {
            "columns": {"col": {"dtype": "int64", "null_count": 0, "total_count": 3}},
            "shape": [3, 1]
        }
        storage = Mock()
        alerter = Mock()
        storage.load_schemas.return_value = {"test.py:10": schema}
        
        validator = DfValidator(storage=storage, alerter=alerter)
        df = pd.DataFrame({'col': [1, 2, 3]})
        
        with patch('inspect.currentframe') as mock_frame:
            mock_caller = Mock()
            mock_caller.f_code.co_filename = "test.py"
            mock_caller.f_lineno = 10
            mock_frame.return_value.f_back = mock_caller
            
            validator.validate(df)
        
        storage.save_schema.assert_called_once()
        alerter.alert.assert_not_called()

    def test_validate_schema_unchanged_different_row_count(self):
        """Test that changing only row count doesn't trigger alert"""
        schema = {
            "columns": {"col": {"dtype": "int64", "null_count": 0, "total_count": 3}},
            "shape": [3, 1]
        }
        storage = Mock()
        alerter = Mock()
        storage.load_schemas.return_value = {"test.py:10": schema}
        
        validator = DfValidator(storage=storage, alerter=alerter)
        # Same dtype, different row count
        df = pd.DataFrame({'col': [1, 2, 3, 4, 5]})  # 5 rows instead of 3
        
        with patch('inspect.currentframe') as mock_frame:
            mock_caller = Mock()
            mock_caller.f_code.co_filename = "test.py"
            mock_caller.f_lineno = 10
            mock_frame.return_value.f_back = mock_caller
            
            validator.validate(df)
        
        storage.save_schema.assert_called_once()
        # Should NOT trigger alert even though row count changed
        alerter.alert.assert_not_called()