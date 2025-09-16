"""Tests for the new Reprompt client."""

from __future__ import annotations

import os

from reprompt import RepromptClient

# Removed PlaceJob and AttributeSet imports - read-only client


def assert_raises(exception_class, func, *args, **kwargs):
    """Simple assert_raises implementation."""
    try:
        func(*args, **kwargs)
        raise AssertionError(f"Expected {exception_class.__name__} to be raised")
    except exception_class:
        pass  # Expected exception was raised


def test_client_initialization():
    """Test basic client initialization."""
    # Test successful initialization
    client = RepromptClient(api_key="test-key", org_slug="test-hp")
    assert client.api_key == "test-key"
    assert client.org_slug == "test-hp"
    assert client.base_url == "https://api.repromptai.com/v1"
    client.close()

    # Test with custom base URL
    custom_client = RepromptClient(api_key="test-key", org_slug="test-org", base_url="https://custom.api.com/v1")
    assert custom_client.base_url == "https://custom.api.com/v1"
    custom_client.close()

    # Test error on missing API key
    assert_raises(ValueError, RepromptClient, api_key="", org_slug="test")

    # Test error on missing org_slug (clear env var first)
    old_org_slug = os.environ.get("REPROMPT_ORG_SLUG")
    if "REPROMPT_ORG_SLUG" in os.environ:
        del os.environ["REPROMPT_ORG_SLUG"]
    assert_raises(ValueError, RepromptClient, api_key="test-key")
    if old_org_slug:
        os.environ["REPROMPT_ORG_SLUG"] = old_org_slug


def test_client_properties():
    """Test client property access."""
    client = RepromptClient(api_key="test-key", org_slug="test-hp")

    # Test that API sub-clients are accessible
    assert hasattr(client, "batches")
    assert hasattr(client, "jobs")
    assert hasattr(client.batches, "list_batches")
    assert hasattr(client.jobs, "get_jobs_by_batch_id")

    # Test client properties
    assert client.api_key == "test-key"
    assert client.org_slug == "test-hp"

    client.close()


def test_context_managers():
    """Test context manager functionality."""
    # Test sync context manager
    with RepromptClient(api_key="test-key", org_slug="test-hp") as client:
        assert client.api_key == "test-key"

    # Test that client sub-APIs are accessible
    with RepromptClient(api_key="test-key", org_slug="test-hp") as client:
        assert hasattr(client, "batches")
        assert hasattr(client, "jobs")


# Removed test_place_job_creation - read-only client doesn't create jobs


if __name__ == "__main__":
    # Simple test runner for development
    test_client_initialization()
    test_client_properties()
    test_context_managers()
    print("✓ All tests passed!")
