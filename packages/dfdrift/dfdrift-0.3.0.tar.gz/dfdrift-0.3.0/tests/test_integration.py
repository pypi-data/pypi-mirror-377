import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

import dfdrift.pandas as dfdrift_pandas
from dfdrift.storages import LocalFileStorage


class TestSchemaChangeDetection:
    def test_schema_drift_detection_workflow(self):
        """Test complete workflow of schema drift detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            # First execution - create initial schema
            df1 = dfdrift_pandas.DataFrame({
                'user_id': [1, 2, 3],
                'name': ['Alice', 'Bob', 'Charlie'],
                'age': [25, 30, 35]
            })
            
            # Verify schema was saved
            schemas = storage.load_schemas()
            assert len(schemas) == 1
            schema_key = list(schemas.keys())[0]
            initial_schema = schemas[schema_key]
            
            assert initial_schema['shape'] == [3, 3]
            assert 'user_id' in initial_schema['columns']
            assert initial_schema['columns']['user_id']['dtype'] == 'int64'
            assert initial_schema['columns']['name']['dtype'] == 'object'
            assert initial_schema['columns']['age']['dtype'] == 'int64'
            
            # Second execution - same schema (no drift)
            df2 = dfdrift_pandas.DataFrame({
                'user_id': [4, 5, 6],
                'name': ['David', 'Eve', 'Frank'],
                'age': [28, 32, 27]
            })
            
            # Schema should now have 2 entries (different line numbers)
            schemas = storage.load_schemas()
            assert len(schemas) == 2
            
            # Third execution - schema drift (dtype change)
            df3 = dfdrift_pandas.DataFrame({
                'user_id': ['a', 'b', 'c'],  # Changed to string
                'name': ['Grace', 'Henry', 'Iris'],
                'age': [29, 31, 26]
            })
            
            # Should now have 3 schemas (3 different locations)
            schemas = storage.load_schemas()
            assert len(schemas) == 3
            
            # Find the schema with object dtype for user_id
            object_schema = None
            for schema in schemas.values():
                if schema['columns']['user_id']['dtype'] == 'object':
                    object_schema = schema
                    break
            
            assert object_schema is not None

    def test_multiple_locations_tracking(self):
        """Test that different code locations are tracked separately"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            def create_user_data():
                return dfdrift_pandas.DataFrame({
                    'user_id': [1, 2],
                    'email': ['a@example.com', 'b@example.com']
                })
            
            def create_product_data():
                return dfdrift_pandas.DataFrame({
                    'product_id': [101, 102],
                    'price': [29.99, 39.99]
                })
            
            # Create DataFrames from different functions
            user_df = create_user_data()
            product_df = create_product_data()
            
            # Should have two separate schema entries
            schemas = storage.load_schemas()
            assert len(schemas) == 2
            
            # Each should have different columns
            schema_keys = list(schemas.keys())
            schemas_values = list(schemas.values())
            
            user_columns = set()
            product_columns = set()
            for schema in schemas_values:
                cols = set(schema['columns'].keys())
                if 'user_id' in cols:
                    user_columns = cols
                elif 'product_id' in cols:
                    product_columns = cols
            
            assert user_columns == {'user_id', 'email'}
            assert product_columns == {'product_id', 'price'}

    def test_read_csv_schema_tracking(self):
        """Test schema tracking for CSV files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test CSV files
            csv_path1 = Path(tmpdir) / "test1.csv"
            csv_path2 = Path(tmpdir) / "test2.csv"
            
            # First CSV with integer columns
            pd.DataFrame({
                'id': [1, 2, 3],
                'value': [10, 20, 30]
            }).to_csv(csv_path1, index=False)
            
            # Second CSV with mixed types
            pd.DataFrame({
                'id': ['a', 'b', 'c'],
                'value': [10.5, 20.5, 30.5]
            }).to_csv(csv_path2, index=False)
            
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            # Read first CSV
            df1 = dfdrift_pandas.read_csv(str(csv_path1))
            schemas = storage.load_schemas()
            assert len(schemas) == 1
            
            # Read second CSV from same location
            df2 = dfdrift_pandas.read_csv(str(csv_path2))
            schemas = storage.load_schemas()
            
            # Should have 2 schemas (different read_csv calls)
            assert len(schemas) == 2
            
            # Find the schema with object dtype for id
            object_schema = None
            for schema in schemas.values():
                if schema['columns']['id']['dtype'] == 'object':
                    object_schema = schema
                    break
            
            assert object_schema is not None
            assert object_schema['columns']['value']['dtype'] == 'float64'

    def test_empty_dataframe_handling(self):
        """Test that empty DataFrames are handled correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            # Create empty DataFrame
            empty_df = dfdrift_pandas.DataFrame()
            
            # Should not create any schema entries
            schemas = storage.load_schemas()
            assert len(schemas) == 0
            
            # Create DataFrame with data
            data_df = dfdrift_pandas.DataFrame({'col': [1, 2, 3]})
            
            # Should create schema entry
            schemas = storage.load_schemas()
            assert len(schemas) == 1

    def test_dataframe_with_null_values(self):
        """Test schema tracking with null values"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            # DataFrame with null values
            df = dfdrift_pandas.DataFrame({
                'name': ['Alice', None, 'Charlie'],
                'age': [25, None, 35],
                'score': [85.5, 92.0, None]
            })
            
            schemas = storage.load_schemas()
            schema = list(schemas.values())[0]
            
            # Check null counts are tracked
            assert schema['columns']['name']['null_count'] == 1
            assert schema['columns']['name']['total_count'] == 3
            assert schema['columns']['age']['null_count'] == 1
            assert schema['columns']['score']['null_count'] == 1

    def test_shape_change_detection(self):
        """Test detection of shape changes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            def create_data():
                return dfdrift_pandas.DataFrame({'col': [1, 2, 3]})
            
            # First creation - 3 rows
            df1 = create_data()
            schemas = storage.load_schemas()
            initial_schema = list(schemas.values())[0]
            assert initial_schema['shape'] == [3, 1]
            
            # Simulate different data size at same location
            def create_data_larger():
                return dfdrift_pandas.DataFrame({'col': [1, 2, 3, 4, 5]})
            
            # Second creation - 5 rows (different function, so different location)
            df2 = create_data_larger()
            schemas = storage.load_schemas()
            
            # Should have 2 schemas now (different locations)
            assert len(schemas) == 2
            
            # Find the schema with 5 rows
            larger_schema = None
            for schema in schemas.values():
                if schema['shape'][0] == 5:
                    larger_schema = schema
                    break
            
            assert larger_schema is not None
            assert larger_schema['shape'] == [5, 1]