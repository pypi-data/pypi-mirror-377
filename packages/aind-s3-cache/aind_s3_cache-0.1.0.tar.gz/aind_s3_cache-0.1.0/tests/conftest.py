"""
Shared testing infrastructure for aind-s3-cache.

This module provides unified mock objects and fixtures to be used across
all test modules, reducing duplication and ensuring consistent behavior.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from botocore.exceptions import ClientError

# ============================================================================
# S3 Infrastructure
# ============================================================================


class UnifiedS3Client:
    """
    Comprehensive S3 client mock supporting all operations across modules.

    Extends the original DummyS3Client pattern to support:
    - Basic operations (get_object, list_objects)
    - Advanced operations (head_object, download_file)
    - Error simulation (ClientError with various HTTP codes)
    - Range requests for s3_cache peek operations
    """

    def __init__(
        self,
        data: dict = None,
        *,
        etag: str = "mock-etag-12345",
        content_length: int = 1024,
        simulate_head_blocked: bool = False,
        simulate_errors: dict = None,
    ) -> None:
        self.data = data or {}
        self.etag = etag
        self.content_length = content_length
        self.simulate_head_blocked = simulate_head_blocked
        self.simulate_errors = simulate_errors or {}

        # Track downloads for validation
        self.downloads = []

    # ---- Core S3 Operations (from original DummyS3Client) ----

    def get_object(self, Bucket: str, Key: str, Range: str = None):
        """Mock S3 get_object with optional Range support for s3_cache."""
        if f"{Bucket}/{Key}" in self.simulate_errors:
            error_code = self.simulate_errors[f"{Bucket}/{Key}"]
            raise ClientError(
                {"ResponseMetadata": {"HTTPStatusCode": error_code}},
                "GetObject",
            )

        headers = {"etag": f'"{self.etag}"'}

        # Handle range requests for s3_cache peek operations
        if Range and Range.startswith("bytes="):
            # Parse range like "bytes=0-0"
            range_match = re.match(r"bytes=(\d+)-(\d+)", Range)
            if range_match:
                start, end = range_match.groups()
                headers["content-range"] = f"bytes {start}-{end}/{self.content_length}"

        return {
            "Body": self,
            "ETag": f'"{self.etag}"',
            "ResponseMetadata": {"HTTPHeaders": headers},
        }

    def head_object(self, Bucket: str, Key: str):
        """Mock S3 head_object with optional blocking simulation."""
        if self.simulate_head_blocked:
            raise ClientError({"ResponseMetadata": {"HTTPStatusCode": 403}}, "HeadObject")

        if f"{Bucket}/{Key}" in self.simulate_errors:
            error_code = self.simulate_errors[f"{Bucket}/{Key}"]
            raise ClientError(
                {"ResponseMetadata": {"HTTPStatusCode": error_code}},
                "HeadObject",
            )

        return {
            "ETag": f'"{self.etag}"',
            "ContentLength": self.content_length,
        }

    def download_file(self, Bucket: str, Key: str, Filename: str, Config=None) -> None:
        """Mock S3 download_file for s3_cache testing."""
        self.downloads.append((Bucket, Key, Filename))

        if f"{Bucket}/{Key}" in self.simulate_errors:
            error_code = self.simulate_errors[f"{Bucket}/{Key}"]
            raise ClientError(
                {"ResponseMetadata": {"HTTPStatusCode": error_code}},
                "GetObject",
            )

        # Create mock file content
        Path(Filename).parent.mkdir(parents=True, exist_ok=True)
        with open(Filename, "w") as f:
            f.write(json.dumps(self.data))

    # ---- File-like interface for Body operations ----

    def read(self, *args, **kwargs):
        return json.dumps(self.data).encode()

    def __iter__(self):
        return iter([json.dumps(self.data).encode()])

    def __next__(self):
        raise StopIteration

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def readlines(self):
        return [json.dumps(self.data).encode()]

    def readline(self):
        return json.dumps(self.data).encode()

    def seek(self, *args, **kwargs) -> None:
        pass

    def tell(self) -> int:
        return 0

    # ---- Dict-like interface compatibility ----

    def __getitem__(self, item):
        return self.data[item]

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return repr(self.data)

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return 1

    def __contains__(self, item) -> bool:
        return item in self.data

    def __eq__(self, other):
        if hasattr(other, "data"):
            return self.data == other.data
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self.data))

    def __call__(self, *args, **kwargs):
        return self.data

    def __getattr__(self, item):
        return getattr(self.data, item)

    def __setattr__(self, key, value) -> None:
        if key in (
            "data",
            "etag",
            "content_length",
            "simulate_head_blocked",
            "simulate_errors",
            "downloads",
        ):
            object.__setattr__(self, key, value)
        else:
            setattr(self.data, key, value)


class DummyResponse:
    """HTTP response mock for requests operations."""

    def __init__(self, json_data: dict, status_code: int = 200) -> None:
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self) -> None:
        if self.status_code != 200:
            raise Exception("HTTP Error")


@pytest.fixture
def mock_s3_client():
    """Provide a unified S3 client mock for all tests."""
    return UnifiedS3Client()


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for URL-based JSON fetching."""

    def _mock_get(url, **kwargs):
        # Default response data
        return DummyResponse({"mocked": "data", "url": url})

    return _mock_get
