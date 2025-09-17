"""Tests for the A2A utils module."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from a2a.client import ClientConfig, ClientFactory, A2ACardResolver
from a2a.server.agent_execution import RequestContext
from a2a.types import AgentCard

from aixtools.a2a.google_sdk.utils import (
    _AgentCardResolver,
    get_a2a_clients,
    get_session_id_tuple,
)
from aixtools.a2a.google_sdk.remote_agent_connection import RemoteAgentConnection
from aixtools.context import DEFAULT_USER_ID, DEFAULT_SESSION_ID


class TestAgentCardResolver(unittest.IsolatedAsyncioTestCase):
    """Tests for the _AgentCardResolver class."""

    def setUp(self):
        self.mock_client = AsyncMock(spec=httpx.AsyncClient)
        self.resolver = _AgentCardResolver(self.mock_client)

    @patch("aixtools.a2a.google_sdk.utils.ClientFactory")
    def test_init(self, mock_client_factory_class):
        """Test _AgentCardResolver initialization."""
        mock_factory = MagicMock(spec=ClientFactory)
        mock_client_factory_class.return_value = mock_factory
        
        resolver = _AgentCardResolver(self.mock_client)
        
        # Verify ClientFactory was created with correct config
        mock_client_factory_class.assert_called_once()
        call_args = mock_client_factory_class.call_args[0][0]
        self.assertIsInstance(call_args, ClientConfig)
        self.assertEqual(call_args.httpx_client, self.mock_client)
        
        # Verify attributes are set
        self.assertEqual(resolver._httpx_client, self.mock_client)
        self.assertEqual(resolver._a2a_client_factory, mock_factory)
        self.assertEqual(resolver.clients, {})

    @patch("aixtools.a2a.google_sdk.utils.RemoteAgentConnection")
    def test_register_agent_card(self, mock_connection_class):
        """Test registering an agent card."""
        mock_card = MagicMock(spec=AgentCard)
        mock_card.name = "test_agent"
        
        mock_client = MagicMock()
        mock_factory = MagicMock(spec=ClientFactory)
        mock_factory.create.return_value = mock_client
        self.resolver._a2a_client_factory = mock_factory
        
        mock_connection = MagicMock(spec=RemoteAgentConnection)
        mock_connection_class.return_value = mock_connection
        
        self.resolver.register_agent_card(mock_card)
        
        # Verify client was created
        mock_factory.create.assert_called_once_with(mock_card)
        
        # Verify RemoteAgentConnection was created
        mock_connection_class.assert_called_once_with(mock_card, mock_client)
        
        # Verify connection was stored
        self.assertEqual(self.resolver.clients["test_agent"], mock_connection)

    @patch("aixtools.a2a.google_sdk.utils.A2ACardResolver")
    async def test_retrieve_card(self, mock_resolver_class):
        """Test retrieving a card from an address."""
        mock_resolver = AsyncMock(spec=A2ACardResolver)
        mock_resolver_class.return_value = mock_resolver
        
        mock_card = MagicMock(spec=AgentCard)
        mock_card.name = "test_agent"
        mock_resolver.get_agent_card.return_value = mock_card
        
        with patch.object(self.resolver, 'register_agent_card') as mock_register:
            await self.resolver.retrieve_card("http://test.com")
            
            # Verify resolver was created correctly (it tries the first card path)
            mock_resolver_class.assert_called_with(self.mock_client, "http://test.com", "/.well-known/agent-card.json")
            
            # Verify card was retrieved
            mock_resolver.get_agent_card.assert_called_once()
            
            # Verify card was registered
            mock_register.assert_called_once_with(mock_card)

    async def test_get_a2a_clients(self):
        """Test getting A2A clients for multiple hosts."""
        agent_hosts = ["http://agent1.com", "http://agent2.com"]
        
        with patch.object(self.resolver, 'retrieve_card') as mock_retrieve:
            mock_retrieve.return_value = None  # Mock async function
            
            # Set up some mock clients
            mock_connection1 = MagicMock(spec=RemoteAgentConnection)
            mock_connection2 = MagicMock(spec=RemoteAgentConnection)
            self.resolver.clients = {
                "agent1": mock_connection1,
                "agent2": mock_connection2
            }
            
            result = await self.resolver.get_a2a_clients(agent_hosts)
            
            # Verify retrieve_card was called for each host
            self.assertEqual(mock_retrieve.call_count, 2)
            mock_retrieve.assert_any_call("http://agent1.com")
            mock_retrieve.assert_any_call("http://agent2.com")
            
            # Verify result contains the clients
            self.assertEqual(result, self.resolver.clients)


class TestGetA2AClients(unittest.IsolatedAsyncioTestCase):
    """Tests for the get_a2a_clients function."""

    @patch("aixtools.a2a.google_sdk.utils._AgentCardResolver")
    @patch("aixtools.a2a.google_sdk.utils.httpx.AsyncClient")
    async def test_get_a2a_clients(self, mock_client_class, mock_resolver_class):
        """Test the get_a2a_clients function."""
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        mock_resolver = AsyncMock(spec=_AgentCardResolver)
        mock_resolver_class.return_value = mock_resolver
        
        mock_clients = {"agent1": MagicMock(), "agent2": MagicMock()}
        mock_resolver.get_a2a_clients.return_value = mock_clients
        
        ctx = ("user123", "session456")
        agent_hosts = ["http://agent1.com", "http://agent2.com"]
        
        result = await get_a2a_clients(ctx, agent_hosts)
        
        # Verify httpx client was created with correct headers
        expected_headers = {
            "user-id": "user123",
            "session-id": "session456",
        }
        mock_client_class.assert_called_once_with(headers=expected_headers, timeout=60.0)
        
        # Verify resolver was created with the client
        mock_resolver_class.assert_called_once_with(mock_client)
        
        # Verify get_a2a_clients was called with the hosts
        mock_resolver.get_a2a_clients.assert_called_once_with(agent_hosts)
        
        # Verify result
        self.assertEqual(result, mock_clients)


class TestGetSessionIdTuple(unittest.TestCase):
    """Tests for the get_session_id_tuple function."""

    def test_get_session_id_tuple_with_headers(self):
        """Test getting session ID tuple when headers are present."""
        mock_context = MagicMock(spec=RequestContext)
        mock_context.call_context.state = {
            "headers": {
                "user-id": "test_user",
                "session-id": "test_session"
            }
        }
        
        result = get_session_id_tuple(mock_context)
        
        self.assertEqual(result, ("test_user", "test_session"))

    def test_get_session_id_tuple_with_partial_headers(self):
        """Test getting session ID tuple when only some headers are present."""
        mock_context = MagicMock(spec=RequestContext)
        mock_context.call_context.state = {
            "headers": {
                "user-id": "test_user"
                # session-id is missing
            }
        }
        
        result = get_session_id_tuple(mock_context)
        
        self.assertEqual(result, ("test_user", DEFAULT_SESSION_ID))

    def test_get_session_id_tuple_no_headers(self):
        """Test getting session ID tuple when no headers are present."""
        mock_context = MagicMock(spec=RequestContext)
        mock_context.call_context.state = {}
        
        result = get_session_id_tuple(mock_context)
        
        self.assertEqual(result, (DEFAULT_USER_ID, DEFAULT_SESSION_ID))

    def test_get_session_id_tuple_empty_headers(self):
        """Test getting session ID tuple when headers dict is empty."""
        mock_context = MagicMock(spec=RequestContext)
        mock_context.call_context.state = {"headers": {}}
        
        result = get_session_id_tuple(mock_context)
        
        self.assertEqual(result, (DEFAULT_USER_ID, DEFAULT_SESSION_ID))


if __name__ == '__main__':
    unittest.main()
