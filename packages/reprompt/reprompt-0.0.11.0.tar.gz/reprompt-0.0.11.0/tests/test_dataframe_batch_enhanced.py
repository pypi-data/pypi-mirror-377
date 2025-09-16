"""Tests for enhanced DataFrame batch creation with strict validation and performance optimizations."""

from __future__ import annotations

import asyncio
import unittest.mock
from unittest.mock import AsyncMock, Mock, patch

import pytest

from reprompt import RepromptClient
from reprompt.exceptions import RepromptAPIError
from reprompt.generated.models import AttributeSet


class TestStrictValidation:
    """Test strict validation requirements with clear error messages."""

    def test_missing_required_column_name(self):
        """Test missing 'name' column raises clear error."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            df = pd.DataFrame([{"place_id": "p1", "full_address": "123 Main St", "latitude": 40.0, "longitude": -74.0}])

            with pytest.raises(ValueError, match="Missing required column: name"):
                client.batches.create_from_dataframe(df, batch_name="Test")

        client.close()

    def test_missing_required_column_place_id(self):
        """Test missing 'place_id' column raises clear error."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            df = pd.DataFrame(
                [{"name": "Test Place", "full_address": "123 Main St", "latitude": 40.0, "longitude": -74.0}]
            )

            with pytest.raises(ValueError, match="Missing required column: place_id"):
                client.batches.create_from_dataframe(df, batch_name="Test")

        client.close()

    def test_missing_required_column_full_address(self):
        """Test missing 'full_address' column raises clear error (now required)."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            df = pd.DataFrame([{"name": "Test Place", "place_id": "p1", "latitude": 40.0, "longitude": -74.0}])

            with pytest.raises(ValueError, match="Missing required column: full_address"):
                client.batches.create_from_dataframe(df, batch_name="Test")

        client.close()

    def test_missing_multiple_columns(self):
        """Test missing multiple columns shows all missing."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            df = pd.DataFrame([{"name": "Test Place"}])  # Missing place_id, full_address, latitude, longitude

            with pytest.raises(ValueError) as exc_info:
                client.batches.create_from_dataframe(df, batch_name="Test")

            error_msg = str(exc_info.value)
            assert "Missing required columns:" in error_msg
            assert "place_id" in error_msg
            assert "full_address" in error_msg
            assert "latitude" in error_msg
            assert "longitude" in error_msg

        client.close()

    def test_empty_dataframe(self):
        """Test empty DataFrame raises clear error."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            df = pd.DataFrame()

            with pytest.raises(ValueError, match="DataFrame is empty"):
                client.batches.create_from_dataframe(df, batch_name="Test")

        client.close()


class TestDuplicateDetection:
    """Test efficient duplicate detection with configurable behavior."""

    def test_duplicate_place_ids_default_strict(self):
        """Test duplicate place_ids raise exception by default."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            df = pd.DataFrame(
                [
                    {
                        "name": "Place 1",
                        "place_id": "duplicate",
                        "full_address": "123 Main St",
                        "latitude": 40.0,
                        "longitude": -74.0,
                    },
                    {
                        "name": "Place 2",
                        "place_id": "duplicate",
                        "full_address": "456 Oak Ave",
                        "latitude": 41.0,
                        "longitude": -75.0,
                    },
                ]
            )

            with pytest.raises(ValueError) as exc_info:
                client.batches.create_from_dataframe(df, batch_name="Test")

            error_msg = str(exc_info.value)
            assert "Duplicate place_id found" in error_msg
            assert "duplicate" in error_msg
            assert "rows [0, 1]" in error_msg

        client.close()

    def test_duplicate_place_ids_allow_override(self):
        """Test ignore_duplicate_place_ids parameter allows duplicates."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            # Mock successful API response
            with patch.object(client.batches._transport, "post") as mock_post:
                mock_post.return_value = {
                    "id": "batch_123",
                    "batch_name": "Test",
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

                df = pd.DataFrame(
                    [
                        {
                            "name": "Place 1",
                            "place_id": "duplicate",
                            "full_address": "123 Main St",
                            "latitude": 40.0,
                            "longitude": -74.0,
                        },
                        {
                            "name": "Place 2",
                            "place_id": "duplicate",
                            "full_address": "456 Oak Ave",
                            "latitude": 41.0,
                            "longitude": -75.0,
                        },
                    ]
                )

                # Should succeed with ignore_duplicate_place_ids=True
                response = client.batches.create_from_dataframe(df, batch_name="Test", ignore_duplicate_place_ids=True)

                assert response.id == "batch_123"
                assert mock_post.called

        client.close()

    def test_large_dataset_duplicate_detection_performance(self):
        """Test duplicate detection is efficient on large datasets."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd
            import time

            # Create large dataset with one duplicate at the end
            size = 50000
            data = []
            for i in range(size - 1):
                data.append(
                    {
                        "name": f"Place {i}",
                        "place_id": f"place_{i}",
                        "full_address": f"{i} Test St",
                        "latitude": 40.0 + (i * 0.001),
                        "longitude": -74.0 + (i * 0.001),
                    }
                )
            # Add duplicate
            data.append(
                {
                    "name": "Place Duplicate",
                    "place_id": "place_0",  # Duplicate of first row
                    "full_address": "999 Duplicate St",
                    "latitude": 40.999,
                    "longitude": -73.999,
                }
            )

            df = pd.DataFrame(data)

            start_time = time.time()
            with pytest.raises(ValueError, match="Duplicate place_id found"):
                client.batches.create_from_dataframe(df, batch_name="Large Test")

            elapsed = time.time() - start_time
            # Should be fast (< 1 second for vectorized operations)
            assert elapsed < 1.0, f"Duplicate detection too slow: {elapsed:.2f}s"

        client.close()


class TestVectorizedOperations:
    """Test vectorized DataFrame operations for performance."""

    def test_vectorized_column_normalization(self):
        """Test vectorized column name normalization."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            # Mock successful API response
            with patch.object(client.batches._transport, "post") as mock_post:
                mock_post.return_value = {
                    "id": "batch_123",
                    "batch_name": "Test",
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

                # DataFrame with various column name formats
                df = pd.DataFrame(
                    [
                        {
                            "NAME": "Place 1",
                            "Place_ID": "p1",
                            "FULL_ADDRESS": "123 Main St",
                            "LAT": 40.0,
                            "LNG": -74.0,
                            "Country_Code": "US",
                        }
                    ]
                )

                response = client.batches.create_from_dataframe(df, batch_name="Test")
                assert response.id == "batch_123"

                # Verify API call structure
                call_args = mock_post.call_args
                payload = call_args[1]["json"]
                job = payload["jobs"][0]

                # Should have normalized inputs
                assert job["inputs"]["name"] == "Place 1"
                assert job["inputs"]["full_address"] == "123 Main St"
                assert job["inputs"]["latitude"] == 40.0
                assert job["inputs"]["longitude"] == -74.0
                assert job["place_id"] == "p1"

        client.close()

    def test_vectorized_data_cleaning(self):
        """Test vectorized string cleaning operations."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            with patch.object(client.batches._transport, "post") as mock_post:
                mock_post.return_value = {
                    "id": "batch_123",
                    "batch_name": "Test",
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

                df = pd.DataFrame(
                    [
                        {
                            "name": "  Place With Spaces  ",
                            "place_id": "p1  ",
                            "full_address": "\t123 Main St\n",
                            "latitude": 40.0,
                            "longitude": -74.0,
                        }
                    ]
                )

                response = client.batches.create_from_dataframe(df, batch_name="Test")

                call_args = mock_post.call_args
                payload = call_args[1]["json"]
                job = payload["jobs"][0]

                # Should have cleaned strings
                assert job["inputs"]["name"] == "Place With Spaces"
                assert job["inputs"]["full_address"] == "123 Main St"
                assert job["place_id"] == "p1"

        client.close()


class TestAsyncBatchCreation:
    """Test async batch creation with semaphore for large datasets."""

    @pytest.mark.asyncio
    async def test_async_multiple_batches_with_semaphore(self):
        """Test async batch creation with controlled concurrency."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            # Create dataset that will be split into multiple batches
            size = 1000
            data = []
            for i in range(size):
                data.append(
                    {
                        "name": f"Place {i}",
                        "place_id": f"place_{i}",
                        "full_address": f"{i} Test St",
                        "latitude": 40.0,
                        "longitude": -74.0,
                    }
                )

            df = pd.DataFrame(data)

            # Mock async transport post method
            call_count = 0

            async def mock_post_async(path, json=None):
                nonlocal call_count
                call_count += 1
                await asyncio.sleep(0.01)  # Simulate network delay
                return {
                    "id": f"batch_{call_count}",
                    "batch_name": json["batch_name"],
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

            with patch.object(client.batches._transport, "post_async", mock_post_async):
                # Split into 10 batches with max 3 concurrent
                responses = await client.batches.create_from_dataframe_async(
                    df, batch_name="Async Test", batch_size=100, max_concurrent_batches=3
                )

                assert len(responses) == 10  # Should create 10 batches
                assert all(r.id.startswith("batch_") for r in responses)
                assert call_count == 10

        client.close()

    @pytest.mark.asyncio
    async def test_async_batch_partial_failures(self):
        """Test handling of partial failures in async batch creation."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            data = []
            for i in range(300):  # Will create 3 batches
                data.append(
                    {
                        "name": f"Place {i}",
                        "place_id": f"place_{i}",
                        "full_address": f"{i} Test St",
                        "latitude": 40.0,
                        "longitude": -74.0,
                    }
                )

            df = pd.DataFrame(data)

            # Mock async post that fails on second batch
            call_count = 0

            async def mock_post_with_failure(path, json=None):
                nonlocal call_count
                call_count += 1
                if call_count == 2:
                    raise Exception("Network error on batch 2")
                return {
                    "id": f"batch_{call_count}",
                    "batch_name": json["batch_name"],
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

            with patch.object(client.batches._transport, "post_async", mock_post_with_failure):
                results = await client.batches.create_from_dataframe_async(
                    df, batch_name="Partial Failure Test", batch_size=100
                )

                # Should return results for all batches, some successful, some failed
                assert len(results) == 3

                # Two should be successful responses
                successful = [r for r in results if hasattr(r, "id")]
                failed = [r for r in results if isinstance(r, Exception)]

                assert len(successful) == 2
                assert len(failed) == 1
                assert "Network error on batch 2" in str(failed[0])

        client.close()


class TestLargeDatasetHandling:
    """Test handling of large datasets (50K+ rows)."""

    def test_large_dataset_memory_efficiency(self):
        """Test memory-efficient processing of large datasets."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd
            import psutil
            import os

            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Create 50K row dataset
            size = 50000
            data = []
            for i in range(size):
                data.append(
                    {
                        "name": f"Place {i}",
                        "place_id": f"place_{i}",
                        "full_address": f"{i} Test Street, City, State 12345",
                        "latitude": 40.0 + (i * 0.0001),
                        "longitude": -74.0 + (i * 0.0001),
                        "country_code": "US",
                    }
                )

            df = pd.DataFrame(data)

            with patch.object(client.batches._transport, "post") as mock_post:
                mock_post.return_value = {
                    "id": "batch_large",
                    "batch_name": "Large Dataset Test",
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

                # Process as single batch first (should work)
                response = client.batches.create_from_dataframe(df, batch_name="Large Dataset Test")

                # Check memory didn't explode
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory

                # Should not use more than 500MB additional memory
                assert memory_increase < 500, f"Memory usage too high: {memory_increase:.1f}MB"
                assert response.id == "batch_large"

        client.close()

    def test_large_dataset_batch_splitting_performance(self):
        """Test performance of splitting large datasets into multiple batches."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd
            import time

            # Create 100K row dataset
            size = 100000
            data = []
            for i in range(size):
                data.append(
                    {
                        "name": f"Place {i}",
                        "place_id": f"place_{i}",
                        "full_address": f"{i} Test St",
                        "latitude": 40.0,
                        "longitude": -74.0,
                    }
                )

            df = pd.DataFrame(data)

            batch_responses = []

            def mock_post(path, json=None):
                batch_id = f"batch_{len(batch_responses) + 1}"
                batch_responses.append(batch_id)
                return {
                    "id": batch_id,
                    "batch_name": json["batch_name"],
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

            with patch.object(client.batches._transport, "post", mock_post):
                start_time = time.time()

                # Split into 10 batches of 10K each
                responses = client.batches.create_from_dataframe(df, batch_name="Performance Test", batch_size=10000)

                elapsed = time.time() - start_time

                # Should complete in reasonable time (< 5 seconds)
                assert elapsed < 5.0, f"Batch splitting too slow: {elapsed:.2f}s"
                assert len(responses) == 10
                assert len(batch_responses) == 10

        client.close()

    def test_cross_batch_place_id_uniqueness(self):
        """Test that place_id uniqueness is maintained across batch splits."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            # Create dataset with intentional duplicate that would span batches
            size = 1500  # Will create 2 batches of 1000 each, with duplicate in different batches
            data = []
            for i in range(size):
                data.append(
                    {
                        "name": f"Place {i}",
                        "place_id": f"place_{i}",
                        "full_address": f"{i} Test St",
                        "latitude": 40.0,
                        "longitude": -74.0,
                    }
                )

            # Add duplicate place_id that will be in second batch
            data.append(
                {
                    "name": "Duplicate Place",
                    "place_id": "place_0",  # Same as first row, but will be in different batch
                    "full_address": "999 Duplicate St",
                    "latitude": 41.0,
                    "longitude": -75.0,
                }
            )

            df = pd.DataFrame(data)

            # Should detect duplicate even across batch boundaries
            with pytest.raises(ValueError, match="Duplicate place_id found"):
                client.batches.create_from_dataframe(df, batch_name="Cross Batch Duplicate Test", batch_size=1000)

        client.close()


class TestCountryCodeSupport:
    """Test optional country_code support."""

    def test_country_code_included_when_present(self):
        """Test country_code is included in API payload when present."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            with patch.object(client.batches._transport, "post") as mock_post:
                mock_post.return_value = {
                    "id": "batch_123",
                    "batch_name": "Test",
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

                df = pd.DataFrame(
                    [
                        {
                            "name": "Place 1",
                            "place_id": "p1",
                            "full_address": "123 Main St",
                            "latitude": 40.0,
                            "longitude": -74.0,
                            "country_code": "US",
                        }
                    ]
                )

                response = client.batches.create_from_dataframe(df, batch_name="Test")

                call_args = mock_post.call_args
                payload = call_args[1]["json"]
                job = payload["jobs"][0]

                assert job["inputs"]["country_code"] == "US"

        client.close()

    def test_country_code_optional(self):
        """Test country_code is not required."""
        client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

        with patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
            import pandas as pd

            with patch.object(client.batches._transport, "post") as mock_post:
                mock_post.return_value = {
                    "id": "batch_123",
                    "batch_name": "Test",
                    "status": "pending",
                    "jobs": {},
                    "metadata": None,
                }

                df = pd.DataFrame(
                    [
                        {
                            "name": "Place 1",
                            "place_id": "p1",
                            "full_address": "123 Main St",
                            "latitude": 40.0,
                            "longitude": -74.0,
                            # No country_code
                        }
                    ]
                )

                response = client.batches.create_from_dataframe(df, batch_name="Test")
                assert response.id == "batch_123"

                call_args = mock_post.call_args
                payload = call_args[1]["json"]
                job = payload["jobs"][0]

                # Should not include country_code in inputs
                assert "country_code" not in job["inputs"]

        client.close()
