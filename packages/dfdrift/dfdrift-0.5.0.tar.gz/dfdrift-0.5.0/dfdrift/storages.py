import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Union, Optional


class SchemaStorage(ABC):
    @abstractmethod
    def save_schema(self, location_key: str, schema: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def load_schemas(self) -> Dict[str, Any]:
        pass


class LocalFileStorage(SchemaStorage):
    def __init__(self, storage_path: Union[str, Path] = ".dfdrift_schemas"):
        self.storage_path = Path(storage_path)
        self.schema_file = self.storage_path / "schemas.json"
    
    def save_schema(self, location_key: str, schema: Dict[str, Any]) -> None:
        self.storage_path.mkdir(exist_ok=True)
        
        all_schemas = self.load_schemas()
        all_schemas[location_key] = schema
        
        with open(self.schema_file, "w", encoding="utf-8") as f:
            json.dump(all_schemas, f, indent=2, ensure_ascii=False)
    
    def load_schemas(self) -> Dict[str, Any]:
        if self.schema_file.exists():
            with open(self.schema_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}


class GcsStorage(SchemaStorage):
    def __init__(self, bucket: Optional[str] = None, prefix: Optional[str] = None):
        self.bucket = bucket or os.getenv("DFDRIFT_GCS_BUCKET")
        self.prefix = prefix or os.getenv("DFDRIFT_GCS_PREFIX", "dfdrift")
        
        if not self.bucket:
            raise ValueError("GCS bucket must be provided either as argument or DFDRIFT_GCS_BUCKET environment variable")
        
        # Ensure prefix doesn't start with / and ends with /
        if self.prefix.startswith("/"):
            self.prefix = self.prefix[1:]
        if not self.prefix.endswith("/"):
            self.prefix += "/"
            
        self.schema_blob_name = f"{self.prefix}schemas.json"
        self.client = self._import_gcs_client()
    
    def _import_gcs_client(self):
        """Import Google Cloud Storage client"""
        try:
            from google.cloud import storage
            return storage.Client()
        except ImportError:
            raise ImportError("google-cloud-storage package is required for GcsStorage. Install with: pip install dfdrift[gcs]")
    
    def save_schema(self, location_key: str, schema: Dict[str, Any]) -> None:
        try:
            # Load existing schemas
            all_schemas = self.load_schemas()
            all_schemas[location_key] = schema
            
            # Save to GCS
            bucket = self.client.bucket(self.bucket)
            blob = bucket.blob(self.schema_blob_name)
            
            schema_json = json.dumps(all_schemas, indent=2, ensure_ascii=False)
            blob.upload_from_string(schema_json, content_type="application/json")
            
        except Exception as e:
            raise RuntimeError(f"Failed to save schema to GCS: {e}")
    
    def load_schemas(self) -> Dict[str, Any]:
        try:
            bucket = self.client.bucket(self.bucket)
            blob = bucket.blob(self.schema_blob_name)
            
            if blob.exists():
                schema_json = blob.download_as_text()
                return json.loads(schema_json)
            return {}
            
        except Exception as e:
            # Return empty dict if file doesn't exist or other errors
            return {}