# API Reference

Complete API documentation for all modules in aind-s3-cache.

## Quick Reference

### Core Functions

```{eval-rst}
.. autosummary::
   :nosignatures:

   aind_s3_cache.get_local_path_for_resource
   aind_s3_cache.get_json
   aind_s3_cache.parse_s3_uri
   aind_s3_cache.CacheManager
   aind_s3_cache.LocalizedResource
```

### JSON Utilities

```{eval-rst}
.. autosummary::
   :nosignatures:

   aind_s3_cache.get_json_s3
   aind_s3_cache.get_json_url
```

### URI/Path Utilities

```{eval-rst}
.. autosummary::
   :nosignatures:

   aind_s3_cache.is_url
   aind_s3_cache.is_file_path
   aind_s3_cache.join_any
```

## Module Documentation

```{toctree}
:maxdepth: 2

s3_cache
json_utils
uri_utils
```

## Module Overview

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| **s3_cache** | S3 resource caching | `get_local_path_for_resource`, `CacheManager`, `LocalizedResource` |
| **json_utils** | Multi-source JSON loading | `get_json`, `get_json_s3`, `get_json_url` |
| **uri_utils** | URI/path manipulation | `parse_s3_uri`, `join_any`, `is_url`, `is_file_path` |