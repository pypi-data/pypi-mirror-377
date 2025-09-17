"""Tests for the A2A card module."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from a2a.client import A2ACardResolver
from a2a.types import AgentCard

from aixtools.a2a.google_sdk.card import get_agent_card


class TestCard(unittest.IsolatedAsyncioTestCase):
    """Tests for the A2A card module."""

    def setUp(self):
        self.test_agent_host = "http://localhost:9999"

    @patch("aixtools.a2a.google_sdk.card.A2ACardResolver")
    async def test_get_agent_card_success(self, mock_resolver_class):
        """Test successful retrieval of agent card."""
        # Setup
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        
        mock_resolver = AsyncMock(spec=A2ACardResolver)
        mock_resolver_class.return_value = mock_resolver
        
        mock_card = MagicMock(spec=AgentCard)
        mock_card.model_dump_json.return_value = '{"test": "data"}'
        mock_resolver.get_agent_card.return_value = mock_card
        
        # Call the function
        result = await get_agent_card(mock_client, self.test_agent_host)
        
        # Verify the result
        self.assertEqual(result, mock_card)
        
        # Verify the resolver was created correctly
        mock_resolver_class.assert_called_once_with(
            httpx_client=mock_client,
            base_url=self.test_agent_host
        )
        
        # Verify the card was fetched
        mock_resolver.get_agent_card.assert_called_once()
        
        # Verify the URL was set
        self.assertEqual(result.url, self.test_agent_host)

    @patch("aixtools.a2a.google_sdk.card.A2ACardResolver")
    async def test_get_agent_card_failure(self, mock_resolver_class):
        """Test handling of errors when retrieving agent card."""
        # Setup
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        
        mock_resolver = AsyncMock(spec=A2ACardResolver)
        mock_resolver_class.return_value = mock_resolver
        
        # Make the resolver raise an exception
        mock_resolver.get_agent_card.side_effect = Exception("Failed to fetch card")
        
        # Call the function and expect an exception
        with self.assertRaises(RuntimeError) as context:
            await get_agent_card(mock_client, self.test_agent_host)
        
        self.assertIn("Failed to fetch the public agent card", str(context.exception))

    @patch("aixtools.a2a.google_sdk.card.logger")
    @patch("aixtools.a2a.google_sdk.card.A2ACardResolver")
    async def test_get_agent_card_logging(self, mock_resolver_class, mock_logger):
        """Test that proper logging occurs during card retrieval."""
        # Setup
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        
        mock_resolver = AsyncMock(spec=A2ACardResolver)
        mock_resolver_class.return_value = mock_resolver
        
        mock_card = MagicMock(spec=AgentCard)
        mock_card.model_dump_json.return_value = '{"test": "data"}'
        mock_resolver.get_agent_card.return_value = mock_card
        
        # Call the function
        await get_agent_card(mock_client, self.test_agent_host)
        
        # Verify logging calls
        mock_logger.info.assert_called()
        self.assertEqual(mock_logger.info.call_count, 2)  # Two info calls in the function

    @patch("aixtools.a2a.google_sdk.card.logger")
    @patch("aixtools.a2a.google_sdk.card.A2ACardResolver")
    async def test_get_agent_card_error_logging(self, mock_resolver_class, mock_logger):
        """Test that errors are properly logged."""
        # Setup
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        
        mock_resolver = AsyncMock(spec=A2ACardResolver)
        mock_resolver_class.return_value = mock_resolver
        
        test_error = Exception("Test error")
        mock_resolver.get_agent_card.side_effect = test_error
        
        # Call the function and expect an exception
        with self.assertRaises(RuntimeError):
            await get_agent_card(mock_client, self.test_agent_host)
        
        # Verify error logging
        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        self.assertIn("Critical error fetching public agent card", args[0])
        self.assertTrue(kwargs.get('exc_info'))


if __name__ == '__main__':
    unittest.main()
