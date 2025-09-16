import inspect
import pandas as _pd
from typing import Any, Optional
from .validator import DfValidator, SchemaStorage, Alerter

_global_validator: Optional[DfValidator] = None


def configure_validation(storage: Optional[SchemaStorage] = None, alerter: Optional[Alerter] = None) -> None:
    global _global_validator
    _global_validator = DfValidator(storage=storage, alerter=alerter)


def _validate_dataframe(df: _pd.DataFrame) -> None:
    if _global_validator is None or len(df) == 0:
        return
    
    frame = inspect.currentframe()
    if frame is None:
        return
    
    try:
        caller_frame = frame.f_back.f_back
        if caller_frame is None:
            return
        
        filename = caller_frame.f_code.co_filename
        line_number = caller_frame.f_lineno
        location_key = f"{filename}:{line_number}"
        
        current_schema = _global_validator._get_dataframe_schema(df)
        
        existing_schemas = _global_validator.storage.load_schemas()
        if location_key in existing_schemas:
            previous_schema = existing_schemas[location_key]
            if not _global_validator._schemas_equal(previous_schema, current_schema):
                differences = _global_validator._get_schema_differences(previous_schema, current_schema)
                _global_validator.alerter.alert(
                    f"DataFrame schema changed at {location_key}. Changes: {differences}",
                    location_key,
                    previous_schema,
                    current_schema
                )
        
        _global_validator.storage.save_schema(location_key, current_schema)
    except Exception:
        pass
    finally:
        del frame


class DataFrame(_pd.DataFrame):
    def __init__(self, data=None, index=None, columns=None, dtype=None, copy=None):
        super().__init__(data=data, index=index, columns=columns, dtype=dtype, copy=copy)
        _validate_dataframe(self)
    
    @classmethod
    def from_dict(cls, data, orient='columns', dtype=None, columns=None):
        df = super().from_dict(data, orient=orient, dtype=dtype, columns=columns)
        _validate_dataframe(df)
        return df


def read_csv(*args, **kwargs):
    df = _pd.read_csv(*args, **kwargs)
    _validate_dataframe(df)
    return df


def read_excel(*args, **kwargs):
    df = _pd.read_excel(*args, **kwargs)
    _validate_dataframe(df)
    return df


def read_json(*args, **kwargs):
    df = _pd.read_json(*args, **kwargs)
    _validate_dataframe(df)
    return df


def read_parquet(*args, **kwargs):
    df = _pd.read_parquet(*args, **kwargs)
    _validate_dataframe(df)
    return df


def __getattr__(name: str) -> Any:
    return getattr(_pd, name)