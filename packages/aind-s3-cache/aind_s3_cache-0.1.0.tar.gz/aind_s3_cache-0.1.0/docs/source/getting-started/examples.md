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

# Examples

Real-world examples demonstrating common aind-s3-cache workflows.

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

## Basic Examples

### Example 1: Multi-source JSON Loading

```{code-cell} python
from aind_s3_cache import get_json
import json

# Test different data sources with mock S3 data
data_sources = {
    "s3_metadata": "s3://aind-example-bucket/experiments/metadata.json",
    "s3_config": "s3://aind-example-bucket/config/cache_config.json",
    "s3_large_data": "s3://aind-example-bucket/data/large_dataset.json"
}

print("Testing multi-source JSON loading:")
print("-" * 50)

for source_name, source_uri in data_sources.items():
    try:
        data = get_json(source_uri)

        if isinstance(data, dict):
            keys = list(data.keys())[:5]  # First 5 keys
            print(f"✓ {source_name}: {len(data)} keys, sample: {keys}")
        else:
            print(f"✓ {source_name}: {type(data)} with {len(str(data))} chars")

    except Exception as e:
        print(f"✗ {source_name}: {e}")

print("\nAll sources processed!")
```
--------------------------------------------------
✓ s3_public: 15 keys, sample: ['describedBy', 'schema_version', 'acquisition', 'data_description', 'subject']
✓ s3_anonymous: 12 keys, sample: ['describedBy', 'schema_version', 'acquisition', 'data_description', 'subject']
✓ http: 4 keys, sample: ['userId', 'id', 'title', 'body']

All sources processed!
```

### Example 2: S3 Caching Performance Comparison

```python
from aind_s3_cache import get_local_path_for_resource, CacheManager
import time
import tempfile

def time_operation(description, operation):
    """Helper to time operations."""
    print(f"\n{description}...")
    start = time.time()
    result = operation()
    elapsed = time.time() - start
    print(f"  Completed in {elapsed:.2f}s")
    return result, elapsed

# Test file (use a reasonably sized public file)
test_uri = "s3://aind-open-data/exaspim_708373_2024-02-02_11-26-44/metadata.json"

print("S3 Caching Performance Test")
print("=" * 40)

with CacheManager(persistent=False) as cm:  # Clean cache each time
    print(f"Cache directory: {cm.dir}")

    # First download (no cache)
    result1, time1 = time_operation(
        "First download (cold cache)",
        lambda: get_local_path_for_resource(test_uri, cache_dir=cm.dir)
    )
    print(f"  From cache: {result1.from_cache}")
    print(f"  File size: {result1.path.stat().st_size} bytes")

    # Second access (warm cache)
    result2, time2 = time_operation(
        "Second access (warm cache)",
        lambda: get_local_path_for_resource(test_uri, cache_dir=cm.dir)
    )
    print(f"  From cache: {result2.from_cache}")

    # Third access (confirm cache consistency)
    result3, time3 = time_operation(
        "Third access (cache hit)",
        lambda: get_local_path_for_resource(test_uri, cache_dir=cm.dir)
    )
    print(f"  From cache: {result3.from_cache}")

    print(f"\nPerformance Summary:")
    print(f"  Initial download: {time1:.2f}s")
    print(f"  Cache hit #1: {time2:.2f}s ({time1/time2:.1f}x faster)")
    print(f"  Cache hit #2: {time3:.2f}s ({time1/time3:.1f}x faster)")
    print(f"  Cache speedup: {((time1 - time2) / time1 * 100):.1f}% faster")
```

### Example 3: Batch S3 Data Processing

```python
from aind_s3_cache import CacheManager, get_local_path_for_resource, get_json
import json
import time
from pathlib import Path

def analyze_metadata(metadata):
    """Simple analysis function."""
    return {
        "session_id": metadata.get("session_id"),
        "subject_id": metadata.get("subject_id"),
        "acquisition_datetime": metadata.get("acquisition", {}).get("acquisition_datetime"),
        "modality": metadata.get("acquisition", {}).get("instrument", {}).get("name", "unknown"),
        "has_processing": "processing" in metadata
    }

# Multiple datasets to process (example public datasets)
datasets = [
    "exaspim_708373_2024-02-02_11-26-44",
    "smartspim_679848_2024-01-12_14-33-35",
    # Add more dataset IDs as available in aind-open-data
]

def process_datasets_with_caching(dataset_ids, cache_dir=None):
    """Process multiple datasets efficiently with caching."""
    results = []

    with CacheManager(persistent=True, cache_dir=cache_dir) as cm:
        print(f"Using cache directory: {cm.dir}")
        print(f"Processing {len(dataset_ids)} datasets...\n")

        for i, dataset_id in enumerate(dataset_ids, 1):
            print(f"[{i}/{len(dataset_ids)}] Processing {dataset_id}")
            metadata_uri = f"s3://aind-open-data/{dataset_id}/metadata.json"

            try:
                # Time the cache operation
                start_time = time.time()
                cache_result = get_local_path_for_resource(metadata_uri, cache_dir=cm.dir)
                cache_time = time.time() - start_time

                # Load and analyze
                with open(cache_result.path) as f:
                    metadata = json.load(f)

                analysis = analyze_metadata(metadata)
                analysis.update({
                    "dataset_id": dataset_id,
                    "from_cache": cache_result.from_cache,
                    "cache_time": cache_time,
                    "file_size": cache_result.path.stat().st_size
                })

                results.append(analysis)

                status = "cache hit" if cache_result.from_cache else "downloaded"
                print(f"  ✓ {status} in {cache_time:.2f}s ({analysis['file_size']:,} bytes)")
                print(f"    Session: {analysis['session_id']}")
                print(f"    Subject: {analysis['subject_id']}")
                print(f"    Modality: {analysis['modality']}")

            except Exception as e:
                print(f"  ✗ Failed: {e}")
                results.append({
                    "dataset_id": dataset_id,
                    "error": str(e),
                    "success": False
                })

    return results

# Run the batch processing
print("Batch S3 Data Processing Example")
print("=" * 40)

results = process_datasets_with_caching(datasets, cache_dir="~/.aind_cache")

# Summary statistics
successful = [r for r in results if r.get("success", True)]
cache_hits = [r for r in successful if r.get("from_cache", False)]
downloads = [r for r in successful if not r.get("from_cache", False)]

print(f"\n📊 Processing Summary:")
print(f"   Total datasets: {len(results)}")
print(f"   Successful: {len(successful)}")
print(f"   Cache hits: {len(cache_hits)}")
print(f"   Downloads: {len(downloads)}")

if successful:
    avg_cache_time = sum(r["cache_time"] for r in successful) / len(successful)
    total_size = sum(r.get("file_size", 0) for r in successful)
    print(f"   Average access time: {avg_cache_time:.2f}s")
    print(f"   Total data processed: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")

if cache_hits and downloads:
    avg_download_time = sum(r["cache_time"] for r in downloads) / len(downloads)
    avg_cache_time = sum(r["cache_time"] for r in cache_hits) / len(cache_hits)
    speedup = avg_download_time / avg_cache_time if avg_cache_time > 0 else 0
    print(f"   Cache speedup: {speedup:.1f}x faster")
```

## Advanced Examples

### Example 4: Concurrent S3 Downloads

```python
from aind_s3_cache import CacheManager, get_local_path_for_resource
import concurrent.futures
import time
import json

def download_and_analyze(args):
    """Download file and perform basic analysis."""
    s3_uri, cache_dir = args
    dataset_id = s3_uri.split('/')[-2]  # Extract dataset ID from URI

    try:
        start_time = time.time()

        # Download/cache the file
        result = get_local_path_for_resource(s3_uri, cache_dir=cache_dir)
        download_time = time.time() - start_time

        # Analyze the content
        with open(result.path) as f:
            data = json.load(f)

        return {
            "dataset_id": dataset_id,
            "success": True,
            "from_cache": result.from_cache,
            "download_time": download_time,
            "file_size": result.path.stat().st_size,
            "session_id": data.get("session_id", "unknown"),
            "keys_count": len(data)
        }

    except Exception as e:
        return {
            "dataset_id": dataset_id,
            "success": False,
            "error": str(e),
            "download_time": time.time() - start_time
        }

def process_files_concurrently(s3_uris, max_workers=4):
    """Process multiple S3 files concurrently."""

    with CacheManager(persistent=True, cache_dir="~/.concurrent_cache") as cm:
        print(f"Processing {len(s3_uris)} files with {max_workers} workers")
        print(f"Cache directory: {cm.dir}")

        # Prepare arguments for concurrent processing
        args_list = [(uri, cm.dir) for uri in s3_uris]

        results = []
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_uri = {
                executor.submit(download_and_analyze, args): args[0]
                for args in args_list
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_uri):
                uri = future_to_uri[future]
                try:
                    result = future.result()
                    results.append(result)

                    if result["success"]:
                        status = "cached" if result["from_cache"] else "downloaded"
                        print(f"✓ {result['dataset_id']}: {status} in {result['download_time']:.2f}s")
                    else:
                        print(f"✗ {result['dataset_id']}: {result['error']}")

                except Exception as e:
                    print(f"✗ {uri}: Unexpected error: {e}")

        total_time = time.time() - start_time

        return results, total_time

# Example usage
s3_uris = [
    "s3://aind-open-data/exaspim_708373_2024-02-02_11-26-44/metadata.json",
    "s3://aind-open-data/smartspim_679848_2024-01-12_14-33-35/metadata.json",
    # Add more URIs as available
]

print("Concurrent S3 Downloads Example")
print("=" * 40)

# Process with different worker counts to show performance impact
for workers in [1, 2, 4]:
    print(f"\n🔄 Testing with {workers} worker(s):")
    results, total_time = process_files_concurrently(s3_uris, max_workers=workers)

    successful = [r for r in results if r["success"]]
    cache_hits = sum(1 for r in successful if r["from_cache"])
    downloads = len(successful) - cache_hits

    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful: {len(successful)}/{len(results)}")
    print(f"   Cache hits: {cache_hits}, Downloads: {downloads}")

    if successful:
        avg_time_per_file = total_time / len(successful)
        total_size = sum(r.get("file_size", 0) for r in successful)
        print(f"   Avg time per file: {avg_time_per_file:.2f}s")
        print(f"   Total data: {total_size:,} bytes")
```

### Example 5: Cache Management and Cleanup

```python
from aind_s3_cache import CacheManager, get_local_path_for_resource
from pathlib import Path
import shutil
import time
import os

def get_directory_size(path):
    """Calculate total size of directory."""
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += get_directory_size(entry.path)
    return total

def demonstrate_cache_strategies():
    """Demonstrate different caching strategies and cleanup."""

    test_uri = "s3://aind-open-data/exaspim_708373_2024-02-02_11-26-44/metadata.json"

    print("Cache Management Strategies Demo")
    print("=" * 40)

    # Strategy 1: Ephemeral cache (auto-cleanup)
    print("\n1. Ephemeral Cache (Auto-cleanup)")
    with CacheManager(persistent=False) as cm:
        print(f"   Cache dir: {cm.dir}")
        result = get_local_path_for_resource(test_uri, cache_dir=cm.dir)
        print(f"   Cached file size: {result.path.stat().st_size:,} bytes")
        print(f"   Cache exists: {cm.dir.exists()}")
        temp_dir = cm.dir  # Save reference to check after context

    print(f"   After context - Cache exists: {temp_dir.exists()}")
    print("   ✓ Cache automatically cleaned up")

    # Strategy 2: Persistent cache
    print("\n2. Persistent Cache")
    persistent_cache = Path.home() / ".aind_s3_cache_demo"

    with CacheManager(cache_dir=persistent_cache) as cm:
        print(f"   Cache dir: {cm.dir}")

        # First access
        start_time = time.time()
        result1 = get_local_path_for_resource(test_uri, cache_dir=cm.dir)
        time1 = time.time() - start_time

        cache_size_before = get_directory_size(cm.dir)
        print(f"   First access: {time1:.2f}s, from_cache: {result1.from_cache}")
        print(f"   Cache size: {cache_size_before:,} bytes")

        # Second access
        start_time = time.time()
        result2 = get_local_path_for_resource(test_uri, cache_dir=cm.dir)
        time2 = time.time() - start_time

        print(f"   Second access: {time2:.2f}s, from_cache: {result2.from_cache}")
        print(f"   Speedup: {time1/time2:.1f}x faster")

    print(f"   After context - Cache exists: {persistent_cache.exists()}")
    print(f"   Cache persists with {len(list(persistent_cache.rglob('*')))} files")

    # Strategy 3: Manual cache cleanup
    print("\n3. Manual Cache Cleanup")

    def cleanup_cache(cache_dir, max_age_days=7, dry_run=True):
        """Clean up old cache files."""
        if not cache_dir.exists():
            return 0, 0

        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        removed_count = 0
        removed_size = 0

        for file_path in cache_dir.rglob("*"):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_size = file_path.stat().st_size
                if not dry_run:
                    file_path.unlink()
                removed_count += 1
                removed_size += file_size
                print(f"   {'Would remove' if dry_run else 'Removed'}: {file_path.name} ({file_size:,} bytes)")

        return removed_count, removed_size

    # Simulate old files (for demo purposes, we'll just analyze current files)
    removed_count, removed_size = cleanup_cache(persistent_cache, max_age_days=0, dry_run=True)
    print(f"   Found {removed_count} files that would be cleaned ({removed_size:,} bytes)")

    # Actually clean up the demo cache
    if persistent_cache.exists():
        shutil.rmtree(persistent_cache)
        print("   ✓ Demo cache cleaned up")

    # Strategy 4: Size-based cache management
    print("\n4. Cache Size Monitoring")

    def check_cache_size(cache_dir, max_size_mb=100):
        """Check if cache exceeds size limit."""
        if not cache_dir.exists():
            return 0, False

        total_size = get_directory_size(cache_dir)
        total_size_mb = total_size / 1024 / 1024
        exceeds_limit = total_size_mb > max_size_mb

        print(f"   Cache size: {total_size_mb:.2f} MB")
        print(f"   Limit: {max_size_mb} MB")
        print(f"   Exceeds limit: {exceeds_limit}")

        return total_size, exceeds_limit

    # Create a temporary cache for testing
    with CacheManager(persistent=True, cache_dir="~/.size_test_cache") as cm:
        # Download a file
        result = get_local_path_for_resource(test_uri, cache_dir=cm.dir)

        # Check size
        total_size, exceeds = check_cache_size(cm.dir, max_size_mb=0.1)  # Very small limit for demo

        if exceeds:
            print("   ⚠️  Cache size exceeds limit - cleanup recommended")
        else:
            print("   ✓ Cache size within limits")

# Run the demonstration
demonstrate_cache_strategies()
```

### Example 6: Error Handling and Retry Logic

```python
from aind_s3_cache import get_json, get_local_path_for_resource
from botocore.exceptions import ClientError, NoCredentialsError
import time
import random

def resilient_s3_access(uri, max_retries=3, backoff_factor=2.0):
    """Access S3 resource with retry logic and comprehensive error handling."""

    for attempt in range(max_retries + 1):
        try:
            print(f"  Attempt {attempt + 1}/{max_retries + 1}: {uri}")

            start_time = time.time()
            result = get_local_path_for_resource(uri)
            access_time = time.time() - start_time

            print(f"    ✓ Success in {access_time:.2f}s (from_cache: {result.from_cache})")
            return result

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            print(f"    ✗ AWS Error: {error_code}")

            if error_code in ['NoSuchBucket', 'NoSuchKey']:
                print(f"    Resource not found - not retrying")
                break
            elif error_code == 'AccessDenied':
                print(f"    Access denied - check permissions")
                break
            elif error_code in ['ServiceUnavailable', 'SlowDown']:
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    print(f"    Service unavailable - waiting {wait_time:.1f}s before retry")
                    time.sleep(wait_time)
                    continue
            else:
                print(f"    Unexpected AWS error: {e}")
                break

        except NoCredentialsError:
            print(f"    ✗ No AWS credentials found")
            break

        except Exception as e:
            print(f"    ✗ Unexpected error: {e}")
            if attempt < max_retries:
                wait_time = backoff_factor ** attempt
                print(f"    Waiting {wait_time:.1f}s before retry")
                time.sleep(wait_time)

    print(f"    Failed after {max_retries + 1} attempts")
    return None

def test_error_scenarios():
    """Test various error scenarios and recovery."""

    print("Error Handling and Retry Logic Example")
    print("=" * 50)

    test_cases = [
        {
            "name": "Valid public file",
            "uri": "s3://aind-open-data/exaspim_708373_2024-02-02_11-26-44/metadata.json",
            "expected": "success"
        },
        {
            "name": "Non-existent bucket",
            "uri": "s3://definitely-does-not-exist-bucket-12345/file.json",
            "expected": "no_such_bucket"
        },
        {
            "name": "Non-existent key",
            "uri": "s3://aind-open-data/definitely/does/not/exist.json",
            "expected": "no_such_key"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   URI: {test_case['uri']}")

        result = resilient_s3_access(test_case['uri'], max_retries=2)

        if result:
            print(f"   Result: Success - {result.path}")
        else:
            print(f"   Result: Failed as expected ({test_case['expected']})")

def demonstrate_json_error_handling():
    """Demonstrate JSON-specific error handling."""

    print("\n" + "="*50)
    print("JSON Error Handling Examples")
    print("="*50)

    def safe_get_json(uri, description):
        """Safely load JSON with detailed error reporting."""
        print(f"\nTesting: {description}")
        print(f"URI: {uri}")

        try:
            result = get_json(uri)
            print(f"✓ Success: Loaded {len(result)} keys")
            return result

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            print(f"✗ AWS Error: {error_code}")

        except ValueError as e:
            print(f"✗ JSON Parse Error: {e}")

        except TypeError as e:
            print(f"✗ Type Error: {e}")

        except Exception as e:
            print(f"✗ Unexpected Error: {type(e).__name__}: {e}")

        return None

    # Test cases for JSON error handling
    test_cases = [
        ("Valid JSON file", "s3://aind-open-data/exaspim_708373_2024-02-02_11-26-44/metadata.json"),
        ("Non-existent file", "s3://aind-open-data/does-not-exist.json"),
        ("Invalid JSON URL", "https://httpbin.org/xml"),  # Returns XML, not JSON
    ]

    results = []
    for description, uri in test_cases:
        result = safe_get_json(uri, description)
        results.append((description, result is not None))

    print(f"\n📊 JSON Loading Results:")
    for description, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {description}")

# Run the demonstrations
test_error_scenarios()
demonstrate_json_error_handling()
```

These examples demonstrate the full range of aind-s3-cache capabilities, from
basic data loading to complex caching strategies and error handling. Each
example includes practical code that you can adapt for your specific use cases.
