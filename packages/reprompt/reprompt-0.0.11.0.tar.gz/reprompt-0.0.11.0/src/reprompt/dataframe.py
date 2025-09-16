"""DataFrame helpers and CSV upload utilities for Reprompt."""

from __future__ import annotations

import json
import logging
from typing import List, TYPE_CHECKING, Any

from .generated.models import PlaceJobResult, BatchJob

if TYPE_CHECKING:
    import pandas as pd

    PANDAS_AVAILABLE = True
else:
    try:
        import pandas as pd

        PANDAS_AVAILABLE = True
    except ImportError:
        pd = None
        PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)


# DataFrame serialization helpers
def batches_to_dataframe(batches: List[BatchJob]) -> Any:
    """
    Convert a list of BatchJob objects to a pandas DataFrame.

    Args:
        batches: List of BatchJob objects from the API

    Returns:
        pd.DataFrame with flattened batch data

    Raises:
        ImportError: If pandas is not installed
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame conversion. Install with: pip install pandas")

    if not batches:
        return pd.DataFrame()

    # Convert BatchJob objects to flattened dictionaries
    data = []
    for batch in batches:
        # Work directly with the BatchJob model
        flattened = _flatten_batch_job(batch)
        data.append(flattened)

    return pd.DataFrame(data)


def jobs_to_dataframe(
    jobs: List[PlaceJobResult],
    include_inputs: bool = True,
    include_reasoning: bool = True,
    include_confidence: bool = True,
    include_batch: bool = True,
    include_not_run: bool = False,
) -> Any:
    """
    Convert a list of PlaceJobResult objects to a pandas DataFrame with flattened structure.

    Args:
        jobs: List of PlaceJobResult objects from the API
        include_inputs: Include input fields (default: True)
        include_reasoning: Include reasoning fields (default: True)
        include_confidence: Include confidence score fields (default: True)
        include_batch: Include batch_id field (default: True)
        include_not_run: Include columns with all None/NaN values (default: False)

    Returns:
        pd.DataFrame with flattened job data

    Raises:
        ImportError: If pandas is not installed
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame conversion. Install with: pip install pandas")

    if not jobs:
        return pd.DataFrame()

    # Convert PlaceJobResult objects to flattened dictionaries
    data = []
    for job in jobs:
        # We know job is a PlaceJobResult, work with it directly
        flattened = _flatten_place_job_result(
            job,
            include_inputs=include_inputs,
            include_reasoning=include_reasoning,
            include_confidence=include_confidence,
            include_batch=include_batch,
        )
        data.append(flattened)

    df = pd.DataFrame(data)

    # Apply include_not_run filtering if requested
    if not include_not_run:
        df = _remove_null_columns(df)

    return df


def _remove_null_columns(df: Any) -> Any:
    """Remove columns that contain only None/NaN values."""
    if df.empty:
        return df

    # Find columns that are all null (None or NaN)
    null_columns = []
    for col in df.columns:
        if df[col].isnull().all():
            null_columns.append(col)

    # Drop null columns
    if null_columns:
        df = df.drop(columns=null_columns)

    return df


def _flatten_batch_job(batch: BatchJob) -> dict:
    """Flatten BatchJob model structure for DataFrame format."""
    flattened = {}

    # Only include batch_id and batch_name
    flattened["batch_id"] = batch.id
    flattened["batch_name"] = batch.batch_name

    return flattened


def _flatten_place_job_result(  # pylint: disable=too-many-locals,too-many-branches
    job: PlaceJobResult,
    include_inputs: bool = True,
    include_reasoning: bool = True,
    include_confidence: bool = True,
    include_batch: bool = True,  # pylint: disable=unused-argument
) -> dict:
    """Flatten PlaceJobResult structure for DataFrame format with selective field inclusion."""

    # Create a sentinel for unset values
    class UNSET:  # pylint: disable=too-few-public-methods
        pass

    flattened = {}

    # Basic job info - directly access typed attributes
    flattened["place_id"] = job.place_id
    flattened["status"] = job.status

    # Handle inputs with dot notation prefix
    if include_inputs and job.inputs:
        # Only include the core fields, ignore additional/extra fields
        if hasattr(job.inputs, "model_dump"):
            inputs_dict = job.inputs.model_dump(exclude_unset=True, mode="json")
            # Filter out standard UniversalPlace fields only
            core_fields = {"type", "input_type", "name", "full_address", "latitude", "longitude"}
            for key, value in inputs_dict.items():
                if key in core_fields:
                    flattened[f"inputs.{key}"] = value
        else:
            # Fallback for dict inputs
            inputs_dict = job.inputs if isinstance(job.inputs, dict) else {}
            for key, value in inputs_dict.items():
                flattened[f"inputs.{key}"] = value

    # Handle outputs with dot notation prefix
    # Handle outputs - it's a dict in the new models
    outputs = job.outputs if isinstance(job.outputs, dict) else {}
    if outputs:
        for key, value in outputs.items():
            # For nested dicts, keep the nested structure but with dot prefix
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flattened[f"outputs.{key}_{sub_key}"] = (
                        sub_value if not isinstance(sub_value, (dict, list)) else json.dumps(sub_value)
                    )
            elif isinstance(value, list):
                flattened[f"outputs.{key}"] = json.dumps(value)
            else:
                flattened[f"outputs.{key}"] = value

    # Handle reasoning with dot notation prefix
    if include_reasoning and job.reasoning:
        reasoning_dict = job.reasoning if isinstance(job.reasoning, dict) else {}
        if "additional_properties" in reasoning_dict:
            reasoning_dict = reasoning_dict["additional_properties"]
        # Add reasoning for each field with dot notation
        for key, value in reasoning_dict.items():
            flattened[f"reasoning.{key}"] = value if not isinstance(value, (dict, list)) else json.dumps(value)

    # Handle confidence_scores with dot notation prefix
    if include_confidence and job.confidence_scores is not None and not isinstance(job.confidence_scores, type(UNSET)):
        if hasattr(job.confidence_scores, "model_dump"):
            confidence_dict = job.confidence_scores.model_dump(mode="json")
        else:
            confidence_dict = {}
        if "additional_properties" in confidence_dict:
            confidence_dict = confidence_dict["additional_properties"]
        # Add confidence for each field with dot notation
        for key, value in confidence_dict.items():
            flattened[f"confidence.{key}"] = value if not isinstance(value, (dict, list)) else json.dumps(value)

    # Handle job_metadata
    if job.job_metadata:
        if hasattr(job.job_metadata, "model_dump"):
            # Use model_dump with mode='json' to handle datetime serialization
            metadata_dict = job.job_metadata.model_dump(mode="json")
        else:
            metadata_dict = {}
        flattened["job_metadata"] = json.dumps(metadata_dict)

    return flattened


def _normalize_columns(df: Any) -> Any:
    """
    Normalize column names and map synonyms to standard names using vectorized operations.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with normalized column names
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame normalization. Install with: pip install pandas")

    # Make a copy to avoid modifying the original
    df = df.copy()

    # Handle empty DataFrame case - pandas str accessor fails on empty columns
    if df.empty or len(df.columns) == 0:
        return df

    # Vectorized lowercase operation
    df.columns = df.columns.str.lower().str.strip()

    # Map synonyms to standard names
    column_mapping = {
        "lat": "latitude",
        "lon": "longitude",
        "lng": "longitude",
        "place_name": "name",
        "business_name": "name",
        "address": "full_address",
        "addr": "full_address",
    }

    # Vectorized column rename
    df = df.rename(columns=column_mapping)

    return df


def _trim_and_clean(df: Any) -> Any:
    """
    Clean and trim string values using vectorized pandas operations.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with cleaned string values
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame cleaning. Install with: pip install pandas")

    # Make a copy to avoid modifying the original
    df = df.copy()

    # Vectorized string cleaning for all object columns
    string_columns = df.select_dtypes(include=["object"]).columns

    for col in string_columns:
        # Vectorized operations: strip whitespace, replace empty/nan strings
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["", "nan", "None", "null"], None)
        # Convert back to None where originally null
        df.loc[df[col] == "nan", col] = None

    # Convert coordinate columns to numeric if they exist
    for coord_col in ["latitude", "longitude"]:
        if coord_col in df.columns:
            df[coord_col] = pd.to_numeric(df[coord_col], errors="coerce")

    return df


def _validate_required_columns(df: Any) -> None:
    """
    Validate that all required columns are present.

    Args:
        df: Input DataFrame

    Raises:
        ValueError: If required columns are missing
    """
    required_columns = {"name", "place_id", "latitude", "longitude", "full_address"}

    # Check for empty DataFrame first
    if df.empty:
        raise ValueError("DataFrame is empty")

    # Check for DataFrame with no columns (has rows but no columns)
    if len(df.columns) == 0:
        required_str = ", ".join(sorted(required_columns))
        raise ValueError(f"DataFrame has no columns. Required: {required_str}")

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        required_str = ", ".join(sorted(required_columns))
        raise ValueError(
            f"Missing required column{'s' if len(missing_columns) > 1 else ''}: {missing_str}. Required: {required_str}"
        )


def _check_duplicates_efficient(df: Any, ignore_duplicates: bool = False) -> None:
    """
    Efficient duplicate detection using vectorized pandas operations.

    Args:
        df: Input DataFrame with place_id column
        ignore_duplicates: If True, skip duplicate checking

    Raises:
        ValueError: If duplicates found and ignore_duplicates=False
    """
    if ignore_duplicates:
        return

    # Vectorized duplicate check - much faster than row-by-row
    if df["place_id"].duplicated().any():
        # Find all duplicate place_ids and their row indices
        duplicated_mask = df["place_id"].duplicated(keep=False)
        duplicate_place_ids = df[duplicated_mask]["place_id"].unique()

        # Show details for first few duplicates
        duplicate_details = []
        for place_id in duplicate_place_ids[:3]:  # Limit to first 3 for readability
            rows = df[df["place_id"] == place_id].index.tolist()
            duplicate_details.append(f"'{place_id}' in rows {rows}")

        details_str = "; ".join(duplicate_details)
        if len(duplicate_place_ids) > 3:
            details_str += f" (and {len(duplicate_place_ids) - 3} more)"

        raise ValueError(f"Duplicate place_id found: {details_str}. Set ignore_duplicate_place_ids=True to allow.")


def _validate_data_integrity(df: Any) -> None:
    """
    Validate data integrity using vectorized operations.

    Args:
        df: Input DataFrame

    Raises:
        ValueError: If data integrity issues found
    """
    errors = []

    # Vectorized null checks for required fields
    for col in ["name", "place_id", "full_address"]:
        null_mask = df[col].isna() | (df[col].astype(str).str.strip() == "")
        if null_mask.any():
            null_indices = df[null_mask].index.tolist()[:5]  # Show first 5
            errors.append(f"Empty/null values in '{col}' at rows: {null_indices}")

    # Vectorized coordinate validation - check for NaN first, then ranges
    lat_nan_mask = df["latitude"].isna()
    if lat_nan_mask.any():
        nan_indices = df[lat_nan_mask].index.tolist()[:5]
        errors.append(f"NaN/null values in 'latitude' at rows: {nan_indices}")

    lng_nan_mask = df["longitude"].isna()
    if lng_nan_mask.any():
        nan_indices = df[lng_nan_mask].index.tolist()[:5]
        errors.append(f"NaN/null values in 'longitude' at rows: {nan_indices}")

    # Only check ranges for non-NaN values
    if not lat_nan_mask.all():  # If not all values are NaN
        lat_invalid = ((df["latitude"] < -90) | (df["latitude"] > 90)) & ~lat_nan_mask
        if lat_invalid.any():
            invalid_indices = df[lat_invalid].index.tolist()[:5]
            errors.append(f"Invalid latitude values (must be -90 to 90) at rows: {invalid_indices}")

    if not lng_nan_mask.all():  # If not all values are NaN
        lng_invalid = ((df["longitude"] < -180) | (df["longitude"] > 180)) & ~lng_nan_mask
        if lng_invalid.any():
            invalid_indices = df[lng_invalid].index.tolist()[:5]
            errors.append(f"Invalid longitude values (must be -180 to 180) at rows: {invalid_indices}")

    if errors:
        error_summary = "; ".join(errors[:5])
        if len(errors) > 5:
            error_summary += f" (and {len(errors) - 5} more issues)"
        raise ValueError(f"Data validation failed: {error_summary}")


def prepare_places_dataframe(df: Any, ignore_duplicate_place_ids: bool = False) -> Any:
    """
    Prepare and validate a DataFrame for place batch creation with strict requirements.

    Required columns: name, place_id, latitude, longitude, full_address
    Optional columns: country_code

    Args:
        df: Input pandas DataFrame
        ignore_duplicate_place_ids: If True, allow duplicate place_ids

    Returns:
        Normalized and validated DataFrame

    Raises:
        ImportError: If pandas is not installed
        ValueError: If validation fails
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("pandas is required for DataFrame preparation. Install with: pip install pandas")

    # Step 1: Normalize column names (vectorized)
    df = _normalize_columns(df)

    # Step 2: Validate required columns early
    _validate_required_columns(df)

    # Step 3: Clean data (vectorized)
    df = _trim_and_clean(df)

    # Step 4: Validate data integrity (vectorized)
    _validate_data_integrity(df)

    # Step 5: Check for duplicates (vectorized)
    _check_duplicates_efficient(df, ignore_duplicate_place_ids)

    return df
