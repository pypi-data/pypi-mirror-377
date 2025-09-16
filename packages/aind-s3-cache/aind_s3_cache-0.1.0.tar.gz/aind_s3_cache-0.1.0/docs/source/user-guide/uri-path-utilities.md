# URI and Path Utilities Guide

This guide covers cross-platform path handling and URI manipulation utilities in aind-s3-cache.

## Overview

The URI utilities module provides robust, cross-platform support for:

- **Path Type Detection**: Distinguish between URLs, local paths, and special cases
- **S3 URI Parsing**: Extract bucket and key components from S3 URIs  
- **Cross-platform Path Handling**: Support Windows UNC paths, drive letters, and POSIX paths
- **Scheme-aware Path Joining**: Build paths correctly for both local and S3 schemes

## Core Functions

### Path Type Detection

```python
from aind_s3_cache import is_url, is_file_path

# URL detection  
assert is_url("https://example.com/data.json") == True
assert is_url("s3://bucket/file.json") == True
assert is_url("/local/path.json") == False

# File path detection
assert is_file_path("/local/path.json") == True  
assert is_file_path("C:\\Windows\\file.json") == True
assert is_file_path("https://example.com") == False
```

### S3 URI Parsing

```python
from aind_s3_cache import parse_s3_uri

# Parse S3 URIs
bucket, key = parse_s3_uri("s3://my-bucket/path/to/file.txt") 
# Returns: ("my-bucket", "path/to/file.txt")

# Handles edge cases
bucket, key = parse_s3_uri("s3://bucket/")
# Returns: ("bucket", "")
```

### Cross-platform Path Manipulation

```python
from aind_s3_cache import join_any, as_pathlike, as_string

# Join paths (works for both local and S3)
s3_result = join_any("s3://bucket/base", "subdir", "file.txt")
# Returns: "s3://bucket/base/subdir/file.txt"

local_result = join_any("/home/user", "documents", "file.txt") 
# Returns: "/home/user/documents/file.txt"

# Windows paths
windows_result = join_any("C:\\Users\\Name", "Documents", "file.txt")
# Returns: "C:\\Users\\Name\\Documents\\file.txt"
```

## Advanced Usage

### Normalize and Reconstruct URIs

```python  
from aind_s3_cache import as_pathlike, as_string

# Parse into components
kind, bucket, path = as_pathlike("s3://bucket/path/file.txt")
print(f"Kind: {kind}, Bucket: {bucket}, Path: {path}")
# Kind: s3, Bucket: bucket, Path: path/file.txt

# Reconstruct URI
reconstructed = as_string(kind, bucket, path)
# Returns: "s3://bucket/path/file.txt"

# Works with local paths too
kind, bucket, path = as_pathlike("/home/user/file.txt")
# Kind: file, Bucket: None, Path: /home/user/file.txt
```

### Cross-platform Compatibility

```python
# Windows UNC paths
unc_path = "\\\\server\\share\\file.txt"
kind, bucket, path = as_pathlike(unc_path)
# Handles UNC paths correctly across platforms

# File URIs
file_uri = "file:///absolute/path/file.txt" 
kind, bucket, path = as_pathlike(file_uri)
# Converts to native path representation
```

## Best Practices

1. **Use `join_any()` for path building**: Works correctly with both local and S3 schemes
2. **Validate URIs before processing**: Use `is_url()` and `is_file_path()` to check inputs
3. **Handle cross-platform differences**: The utilities automatically handle Windows vs POSIX paths
4. **Normalize URIs for comparison**: Use `as_pathlike()` and `as_string()` for consistent formatting