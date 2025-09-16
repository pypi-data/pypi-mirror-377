"""Mock setup utilities for documentation examples.

This module provides mock S3 services and sample data for documentation
code examples to run without real network dependencies.
"""

import json
import tempfile

import boto3

try:
    from moto import mock_s3
except ImportError:
    # Fallback if moto is not available
    class MockS3Fallback:
        def start(self):
            pass

        def stop(self):
            pass

    def mock_s3():
        return MockS3Fallback()


# Sample JSON data for examples
SAMPLE_METADATA = {
    "experiment_id": "exp_001",
    "session_date": "2024-01-15",
    "subject": "mouse_42",
    "conditions": ["baseline", "stimulus"],
    "data_files": ["recording_001.zarr", "recording_002.zarr"],
}

SAMPLE_CONFIG = {
    "cache_dir": "/tmp/s3_cache",
    "max_cache_size_gb": 10,
    "etag_validation": True,
    "download_timeout": 300,
}

SAMPLE_LARGE_JSON = {
    "neuronal_data": {
        "units": [{"unit_id": i, "spike_times": [0.1 * j for j in range(10)]} for i in range(100)],
        "channels": {f"ch_{i:03d}": {"impedance": 1000 + i} for i in range(384)},
    },
    "stimulus_info": {"trials": [{"trial_id": i, "stimulus_type": "grating", "angle": i * 30} for i in range(50)]},
}


class MockS3Context:
    """Context manager for setting up mock S3 environment."""

    def __init__(self):
        self.mock_s3 = mock_s3()
        self.temp_dir = None

    def __enter__(self):
        """Set up mock S3 with sample data."""
        self.mock_s3.start()

        # Create mock S3 client
        s3_client = boto3.client(
            "s3", region_name="us-west-2", aws_access_key_id="testing", aws_secret_access_key="testing"
        )

        # Create test bucket
        s3_client.create_bucket(
            Bucket="aind-example-bucket", CreateBucketConfiguration={"LocationConstraint": "us-west-2"}
        )

        # Upload sample files
        s3_client.put_object(
            Bucket="aind-example-bucket",
            Key="experiments/metadata.json",
            Body=json.dumps(SAMPLE_METADATA, indent=2),
            ContentType="application/json",
        )

        s3_client.put_object(
            Bucket="aind-example-bucket",
            Key="config/cache_config.json",
            Body=json.dumps(SAMPLE_CONFIG, indent=2),
            ContentType="application/json",
        )

        s3_client.put_object(
            Bucket="aind-example-bucket",
            Key="data/large_dataset.json",
            Body=json.dumps(SAMPLE_LARGE_JSON, indent=2),
            ContentType="application/json",
        )

        # Create a temporary directory for caching examples
        self.temp_dir = tempfile.mkdtemp(prefix="s3_cache_docs_")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up mock environment."""
        self.mock_s3.stop()
        if self.temp_dir:
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    @property
    def cache_dir(self):
        """Get temporary cache directory path."""
        return self.temp_dir


def setup_mock_environment():
    """Set up mock S3 environment for examples (standalone function)."""
    return MockS3Context()
