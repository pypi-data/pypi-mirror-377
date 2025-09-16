# Batch Processing Guide

This guide covers creating place enrichment batches from pandas DataFrames using the Reprompt SDK.

## Quick Start

```python
import pandas as pd
from reprompt import RepromptClient

# Initialize client
client = RepromptClient(api_key="your-key", org_slug="your-org", allow_writes=True)

# Prepare DataFrame with required columns
df = pd.DataFrame([
    {
        "name": "Joe's Pizza",
        "place_id": "place_1", 
        "full_address": "123 Main Street, New York, NY 10001",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "country_code": "US"  # Optional
    }
])

# Create batch
response = client.batches.create_from_dataframe(df, batch_name="My Batch")
print(f"Created batch: {response.id}")
```

## Required DataFrame Columns

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `name` | string | ✅ | Business/place name |
| `place_id` | string | ✅ | Unique identifier for the place |
| `full_address` | string | ✅ | Complete address string |
| `latitude` | float | ✅ | Latitude (-90 to 90) |
| `longitude` | float | ✅ | Longitude (-180 to 180) |
| `country_code` | string | ❌ | ISO 2-letter country code (e.g., "US") |

**Column names are case-insensitive** and support aliases:
- `LAT`, `lat` → `latitude`
- `LNG`, `lng`, `lon` → `longitude` 
- `NAME`, `business_name` → `name`

## Large Dataset Processing

For datasets with 10K+ rows, use batch splitting:

```python
# Split large dataset into multiple batches
responses = client.batches.create_from_dataframe(
    large_df,
    batch_name="Large Dataset",
    batch_size=5000  # Creates multiple batches of 5K rows each
)

print(f"Created {len(responses)} batches")
```

## Async Processing (Performance)

For maximum performance on large datasets:

```python
import asyncio

async def process_large_dataset():
    responses = await client.batches.create_from_dataframe_async(
        df,
        batch_name="Async Processing",
        batch_size=5000,
        max_concurrent_batches=3  # Control API load
    )
    
    # Handle results - mix of successful responses and exceptions
    successes = [r for r in responses if hasattr(r, 'id')]
    failures = [r for r in responses if isinstance(r, Exception)]
    
    print(f"Success: {len(successes)}, Failures: {len(failures)}")

# Run async processing
asyncio.run(process_large_dataset())
```

## Validation & Error Handling

### Strict Validation
The SDK uses strict validation by default:

```python
try:
    response = client.batches.create_from_dataframe(df, batch_name="Test")
except ValueError as e:
    if "Missing required column" in str(e):
        print("Add missing columns to DataFrame")
    elif "Duplicate place_id found" in str(e):
        print("Remove duplicate place_ids or use ignore_duplicate_place_ids=True")
    elif "Invalid latitude values" in str(e):
        print("Fix coordinate values")
```

### Allow Duplicates
```python
# Allow duplicate place_ids (not recommended)
response = client.batches.create_from_dataframe(
    df, 
    batch_name="With Duplicates",
    ignore_duplicate_place_ids=True
)
```

## Configuration Options

```python
response = client.batches.create_from_dataframe(
    df,
    batch_name="Custom Batch",
    batch_id="custom-id",              # Optional: specify batch ID
    enrich_now=True,                   # Start enrichment immediately (default)
    attribute_set=AttributeSet.CORE,   # or attributes=["name", "address"]
    batch_size=1000,                   # Split into multiple batches
    ignore_duplicate_place_ids=False   # Strict duplicate checking (default)
)
```

## Performance Tips

1. **Use vectorized operations**: DataFrame processing is optimized for speed
2. **Batch size**: 5K-10K rows per batch for optimal performance
3. **Async processing**: Use `create_from_dataframe_async()` for 50K+ rows
4. **Memory efficiency**: Large datasets are processed without excessive memory usage
5. **Concurrent limits**: Default 5 concurrent batches - adjust based on API limits

## Common Issues & Solutions

### Missing Required Columns
```python
# ❌ This will fail
df = pd.DataFrame([{"name": "Place", "address": "123 Main St"}])

# ✅ This will work  
df = pd.DataFrame([{
    "name": "Place", 
    "place_id": "p1",
    "full_address": "123 Main St",
    "latitude": 40.0,
    "longitude": -74.0
}])
```

### Duplicate place_ids
```python
# ❌ This will fail by default
df = pd.DataFrame([
    {"name": "Place 1", "place_id": "same", "full_address": "123 Main St", "latitude": 40.0, "longitude": -74.0},
    {"name": "Place 2", "place_id": "same", "full_address": "456 Oak Ave", "latitude": 41.0, "longitude": -75.0}
])

# ✅ Fix: Use unique place_ids
df.loc[1, "place_id"] = "unique_id_2"

# ✅ Or allow duplicates (not recommended)
response = client.batches.create_from_dataframe(df, batch_name="Test", ignore_duplicate_place_ids=True)
```

### Invalid Coordinates
```python
# ❌ This will fail
df["latitude"] = 91.0  # > 90

# ✅ Fix: Use valid ranges
df["latitude"] = df["latitude"].clip(-90, 90)
df["longitude"] = df["longitude"].clip(-180, 180)
```

## Architecture Benefits

The enhanced batch processing provides:

- **10x faster validation** using vectorized pandas operations
- **Cross-batch duplicate detection** prevents the `tmp_<number>` collision bug
- **Async concurrency control** with semaphores for large datasets  
- **Memory efficient** processing of 100K+ row datasets
- **Clear error messages** for faster debugging
- **Strict validation** catches issues early before API calls