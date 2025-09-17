"""Unit tests for aixtools.mcp.client module."""

import asyncio
import unittest
from unittest.mock import Mock, patch

from mcp import types as mcp_types
from pydantic_ai import exceptions

from aixtools.mcp.client import (
    CACHE_KEY,
    DEFAULT_MCP_CONNECTION_TIMEOUT,
    CachedMCPServerStreamableHTTP,
    get_configured_mcp_servers,
    get_mcp_headers,
)


class TestGetMcpHeaders(unittest.TestCase):
    """Test cases for get_mcp_headers function."""

    def test_get_mcp_headers_with_both_ids(self):
        """Test get_mcp_headers with both user_id and session_id."""
        session_id_tuple = ("user123", "session456")
        result = get_mcp_headers(session_id_tuple)
        
        expected = {
            "user-id": "user123",
            "session-id": "session456"
        }
        self.assertEqual(result, expected)

    def test_get_mcp_headers_with_user_id_only(self):
        """Test get_mcp_headers with only user_id."""
        session_id_tuple = ("user123", None)  # type: ignore
        result = get_mcp_headers(session_id_tuple)
        
        expected = {
            "user-id": "user123"
        }
        self.assertEqual(result, expected)

    def test_get_mcp_headers_with_session_id_only(self):
        """Test get_mcp_headers with only session_id."""
        session_id_tuple = (None, "session456")  # type: ignore
        result = get_mcp_headers(session_id_tuple)
        
        expected = {
            "session-id": "session456"
        }
        self.assertEqual(result, expected)

    def test_get_mcp_headers_with_empty_strings(self):
        """Test get_mcp_headers with empty strings."""
        session_id_tuple = ("", "")
        result = get_mcp_headers(session_id_tuple)
        
        self.assertIsNone(result)

    def test_get_mcp_headers_with_none_values(self):
        """Test get_mcp_headers with None values."""
        session_id_tuple = (None, None)  # type: ignore
        result = get_mcp_headers(session_id_tuple)
        
        self.assertIsNone(result)

    def test_get_mcp_headers_with_mixed_empty_and_none(self):
        """Test get_mcp_headers with mixed empty and None values."""
        session_id_tuple = ("", None)  # type: ignore
        result = get_mcp_headers(session_id_tuple)
        
        self.assertIsNone(result)


class TestGetConfiguredMcpServers(unittest.TestCase):
    """Test cases for get_configured_mcp_servers function."""

    @patch('aixtools.mcp.client.CachedMCPServerStreamableHTTP')
    def test_get_configured_mcp_servers_basic(self, mock_cached_server):
        """Test get_configured_mcp_servers with basic parameters."""
        session_id_tuple = ("user123", "session456")
        mcp_urls = ["http://server1.com", "http://server2.com"]
        
        mock_server_instances = [Mock(), Mock()]
        mock_cached_server.side_effect = mock_server_instances
        
        result = get_configured_mcp_servers(session_id_tuple, mcp_urls)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result, mock_server_instances)
        
        # Verify that CachedMCPServerStreamableHTTP was called correctly
        expected_headers = {"user-id": "user123", "session-id": "session456"}
        mock_cached_server.assert_any_call(
            url="http://server1.com", 
            headers=expected_headers, 
            timeout=DEFAULT_MCP_CONNECTION_TIMEOUT
        )
        mock_cached_server.assert_any_call(
            url="http://server2.com", 
            headers=expected_headers, 
            timeout=DEFAULT_MCP_CONNECTION_TIMEOUT
        )

    @patch('aixtools.mcp.client.CachedMCPServerStreamableHTTP')
    def test_get_configured_mcp_servers_custom_timeout(self, mock_cached_server):
        """Test get_configured_mcp_servers with custom timeout."""
        session_id_tuple = ("user123", "session456")
        mcp_urls = ["http://server1.com"]
        custom_timeout = 60
        
        mock_server_instance = Mock()
        mock_cached_server.return_value = mock_server_instance
        
        result = get_configured_mcp_servers(session_id_tuple, mcp_urls, custom_timeout)
        
        self.assertEqual(len(result), 1)
        mock_cached_server.assert_called_once_with(
            url="http://server1.com",
            headers={"user-id": "user123", "session-id": "session456"},
            timeout=custom_timeout
        )

    @patch('aixtools.mcp.client.CachedMCPServerStreamableHTTP')
    def test_get_configured_mcp_servers_no_headers(self, mock_cached_server):
        """Test get_configured_mcp_servers when no headers are generated."""
        session_id_tuple = (None, None)  # type: ignore
        mcp_urls = ["http://server1.com"]
        
        mock_server_instance = Mock()
        mock_cached_server.return_value = mock_server_instance
        
        result = get_configured_mcp_servers(session_id_tuple, mcp_urls)
        
        self.assertEqual(len(result), 1)
        mock_cached_server.assert_called_once_with(
            url="http://server1.com",
            headers=None,
            timeout=DEFAULT_MCP_CONNECTION_TIMEOUT
        )

    @patch('aixtools.mcp.client.CachedMCPServerStreamableHTTP')
    def test_get_configured_mcp_servers_empty_urls(self, mock_cached_server):
        """Test get_configured_mcp_servers with empty URL list."""
        session_id_tuple = ("user123", "session456")
        mcp_urls = []
        
        result = get_configured_mcp_servers(session_id_tuple, mcp_urls)
        
        self.assertEqual(len(result), 0)
        mock_cached_server.assert_not_called()


class TestCachedMCPServerStreamableHTTP(unittest.IsolatedAsyncioTestCase):
    """Test cases for CachedMCPServerStreamableHTTP class."""

    def setUp(self):
        """Set up test fixtures."""
        self.server = CachedMCPServerStreamableHTTP(url="http://test.com")
        self.server._client = Mock()

    def test_init(self):
        """Test CachedMCPServerStreamableHTTP initialization."""
        server = CachedMCPServerStreamableHTTP(url="http://test.com")
        
        self.assertIsNotNone(server._tools_cache)
        self.assertIsNone(server._tools_list)
        self.assertIsNotNone(server._isolation_lock)

    async def test_run_direct_or_isolated_success(self):
        """Test _run_direct_or_isolated with successful execution."""
        async def test_func():
            return "success"
        
        def fallback(exc):
            return "fallback"
        
        result = await self.server._run_direct_or_isolated(test_func, fallback, None)
        self.assertEqual(result, "success")

    async def test_run_direct_or_isolated_timeout(self):
        """Test _run_direct_or_isolated with timeout."""
        async def test_func():
            await asyncio.sleep(2)
            return "success"
        
        def fallback(exc):
            return "fallback"
        
        result = await self.server._run_direct_or_isolated(test_func, fallback, 0.1)
        self.assertEqual(result, "fallback")

    async def test_run_direct_or_isolated_exception(self):
        """Test _run_direct_or_isolated with exception."""
        async def test_func():
            raise ValueError("test error")
        
        def fallback(exc):
            return f"fallback: {exc}"
        
        result = await self.server._run_direct_or_isolated(test_func, fallback, None)
        self.assertEqual(result, "fallback: test error")

    async def test_run_direct_or_isolated_model_retry(self):
        """Test _run_direct_or_isolated with ModelRetry exception."""
        async def test_func():
            raise exceptions.ModelRetry("retry error")
        
        def fallback(exc):
            return "fallback"
        
        with self.assertRaises(exceptions.ModelRetry):
            await self.server._run_direct_or_isolated(test_func, fallback, None)

    async def test_list_tools_uninitialized_client(self):
        """Test list_tools with uninitialized client."""
        self.server._client = None  # type: ignore
        
        result = await self.server.list_tools()
        
        self.assertEqual(result, [])

    async def test_list_tools_cached(self):
        """Test list_tools with cached result."""
        cached_tools = [Mock(spec=mcp_types.Tool)]
        self.server._tools_cache[CACHE_KEY] = cached_tools
        
        result = await self.server.list_tools()
        
        self.assertEqual(result, cached_tools)

    async def test_call_tool_uninitialized_client(self):
        """Test call_tool with uninitialized client."""
        self.server._client = None  # type: ignore
        
        result = await self.server.call_tool("test_tool", {}, Mock(), Mock())
        
        self.assertIn("MCP connection is uninitialized", str(result))


if __name__ == '__main__':
    unittest.main()
