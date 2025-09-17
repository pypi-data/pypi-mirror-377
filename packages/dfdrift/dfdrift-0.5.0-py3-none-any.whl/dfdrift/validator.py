import inspect
import pandas as pd
from typing import Dict, Any

from .alerters import Alerter, StderrAlerter
from .storages import SchemaStorage, LocalFileStorage



class DfValidator:
    def __init__(self, storage: SchemaStorage = None, alerter: Alerter = None):
        self.storage = storage if storage is not None else LocalFileStorage()
        self.alerter = alerter if alerter is not None else StderrAlerter()
    
    def validate(self, df: pd.DataFrame) -> None:
        frame = inspect.currentframe()
        if frame is None:
            return
        
        caller_frame = frame.f_back
        if caller_frame is None:
            return
        
        filename = caller_frame.f_code.co_filename
        line_number = caller_frame.f_lineno
        location_key = f"{filename}:{line_number}"
        
        current_schema = self._get_dataframe_schema(df)
        
        existing_schemas = self.storage.load_schemas()
        if location_key in existing_schemas:
            previous_schema = existing_schemas[location_key]
            if not self._schemas_equal(previous_schema, current_schema):
                differences = self._get_schema_differences(previous_schema, current_schema)
                self.alerter.alert(
                    f"DataFrame schema changed at {location_key}. Changes: {differences}",
                    location_key,
                    previous_schema,
                    current_schema
                )
        
        self.storage.save_schema(location_key, current_schema)
    
    def _get_dataframe_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        schema = {}
        for column in df.columns:
            schema[column] = {
                "dtype": str(df[column].dtype),
                "null_count": int(df[column].isnull().sum()),
                "total_count": len(df)
            }
        
        return {
            "columns": schema,
            "shape": list(df.shape)
        }
    
    def _schemas_equal(self, schema1: Dict[str, Any], schema2: Dict[str, Any]) -> bool:
        # Compare only column dtypes, not shape or row counts (these can vary)
        columns1 = schema1.get("columns", {})
        columns2 = schema2.get("columns", {})
        
        if set(columns1.keys()) != set(columns2.keys()):
            return False
        
        for column in columns1:
            if columns1[column]["dtype"] != columns2[column]["dtype"]:
                return False
        
        return True
    
    def _get_schema_differences(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> str:
        differences = []
        
        old_columns = set(old_schema.get("columns", {}).keys())
        new_columns = set(new_schema.get("columns", {}).keys())
        
        added_columns = new_columns - old_columns
        removed_columns = old_columns - new_columns
        common_columns = old_columns & new_columns
        
        if added_columns:
            differences.append(f"Added columns: {list(added_columns)}")
        if removed_columns:
            differences.append(f"Removed columns: {list(removed_columns)}")
        
        for column in common_columns:
            old_col = old_schema["columns"][column]
            new_col = new_schema["columns"][column]
            if old_col["dtype"] != new_col["dtype"]:
                differences.append(f"Column '{column}' dtype changed: {old_col['dtype']} → {new_col['dtype']}")
        
        # Note: Shape (row count) changes are ignored as they are expected to vary
        
        return "; ".join(differences) if differences else "Unknown change"


