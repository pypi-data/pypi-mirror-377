# Reprompt Python SDK

A modern, type-safe Python client for the Reprompt Place Enrichment API. This **read-only** SDK provides access to jobs and batches data with full async support, parallel processing, and automatic request/response validation.

## Installation

```bash
pip install reprompt
```

## Development

### Quick Start

```bash
# Install with test dependencies
pip install -e ".[test]"

# Run the complete CI pipeline locally (equivalent to GitHub Actions)
tox -e lint,type,py312,build
```

### Manual Commands

```bash
# Testing
pytest                          # Run unit tests
pytest -m integration           # Run integration tests
pytest tests/test_client.py     # Run specific test file

# Code Quality
black src tests                 # Format code
flake8 src                      # Style checking
pylint src/reprompt             # Linting
pyright src                     # Type checking

# Building
flit build                      # Build wheel and sdist
```

## Quick Start

```python
from reprompt import RepromptClient

# Read data from Reprompt API (recommended: use context manager)
with RepromptClient(api_key="your-api-key", org_slug="your-org-slug") as client:
    # List all batches
    batches = client.batches.list_batches()
    for batch in batches:
        print(f"Batch: {batch.batch_name} - {batch.status}")

    # Get batch details
    batch = client.batches.get_batch("batch-id")
    print(f"Batch status: {batch.status}")

    # List jobs from a specific batch
    jobs = client.jobs.get_jobs_by_batch_id("batch-id")
    for job in jobs:
        print(f"Job: {job.place_id} - {job.status}")

    # Get a specific job
    job = client.jobs.get_job("place-id")
    print(f"Job status: {job.status}")
```

## API Reference

### Jobs (Read-Only)
- `client.jobs.get_jobs_by_batch_id(batch_id)` - Iterator over jobs in a batch (auto-paginated)
- `client.jobs.get_job(place_id)` - Get specific job details

### Batches (Read-Only)
- `client.batches.list_batches(query=None)` - Iterator over all batches (auto-paginated)
- `client.batches.get_batch(batch_id)` - Get batch details

### Client
```python
RepromptClient(api_key, org_slug, base_url="https://api.repromptai.com/v1", timeout=30.0, readonly=True)
```

## Models & Error Handling

**Key Models:** `BatchJob`, `PlaceJobResult`, `JobListResponse`, `PaginatedBatchesResponse`

**Errors:** Import `RepromptAPIError` for API error handling. Client raises `ValueError` for config errors.

**Legacy:** Use `init(api_key, org_slug, debug=False)` for backward compatibility.

## CLI

Set credentials: `export REPROMPT_API_KEY="key"` `export REPROMPT_ORG_SLUG="org"`

**Jobs:** `reprompt jobs {list,get} [options]`
**Batches:** `reprompt batches {list,get} [options]`

**Output:** `--output {pretty,json,jsonl,csv}` (default: pretty)

```bash
# List batches in different formats
reprompt batches list --output json   # JSON array
reprompt batches list --output jsonl  # JSON Lines (one object per line)
reprompt batches list --output csv    # CSV format

# List jobs from a batch
reprompt jobs list --batch-id batch_123 --output csv
```

## Examples

See the `examples/` directory for complete working examples:

- `list_batches_example.ipynb`: Jupyter notebook showing batch operations
- `cli_test.sh`: CLI usage examples

Built with httpx, Pydantic v2, and auto-generated OpenAPI models.


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run tests: `python -m pytest tests/`
5. Submit a pull request

## Development Tooling

This project is based on the [Microsoft Python Package Template](https://github.com/microsoft/python-package-template), which provides a modern Python development setup with automated CI/CD, testing, and code quality tools.

### Build System
- **Flit**: Modern PEP 517 build backend for pure Python packages
- **pyproject.toml**: Single source of truth for all project metadata and tool configuration (PEP 621)
- **Tox**: Test automation across Python versions (3.10, 3.11, 3.12)

### Code Quality Tools
- **Black**: Opinionated code formatter (120 char line length)
- **Flake8**: Style guide enforcement with flake8-bugbear plugin
- **Pylint**: Static code analysis for errors and code smells
- **Pyright**: Microsoft's type checker for Python
- **Bandit**: Security vulnerability scanner

### Testing
- **Pytest**: Test framework with coverage reporting
- **pytest-cov**: Coverage plugin with 20% minimum threshold
- **pytest-mock**: Mock object library
- Test markers: `unit`, `integration`, `spark`, `slow`

### CI/CD
- **GitHub Actions**: Automated validation and publishing workflows
- **Pre-commit hooks**: Local checks before committing
- Matrix testing across multiple Python versions

### Quick CI Command

Run the complete CI pipeline locally with a single command:
```bash
# Install tox if needed
pip install tox

# Run all CI checks (equivalent to GitHub Actions)
tox -e lint,type,py312,build
```

This runs:
1. **lint**: Black formatting check, Flake8 style check, Pylint analysis
2. **type**: Pyright type checking
3. **py312**: Unit tests with pytest on Python 3.12
4. **build**: Package build with Flit

### Individual Tox Environments

```bash
tox -e py          # Test on current Python version
tox -e integration # Integration tests
tox -e spark       # Spark tests
tox -e format      # Auto-format with Black
tox -e generate-models  # Regenerate OpenAPI models
```

## License

This project uses the same license as the original Microsoft Python package template.
