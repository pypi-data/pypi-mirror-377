# Installation

## Requirements

- Python 3.12 or higher
- pip or uv (recommended)

## Install from PyPI

```bash
uv add aind-s3-cache
# or with pip instead:
pip install aind-s3-cache
```

## Development Installation

If you want to contribute to aind-s3-cache or need the latest development version:

### Using uv (Recommended)

```bash
git clone https://github.com/AllenNeuralDynamics/aind-s3-cache.git
cd aind-s3-cache
uv sync
```

### Using pip

```bash
git clone https://github.com/AllenNeuralDynamics/aind-s3-cache.git
cd aind-s3-cache
pip install -e . --group dev
```

## Verify Installation

Test that aind-s3-cache is installed correctly:

```python
import aind_s3_cache
print(f"aind-s3-cache version: {aind_s3_cache.__version__}")

# Test basic functionality
from aind_s3_cache import get_json, parse_s3_uri

# Test URI parsing
bucket, key = parse_s3_uri("s3://my-bucket/path/file.json")
print(f"Parsed S3 URI: bucket='{bucket}', key='{key}'")
```

## Dependency Groups

aind-s3-cache has minimal required dependencies, but you may want to install additional packages for specific use cases:

### For Development

```bash
pip install aind-s3-cache --group dev
# or with uv (dev implied)
uv sync
```

This includes:
- **Testing**: pytest, pytest-cov
- **Linting**: ruff, mypy
- **Type checking**: boto3-stubs, types-requests

### For Documentation

```bash
pip install aind-s3-cache --group docs
# or with uv
uv sync --group docs
```

This includes:
- **Sphinx**: Documentation building
- **Furo**: Modern documentation theme
- **MyST Parser**: Markdown support in Sphinx

## AWS Configuration (Optional)

For accessing private S3 buckets, configure AWS credentials using one of these methods:

### Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

### AWS Credentials File

Create `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
region = us-west-2
```

### AWS SSO or IAM Roles

Configure AWS SSO or use IAM roles if running on AWS infrastructure.

**Note**: No AWS configuration is needed for accessing public buckets like `aind-open-data`.

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Check installation
pip list | grep aind-s3-cache

# Reinstall if needed
pip uninstall aind-s3-cache
pip install aind-s3-cache
```

### Missing Dependencies

If you get "ModuleNotFoundError" for optional dependencies:

```bash
# Install all optional dependencies
pip install aind-s3-cache --group dev --group docs
```

### AWS Permission Issues

If you get AWS permission errors:

1. **For public data**: No credentials needed, ensure you're using `anonymous=True` or letting the library auto-detect
2. **For private data**: Verify your AWS credentials are configured correctly
3. **For cross-region access**: Ensure your credentials have permissions for the target region

## Next Steps

Once installed, continue to the [Quick Start](quickstart.md) guide to learn the basics, or explore the [Examples](examples.md) for real-world usage patterns.
