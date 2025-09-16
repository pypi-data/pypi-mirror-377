# dfdrift

A DataFrame schema drift detection and alerting library for pandas DataFrames.

## Features

- **Schema Tracking**: Automatically save DataFrame schemas with location information (file:line)
- **Change Detection**: Detect schema changes between executions and alert when differences are found
- **Configurable Storage**: Support for local file storage and Google Cloud Storage with extensible interface for future cloud storage
- **Configurable Alerting**: Built-in stderr alerter and Slack integration with extensible interface for future integrations

## Installation

```bash
# Basic installation
pip install dfdrift

# With Slack support
pip install dfdrift[slack]

# With Google Cloud Storage support
pip install dfdrift[gcs]

# With all optional features
pip install dfdrift[slack,gcs]

# Development installation
uv pip install -e .
```

## Usage

dfdrift offers two ways to validate DataFrames:

### 1. Import Replacement

Simply replace your pandas import with dfdrift.pandas:

```python
import dfdrift.pandas as pd

# Configure validation (optional - uses default settings if omitted)
pd.configure_validation()

# All DataFrame operations are automatically validated
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['Tokyo', 'Osaka', 'Kyoto']
})
# Schema automatically saved with location info
```

### 2. Explicit Validation

```python
import pandas as pd
import dfdrift

# Create a validator instance
validator = dfdrift.DfValidator()

# Validate a DataFrame manually
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'city': ['Tokyo', 'Osaka', 'Kyoto']
})

validator.validate(df)
```

## Configuration

### Custom Storage

#### Local File Storage
```python
import dfdrift.pandas as pd

# Use custom local directory
pd.configure_validation(
    storage=dfdrift.LocalFileStorage("./my_schemas")
)
```

#### Google Cloud Storage
```python
import dfdrift.pandas as pd

# Configure GCS storage (requires: pip install dfdrift[gcs])
# Set GCS_BUCKET and optionally GCS_PREFIX environment variables
gcs_storage = dfdrift.GcsStorage()  # bucket and prefix from env vars
pd.configure_validation(storage=gcs_storage)

# Or pass parameters directly
gcs_storage = dfdrift.GcsStorage(
    bucket="my-dfdrift-bucket",
    prefix="schemas/production"  # Optional, defaults to "dfdrift"
)
pd.configure_validation(storage=gcs_storage)
```

**GCS Authentication**: Use one of the following methods:
- Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable to service account key file
- Use Application Default Credentials: `gcloud auth application-default login`
- Use Workload Identity in GKE/Cloud Run environments

### Custom Alerter

#### Stderr Alerter (Default)
```python
import dfdrift.pandas as pd

# Built-in stderr alerter (default)
pd.configure_validation(alerter=dfdrift.StderrAlerter())
```

#### Slack Alerter
```python
import dfdrift.pandas as pd

# Configure Slack alerts (requires: pip install dfdrift[slack])
# Set SLACK_BOT_TOKEN and SLACK_CHANNEL environment variables
slack_alerter = dfdrift.SlackAlerter()  # Uses env vars
pd.configure_validation(alerter=slack_alerter)

# Or specify channel argument (token from env var)
slack_alerter = dfdrift.SlackAlerter(channel="#data-alerts")
pd.configure_validation(alerter=slack_alerter)

# Or pass both token and channel directly (not recommended for production)
slack_alerter = dfdrift.SlackAlerter(
    channel="#data-alerts",
    token="xoxb-your-bot-token"
)
pd.configure_validation(alerter=slack_alerter)
```

#### Custom Alerter
```python
import dfdrift

# Implement your own alerter
class CustomAlerter(dfdrift.Alerter):
    def alert(self, message, location_key, old_schema, new_schema):
        # Send to email, webhook, etc.
        pass

pd.configure_validation(alerter=CustomAlerter())
```

## Schema Change Detection

When a DataFrame schema changes between executions, dfdrift will automatically detect and alert:

- **Added columns**: New columns that weren't in the previous schema
- **Removed columns**: Columns that existed before but are now missing
- **Type changes**: When a column's dtype changes (e.g., int64 → object)
- **Shape changes**: When the DataFrame dimensions change

Example alert output:
```
WARNING: DataFrame schema changed at /path/to/file.py:25. Changes: Added columns: ['new_col']; Column 'age' dtype changed: int64 → object
Location: /path/to/file.py:25
```

## Examples

See the `samples/` directory for usage examples:

- `samples/sample.py`: Explicit validation
- `samples/sample_custom_path.py`: Custom storage path
- `samples/sample_changing_schema.py`: Schema change detection demo
- `samples/sample_pandas_import.py`: Import replacement

## Architecture

### Storage Interface

```python
class SchemaStorage(ABC):
    def save_schema(self, location_key: str, schema: Dict[str, Any]) -> None:
        pass
    
    def load_schemas(self) -> Dict[str, Any]:
        pass
```

### Alerter Interface

```python
class Alerter(ABC):
    def alert(self, message: str, location_key: str, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> None:
        pass
```

## Schema Format

Schemas are stored as JSON with the following structure:

```json
{
  "/path/to/file.py:line_number": {
    "columns": {
      "column_name": {
        "dtype": "int64",
        "null_count": 0,
        "total_count": 100
      }
    },
    "shape": [100, 3]
  }
}
```

## Development

Run the samples to test functionality:

```bash
# Import replacement
uv run python samples/sample_pandas_import.py  # Run twice to see alerts

# Explicit validation
uv run python samples/sample.py

# Test schema change detection
uv run python samples/sample_changing_schema.py  # Run twice to see alerts
```