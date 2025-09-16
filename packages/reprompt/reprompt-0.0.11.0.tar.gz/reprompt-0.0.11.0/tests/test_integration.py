"""Integration tests for the Reprompt SDK using the test API."""

# pylint: disable=redefined-outer-name
# ^ This is expected behavior for pytest fixtures

import os
import pytest
from reprompt import RepromptClient

# Mark entire module as integration tests
pytestmark = pytest.mark.integration

# Test credentials from environment or defaults
TEST_API_KEY = os.getenv("REPROMPT_API_KEY", "test-api-key")
TEST_ORG_SLUG = os.getenv("REPROMPT_ORG_SLUG", "test-hp")


@pytest.fixture
def test_client():
    """Create a test test_client."""
    return RepromptClient(api_key=TEST_API_KEY, org_slug=TEST_ORG_SLUG)


class TestBatchesAPI:
    """Test the batches sub-API."""

    def test_list_batches(self, test_client):
        """Test listing batches with pagination."""
        # Get first 3 batches
        batches = list(test_client.batches.list_batches()[:3])

        # Should return a list (even if empty)
        assert isinstance(batches, list)

        # If we have batches, check their structure
        if batches:
            first_batch = batches[0]
            assert hasattr(first_batch, "id")
            assert hasattr(first_batch, "batch_name")
            assert hasattr(first_batch, "status")
            assert hasattr(first_batch, "status_counts")

    def test_get_batch(self, test_client):
        """Test getting a specific batch."""
        # Get first batch to test with
        batches = list(test_client.batches.list_batches()[:1])

        if batches:
            batch_id = batches[0].id
            batch = test_client.batches.get_batch(batch_id)

            # get_batch returns a raw dict with different structure
            assert batch["id"] == batch_id
            assert "batch_name" in batch
            assert "status" in batch

    def test_batch_search(self, test_client):
        """Test searching batches by name."""
        # Search for E2E batches
        e2e_batches = list(test_client.batches.list_batches(query="E2E")[:5])

        # All returned batches should contain "E2E" in name
        for batch in e2e_batches:
            assert "E2E" in batch.batch_name or "e2e" in batch.batch_name.lower()

    def test_batch_iterator_slicing(self, test_client):
        """Test that batch iterator supports slicing."""
        iterator = test_client.batches.list_batches()

        # Test different slice operations
        first_2 = iterator[:2]
        assert isinstance(first_2, list)
        assert len(first_2) <= 2


class TestJobsAPI:
    """Test the jobs sub-API."""

    def test_get_jobs_by_batch_id(self, test_client):
        """Test getting jobs for a specific batch."""
        # Get first batch with completed jobs
        batches = list(test_client.batches.list_batches()[:10])

        for batch in batches:
            if batch.status_counts.get("completed", 0) > 0:
                # Get first 5 jobs from this batch
                jobs = list(test_client.jobs.get_jobs_by_batch_id(batch.id)[:5])

                assert isinstance(jobs, list)
                if jobs:
                    first_job = jobs[0]
                    assert hasattr(first_job, "place_id")
                    assert hasattr(first_job, "status")
                break

    def test_get_job(self, test_client):
        """Test getting a specific job."""
        # Find a batch with jobs
        batches = list(test_client.batches.list_batches()[:10])

        for batch in batches:
            if batch.status_counts.get("completed", 0) > 0:
                jobs = list(test_client.jobs.get_jobs_by_batch_id(batch.id)[:1])

                if jobs:
                    place_id = jobs[0].place_id
                    job = test_client.jobs.get_job(place_id)

                    assert job.place_id == place_id
                    assert hasattr(job, "inputs")
                    assert hasattr(job, "outputs")
                    break

    def test_jobs_iterator_slicing(self, test_client):
        """Test that jobs iterator supports slicing."""
        # Find a batch with jobs
        batches = list(test_client.batches.list_batches()[:10])

        for batch in batches:
            if batch.status_counts.get("completed", 0) > 0:
                iterator = test_client.jobs.get_jobs_by_batch_id(batch.id)

                # Test slicing
                first_3 = iterator[:3]
                assert isinstance(first_3, list)
                assert len(first_3) <= 3
                break


class TestCompositeOperations:
    """Test composite operations across batches and jobs."""

    def test_get_jobs_from_multiple_batches(self, test_client):
        """Test getting jobs from multiple batches using get_jobs()."""
        # Get batches with E2E in name
        batches_iterator = test_client.batches.list_batches(query="E2E")

        # Get jobs from those batches
        jobs_iterator = batches_iterator.get_jobs()

        # Get first 10 jobs across all E2E batches
        jobs = jobs_iterator[:10]

        assert isinstance(jobs, list)
        # Check all jobs have expected fields
        for job in jobs:
            assert hasattr(job, "place_id")
            assert hasattr(job, "status")

    def test_to_dataframe(self, test_client):
        """Test converting results to DataFrame."""
        try:
            import pandas as pd  # pylint: disable=import-outside-toplevel
        except ImportError:
            pytest.skip("pandas not installed")

        # Get a small batch of data
        batches_iterator = test_client.batches.list_batches(query="E2E")

        # Convert batches to DataFrame
        batches_df = batches_iterator.to_df()
        assert isinstance(batches_df, pd.DataFrame)

        # Check expected columns
        if not batches_df.empty:
            assert "batch_id" in batches_df.columns
            assert "batch_name" in batches_df.columns

        # Convert jobs to DataFrame
        jobs_df = batches_iterator.get_jobs().to_df(parallel=False)
        assert isinstance(jobs_df, pd.DataFrame)

        # Check for flattened columns with dot notation
        if not jobs_df.empty:
            # Should have columns like inputs.name, outputs.field, etc.
            columns = list(jobs_df.columns)
            assert any(col.startswith("inputs.") for col in columns)


class TestClientLifecycle:
    """Test client initialization and lifecycle."""

    def test_client_initialization(self):
        """Test client can be initialized with API key and org slug."""
        client = RepromptClient(api_key=TEST_API_KEY, org_slug=TEST_ORG_SLUG)

        assert client.api_key == TEST_API_KEY
        assert client.org_slug == TEST_ORG_SLUG
        assert client.base_url == "https://api.repromptai.com/v1"

    def test_client_context_manager(self):
        """Test client works as context manager."""
        with RepromptClient(api_key=TEST_API_KEY, org_slug=TEST_ORG_SLUG) as test_client:
            assert test_client.api_key == TEST_API_KEY

            # Test that sub-APIs are accessible
            assert hasattr(test_client, "batches")
            assert hasattr(test_client, "jobs")

            # Test basic operation works
            batches = list(test_client.batches.list_batches()[:1])
            assert isinstance(batches, list)

    def test_sub_apis_accessible(self):
        """Test that sub-APIs are properly initialized."""
        client = RepromptClient(api_key=TEST_API_KEY, org_slug=TEST_ORG_SLUG)

        # Check sub-APIs exist
        assert hasattr(client, "batches")
        assert hasattr(client, "jobs")

        # Check sub-API methods exist
        assert hasattr(client.batches, "list_batches")
        assert hasattr(client.batches, "get_batch")
        assert hasattr(client.batches, "get_batches")

        assert hasattr(client.jobs, "get_jobs_by_batch_id")
        assert hasattr(client.jobs, "get_job")

        client.close()
