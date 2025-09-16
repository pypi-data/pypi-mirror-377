"""Transport layer for HTTP operations."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional, Protocol

import httpx

logger = logging.getLogger(__name__)


class Transport(Protocol):
    """Protocol for HTTP transport operations."""

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a GET request.

        Args:
            path: API endpoint path
            params: Optional query parameters

        Returns:
            JSON response data
        """
        ...

    def post(self, path: str, json: Dict[str, Any]) -> Any:
        """
        Execute a POST request.

        Args:
            path: API endpoint path
            json: JSON request body

        Returns:
            JSON response data
        """
        ...

    async def post_async(self, path: str, json: Dict[str, Any]) -> Any:
        """
        Execute an async POST request.

        Args:
            path: API endpoint path
            json: JSON request body

        Returns:
            JSON response data
        """
        ...

    def close(self) -> None:
        """Close the transport and clean up resources."""
        ...


class HttpxTransport:
    """HTTP transport implementation using httpx."""

    def __init__(
        self,
        base_url: str,
        org_slug: str,
        api_key: str,
        timeout: float = 30.0,
    ):
        """
        Initialize the HTTP transport.

        Args:
            base_url: Base API URL
            org_slug: Organization slug
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.org_slug = org_slug
        self.api_key = api_key
        self.timeout = timeout

        # Create HTTP client with organization-specific URL
        self._full_base_url = f"{base_url.rstrip('/')}/{org_slug}"
        self._client = httpx.Client(timeout=timeout)
        self._async_client = None  # Create lazily when needed

        logger.debug("Initialized HttpxTransport for org: %s", org_slug)

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a GET request."""
        url = f"{self._full_base_url}{path}"
        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json",
        }

        # Clean params - remove None values
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        logger.debug("GET %s with params: %s", url, params)

        response = self._client.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise HTTPStatusError for bad status codes

        return response.json()

    def post(self, path: str, json: Dict[str, Any]) -> Any:
        """Execute a POST request."""
        url = f"{self._full_base_url}{path}"
        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json",
        }

        logger.debug("POST %s with json: %s", url, json)

        response = self._client.post(url, json=json, headers=headers)
        response.raise_for_status()  # Raise HTTPStatusError for bad status codes

        return response.json()

    async def post_async(self, path: str, json: Dict[str, Any]) -> Any:
        """Execute an async POST request."""
        # Create async client lazily
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=self.timeout)

        url = f"{self._full_base_url}{path}"
        headers = {
            "apiKey": self.api_key,
            "Content-Type": "application/json",
        }

        logger.debug("ASYNC POST %s with json: %s", url, json)

        response = await self._async_client.post(url, json=json, headers=headers)
        response.raise_for_status()  # Raise HTTPStatusError for bad status codes

        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client:
            self._client.close()
        # Only close async client if it was created
        if self._async_client is not None:
            try:
                # Try to close async client in current event loop
                asyncio.get_running_loop()
                asyncio.create_task(self._async_client.aclose())
            except RuntimeError:
                # No event loop running, close synchronously
                asyncio.run(self._async_client.aclose())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
