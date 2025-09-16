# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Codebase Overview

This is the Reprompt Python SDK, which has transitioned from its original functionality (prompt enhancement, function tracing, hallucination detection) to a new place enrichment API client. The codebase uses the Microsoft Python package template with modern Python standards (PEP 621).

## Key Architecture

The SDK now provides:
- **RepromptClient** (`src/reprompt/client.py:35`): Modern REST client with sync/async support
- **BatchesAPI** (`src/reprompt/client.py:141`): Batch operations for place enrichment
- **JobsAPI** (`src/reprompt/client.py:368`): Individual job operations
- **Pydantic models** (`src/reprompt/generated_client/models/`): Auto-generated type-safe models from OpenAPI spec

**Note:** The `generated_client/` directory contains auto-generated code from OpenAPI specifications and should be ignored during code reviews and refactoring. Do not manually edit files in this directory.


## Development Commands



### Installation
```bash
pip install -e ".[test]"    # Install with test dependencies
pre-commit install          # Setup pre-commit hooks
```

### Testing
```bash
pytest                      # Run all tests
pytest -m "not integration and not spark"  # Unit tests only (default)
pytest tests/test_new_client.py            # Single file
pytest tests/test_new_client.py::test_func # Single test
```

### Testing with Tox
```bash
# Test environments
tox -e py          # Run unit tests (current Python)
tox -e py310       # Run unit tests on Python 3.10
tox -e py311       # Run unit tests on Python 3.11
tox -e py312       # Run unit tests on Python 3.12
tox -e integration # Run integration tests
tox -e spark       # Run Spark tests

# Quality checks
tox -e lint        # Run black, flake8, pylint
tox -e type        # Run pyright type checking
tox -e format      # Auto-format with black

# Build & generate
tox -e build       # Build wheel and sdist with flit
tox -e generate-models  # Generate Pydantic models from OpenAPI spec

# Run specific test file with tox
tox -e py -- tests/test_client.py
```

### Code Quality
```bash
black src tests             # Format code (120 char line length)
pylint src/reprompt         # Lint code
flake8 src tests            # Style checking
pyright src                 # Type checking
pre-commit run --all-files  # Run all checks
```

### Building
```bash
flit build                  # Build package
flit publish                # Publish to PyPI (usually via CI)
```

## Environment Configuration

- **Python**: >=3.10 (supports 3.10, 3.11, 3.12)
- **API Key**: Set `REPROMPT_API_KEY` environment variable or pass to client
- **Org Slug**: Set `REPROMPT_ORG_SLUG` environment variable (required) or pass to client
- **Base URL**: Defaults to `https://api.repromptai.com/v1` (org slug is appended automatically)

### Testing Configuration

For testing, use the test organization:
```bash
export REPROMPT_API_KEY="your-test-api-key"
export REPROMPT_ORG_SLUG="test-hp"
python3 test_simple.py  # Validate configuration
```

## Important Notes

- The package version is defined in `src/reprompt/__init__.py:24`
- Uses Flit instead of setuptools for packaging
- Coverage requirement is set to 100% (can fail builds)
- Models are auto-generated from OpenAPI spec in `generated_client/models/` (do not edit manually)
- When modifying the SDK, focus on the client architecture in `client.py`
- **NEVER have imports within functions** - All imports must be at the top level of the file

## Code Style Anti-Patterns

### Imports Inside Functions (FORBIDDEN)
**Never place import statements inside functions.** This is a major anti-pattern that causes:
- Performance issues (imports executed repeatedly)
- Dependency resolution problems
- Testing difficulties
- Code readability issues

**Bad:**
```python
def some_function():
    import os  # DON'T DO THIS
    from .module import SomeClass  # DON'T DO THIS
    ...
```

**Good:**
```python
import os
from .module import SomeClass

def some_function():
    ...
```

All imports have been moved to the top level of files.

## Client Usage

The SDK provides a single, unified client interface:

```python
from reprompt import RepromptClient
from reprompt.generated_client.models import PlaceJob, PlaceBatchPayload, AttributeSet

client = RepromptClient(api_key="your-key", org_slug="your-org")

# Create a place job
job = PlaceJob(
    place_id="place_123",
    inputs={
        "name": "Joe's Pizza",
        "full_address": "123 Main St, New York, NY",
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    attribute_set="core"
)

# Create a batch
batch_payload = PlaceBatchPayload(
    batch_name="Test Batch",
    jobs=[job],
    attribute_set=AttributeSet.CORE
)

# Submit the batch
response = client.batches.create_batch(batch_payload)

# Get job results
jobs_response = client.jobs.list_jobs(batch_id=response.batch_id)
```

## CLI Output Formats

The CLI supports multiple output formats for easy data processing:

### Available Formats
- **pretty** (default): Rich-formatted output for human consumption
- **json**: Standard JSON format
- **jsonl**: JSON Lines format (one JSON object per line)
- **csv**: Comma-separated values format

### Usage Examples
```bash
# Get data in different formats
reprompt batches list --output json   # JSON array
reprompt batches list --output jsonl  # JSON Lines (one object per line)
reprompt batches list --output csv    # CSV format

# List jobs from a batch
reprompt jobs list --batch-id batch_123 --output csv
```

## Current Limitations

- Never import modules inside functions. Always import them at the top