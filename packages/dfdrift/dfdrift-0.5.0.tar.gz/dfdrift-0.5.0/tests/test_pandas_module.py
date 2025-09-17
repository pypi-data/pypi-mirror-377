import pytest
import pandas as pd
import tempfile
from unittest.mock import Mock, patch

import dfdrift.pandas as dfdrift_pandas
from dfdrift.storages import LocalFileStorage


class TestPandasModule:
    def test_configure_validation(self):
        storage = Mock()
        alerter = Mock()
        
        dfdrift_pandas.configure_validation(storage=storage, alerter=alerter)
        
        assert dfdrift_pandas._global_validator is not None
        assert dfdrift_pandas._global_validator.storage is storage
        assert dfdrift_pandas._global_validator.alerter is alerter

    def test_configure_validation_defaults(self):
        dfdrift_pandas.configure_validation()
        
        assert dfdrift_pandas._global_validator is not None
        assert isinstance(dfdrift_pandas._global_validator.storage, LocalFileStorage)

    def test_dataframe_creation_with_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            df = dfdrift_pandas.DataFrame({
                'name': ['Alice', 'Bob'],
                'age': [25, 30]
            })
            
            assert isinstance(df, dfdrift_pandas.DataFrame)
            assert len(df) == 2
            
            # Check that schema was saved
            schemas = storage.load_schemas()
            assert len(schemas) > 0

    def test_dataframe_from_dict_with_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            df = dfdrift_pandas.DataFrame.from_dict({
                'id': [1, 2, 3],
                'score': [85.5, 92.0, 78.5]
            })
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 3
            
            # Check that schema was saved
            schemas = storage.load_schemas()
            assert len(schemas) > 0

    def test_read_csv_with_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test CSV file
            csv_path = f"{tmpdir}/test.csv"
            pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']}).to_csv(csv_path, index=False)
            
            storage = LocalFileStorage(tmpdir)
            dfdrift_pandas.configure_validation(storage=storage)
            
            df = dfdrift_pandas.read_csv(csv_path)
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2
            
            # Check that schema was saved
            schemas = storage.load_schemas()
            assert len(schemas) > 0

    def test_read_functions_exist(self):
        # Test that all read functions exist
        assert hasattr(dfdrift_pandas, 'read_csv')
        assert hasattr(dfdrift_pandas, 'read_excel') 
        assert hasattr(dfdrift_pandas, 'read_json')
        assert hasattr(dfdrift_pandas, 'read_parquet')

    def test_getattr_fallback(self):
        # Test that pandas attributes are accessible
        assert hasattr(dfdrift_pandas, '__version__')  # pandas version
        assert hasattr(dfdrift_pandas, 'Series')       # pandas Series
        assert hasattr(dfdrift_pandas, 'concat')       # pandas functions

    def test_empty_dataframe_not_validated(self):
        storage = Mock()
        dfdrift_pandas.configure_validation(storage=storage)
        
        # Empty dataframe should not be validated
        df = dfdrift_pandas.DataFrame()
        
        # _validate_dataframe should not be called for empty df
        storage.save_schema.assert_not_called()

    def test_validation_with_no_global_validator(self):
        # Reset global validator
        dfdrift_pandas._global_validator = None
        
        # Should not raise error
        df = dfdrift_pandas.DataFrame({'col': [1, 2, 3]})
        assert isinstance(df, dfdrift_pandas.DataFrame)

    def test_inheritance_from_pandas_dataframe(self):
        df = dfdrift_pandas.DataFrame({'col': [1, 2, 3]})
        
        # Should inherit all pandas DataFrame methods
        assert hasattr(df, 'head')
        assert hasattr(df, 'tail')
        assert hasattr(df, 'describe')
        assert hasattr(df, 'groupby')
        
        # Test some basic operations work
        assert len(df.head(2)) == 2
        assert df['col'].sum() == 6