---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Quick Start

Get up and running with aind-s3-cache in minutes. This guide covers the most common use cases.

```{code-cell} python
:tags: [hide-cell]
# Set up mock S3 environment for examples
import sys
from pathlib import Path

# Add the docs/source directory to path to find _mock_setup
docs_source_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()
if not (docs_source_path / '_mock_setup.py').exists():
    # Look for docs/source directory from current working directory
    docs_source_path = Path.cwd()
    if (docs_source_path / 'docs' / 'source' / '_mock_setup.py').exists():
        docs_source_path = docs_source_path / 'docs' / 'source'
    elif (docs_source_path / '_mock_setup.py').exists():
        pass  # Already in the right directory
    else:
        # Find it in parent directories
        current = docs_source_path
        while current.parent != current:
            if (current / 'docs' / 'source' / '_mock_setup.py').exists():
                docs_source_path = current / 'docs' / 'source'
                break
            current = current.parent

sys.path.insert(0, str(docs_source_path))

from _mock_setup import MockS3Context
mock_ctx = MockS3Context()
mock_ctx.__enter__()
```

## 5-Minute Start

### 1. Install

```bash
pip install aind-s3-cache
```

### 2. Load JSON from Any Source

```{code-cell} python
from aind_s3_cache import get_json

# Load from S3 (automatic anonymous access)
config = get_json("s3://aind-example-bucket/experiments/metadata.json")

# Load from HTTP URL (would work with real URLs)
# api_data = get_json("https://api.example.com/data.json")

# Load from local file (would work with real files)
# local_data = get_json("/path/to/local/file.json")

print(f"Session date: {config.get('session_date', 'N/A')}")
print(f"Subject: {config.get('subject', 'N/A')}")
print(f"Experiment ID: {config.get('experiment_id', 'N/A')}")
```

### 3. Cache S3 Resources Locally

```{code-cell} python
from aind_s3_cache import get_local_path_for_resource, CacheManager

# Simple caching (uses default cache location)
result = get_local_path_for_resource("s3://aind-example-bucket/data/large_dataset.json", 
                                    cache_dir=mock_ctx.cache_dir)
print(f"Cached to: {result.path}")
print(f"From cache: {result.from_cache}")  # False on first call

# Second call uses cached version
result2 = get_local_path_for_resource("s3://aind-example-bucket/data/large_dataset.json",
                                     cache_dir=mock_ctx.cache_dir)
print(f"From cache: {result2.from_cache}")  # True on subsequent calls

# Process the local file
with open(result.path) as f:
    import json
    data = json.load(f)
    print(f"Dataset contains {len(data.get('neuronal_data', {}).get('units', []))} units")
```

## Common Workflows

### Workflow 1: Multi-source Data Processing

```python
from aind_s3_cache import get_json
import json

# Process data from multiple sources
data_sources = [
    "s3://aind-open-data/dataset1/metadata.json",
    "https://api.example.com/dataset2.json",
    "/local/path/dataset3.json"
]

results = []
for source in data_sources:
    try:
        data = get_json(source)
        results.append({
            "source": source,
            "session_id": data.get("session_id", "unknown"),
            "success": True
        })
        print(f"✓ Loaded {source}")
    except Exception as e:
        results.append({
            "source": source,
            "error": str(e),
            "success": False
        })
        print(f"✗ Failed {source}: {e}")

print(f"Successfully loaded {sum(r['success'] for r in results)}/{len(results)} sources")
```

### Workflow 2: Efficient S3 Data Processing with Caching

```python
from aind_s3_cache import CacheManager, get_local_path_for_resource
import json
import time

# Process multiple S3 files efficiently with caching
s3_files = [
    "s3://aind-open-data/dataset1/metadata.json",
    "s3://aind-open-data/dataset2/metadata.json",
    "s3://aind-open-data/dataset3/metadata.json"
]

results = []
with CacheManager(persistent=True, cache_dir="~/.aind_cache") as cm:
    print(f"Using cache directory: {cm.dir}")

    for s3_uri in s3_files:
        print(f"\nProcessing {s3_uri}...")

        # Time the download/cache access
        start_time = time.time()
        cache_result = get_local_path_for_resource(s3_uri, cache_dir=cm.dir)
        download_time = time.time() - start_time

        # Process local file (much faster than repeated S3 access)
        with open(cache_result.path) as f:
            metadata = json.load(f)

        analysis = {
            "session_id": metadata.get("session_id"),
            "subject_id": metadata.get("subject_id"),
            "from_cache": cache_result.from_cache,
            "download_time": download_time
        }

        results.append(analysis)

        status = "cache hit" if cache_result.from_cache else "downloaded"
        print(f"  {status} in {download_time:.2f}s")

# Summary
cache_hits = sum(1 for r in results if r["from_cache"])
downloads = len(results) - cache_hits
print(f"\nProcessed {len(results)} files:")
print(f"  Cache hits: {cache_hits}")
print(f"  Downloads: {downloads}")
print(f"  Average time: {sum(r['download_time'] for r in results) / len(results):.2f}s")
```

### Workflow 3: URI Manipulation and Path Handling

```{code-cell} python
from aind_s3_cache import parse_s3_uri, join_any, is_url, is_file_path

# Parse S3 URIs
bucket, key = parse_s3_uri("s3://aind-example-bucket/experiments/metadata.json")
print(f"Bucket: {bucket}, Key: {key}")

# Build paths programmatically (works for both S3 and local paths)
base_uri = "s3://aind-example-bucket/experiment_123"
metadata_uri = join_any(base_uri, "processed", "metadata.json")
data_uri = join_any(base_uri, "processed", "data.json")

print(f"Metadata URI: {metadata_uri}")
print(f"Data URI: {data_uri}")

# Detect path types
test_paths = [
    "s3://bucket/file.json",
    "https://example.com/data.json",
    "/local/path/file.json",
    "C:\\Windows\\path\\file.json"
]

for path in test_paths:
    print(f"{path:<35} -> URL: {is_url(path)}, File: {is_file_path(path)}")
```

### Workflow 4: Anonymous vs Authenticated S3 Access

```python
from aind_s3_cache import get_json_s3, get_json_s3_uri
import boto3

# Public data - automatic anonymous access
public_data = get_json("s3://aind-open-data/public/metadata.json")

# Explicit anonymous access
public_data2 = get_json_s3(
    bucket="aind-open-data",
    key="public/metadata.json",
    anonymous=True
)

# Private data - custom S3 client with credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id='your_access_key',
    aws_secret_access_key='your_secret_key',
    region_name='us-west-2'
)

private_data = get_json_s3(
    bucket="private-bucket",
    key="confidential/data.json",
    s3_client=s3_client
)

# Private data - using credential chain (environment variables, ~/.aws/credentials, etc.)
private_data2 = get_json_s3(
    bucket="private-bucket",
    key="data.json",
    anonymous=False  # Use credential chain
)
```

## Essential Concepts

### Cache Management Strategies

Choose the right caching strategy for your use case:

```python
from aind_s3_cache import CacheManager

# 1. Ephemeral cache (auto-cleanup) - for short-term processing
with CacheManager(persistent=False) as cm:
    # Process files, cache automatically deleted after context
    result = get_local_path_for_resource("s3://bucket/file.json", cache_dir=cm.dir)
    # Use result.path...
# Cache directory automatically cleaned up

# 2. Persistent cache (default location) - for repeated access
with CacheManager(persistent=True) as cm:
    # Files remain cached in ~/.cache/s3-ants between sessions
    result = get_local_path_for_resource("s3://bucket/file.json", cache_dir=cm.dir)

# 3. Custom cache location - for high-performance or specific requirements
with CacheManager(cache_dir="/fast/nvme/cache") as cm:
    # Use fastest available storage for cache
    result = get_local_path_for_resource("s3://bucket/file.json", cache_dir=cm.dir)
```

### Performance Optimization

Tips for optimal performance:

```python
import concurrent.futures
from aind_s3_cache import get_local_path_for_resource

# 1. Use concurrent downloads for multiple files
def download_file(s3_uri, cache_dir):
    return get_local_path_for_resource(s3_uri, cache_dir=cache_dir)

s3_uris = [
    "s3://bucket/file1.json",
    "s3://bucket/file2.json",
    "s3://bucket/file3.json"
]

# Download files in parallel
with CacheManager(persistent=True) as cm:
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(download_file, uri, cm.dir) for uri in s3_uris]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

# 2. Configure download parameters for large files
large_file_result = get_local_path_for_resource(
    "s3://bucket/large-file.dat",
    max_concurrency=32,  # More concurrent connections
    multipart_threshold_bytes=16 * 1024 * 1024,  # 16MB threshold for multipart
    anonymous=True
)
```

## Data Sources

### Public AIND Data

Access Allen Institute public datasets without credentials:

```python
from aind_s3_cache import get_json

# Browse available public datasets
public_bucket = "s3://aind-open-data/"

# Example datasets (check AWS S3 console or CLI for complete list)
datasets = [
    "exaspim_708373_2024-02-02_11-26-44",
    "smartspim_679848_2024-01-12_14-33-35",
    # ... more datasets available
]

# No AWS credentials needed for public data
for dataset in datasets:
    try:
        metadata_uri = f"{public_bucket}{dataset}/metadata.json"
        metadata = get_json(metadata_uri)  # Works automatically
        print(f"Dataset: {metadata.get('session_id', dataset)}")
    except Exception as e:
        print(f"Could not access {dataset}: {e}")
```

### Private S3 Data

Configure AWS credentials for private data access:

```python
import boto3
import os

# Method 1: Environment variables (recommended for CI/CD)
os.environ['AWS_ACCESS_KEY_ID'] = 'your_key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_secret'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'

# Method 2: AWS credentials file (~/.aws/credentials)
# [default]
# aws_access_key_id = your_key
# aws_secret_access_key = your_secret
# region = us-west-2

# Method 3: Custom S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id='your_key',
    aws_secret_access_key='your_secret',
    region_name='us-west-2'
)

# Use with aind-s3-cache
from aind_s3_cache import get_json_s3
data = get_json_s3("private-bucket", "data.json", s3_client=s3_client)
```

## Performance Tips

### 1. Use Appropriate Cache Strategy

```python
# For one-time processing: ephemeral cache
with CacheManager(persistent=False) as cm:
    process_files(cache_dir=cm.dir)

# For repeated analysis: persistent cache
with CacheManager(cache_dir="~/.aind_cache") as cm:
    analyze_datasets(cache_dir=cm.dir)

# For high-performance: fast local storage
with CacheManager(cache_dir="/nvme/cache") as cm:
    process_large_files(cache_dir=cm.dir)
```

### 2. Batch Operations

```python
# Process multiple files efficiently
with CacheManager(persistent=True) as cm:
    for uri in s3_uris:
        result = get_local_path_for_resource(uri, cache_dir=cm.dir)
        # Process result.path locally (much faster than repeated S3 access)
```

### 3. Concurrent Downloads

```python
# Use ThreadPoolExecutor for I/O-bound operations
import concurrent.futures

def process_dataset(uri):
    data = get_json(f"{uri}/metadata.json")
    return analyze_data(data)

# Parallel processing
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_dataset, dataset_uris))
```

## Next Steps

Now that you're up and running:

1. **Explore User Guides**: Detailed documentation for specific features
   - [S3 Integration](../user-guide/s3-integration.md)
   - [JSON Utilities](../user-guide/json-utilities.md)
   - [URI/Path Utilities](../user-guide/uri-path-utilities.md)

2. **Check API Reference**: Complete function documentation
   - [s3_cache module](../api-reference/s3_cache.rst)
   - [json_utils module](../api-reference/json_utils.rst)
   - [uri_utils module](../api-reference/uri_utils.rst)

3. **See Examples**: Real-world usage scenarios
   - [Examples Overview](examples.md)

## Common Next Steps

**For Data Analysis**:
```python
# Load and cache datasets efficiently
with CacheManager(persistent=True) as cm:
    metadata = get_json("s3://aind-open-data/dataset/metadata.json")
    # Process metadata for analysis pipeline
```

**For Application Integration**:
```python
# Integrate with existing applications
config = get_json("s3://config-bucket/app-config.json")
app.configure(config)
```

**For Batch Processing**:
```python
# Process multiple datasets with caching
results = []
with CacheManager(cache_dir="~/.batch_cache") as cm:
    for dataset_uri in dataset_list:
        data = get_json(f"{dataset_uri}/metadata.json")
        results.append(process_dataset(data))
```

```{code-cell} python
:tags: [hide-cell]
# Clean up mock environment
mock_ctx.__exit__(None, None, None)
```
