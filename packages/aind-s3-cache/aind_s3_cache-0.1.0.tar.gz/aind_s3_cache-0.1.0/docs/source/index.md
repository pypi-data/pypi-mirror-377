# AIND S3 Cache

A Python utility library developed by Allen Institute for Neural Dynamics for working with S3 objects and multi-source JSON data. This package enables transparent local caching of S3 resources, unified JSON loading from multiple sources, and cross-platform URI/path manipulation.

## Key Features

- **S3 Caching**: Transparent local caching with ETag-based validation and anonymous access support
- **Multi-source JSON Reading**: Unified JSON loading from local files, HTTP URLs, and S3 URIs
- **Cross-platform URI/Path Utilities**: Robust handling of local paths, Windows UNC paths, and S3 URIs
- **Cache Management**: Flexible persistent and ephemeral caching strategies
- **Anonymous Access**: Built-in support for public S3 buckets without credentials
- **Atomic Operations**: Concurrent-safe file operations for reliable caching

## Quick Start

```python
from aind_s3_cache import get_local_path_for_resource, CacheManager, get_json

# S3 caching with automatic anonymous access
result = get_local_path_for_resource("s3://aind-open-data/dataset/file.json")
with open(result.path) as f:
    data = f.read()

# Multi-source JSON loading
config = get_json("s3://bucket/config.json")  # or HTTP URL or local path
metadata = get_json("https://api.example.com/data.json")
local_data = get_json("/path/to/file.json")

# Managed caching
with CacheManager(persistent=True, cache_dir="~/.aind_cache") as cm:
    # All S3 operations will be cached efficiently
    result = get_local_path_for_resource("s3://bucket/large-file.dat", cache_dir=cm.dir)
```

## Documentation

```{toctree}
:maxdepth: 2
:caption: Contents

getting-started/index
user-guide/index
api-reference/index
```

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
