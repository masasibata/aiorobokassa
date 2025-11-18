"""Tests for BaseAPIClient."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp

from aiorobokassa.api.base import BaseAPIClient
from aiorobokassa.exceptions import APIError


class TestBaseAPIClient:
    """Tests for BaseAPIClient."""

    def test_init_with_base_url(self):
        """Test initialization with base URL."""
        client = BaseAPIClient(base_url="https://example.com", test_mode=False)
        assert client.base_url == "https://example.com"
        assert client.test_mode is False

    def test_init_with_test_mode(self):
        """Test initialization with test mode."""
        client = BaseAPIClient(base_url="https://example.com", test_mode=True)
        assert client.test_mode is True

    def test_init_with_session(self):
        """Test initialization with provided session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        client = BaseAPIClient(base_url="https://example.com", session=session)
        assert client._session is session
        assert client._own_session is False

    def test_init_without_session(self):
        """Test initialization without session."""
        client = BaseAPIClient(base_url="https://example.com")
        assert client._session is None
        assert client._own_session is True

    @pytest.mark.asyncio
    async def test_session_property_creates_session(self):
        """Test that session property creates session if needed."""
        client = BaseAPIClient(base_url="https://example.com")
        session = client.session
        assert isinstance(session, aiohttp.ClientSession)
        assert not session.closed
        await client.close()

    @pytest.mark.asyncio
    async def test_session_property_reuses_session(self):
        """Test that session property reuses existing session."""
        client = BaseAPIClient(base_url="https://example.com")
        session1 = client.session
        session2 = client.session
        assert session1 is session2
        await client.close()

    @pytest.mark.asyncio
    async def test_session_property_recreates_if_closed(self):
        """Test that session property recreates session if closed."""
        client = BaseAPIClient(base_url="https://example.com")
        session1 = client.session
        await session1.close()
        session2 = client.session
        assert session1 is not session2
        assert not session2.closed
        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with BaseAPIClient(base_url="https://example.com") as client:
            assert isinstance(client, BaseAPIClient)
            assert client._own_session is True

    @pytest.mark.asyncio
    async def test_context_manager_closes_session(self):
        """Test that context manager closes session."""
        async with BaseAPIClient(base_url="https://example.com") as client:
            session = client.session
            assert not session.closed
        assert session.closed

    @pytest.mark.asyncio
    async def test_context_manager_with_provided_session(self):
        """Test context manager with provided session doesn't close it."""
        session = MagicMock(spec=aiohttp.ClientSession)
        session.closed = False
        async with BaseAPIClient(base_url="https://example.com", session=session):
            pass
        session.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method."""
        client = BaseAPIClient(base_url="https://example.com")
        session = client.session
        await client.close()
        assert session.closed

    @pytest.mark.asyncio
    async def test_close_with_provided_session(self):
        """Test close doesn't close provided session."""
        session = MagicMock(spec=aiohttp.ClientSession)
        session.closed = False
        client = BaseAPIClient(base_url="https://example.com", session=session)
        await client.close()
        session.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_success(self):
        """Test successful request."""
        client = BaseAPIClient(base_url="https://example.com")
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="OK")
        mock_response.closed = False

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request = AsyncMock(return_value=mock_response)
        mock_session.closed = False
        client._session = mock_session

        # Override session property to return our mock
        original_session = client.session
        response = await client._request("GET", "https://example.com/test")
        assert response.status == 200
        # Clean up if we created a real session
        if original_session != mock_session and not original_session.closed:
            await original_session.close()

    @pytest.mark.asyncio
    async def test_request_http_error(self):
        """Test request with HTTP error."""
        client = BaseAPIClient(base_url="https://example.com")
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")
        mock_response.close = MagicMock()  # close() is not async in aiohttp

        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.request = AsyncMock(return_value=mock_response)
        client._session = mock_session

        with pytest.raises(APIError) as exc_info:
            await client._request("GET", "https://example.com/test")
        assert exc_info.value.status_code == 404
        assert "404" in str(exc_info.value)
        await client.close()

    @pytest.mark.asyncio
    async def test_request_network_error(self):
        """Test request with network error."""
        client = BaseAPIClient(base_url="https://example.com")

        with patch.object(
            client.session, "request", side_effect=aiohttp.ClientError("Network error")
        ):
            with pytest.raises(APIError) as exc_info:
                await client._request("GET", "https://example.com/test")
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_request_timeout(self):
        """Test request timeout."""
        client = BaseAPIClient(base_url="https://example.com")

        with patch.object(client.session, "request", side_effect=TimeoutError("Timeout")):
            with pytest.raises(APIError) as exc_info:
                await client._request("GET", "https://example.com/test")
            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get(self):
        """Test GET request."""
        client = BaseAPIClient(base_url="https://example.com")
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200

        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            response = await client._get("https://example.com/test")
            mock_request.assert_called_once_with("GET", "https://example.com/test")
            assert response == mock_response

    @pytest.mark.asyncio
    async def test_post(self):
        """Test POST request."""
        client = BaseAPIClient(base_url="https://example.com")
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200

        with patch.object(client, "_request", return_value=mock_response) as mock_request:
            response = await client._post("https://example.com/test", data="test")
            mock_request.assert_called_once_with("POST", "https://example.com/test", data="test")
            assert response == mock_response
