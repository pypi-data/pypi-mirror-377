"""Pagination iterators for Reprompt API."""

from __future__ import annotations

import concurrent.futures
import itertools
import logging
from typing import Callable, Any

from .dataframe import batches_to_dataframe, jobs_to_dataframe
from .generated.models import PlaceJobResult

logger = logging.getLogger(__name__)


class CompositeJobsIterator:
    """Iterator that fetches jobs from multiple batches sequentially."""

    def __init__(self, batches_iterator, client):
        self.batches_iterator = batches_iterator
        self.client = client
        self.current_jobs_iterator = None
        self.batches = None
        self.batch_index = 0

    def __iter__(self):
        # Materialize all batches first
        self.batches = list(self.batches_iterator)
        self.batch_index = 0
        self.current_jobs_iterator = None
        return self

    def __getitem__(self, key):
        """Support slicing and indexing for the iterator."""
        if isinstance(key, slice):
            # Handle slicing like jobs[:10]
            start = key.start or 0
            stop = key.stop
            step = key.step or 1

            # Use itertools.islice to efficiently slice the iterator
            return list(itertools.islice(self, start, stop, step))
        if isinstance(key, int):
            # Handle single item access
            if key < 0:
                # Negative indexing requires materializing the whole list
                items = list(self)
                return items[key]
            # For positive index, iterate until we reach it
            for i, item in enumerate(self):
                if i == key:
                    return item
            raise IndexError(f"Index {key} out of range")
        raise TypeError(f"Iterator indices must be integers or slices, not {type(key).__name__}")

    def __next__(self):
        while True:
            # If we have a current jobs iterator, try to get next job
            if self.current_jobs_iterator is not None:
                try:
                    return next(self.current_jobs_iterator)
                except StopIteration:
                    # Current batch is exhausted, move to next batch
                    self.current_jobs_iterator = None
                    self.batch_index += 1

            # Check if we've processed all batches
            if self.batches is None or self.batch_index >= len(self.batches):
                raise StopIteration

            # Get current batch and create jobs iterator for it
            current_batch = self.batches[self.batch_index]
            batch_id = current_batch.id if hasattr(current_batch, "id") else str(current_batch)

            try:
                # Use the client's jobs sub-API to get jobs
                self.current_jobs_iterator = self.client.jobs.get_jobs_by_batch_id(batch_id=batch_id, page_size=1000)
            except Exception as e:  # pylint: disable=broad-exception-caught
                # Skip this batch and move to next
                batch_name = (
                    getattr(current_batch, "batch_name", "Unknown")
                    if hasattr(current_batch, "batch_name")
                    else "Unknown"
                )
                logger.error(
                    "Failed to create jobs iterator for batch_id=%s batch_name='%s': %s", batch_id, batch_name, e
                )
                self.batch_index += 1
                continue

    def to_df(
        self,
        parallel: bool = True,
        max_concurrent: int = 20,
        raise_exceptions: bool = True,
        include_inputs: bool = True,
        include_reasoning: bool = True,
        include_confidence: bool = True,
        include_batch: bool = True,
        include_not_run: bool = False,
    ):
        """
        Convert all jobs from the iterator to a pandas DataFrame.

        Args:
            parallel: Use parallel processing (default: True)
            max_concurrent: Maximum concurrent requests when using parallel mode (default: 20)
            raise_exceptions: Raise exceptions on errors (default: True).
                If False, errors are logged and processing continues.
            include_inputs: Include input fields (default: True)
            include_reasoning: Include reasoning fields (default: True)
            include_confidence: Include confidence score fields (default: True)
            include_batch: Include batch_id field (default: True)
            include_not_run: Include columns with all None/NaN values (default: False)

        Returns:
            pd.DataFrame with flattened job data
        """
        if parallel:
            return self._to_df_parallel(
                max_concurrent,
                raise_exceptions,
                include_inputs,
                include_reasoning,
                include_confidence,
                include_batch,
                include_not_run,
            )
        # Sequential processing - collect all jobs from all batches
        all_jobs = list(self)
        return jobs_to_dataframe(
            all_jobs, include_inputs, include_reasoning, include_confidence, include_batch, include_not_run
        )

    def _to_df_parallel(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        max_concurrent: int,
        raise_exceptions: bool,
        include_inputs: bool,
        include_reasoning: bool,
        include_confidence: bool,
        include_batch: bool,
        include_not_run: bool,
    ):
        """Convert all jobs to DataFrame using the generated client."""
        # Get all batches first
        all_batches = list(self.batches_iterator)

        if not all_batches:
            return jobs_to_dataframe(
                [], include_inputs, include_reasoning, include_confidence, include_batch, include_not_run
            )

        # Use the generated client directly (it handles all HTTP operations)
        return self._fetch_jobs_parallel(
            all_batches,
            max_concurrent,
            raise_exceptions,
            include_inputs,
            include_reasoning,
            include_confidence,
            include_batch,
            include_not_run,
        )

    def _fetch_jobs_parallel(  # pylint: disable=too-many-locals,too-many-arguments
        self,
        all_batches,
        max_concurrent: int,
        raise_exceptions: bool,
        include_inputs: bool,
        include_reasoning: bool,
        include_confidence: bool,
        include_batch: bool,
        include_not_run: bool,
    ):
        """Fetch jobs from batches using concurrent.futures for parallel execution."""
        logger.info(
            "Fetching jobs from %s batches in parallel (max_concurrent=%s)...", len(all_batches), max_concurrent
        )

        def fetch_batch_jobs(batch):
            """Fetch jobs for a single batch."""
            batch_id = batch.id if hasattr(batch, "id") else str(batch)
            batch_name = getattr(batch, "batch_name", "Unknown") if hasattr(batch, "batch_name") else "Unknown"

            try:
                logger.debug("Fetching jobs from batch_id=%s batch_name='%s'", batch_id, batch_name)
                # Use the client's jobs sub-API to get jobs
                jobs_iterator = self.client.jobs.get_jobs_by_batch_id(batch_id=batch_id, page_size=1000)
                batch_jobs = list(jobs_iterator)
                logger.debug("Got %s jobs from batch %s", len(batch_jobs), batch_id)
                return batch_jobs
            except Exception as e:  # pylint: disable=broad-exception-caught
                error_msg = f"Failed to fetch jobs from batch_id={batch_id} batch_name='{batch_name}': {e}"
                logger.error(error_msg)
                if raise_exceptions:
                    raise RuntimeError(error_msg) from e
                return []  # Return empty list on error if not raising exceptions

        all_jobs = []

        # Use ThreadPoolExecutor for parallel fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all batch fetches
            future_to_batch = {executor.submit(fetch_batch_jobs, batch): batch for batch in all_batches}

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_batch):
                try:
                    batch_jobs = future.result()
                    all_jobs.extend(batch_jobs)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    if raise_exceptions:
                        raise
                    # Log error and continue
                    logger.error("Error fetching batch jobs: %s", e)
                    continue

        logger.info("Fetched %s total jobs from %s batches", len(all_jobs), len(all_batches))
        return jobs_to_dataframe(
            all_jobs, include_inputs, include_reasoning, include_confidence, include_batch, include_not_run
        )


def default_extractor(response: Any) -> list:
    """Default response data extractor."""
    if hasattr(response, "batches"):
        return response.batches
    if isinstance(response, dict) and "batches" in response:
        return response["batches"]
    if isinstance(response, list):
        return response
    return []


def jobs_extractor(response: Any) -> list:
    """Jobs response data extractor."""
    jobs = []
    if hasattr(response, "jobs"):
        jobs = response.jobs
    elif isinstance(response, dict) and "jobs" in response:
        jobs = response["jobs"]
    else:
        return []

    # Convert dict jobs to PlaceJobResult objects if needed
    # Import here to avoid circular dependency
    from .client import _normalize_datetime_fields  # pylint: disable=import-outside-toplevel,cyclic-import

    result = []
    for job in jobs:
        if isinstance(job, dict):
            # Normalize datetime fields to ensure they have timezone info
            job = _normalize_datetime_fields(job)
            result.append(PlaceJobResult(**job))
        else:
            result.append(job)
    return result


class PaginatedIterator:  # pylint: disable=too-many-instance-attributes
    """Iterator for paginated API responses."""

    def __init__(
        self,
        fetch_func: Callable,
        page_size: int = 100,  # Use 100 as default to match MAX_BATCH_LIMIT
        extractor: Callable[[Any], list] = default_extractor,
        error_context: str = "Pagination",
        client=None,
        **filters,
    ):
        self.fetch_func = fetch_func
        self.page_size = page_size
        self.extractor = extractor
        self.error_context = error_context
        self.client = client  # Store client reference for get_jobs()
        self.filters = filters
        self.offset = 0
        self.current_page = []
        self.current_index = 0
        self.exhausted = False

    def __iter__(self):
        return self

    def __getitem__(self, key):
        """Support slicing and indexing for the iterator."""
        if isinstance(key, slice):
            # Handle slicing like batches[:5]
            start = key.start or 0
            stop = key.stop
            step = key.step or 1

            # Use itertools.islice to efficiently slice the iterator
            return list(itertools.islice(self, start, stop, step))
        if isinstance(key, int):
            # Handle single item access like batches[0]
            if key < 0:
                # Negative indexing requires materializing the whole list
                items = list(self)
                return items[key]
            # For positive index, iterate until we reach it
            for i, item in enumerate(self):
                if i == key:
                    return item
            raise IndexError(f"Index {key} out of range")
        raise TypeError(f"Iterator indices must be integers or slices, not {type(key).__name__}")

    def __next__(self):
        # If we've consumed all items in current page, fetch next page
        if self.current_index >= len(self.current_page):
            if self.exhausted:
                raise StopIteration

            # Fetch next page
            try:
                response = self.fetch_func(limit=self.page_size, offset=self.offset, **self.filters)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("Failed to fetch %s page at offset %s: %s", self.error_context.lower(), self.offset, e)
                raise

            # Extract data using the provided extractor function
            self.current_page = self.extractor(response)
            self.offset += len(self.current_page)
            self.current_index = 0

            # If we got less than page_size items, we've reached the end
            if len(self.current_page) < self.page_size:
                self.exhausted = True

            # If no items in this page, we're done
            if not self.current_page:
                raise StopIteration

        # Return current item and advance index
        item = self.current_page[self.current_index]
        self.current_index += 1
        return item

    def to_df(self):
        """
        Convert all items from the iterator to a pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing all items from the iterator

        Raises:
            ImportError: If pandas is not installed
            Exception: If API call fails during iteration
        """
        # Collect all items from iterator
        all_items = list(self)

        # Use the helper function for batches
        return batches_to_dataframe(all_items)

    # Removed to_jobs_df method - use .get_jobs().to_df() pattern instead

    def get_jobs(self):
        """
        Get a jobs iterator that fetches jobs from all batches in this iterator.

        Returns:
            JobsPaginatedIterator: Iterator that yields jobs from all batches

        Raises:
            ValueError: If client is not available
        """
        if self.client is None:
            raise ValueError("Client reference not available. get_jobs() requires a client to fetch job data.")

        # Create a composite jobs iterator that fetches from all batches
        return CompositeJobsIterator(self, self.client)


class JobsPaginatedIterator(PaginatedIterator):
    """Specialized iterator for jobs pagination."""

    def __init__(self, fetch_func: Callable, page_size: int = 1000, client=None, **filters):
        super().__init__(
            fetch_func=fetch_func,
            page_size=page_size,
            extractor=jobs_extractor,
            error_context="Jobs pagination",
            client=client,
            **filters,
        )

    def to_df(self):
        """
        Convert all jobs from the iterator to a pandas DataFrame with flattened structure.

        Returns:
            pd.DataFrame: DataFrame with flattened job data including inputs and results

        Raises:
            ImportError: If pandas is not installed
            Exception: If API call fails during iteration
        """
        # Collect all items from iterator
        all_items = list(self)

        # Use the helper function for jobs
        return jobs_to_dataframe(all_items)
