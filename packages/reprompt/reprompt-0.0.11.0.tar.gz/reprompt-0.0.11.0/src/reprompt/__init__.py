"""Reprompt - Modern Python SDK for place enrichment API."""

from __future__ import annotations

import logging

from .client import (
    RepromptClient,
    BatchJob,
    BatchJobStatus,
    PlaceJobResult,
)
from .exceptions import RepromptAPIError
from .generated.models import AttributeSet, ReprocessJobRequest, UniversalPlace

logger = logging.getLogger(__name__)

# IMPORTANT: setting version for Reprompt package
__version__ = "0.0.11.0"

# IMPORTANT: All the classes and functions we want to expose publicly
__all__ = [
    # Main client (read-only)
    "RepromptClient",
    "RepromptAPIError",
    # Key models for read operations
    "PlaceJobResult",
    "BatchJob",
    # Enums
    "BatchJobStatus",
    "AttributeSet",
    # Models for creating requests
    "ReprocessJobRequest",
    "UniversalPlace",
    # Legacy compatibility
    "init",
]


def init(
    api_key: str, org_slug: str | None = None, base_url: str = "https://api.repromptai.com/v1", debug: bool = False
) -> RepromptClient:
    """
    Initialize and return a RepromptClient instance.

    This function provides backward compatibility while transitioning to the new client-based API.
    For new code, it's recommended to use RepromptClient directly.

    Args:
        api_key: Your Reprompt API key
        org_slug: Organization slug (e.g., 'test-hp'). If not provided, tries REPROMPT_ORG_SLUG env var
        base_url: Base URL for the API (default: https://api.repromptai.com/v1)
        debug: Enable debug logging (default: False)

    Returns:
        RepromptClient: Configured client instance

    Example:
        >>> client = init(api_key="your-api-key", org_slug="test-hp")
        >>> batches = client.batches.list_batches()
    """
    if debug:
        logging.getLogger("reprompt").setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    if not api_key:
        raise ValueError("API key is required")

    client = RepromptClient(api_key=api_key, org_slug=org_slug, base_url=base_url)
    logger.info("Reprompt v%s client initialized", __version__)

    return client
