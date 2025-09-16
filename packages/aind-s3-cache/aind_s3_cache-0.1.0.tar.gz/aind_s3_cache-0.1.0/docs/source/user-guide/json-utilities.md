# JSON Utilities Guide

This guide covers multi-source JSON loading capabilities in aind-s3-cache, including unified access to local files, HTTP URLs, and S3 URIs.

## Overview

The JSON utilities module provides a unified interface for loading JSON data from multiple sources:

- **Local files**: Traditional filesystem access with proper encoding
- **HTTP/HTTPS URLs**: Web API and remote resource access
- **S3 URIs**: Both anonymous and authenticated S3 access
- **File URIs**: Cross-platform `file://` URI support

All functions return parsed Python dictionaries and include comprehensive error handling.

## Core Functions

### get_json(): Universal JSON Loader

The `get_json()` function is the primary interface that automatically detects the source type and loads JSON appropriately:

```python
from aind_s3_cache import get_json

# Local file
config = get_json("/path/to/config.json")

# HTTP URL  
api_data = get_json("https://api.example.com/data.json")

# S3 URI (automatic anonymous access for public buckets)
metadata = get_json("s3://aind-open-data/dataset/metadata.json")

# File URI (cross-platform)
file_data = get_json("file:///path/to/data.json")
```

### Specialized Functions

For more control or specific use cases, use the specialized functions:

```python
from aind_s3_cache import get_json_s3, get_json_s3_uri, get_json_url

# Direct S3 bucket/key access
s3_data = get_json_s3(
    bucket="my-bucket",
    key="path/to/data.json",
    anonymous=True  # Explicit anonymous access
)

# S3 URI with explicit parameters
s3_uri_data = get_json_s3_uri(
    uri="s3://bucket/data.json",
    anonymous=False  # Use credential chain
)

# Direct HTTP/HTTPS access
web_data = get_json_url("https://api.example.com/endpoint.json")
```

## Source Type Detection

The `get_json()` function automatically detects source types using the following logic:

### S3 URIs
```python
# Detected as S3
get_json("s3://bucket/file.json")
get_json("S3://BUCKET/FILE.JSON")  # Case insensitive
```

### HTTP/HTTPS URLs
```python
# Detected as web URLs
get_json("https://api.example.com/data.json")
get_json("http://example.com/file.json")
```

### File URIs
```python
# Detected as file URIs
get_json("file:///absolute/path/file.json")
get_json("file://server/share/file.json")  # UNC paths on Windows
```

### Local Paths
```python
# Detected as local paths
get_json("/absolute/path/file.json")        # POSIX
get_json("relative/path/file.json")         # Relative paths
get_json("C:\\Windows\\path\\file.json")    # Windows absolute
get_json("\\\\server\\share\\file.json")   # Windows UNC
```

## Authentication and Access Control

### Anonymous S3 Access

For public S3 buckets, no credentials are required:

```python
# Automatic anonymous access for known public buckets
public_data = get_json("s3://aind-open-data/public/data.json")

# Explicit anonymous access
public_data2 = get_json_s3(
    bucket="public-bucket",
    key="data.json", 
    anonymous=True
)
```

### Authenticated S3 Access

For private S3 buckets, provide credentials using standard AWS methods:

#### Method 1: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

```python
# Will automatically use environment credentials
private_data = get_json("s3://private-bucket/confidential.json")
```

#### Method 2: AWS Credentials File
Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
region = us-west-2
```

#### Method 3: Custom S3 Client
```python
import boto3

# Create custom S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id='your_key',
    aws_secret_access_key='your_secret',
    region_name='us-west-2'
)

# Use custom client
private_data = get_json_s3(
    bucket="private-bucket",
    key="data.json",
    s3_client=s3_client
)
```

## Error Handling Patterns

### Comprehensive Error Handling

```python
from aind_s3_cache import get_json
from botocore.exceptions import ClientError, NoCredentialsError
import requests

def safe_load_json(source):
    """Load JSON with comprehensive error handling."""
    try:
        return get_json(source)
        
    except ClientError as e:
        # AWS/S3 specific errors
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        print(f"AWS Error {error_code}: {e}")
        
        if error_code == 'NoSuchBucket':
            print("The S3 bucket does not exist")
        elif error_code == 'NoSuchKey':
            print("The file was not found in the bucket")
        elif error_code == 'AccessDenied':
            print("Access denied - check your permissions")
            
    except NoCredentialsError:
        print("AWS credentials not found")
        
    except requests.HTTPError as e:
        # HTTP request errors
        print(f"HTTP Error {e.response.status_code}: {e}")
        
    except ValueError as e:
        # JSON parsing errors
        print(f"Invalid JSON: {e}")
        
    except FileNotFoundError:
        print("Local file not found")
        
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        
    return None

# Usage
data = safe_load_json("s3://bucket/file.json")
if data is not None:
    print(f"Loaded {len(data)} keys successfully")
```

### Retry Logic for Network Operations

```python
import time
import random

def resilient_json_load(source, max_retries=3):
    """Load JSON with retry logic for network failures."""
    
    for attempt in range(max_retries):
        try:
            return get_json(source)
            
        except (requests.ConnectionError, requests.Timeout, ClientError) as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time:.1f}s")
                time.sleep(wait_time)
                continue
            else:
                print(f"Failed after {max_retries} attempts: {e}")
                raise
                
    return None
```

## Type Safety and Validation

### JSON Structure Validation

```python
from aind_s3_cache import get_json
from typing import Dict, Any, Optional

def load_config(source: str) -> Optional[Dict[str, Any]]:
    """Load and validate configuration JSON."""
    try:
        data = get_json(source)
        
        # Validate expected structure
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object, got {type(data)}")
            
        # Check for required keys
        required_keys = ['version', 'settings']
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")
            
        return data
        
    except Exception as e:
        print(f"Configuration load failed: {e}")
        return None

# Usage
config = load_config("s3://config-bucket/app-config.json")
if config:
    version = config['version']
    settings = config['settings']
```

### Schema Validation with Pydantic

```python
from aind_s3_cache import get_json
from pydantic import BaseModel, ValidationError
from typing import List, Optional

class DatasetMetadata(BaseModel):
    session_id: str
    subject_id: str
    acquisition_datetime: str
    modality: str
    processing_level: Optional[str] = None
    
class Config(BaseModel):
    version: str
    datasets: List[DatasetMetadata]
    cache_settings: dict

def load_validated_config(source: str) -> Optional[Config]:
    """Load and validate JSON against Pydantic schema."""
    try:
        raw_data = get_json(source)
        config = Config(**raw_data)  # Validates structure
        return config
        
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None
    except Exception as e:
        print(f"Load failed: {e}")
        return None

# Usage
config = load_validated_config("s3://bucket/structured-config.json")
if config:
    print(f"Config version: {config.version}")
    print(f"Found {len(config.datasets)} datasets")
```

## Performance Optimization

### Concurrent JSON Loading

```python
from aind_s3_cache import get_json
import concurrent.futures
from typing import Dict, List, Any

def load_json_files_concurrently(sources: List[str], max_workers: int = 4) -> Dict[str, Any]:
    """Load multiple JSON files concurrently."""
    
    def load_single(source: str) -> tuple[str, Any]:
        try:
            data = get_json(source)
            return source, data
        except Exception as e:
            return source, {"error": str(e)}
    
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_source = {executor.submit(load_single, source): source for source in sources}
        
        # Collect results
        for future in concurrent.futures.as_completed(future_to_source):
            source, result = future.result()
            results[source] = result
            
    return results

# Usage
sources = [
    "s3://bucket/config1.json",
    "https://api.example.com/data.json", 
    "/local/path/file.json"
]

results = load_json_files_concurrently(sources)
for source, data in results.items():
    if "error" in data:
        print(f"Failed to load {source}: {data['error']}")
    else:
        print(f"Loaded {source}: {len(data)} keys")
```

### Caching Frequently Accessed JSON

```python
from aind_s3_cache import get_json
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def cached_get_json(source: str, cache_key: str = None) -> dict:
    """Cache JSON loads in memory with LRU eviction."""
    return get_json(source)

def get_cache_key(source: str, params: dict = None) -> str:
    """Generate cache key for parameterized requests."""
    key_data = source
    if params:
        key_data += str(sorted(params.items()))
    return hashlib.md5(key_data.encode()).hexdigest()

# Usage - same file will be cached
config1 = cached_get_json("s3://bucket/config.json")
config2 = cached_get_json("s3://bucket/config.json")  # Cache hit
```

## Integration Examples

### Configuration Management

```python
from aind_s3_cache import get_json
import os
from typing import Dict, Any

class ConfigManager:
    """Hierarchical configuration management with multiple sources."""
    
    def __init__(self, sources: List[str]):
        self.sources = sources
        self.config = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from all sources in order (later overrides earlier)."""
        for source in self.sources:
            try:
                data = get_json(source)
                self.config.update(data)
                print(f"✓ Loaded config from {source}")
            except Exception as e:
                print(f"⚠ Failed to load {source}: {e}")
                
        return self.config
    
    def get(self, key: str, default=None):
        """Get configuration value with default."""
        return self.config.get(key, default)

# Usage - hierarchical configuration
config_sources = [
    "/etc/app/default.json",                    # System defaults
    "s3://config-bucket/production.json",      # Environment config  
    os.path.expanduser("~/.app-config.json"),  # User overrides
]

config = ConfigManager(config_sources)
config.load()

# Access configuration values
database_url = config.get("database_url", "sqlite:///:memory:")
cache_size = config.get("cache_size", 100)
```

### Data Pipeline Integration

```python
from aind_s3_cache import get_json
from pathlib import Path
import logging

class DataPipeline:
    """Example pipeline using JSON metadata."""
    
    def __init__(self, manifest_source: str):
        self.manifest = get_json(manifest_source)
        self.logger = logging.getLogger(__name__)
        
    def process_datasets(self):
        """Process all datasets listed in manifest."""
        datasets = self.manifest.get("datasets", [])
        
        for dataset_config in datasets:
            try:
                self._process_dataset(dataset_config)
                self.logger.info(f"✓ Processed {dataset_config['id']}")
            except Exception as e:
                self.logger.error(f"✗ Failed {dataset_config['id']}: {e}")
                
    def _process_dataset(self, config: dict):
        """Process individual dataset."""
        dataset_id = config["id"]
        metadata_source = config["metadata_uri"]
        
        # Load dataset metadata
        metadata = get_json(metadata_source)
        
        # Process based on metadata
        session_id = metadata["session_id"]
        modality = metadata.get("acquisition", {}).get("instrument", {}).get("name")
        
        print(f"Processing {dataset_id}: {session_id} ({modality})")
        # ... actual processing logic

# Usage
manifest_uri = "s3://pipeline-config/processing-manifest.json"
pipeline = DataPipeline(manifest_uri)
pipeline.process_datasets()
```

## Best Practices

1. **Use `get_json()` for simplicity**: Let the function auto-detect source types unless you need specific control

2. **Handle errors gracefully**: Network operations can fail; always include error handling

3. **Validate JSON structure**: Check for expected keys and data types before processing

4. **Cache frequently accessed data**: Use in-memory caching or file caching for repeated access

5. **Use concurrent loading**: Load multiple JSON files in parallel for better performance

6. **Specify explicit parameters**: When you need control over authentication or caching behavior

7. **Prefer environment variables**: For credentials, use standard AWS environment variables or credential files

8. **Monitor data sources**: Include logging to track which sources are accessed and any failures

## Troubleshooting

### Common Issues and Solutions

**JSON Parse Errors**:
```python
try:
    data = get_json(source)
except ValueError as e:
    print(f"Invalid JSON in {source}: {e}")
    # Check if source returns HTML error page instead of JSON
```

**S3 Access Denied**:
```python
try:
    data = get_json("s3://private-bucket/file.json")
except ClientError as e:
    if e.response['Error']['Code'] == 'AccessDenied':
        # Try with explicit anonymous access for public buckets
        data = get_json_s3("private-bucket", "file.json", anonymous=True)
```

**HTTP Timeouts**:
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# For HTTP sources, you may need custom session configuration
# This is handled automatically by get_json, but for direct requests:
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

**File Encoding Issues**:
- All JSON files are assumed to be UTF-8 encoded
- If you encounter encoding errors, check the source file encoding
- The library handles BOM (Byte Order Mark) automatically