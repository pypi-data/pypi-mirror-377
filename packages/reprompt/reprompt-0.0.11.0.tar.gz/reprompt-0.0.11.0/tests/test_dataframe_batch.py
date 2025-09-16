"""Updated tests for DataFrame batch creation functionality with new validation."""

from __future__ import annotations

import unittest.mock

import pytest

from reprompt import RepromptClient
from reprompt.generated.models import AttributeSet


def test_client_gating_read_only():
    """Test that read-only client prevents batch creation."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=False)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "name": "Test Place",
                    "place_id": "p1",
                    "full_address": "123 Main St",
                    "latitude": 40.0,
                    "longitude": -74.0,
                }
            ]
        )

        with pytest.raises(ValueError, match="Client is read-only; set allow_writes=True to create batches"):
            client.batches.create_from_dataframe(df, batch_name="Test Batch")

    client.close()


def test_validation_missing_name():
    """Test that empty name raises ValueError."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        # DataFrame with one empty name field
        df = pd.DataFrame(
            [
                {
                    "name": "Valid Place",
                    "place_id": "p1",
                    "full_address": "123 Main St",
                    "latitude": 40.0,
                    "longitude": -74.0,
                },
                {
                    "name": "",
                    "place_id": "p2",
                    "full_address": "456 Oak Ave",
                    "latitude": 41.0,
                    "longitude": -75.0,
                },  # Empty name
            ]
        )

        with pytest.raises(ValueError) as exc_info:
            client.batches.create_from_dataframe(df, batch_name="Test Batch")

        assert "Empty/null values in 'name'" in str(exc_info.value)

    client.close()


def test_validation_required_columns():
    """Test that missing required columns raises clear error."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        # DataFrame missing place_id column
        df = pd.DataFrame([{"name": "Test Place", "full_address": "123 Main St", "latitude": 40.0, "longitude": -74.0}])

        with pytest.raises(ValueError) as exc_info:
            client.batches.create_from_dataframe(df, batch_name="Test Batch")

        assert "Missing required column: place_id" in str(exc_info.value)

    client.close()


def test_successful_batch_creation():
    """Test successful batch creation with all required fields."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        # Mock successful transport.post
        with unittest.mock.patch.object(client.batches._transport, "post") as mock_post:
            mock_post.return_value = {
                "id": "batch_123",
                "batch_name": "Test Batch",
                "status": "pending",
                "jobs": {},
                "metadata": None,
            }

            # Valid DataFrame with all required fields
            df = pd.DataFrame(
                [
                    {
                        "name": "Place 1",
                        "place_id": "p1",
                        "full_address": "123 Main St",
                        "latitude": 40.7128,
                        "longitude": -74.0060,
                    },
                    {
                        "name": "Place 2",
                        "place_id": "p2",
                        "full_address": "456 Oak Ave",
                        "latitude": 40.7129,
                        "longitude": -74.0061,
                        "country_code": "US",
                    },
                ]
            )

            # Should succeed
            response = client.batches.create_from_dataframe(df, batch_name="Test Batch")
            assert response.id == "batch_123"
            assert mock_post.called

            # Verify payload structure
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            assert len(payload["jobs"]) == 2

            # Check first job
            job1 = payload["jobs"][0]
            assert job1["place_id"] == "p1"
            assert set(job1["inputs"].keys()) == {"name", "full_address", "latitude", "longitude"}

            # Check second job (has country_code)
            job2 = payload["jobs"][1]
            assert job2["place_id"] == "p2"
            assert set(job2["inputs"].keys()) == {"name", "full_address", "latitude", "longitude", "country_code"}

    client.close()


def test_duplicate_detection_with_place_id():
    """Test duplicate place_id detection."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        # DataFrame with duplicate place_id
        df = pd.DataFrame(
            [
                {
                    "place_id": "place_1",
                    "name": "Place 1",
                    "full_address": "123 Main St",
                    "latitude": 40.0,
                    "longitude": -74.0,
                },
                {
                    "place_id": "place_1",
                    "name": "Place 2",
                    "full_address": "456 Oak Ave",
                    "latitude": 41.0,
                    "longitude": -75.0,
                },  # Duplicate
            ]
        )

        with pytest.raises(ValueError) as exc_info:
            client.batches.create_from_dataframe(df, batch_name="Test Batch")

        assert "Duplicate place_id found" in str(exc_info.value)
        assert "place_1" in str(exc_info.value)

    client.close()


def test_duplicate_detection_override():
    """Test that ignore_duplicate_place_ids parameter works."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        # Mock successful transport.post
        with unittest.mock.patch.object(client.batches._transport, "post") as mock_post:
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


def test_attribute_selection_exclusivity():
    """Test that providing both attribute_set and attributes raises ValueError."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        df = pd.DataFrame(
            [
                {
                    "name": "Test Place",
                    "place_id": "p1",
                    "full_address": "123 Main St",
                    "latitude": 40.0,
                    "longitude": -74.0,
                }
            ]
        )

        with pytest.raises(ValueError, match="Cannot specify both attribute_set and attributes"):
            client.batches.create_from_dataframe(
                df, batch_name="Test Batch", attribute_set=AttributeSet.core, attributes=["name", "address"]
            )

    client.close()


def test_coordinate_range_validation():
    """Test that invalid coordinate ranges are caught."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        # DataFrame with invalid coordinates
        df = pd.DataFrame(
            [
                {
                    "name": "Invalid Place",
                    "place_id": "p1",
                    "full_address": "123 Main St",
                    "latitude": 91.0,
                    "longitude": -74.0060,
                },  # lat > 90
            ]
        )

        with pytest.raises(ValueError) as exc_info:
            client.batches.create_from_dataframe(df, batch_name="Test Batch")

        assert "Invalid latitude values" in str(exc_info.value)
        assert "must be -90 to 90" in str(exc_info.value)

        # Test invalid longitude
        df2 = pd.DataFrame(
            [
                {
                    "name": "Invalid Place",
                    "place_id": "p1",
                    "full_address": "123 Main St",
                    "latitude": 40.0,
                    "longitude": 181.0,
                },  # lng > 180
            ]
        )

        with pytest.raises(ValueError) as exc_info:
            client.batches.create_from_dataframe(df2, batch_name="Test Batch")

        assert "Invalid longitude values" in str(exc_info.value)
        assert "must be -180 to 180" in str(exc_info.value)

    client.close()


def test_pandas_not_available():
    """Test graceful handling when pandas is not available."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    # Mock pandas as not available
    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", False):
        with pytest.raises(ImportError, match="pandas is required"):
            client.batches.create_from_dataframe([], batch_name="Test")

    client.close()


def test_vectorized_column_normalization():
    """Test vectorized column name normalization works correctly."""
    client = RepromptClient(api_key="test-key", org_slug="test-org", allow_writes=True)

    with unittest.mock.patch("reprompt.dataframe.PANDAS_AVAILABLE", True):
        import pandas as pd

        # Mock successful transport.post
        with unittest.mock.patch.object(client.batches._transport, "post") as mock_post:
            mock_post.return_value = {
                "id": "batch_123",
                "batch_name": "Test",
                "status": "pending",
                "jobs": {},
                "metadata": None,
            }

            # DataFrame with various column name formats that should be normalized
            df = pd.DataFrame(
                [
                    {
                        "NAME": "Place 1",
                        "Place_ID": "p1",
                        "FULL_ADDRESS": "123 Main St",
                        "LAT": 40.0,
                        "LNG": -74.0,
                    }
                ]
            )

            response = client.batches.create_from_dataframe(df, batch_name="Test")
            assert response.id == "batch_123"

            # Verify normalized data in API call
            call_args = mock_post.call_args
            payload = call_args[1]["json"]
            job = payload["jobs"][0]

            assert job["inputs"]["name"] == "Place 1"
            assert job["inputs"]["full_address"] == "123 Main St"
            assert job["inputs"]["latitude"] == 40.0
            assert job["inputs"]["longitude"] == -74.0
            assert job["place_id"] == "p1"

    client.close()
