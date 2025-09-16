# Caching Strategies Guide

This guide covers effective caching strategies and cache management with aind-s3-cache.

## Cache Types

### Ephemeral Cache (Auto-cleanup)
```python
from aind_s3_cache import CacheManager, get_local_path_for_resource

# Temporary cache - automatically cleaned up
with CacheManager(persistent=False) as cm:
    result = get_local_path_for_resource("s3://bucket/file.json", cache_dir=cm.dir)
    # Use result.path...
# Cache directory automatically deleted
```

### Persistent Cache (Default Location)
```python
# Persistent cache in ~/.cache/s3-ants
with CacheManager(persistent=True) as cm:
    result = get_local_path_for_resource("s3://bucket/file.json", cache_dir=cm.dir)
    # Files remain cached between sessions
```

### Custom Cache Location
```python
# Use specific directory
with CacheManager(cache_dir="~/.my_app_cache") as cm:
    result = get_local_path_for_resource("s3://bucket/file.json", cache_dir=cm.dir)

# High-performance storage
with CacheManager(cache_dir="/nvme/fast_cache") as cm:
    result = get_local_path_for_resource("s3://bucket/large_file.dat", cache_dir=cm.dir)
```

## Cache Strategies by Use Case

### Short-term Processing
- **Use**: Ephemeral cache (`persistent=False`)
- **Benefits**: Automatic cleanup, no disk space concerns
- **Best for**: One-time analysis, temporary workflows

### Repeated Analysis  
- **Use**: Persistent cache with consistent location
- **Benefits**: Faster subsequent access, reduced network usage
- **Best for**: Development, iterative analysis

### Production Workflows
- **Use**: Custom cache location on fast storage
- **Benefits**: Predictable performance, controlled location
- **Best for**: Automated pipelines, high-throughput processing

## Performance Optimization

### ETag-based Validation
Files are automatically re-downloaded only when changed on S3:

```python
# First access - downloads file
result1 = get_local_path_for_resource("s3://bucket/file.json")
print(f"From cache: {result1.from_cache}")  # False

# Second access - uses cache
result2 = get_local_path_for_resource("s3://bucket/file.json") 
print(f"From cache: {result2.from_cache}")  # True

# If file changes on S3, automatically re-downloads
```

### Cache Management

```python
# Monitor cache size
def get_cache_size(cache_dir):
    total_size = sum(f.stat().st_size for f in Path(cache_dir).rglob('*') if f.is_file())
    return total_size

# Clean old cache files
def cleanup_old_files(cache_dir, max_age_days=30):
    cutoff_time = time.time() - (max_age_days * 24 * 3600)
    for file_path in Path(cache_dir).rglob("*"):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            file_path.unlink()
```

## Best Practices

1. **Choose appropriate cache strategy**: Match cache lifetime to your use case
2. **Monitor cache size**: Set up periodic cleanup for long-running applications  
3. **Use fast storage**: Place caches on SSD/NVMe for better performance
4. **Consider concurrency**: aind-s3-cache handles concurrent access safely
5. **Plan cache location**: Ensure sufficient disk space and appropriate permissions