"""Small library providing a transparent local cache for S3 objects."""

__version__ = "0.1.0"

# Core S3 caching functionality
# Multi-source JSON reading
from .json_utils import get_json, get_json_s3, get_json_url
from .s3_cache import CacheManager, LocalizedResource, get_local_path_for_resource

# URI and path utilities
from .uri_utils import is_file_path, is_url, join_any, parse_s3_uri

__all__ = [
    # Version
    "__version__",
    # Core S3 caching
    "get_local_path_for_resource",
    "CacheManager",
    "LocalizedResource",
    # JSON utilities
    "get_json",
    "get_json_s3",
    "get_json_url",
    # URI/path utilities
    "parse_s3_uri",
    "is_url",
    "is_file_path",
    "join_any",
]
