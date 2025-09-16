"""Reprompt API Client - A modern REST client for place enrichment."""

from __future__ import annotations

import asyncio
import concurrent.futures
import logging
import math
import os
import re
from collections import Counter, defaultdict
from typing import Any, Dict, List, Union

import httpx

from .exceptions import RepromptAPIError
from .transport import HttpxTransport
from .generated.models import (
    AttributeSet,
    BatchJob,
    BatchJobStatus,
    PlaceJobResult,
    SubmittedPlaceBatchResponse,
    AttributeStatusEnum,
)
from .iterators import JobsPaginatedIterator, PaginatedIterator
from .dataframe import prepare_places_dataframe

# For pandas operations in create_from_dataframe
try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)

# Note: BatchJob models from generated client are immutable (frozen attrs classes)
# Access status counts via: batch.status_counts.additional_properties['pending']

# Constants
DEFAULT_BASE_URL = "https://api.repromptai.com/v1"
BATCH_PAGE_SIZE = 100  # Default page size for batches
JOB_PAGE_SIZE = 1000  # Default page size for jobs
MAX_BATCH_LIMIT = 100  # Maximum number of batches that can be fetched at once (deprecated, use BATCH_PAGE_SIZE)

# API Endpoints
BATCHES_PATH = "/place_enrichment/batches"
JOBS_PATH = "/place_enrichment/jobs"


def _normalize_datetime_fields(data: dict) -> dict:
    """
    Normalize datetime fields in API responses to ensure they have timezone info.

    The API sometimes returns datetime strings without timezone info, but Pydantic
    models expect timezone-aware datetimes. This function adds 'Z' (UTC) suffix
    to datetime strings that don't have timezone info.

    Args:
        data: Dictionary containing API response data

    Returns:
        Modified dictionary with normalized datetime fields
    """

    def add_timezone_if_missing(dt_string: str) -> str:
        """Add 'Z' suffix to datetime string if it doesn't have timezone info."""
        if (
            isinstance(dt_string, str)
            and not dt_string.endswith("Z")
            and "+" not in dt_string
            and "-" not in dt_string[-6:]
        ):
            return dt_string + "Z"
        return dt_string

    # Handle job_metadata.last_enriched
    if "job_metadata" in data and isinstance(data["job_metadata"], dict):
        if "last_enriched" in data["job_metadata"]:
            data["job_metadata"]["last_enriched"] = add_timezone_if_missing(data["job_metadata"]["last_enriched"])

    # Handle created_at for batches
    if "created_at" in data:
        data["created_at"] = add_timezone_if_missing(data["created_at"])

    return data


# Re-export models for other modules to import from here
__all__ = [
    "RepromptClient",
    "RepromptAPIError",
    "BatchJob",
    "BatchJobStatus",
    "PlaceJobResult",
]


class BatchesAPI:
    """Sub-API for batch operations."""

    def __init__(self, transport, allow_writes: bool = False):
        self._transport = transport
        self.allow_writes = allow_writes

    def list_batches(self, query: str | None = None, page_size: int = BATCH_PAGE_SIZE) -> PaginatedIterator:
        """
        List batches with automatic pagination.

        Always returns an iterator that handles pagination automatically.

        Args:
            query: Optional search query to filter batches
            page_size: Page size for iterator (default: BATCH_PAGE_SIZE, max: BATCH_PAGE_SIZE)

        Returns:
            PaginatedIterator that yields all batches
        """
        # Validate page_size against maximum
        if page_size > BATCH_PAGE_SIZE:
            raise ValueError(f"Page size cannot exceed {BATCH_PAGE_SIZE}, got {page_size}")

        # Always return iterator (Google Cloud pattern)
        logger.debug("Creating batch iterator: page_size=%s, query=%s", page_size, query)
        filters = {}
        if query:
            filters["query"] = query
        return PaginatedIterator(self._list_batches_raw, page_size, **filters)

    def get_batch(self, batch_id: str):
        """Retrieve the detailed status of a specific batch including job IDs."""
        logger.debug("Getting batch: %s", batch_id)

        response = self._transport.get(f"{BATCHES_PATH}/{batch_id}")
        # The get_batch endpoint returns a different structure with job IDs grouped by status
        # It doesn't have status_counts and created_at like the list endpoint
        # For now, return the raw response as it has a different structure than BatchJob
        return response

    def get_batches(
        self,
        limit: int = BATCH_PAGE_SIZE,
        offset: int = 0,
        query: str | None = None,
    ):
        """
        Get a page of batches with direct access to response metadata.

        Args:
            limit: Maximum number of batches to return (default: BATCH_PAGE_SIZE, max: BATCH_PAGE_SIZE)
            offset: Starting offset for pagination (default: 0)
            query: Optional search query to filter batches

        Returns:
            Response with batches and pagination metadata
        """
        # Validate limit against maximum
        if limit > BATCH_PAGE_SIZE:
            raise ValueError(f"Limit cannot exceed {BATCH_PAGE_SIZE}, got {limit}")

        logger.debug("Getting batches: limit=%s, offset=%s, query=%s", limit, offset, query)
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if query is not None:
            params["query"] = query
        return self._transport.get(BATCHES_PATH, params=params)

    def _list_batches_raw(self, limit: int = BATCH_PAGE_SIZE, offset: int = 0, **filters):
        # Validate limit against maximum
        if limit > BATCH_PAGE_SIZE:
            raise ValueError(f"Limit cannot exceed {BATCH_PAGE_SIZE}, got {limit}")

        params = {"limit": limit, "offset": offset, **filters}
        response = self._transport.get(BATCHES_PATH, params=params)

        # Convert batch dicts to BatchJob objects
        if response and "batches" in response:
            batches = response["batches"]
            if batches and isinstance(batches[0], dict):
                # Normalize datetime fields for each batch
                batches = [_normalize_datetime_fields(batch) for batch in batches]
                response["batches"] = [BatchJob(**batch) for batch in batches]
        return response

    def create_from_dataframe(
        self,
        df,
        *,
        batch_name: str,
        batch_id: str | None = None,
        enrich_now: bool = True,
        attribute_set: AttributeSet | None = None,
        attributes: list[str] | None = None,
        batch_size: int | None = None,
        ignore_duplicate_place_ids: bool = False,
    ) -> SubmittedPlaceBatchResponse | List[SubmittedPlaceBatchResponse]:
        """
        Create a batch from a pandas DataFrame with strict validation.

        Required columns: name, place_id, latitude, longitude, full_address
        Optional columns: country_code

        Args:
            df: Input pandas DataFrame with place data
            batch_name: Name for the batch
            batch_id: Optional batch ID (if not provided, server generates one)
            enrich_now: Whether to start enrichment immediately (default: True)
            attribute_set: Attribute set to enrich (mutually exclusive with attributes)
            attributes: List of specific attributes to enrich (mutually exclusive with attribute_set)
            batch_size: Optional batch size to split large datasets into multiple batches.
                        If not provided, creates a single batch. Maximum 200 batches allowed.
            ignore_duplicate_place_ids: If True, allow duplicate place_ids (default: False)

        Returns:
            SubmittedPlaceBatchResponse if single batch, or List[SubmittedPlaceBatchResponse] if split into
            multiple batches

        Raises:
            ValueError: If client is read-only, invalid parameters, validation fails,
                       or batch_size results in >200 batches
            ImportError: If pandas is not installed
        """
        self._validate_batch_creation_parameters(attribute_set, attributes, batch_id, batch_size)
        logger.debug("Creating batch from DataFrame: %s rows, batch_name='%s'", len(df), batch_name)

        # Prepare and validate the DataFrame with strict requirements
        prepared_df = prepare_places_dataframe(df, ignore_duplicate_place_ids=ignore_duplicate_place_ids)

        # Handle batch splitting logic
        if batch_size is not None:
            return self._handle_batch_splitting(
                prepared_df, batch_name, batch_size, enrich_now, attribute_set, attributes
            )

        # Single batch creation (original logic)
        return self._create_single_batch(prepared_df, batch_name, batch_id, enrich_now, attribute_set, attributes)

    def _validate_batch_creation_parameters(self, attribute_set, attributes, batch_id, batch_size):
        """Validate parameters for batch creation."""
        # Check if writes are allowed
        if not self.allow_writes:
            raise ValueError("Client is read-only; set allow_writes=True to create batches")

        # Check if pandas is available
        if pd is None:
            raise ImportError("pandas is required for DataFrame batch creation. Install with: pip install pandas")

        # Validate mutually exclusive parameters
        if attribute_set is not None and attributes is not None:
            raise ValueError("Cannot specify both attribute_set and attributes; choose one")

        # If batch_id is specified and batch_size is also specified, raise error
        if batch_id is not None and batch_size is not None:
            raise ValueError("Cannot specify both batch_id and batch_size; batch_id is only for single batches")

    def _handle_batch_splitting(self, prepared_df, batch_name, batch_size, enrich_now, attribute_set, attributes):
        """Handle splitting of large DataFrames into multiple batches."""
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        total_rows = len(prepared_df)
        num_batches = math.ceil(total_rows / batch_size)

        # If batch_size is larger than or equal to total rows, create single batch
        if num_batches <= 1:
            logger.debug("batch_size %d >= total rows %d, creating single batch", batch_size, total_rows)
            return self._create_single_batch(prepared_df, batch_name, None, enrich_now, attribute_set, attributes)

        # Enforce 200 batch limit
        if num_batches > 200:
            min_batch_size = math.ceil(total_rows / 200)
            raise ValueError(
                f"batch_size={batch_size} would create {num_batches} batches, "
                f"but maximum allowed is 200. Use batch_size >= {min_batch_size}"
            )

        logger.debug("Splitting DataFrame into %d batches of size %d", num_batches, batch_size)
        return self._create_multiple_batches(
            prepared_df, batch_name, batch_size, num_batches, enrich_now, attribute_set, attributes
        )

    def _create_multiple_batches(
        self, prepared_df, batch_name, batch_size, num_batches, enrich_now, attribute_set, attributes
    ):
        """Create multiple batches from DataFrame chunks."""
        responses = []
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, len(prepared_df))
            chunk_df = prepared_df.iloc[start_idx:end_idx]

            # Create batch name with suffix
            chunk_batch_name = f"{batch_name}_batch_{i + 1:03d}_of_{num_batches:03d}"

            # Process this chunk
            response = self._create_single_batch(
                chunk_df, chunk_batch_name, None, enrich_now, attribute_set, attributes
            )
            responses.append(response)

        return responses

    def _create_single_batch(
        self,
        prepared_df,
        batch_name: str,
        batch_id: str | None,
        enrich_now: bool,
        attribute_set: AttributeSet | None,
        attributes: list[str] | None,
    ) -> SubmittedPlaceBatchResponse:
        """
        Create a single batch from a prepared DataFrame using vectorized operations.
        """
        # Vectorized job creation - much faster than row iteration
        jobs = []

        # Since DataFrame is already validated, we know required columns exist
        for _, row in prepared_df.iterrows():
            inputs_dict = {
                "name": row["name"],
                "full_address": row["full_address"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
            }

            # Add optional country_code if present
            if "country_code" in row.index and pd is not None:
                country_code_val = row["country_code"]
                if pd.notna(country_code_val) and country_code_val != "":
                    inputs_dict["country_code"] = country_code_val

            job_dict = {"place_id": row["place_id"], "inputs": inputs_dict}
            jobs.append(job_dict)

        # Build request payload
        payload = {
            "batch_name": batch_name,
            "jobs": jobs,
            "kick_off_jobs_now": enrich_now,
        }

        if batch_id is not None:
            payload["batch_id"] = batch_id

        if attribute_set is not None:
            payload["attribute_set"] = attribute_set.value

        if attributes is not None:
            payload["attributes"] = attributes

        # Submit to API
        logger.debug("Submitting batch with %d jobs to %s", len(jobs), BATCHES_PATH)
        response = self._transport.post(BATCHES_PATH, json=payload)

        # Parse response
        return SubmittedPlaceBatchResponse(**response)

    async def create_from_dataframe_async(
        self,
        df,
        *,
        batch_name: str,
        batch_id: str | None = None,
        enrich_now: bool = True,
        attribute_set: AttributeSet | None = None,
        attributes: list[str] | None = None,
        batch_size: int | None = None,
        ignore_duplicate_place_ids: bool = False,
        max_concurrent_batches: int = 5,
    ) -> List[Union[SubmittedPlaceBatchResponse, BaseException]]:
        """
        Create batches from a pandas DataFrame with async processing and semaphore.

        Args:
            df: Input pandas DataFrame with place data
            batch_name: Name for the batch
            batch_id: Optional batch ID (only for single batch)
            enrich_now: Whether to start enrichment immediately
            attribute_set: Attribute set to enrich
            attributes: List of specific attributes to enrich
            batch_size: Batch size to split large datasets
            ignore_duplicate_place_ids: Allow duplicate place_ids
            max_concurrent_batches: Maximum concurrent API requests (default: 5)

        Returns:
            List of SubmittedPlaceBatchResponse or Exception objects
        """
        # Validate parameters
        self._validate_batch_creation_parameters(attribute_set, attributes, batch_id, batch_size)
        logger.debug("Creating async batch from DataFrame: %s rows, batch_name='%s'", len(df), batch_name)

        # Prepare and validate the DataFrame
        prepared_df = prepare_places_dataframe(df, ignore_duplicate_place_ids=ignore_duplicate_place_ids)

        # Force batch splitting for async (even if batch_size not provided)
        if batch_size is None:
            batch_size = 10000  # Default chunk size for async

        total_rows = len(prepared_df)
        num_batches = math.ceil(total_rows / batch_size)

        if num_batches <= 1:
            # Single batch - use sync method
            response = self._create_single_batch(
                prepared_df, batch_name, batch_id, enrich_now, attribute_set, attributes
            )
            return [response]

        # Multiple batches - async processing
        if num_batches > 200:
            min_batch_size = math.ceil(total_rows / 200)
            raise ValueError(
                f"batch_size={batch_size} would create {num_batches} batches, "
                f"but maximum allowed is 200. Use batch_size >= {min_batch_size}"
            )

        logger.debug("Async processing %d batches with max %d concurrent", num_batches, max_concurrent_batches)
        return await self._create_multiple_batches_async(
            prepared_df,
            batch_name,
            batch_size,
            num_batches,
            enrich_now,
            attribute_set,
            attributes,
            max_concurrent_batches,
        )

    async def _create_multiple_batches_async(
        self,
        prepared_df,
        batch_name: str,
        batch_size: int,
        num_batches: int,
        enrich_now: bool,
        attribute_set: AttributeSet | None,
        attributes: list[str] | None,
        max_concurrent: int,
    ) -> List[Union[SubmittedPlaceBatchResponse, BaseException]]:
        """
        Create multiple batches asynchronously with semaphore-controlled concurrency.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def create_batch_with_semaphore(batch_index: int) -> Union[SubmittedPlaceBatchResponse, Exception]:
            async with semaphore:
                try:
                    start_idx = batch_index * batch_size
                    end_idx = min((batch_index + 1) * batch_size, len(prepared_df))
                    chunk_df = prepared_df.iloc[start_idx:end_idx]

                    chunk_batch_name = f"{batch_name}_batch_{batch_index + 1:03d}_of_{num_batches:03d}"

                    # Create batch payload
                    jobs = []
                    for _, row in chunk_df.iterrows():
                        inputs_dict = {
                            "name": row["name"],
                            "full_address": row["full_address"],
                            "latitude": float(row["latitude"]),
                            "longitude": float(row["longitude"]),
                        }

                        if "country_code" in row.index and pd is not None:
                            country_code_val = row["country_code"]
                            if pd.notna(country_code_val) and country_code_val != "":
                                inputs_dict["country_code"] = country_code_val

                        job_dict = {"place_id": row["place_id"], "inputs": inputs_dict}
                        jobs.append(job_dict)

                    payload = {
                        "batch_name": chunk_batch_name,
                        "jobs": jobs,
                        "kick_off_jobs_now": enrich_now,
                    }

                    if attribute_set is not None:
                        payload["attribute_set"] = attribute_set.value
                    if attributes is not None:
                        payload["attributes"] = attributes

                    # Use async transport
                    response = await self._transport.post_async(BATCHES_PATH, json=payload)
                    return SubmittedPlaceBatchResponse(**response)

                except Exception as e:
                    logger.error("Failed to create batch %d: %s", batch_index + 1, e)
                    return e

        # Create all batch tasks
        tasks = [create_batch_with_semaphore(i) for i in range(num_batches)]

        # Execute with controlled concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes and failures
        successes = [r for r in results if isinstance(r, SubmittedPlaceBatchResponse)]
        failures = [r for r in results if isinstance(r, BaseException)]

        if failures:
            logger.warning("Batch creation completed with %d successes, %d failures", len(successes), len(failures))
        else:
            logger.info("All %d batches created successfully", len(successes))

        return results


class JobsAPI:
    """Sub-API for job operations (read-only)."""

    def __init__(self, transport):
        self._transport = transport

    def get_jobs_by_batch_id(self, batch_id: str, page_size: int = JOB_PAGE_SIZE) -> JobsPaginatedIterator:
        """
        Get all jobs for a specific batch with automatic pagination.

        Args:
            batch_id: Batch ID to get jobs for
            page_size: Page size for iterator (default: 100)

        Returns:
            JobsPaginatedIterator that yields all jobs
        """

        def fetch_jobs(limit: int, offset: int, **kwargs):  # pylint: disable=unused-argument
            logger.debug("Fetching jobs for batch %s: limit=%s, offset=%s", batch_id, limit, offset)
            params = {"limit": limit, "offset": offset, "batchId": batch_id}
            return self._transport.get(JOBS_PATH, params=params)

        return JobsPaginatedIterator(fetch_jobs, page_size=page_size, client=None)

    def get_job(self, place_id: str) -> PlaceJobResult:
        """Get job details for a specific place."""
        logger.debug("Getting job for place_id: %s", place_id)

        response = self._transport.get(f"{JOBS_PATH}/{place_id}")

        # Normalize datetime fields to ensure they have timezone info
        response = _normalize_datetime_fields(response)

        return PlaceJobResult(**response)


class RepromptClient:  # pylint: disable=too-many-instance-attributes
    """
    A REST client for the Reprompt Place Enrichment API.

    This client provides access to jobs and batches with proper
    error handling, parallel processing, and type safety through Pydantic models.

    Read operations are always available. Write operations require allow_writes=True.
    """

    def __init__(
        self,
        api_key: str | None = None,
        org_slug: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        allow_writes: bool = False,
    ):
        """
        Initialize the Reprompt API client.

        Args:
            api_key: Your Reprompt API key. If not provided, tries REPROMPT_API_KEY env var
            org_slug: Organization slug (e.g., 'test-hp'). If not provided, tries REPROMPT_ORG_SLUG env var
            base_url: Base URL for the API (default: https://api.repromptai.com/v1)
            timeout: Request timeout in seconds (default: 30.0)
            allow_writes: Enable write operations like creating batches (default: False)
        """
        # Get api_key from parameter or environment variable
        if api_key is None:
            api_key = os.getenv("REPROMPT_API_KEY")

        if not api_key:
            raise ValueError(
                "API key is required. Provide api_key parameter or set REPROMPT_API_KEY environment variable"
            )

        # Get org_slug from parameter or environment variable
        if org_slug is None:
            org_slug = os.getenv("REPROMPT_ORG_SLUG")

        if not org_slug:
            raise ValueError(
                "Organization slug is required. Provide org_slug parameter "
                "or set REPROMPT_ORG_SLUG environment variable"
            )

        # Validate org_slug format to prevent URL injection
        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,48}[a-zA-Z0-9]$", org_slug):
            raise ValueError(
                f"Invalid org_slug format: '{org_slug}'. "
                "Must be 2-50 characters, alphanumeric with hyphens, "
                "and cannot start or end with a hyphen."
            )

        self.api_key = api_key
        self.org_slug = org_slug
        self.timeout = timeout
        self.allow_writes = allow_writes
        self._base_url = base_url

        # Create transport layer
        self._transport = HttpxTransport(
            base_url=base_url,
            org_slug=org_slug,
            api_key=api_key,
            timeout=timeout,
        )

        # Create sub-APIs
        self.batches = BatchesAPI(self._transport, allow_writes)
        self.jobs = JobsAPI(self._transport)

        logger.debug("Initialized RepromptClient for org: %s", org_slug)

    def get_statistics(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        self,
        batch_ids: list[str],
        *,
        exclude_not_run: bool = False,
        return_dataframe: bool = True,
        max_concurrent: int = 20,
        raise_on_missing: bool = True,
    ):
        """
        Compute attribute status statistics across one or more batches.

        This convenience method fetches jobs for each provided batch ID from
        /place_enrichment/jobs?batchId=... and aggregates statistics on
        job_metadata.attribute_status across ALL batches as if they were one.

        Args:
            batch_ids: List of batch IDs to aggregate
            exclude_not_run: When True, exclude NOT_RUN statuses from counts and drop
                attributes that are NOT_RUN for all jobs in all batches
            return_dataframe: When True, return a pandas DataFrame; otherwise return a dict
            max_concurrent: Maximum concurrent requests while fetching jobs
            raise_on_missing: If True, raise if none of the batch IDs are found

        Returns:
            pandas.DataFrame or dict with aggregated statistics by attribute.

        Raises:
            ValueError: If batch_ids is empty or if attribute "shapes" differ between batches
                (e.g., one batch enriched an attribute while another did not), or if none of
                the provided batch IDs can be found and raise_on_missing=True
            ImportError: If return_dataframe=True but pandas is not installed
        """
        if not batch_ids:
            raise ValueError("batch_ids must be a non-empty list")

        # If returning a DataFrame, ensure pandas is available
        if return_dataframe and pd is None:
            raise ImportError("pandas is required to return a DataFrame. Install with: pip install pandas")

        # Fetch jobs for all batch IDs in parallel
        def fetch_batch_jobs(batch_id: str):
            try:
                iterator = self.jobs.get_jobs_by_batch_id(batch_id=batch_id, page_size=JOB_PAGE_SIZE)
                return batch_id, list(iterator), None
            except httpx.HTTPStatusError as e:  # Treat missing batch as warning
                response = getattr(e, "response", None)
                status_code = response.status_code if response is not None else None
                return batch_id, None, status_code
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Error fetching jobs for batch %s: %s", batch_id, e)
                # Use None jobs to indicate failure; propagate unknown errors later
                return batch_id, None, None

        results = {}
        missing_batches: list[str] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = {executor.submit(fetch_batch_jobs, bid): bid for bid in batch_ids}
            for future in concurrent.futures.as_completed(futures):
                bid, jobs, status_code = future.result()
                if jobs is None:
                    # Mark as missing if 404; otherwise still warn but treat as missing
                    if status_code == 404:
                        logger.warning("Batch not found (404): %s", bid)
                        missing_batches.append(bid)
                    else:
                        logger.warning("Failed to fetch jobs for batch %s", bid)
                        missing_batches.append(bid)
                else:
                    results[bid] = jobs

        if not results:
            # No batches could be fetched
            msg = (
                "None of the provided batch IDs were found or returned results. "
                f"Missing: {', '.join(missing_batches) if missing_batches else 'all'}"
            )
            if raise_on_missing:
                raise ValueError(msg)
            return {"error": msg}

        if missing_batches:
            logger.warning("Some batch IDs could not be fetched: %s", ", ".join(missing_batches))

        # Compute per-batch active attribute sets for shape consistency checks
        per_batch_active_attrs: dict[str, set[str]] = {}
        for bid, jobs in results.items():
            active_attrs = set()
            for job in jobs:
                if not isinstance(job, PlaceJobResult):  # Safety; iterator should already convert
                    continue
                attr_status_map = job.job_metadata.attribute_status or {}
                for attr_name, status in attr_status_map.items():
                    status_value = status.value if hasattr(status, "value") else str(status)
                    if status_value != AttributeStatusEnum.NOT_RUN.value:
                        active_attrs.add(attr_name)
            per_batch_active_attrs[bid] = active_attrs

        # Check shape consistency: all batches must have identical active attribute sets
        active_sets = list(per_batch_active_attrs.values())
        if active_sets:
            base_set = active_sets[0]
            diffs = {}
            for bid, aset in per_batch_active_attrs.items():
                if aset != base_set:
                    missing_in_bid = sorted(list(base_set - aset))
                    extra_in_bid = sorted(list(aset - base_set))
                    diffs[bid] = {"missing": missing_in_bid, "extra": extra_in_bid}
            if diffs:
                details = "; ".join(
                    f"batch {bid}: missing={info['missing']} extra={info['extra']}" for bid, info in diffs.items()
                )
                raise ValueError(
                    "Attribute set mismatch across batches. One batch enriched attributes that another did not. "
                    f"Details: {details}"
                )

        # Create mapping from attribute_status names to output field names
        # This handles the discrepancy between attribute names and output keys
        attr_to_output_mapping = {
            "phoneNumbers": ["phone"],
            "websites": ["website"],
            "openingHours": ["opening_hours", "opening_hours_grouped_by_hours", "is_open_24h"],
            "names": ["name", "multilingual_names", "alt_name"],
            "address": ["address"],
            "coordinates": ["coordinates", "coordinates_distance"],
            "categories": ["categories"],
            "closed_permanently": ["open_closed_status", "open_closed_status_confidence_score"],
            "place_existence": ["place_existence"],
            "naics": ["naics"],
            "placekey": ["placekey"],
            "reprompt_id": ["reprompt_id"],
            "socialHandles": ["social_handles"],
            "tiktok": ["tiktok"],
            "social_media_profile": ["social_media_profile"],
            "instagram_statistics": ["instagram_statistics"],
            "cuisine": ["cuisine"],
            "price_tier": ["price_tier"],
            "email_address": ["email_address"],
            "tripadvisorCategory": ["tripadvisor_category"],
            "building_footprint": ["building_footprint"],
            "name_translations": ["name_translations"],
            "parcel": ["parcel"],
            "foursquare_place": ["foursquare_place"],
            "overture_place": ["overture_place"],
            "merchant": ["merchant"],
            "chain": ["chain"],
            "storefrontImages": ["storefront_images"],
            "user_reviews": ["user_reviews"],
            "approximate_user_reviews": ["approximate_user_reviews"],
            "website_traffic": ["website_traffic"],
            "one_line_summary": ["one_line_summary"],
            "school_geofence": ["school_geofence"],
            "geometry": ["geometry"],
            "orderFoodLinks": ["order_food_links"],
            "menu": ["menu"],
            "vision_open_closed": ["vision_open_closed"],
            "signage": ["signage"],
            "building_condition": ["building_condition"],
            "entrances": ["entrances"],
            "traffic_control": ["traffic_control"],
            "primary_turns": ["primary_turns"],
            "search_aliases": ["search_aliases"],
            "parking_spaces": ["parking_spaces"],
        }

        # Aggregate across all fetched jobs
        status_counts_by_attribute: dict[str, Counter] = defaultdict(Counter)
        value_filled_by_attribute: dict[str, int] = defaultdict(int)
        total_jobs_by_attribute: dict[str, int] = defaultdict(int)

        for jobs in results.values():
            for job in jobs:
                if not isinstance(job, PlaceJobResult):
                    continue
                attr_status_map = job.job_metadata.attribute_status or {}
                outputs_map = job.outputs or {}

                for attr_name, status in attr_status_map.items():
                    status_value = status.value if hasattr(status, "value") else str(status)

                    # Denominator counts jobs where attribute exists in map
                    total_jobs_by_attribute[attr_name] += 1

                    # Optionally skip NOT_RUN in status distribution
                    if exclude_not_run and status_value == AttributeStatusEnum.NOT_RUN.value:
                        pass
                    else:
                        status_counts_by_attribute[attr_name][status_value] += 1

                    # Value fill: check outputs using mapped field names
                    is_filled = False
                    output_fields = attr_to_output_mapping.get(attr_name, [attr_name])

                    for field_name in output_fields:
                        value = outputs_map.get(field_name)
                        if value is not None:
                            if isinstance(value, str):
                                is_filled = bool(value.strip())
                            elif isinstance(value, list):
                                is_filled = len(value) > 0
                            elif isinstance(value, dict):
                                is_filled = len(value) > 0
                            else:
                                # For numbers/booleans, treat non-None as filled
                                is_filled = True

                            if is_filled:
                                break  # Found a filled value, no need to check other fields

                    if is_filled:
                        value_filled_by_attribute[attr_name] += 1

        # If exclude_not_run, drop attributes that are NOT_RUN for all jobs
        # (i.e., have zero non-NOT_RUN statuses)
        if exclude_not_run:
            to_drop = []
            for attr_name in list(total_jobs_by_attribute.keys()):
                # Check if this attribute has any non-NOT_RUN statuses
                non_not_run_count = sum(
                    count
                    for status, count in status_counts_by_attribute[attr_name].items()
                    if status != AttributeStatusEnum.NOT_RUN.value
                )
                if non_not_run_count == 0:
                    # This attribute is NOT_RUN for all jobs, so drop it entirely
                    to_drop.append(attr_name)

            for attr in to_drop:
                status_counts_by_attribute.pop(attr, None)
                value_filled_by_attribute.pop(attr, None)
                total_jobs_by_attribute.pop(attr, None)

        # Build result structure
        all_statuses = set()
        for counter in status_counts_by_attribute.values():
            all_statuses.update(counter.keys())
        sorted_statuses = sorted(all_statuses)

        if return_dataframe and pd is not None:
            rows = []
            for attr in sorted(total_jobs_by_attribute.keys()):
                total = total_jobs_by_attribute.get(attr, 0)
                run_count = status_counts_by_attribute[attr].get(AttributeStatusEnum.RUN.value, 0)
                run_rate = (run_count / total) if total else 0.0
                filled = value_filled_by_attribute.get(attr, 0)
                fill_rate = (filled / total) if total else 0.0

                row = {
                    "attribute": attr,
                    "total_jobs": total,
                    "run_count": run_count,
                    "run_rate": run_rate,
                    "value_filled": filled,
                    "value_fill_rate": fill_rate,
                }
                for status_name in sorted_statuses:
                    row[f"status_{status_name}"] = status_counts_by_attribute[attr].get(status_name, 0)
                rows.append(row)

            return pd.DataFrame(rows)

        # Fallback to dict
        result_dict = {}
        for attr in sorted(total_jobs_by_attribute.keys()):
            total = total_jobs_by_attribute.get(attr, 0)
            run_count = status_counts_by_attribute[attr].get(AttributeStatusEnum.RUN.value, 0)
            filled = value_filled_by_attribute.get(attr, 0)
            result_dict[attr] = {
                "total_jobs": total,
                "status_counts": dict(status_counts_by_attribute[attr]),
                "run_count": run_count,
                "run_rate": (run_count / total) if total else 0.0,
                "value_filled": filled,
                "value_fill_rate": (filled / total) if total else 0.0,
            }
        return result_dict

    @property
    def base_url(self) -> str:
        """Get the base URL for the API."""
        return self._base_url

    def close(self):
        """Close the underlying transport."""
        if self._transport:
            self._transport.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
