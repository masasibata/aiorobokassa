"""Base API client with common functionality."""

import asyncio
import logging
from typing import Optional

import aiohttp

from aiorobokassa.constants import DEFAULT_TIMEOUT
from aiorobokassa.exceptions import APIError

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """Base class for API clients with HTTP session management."""

    def __init__(
        self,
        base_url: str,
        test_mode: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ):
        """
        Initialize base API client.

        Args:
            base_url: Base URL for API requests
            test_mode: Enable test mode
            session: Optional aiohttp session (will be created if not provided)
            timeout: Optional timeout for requests
        """
        self._base_url = base_url
        self.test_mode = test_mode
        self._session = session
        self._own_session = session is None
        self._timeout = timeout or aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout,
                connector=aiohttp.TCPConnector(limit=100),  # Connection pooling
            )
            logger.debug("Created new aiohttp session")
        return self._session

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close session if we own it."""
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()

    async def close(self):
        """Close the client session."""
        if self._own_session and self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        url: str,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        """
        Make HTTP request with error handling.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional arguments for aiohttp request

        Returns:
            Response object (caller is responsible for closing)

        Raises:
            APIError: If request fails
        """
        logger.debug(f"Making {method} request to {url}")
        try:
            response = await self.session.request(method, url, **kwargs)
            logger.debug(f"Response status: {response.status}")
            if response.status >= 400:
                async with response:
                    text = await response.text()
                    logger.error(f"API request failed with status {response.status}: {text}")
                    raise APIError(
                        f"API request failed with status {response.status}",
                        status_code=response.status,
                        response=text,
                    )
            return response
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}", exc_info=True)
            raise APIError(f"Network error: {str(e)}") from e
        except asyncio.TimeoutError as e:
            logger.error(f"Request timeout: {e}", exc_info=True)
            raise APIError(f"Request timeout: {str(e)}") from e

    async def _get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request."""
        return await self._request("GET", url, **kwargs)

    async def _post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make POST request."""
        return await self._request("POST", url, **kwargs)
