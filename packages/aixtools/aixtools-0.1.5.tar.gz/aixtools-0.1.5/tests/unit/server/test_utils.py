"""Unit tests for aixtools.server.utils module."""

import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

from aixtools.server.utils import (
    get_session_id_from_request,
    get_session_id_str,
    get_session_id_tuple,
    get_user_id_from_request,
    run_in_thread,
)


class TestGetSessionIdFromRequest(unittest.TestCase):
    """Test cases for get_session_id_from_request function."""

    @patch('aixtools.server.utils.dependencies')
    def test_get_session_id_with_context_none(self, mock_dependencies):
        """Test getting session ID when context is None."""
        mock_request = Mock()
        mock_request.headers.get.return_value = "test-session-123"
        mock_dependencies.get_http_request.return_value = mock_request
        
        result = get_session_id_from_request(None)
        
        self.assertEqual(result, "test-session-123")
        mock_dependencies.get_http_request.assert_called_once()
        mock_request.headers.get.assert_called_once_with("session-id")

    def test_get_session_id_with_context_provided(self):
        """Test getting session ID when context is provided."""
        mock_ctx = Mock()
        mock_request = Mock()
        mock_request.headers.get.return_value = "ctx-session-456"
        mock_ctx.get_http_request.return_value = mock_request
        
        result = get_session_id_from_request(mock_ctx)
        
        self.assertEqual(result, "ctx-session-456")
        mock_ctx.get_http_request.assert_called_once()
        mock_request.headers.get.assert_called_once_with("session-id")

    @patch('aixtools.server.utils.dependencies')
    def test_get_session_id_header_not_found(self, mock_dependencies):
        """Test getting session ID when header is not found."""
        mock_request = Mock()
        mock_request.headers.get.return_value = None
        mock_dependencies.get_http_request.return_value = mock_request
        
        result = get_session_id_from_request(None)
        
        self.assertIsNone(result)

    @patch('aixtools.server.utils.dependencies')
    def test_get_session_id_value_error(self, mock_dependencies):
        """Test getting session ID when ValueError is raised."""
        mock_dependencies.get_http_request.side_effect = ValueError("Request error")
        
        result = get_session_id_from_request(None)
        
        self.assertIsNone(result)

    @patch('aixtools.server.utils.dependencies')
    def test_get_session_id_runtime_error(self, mock_dependencies):
        """Test getting session ID when RuntimeError is raised."""
        mock_dependencies.get_http_request.side_effect = RuntimeError("Runtime error")
        
        result = get_session_id_from_request(None)
        
        self.assertIsNone(result)


class TestGetUserIdFromRequest(unittest.TestCase):
    """Test cases for get_user_id_from_request function."""

    @patch('aixtools.server.utils.dependencies')
    def test_get_user_id_with_context_none(self, mock_dependencies):
        """Test getting user ID when context is None."""
        mock_request = Mock()
        mock_request.headers.get.return_value = "TEST-USER-123"
        mock_dependencies.get_http_request.return_value = mock_request
        
        result = get_user_id_from_request(None)
        
        self.assertEqual(result, "test-user-123")  # Should be lowercase
        mock_dependencies.get_http_request.assert_called_once()
        mock_request.headers.get.assert_called_once_with("user-id")

    def test_get_user_id_with_context_provided(self):
        """Test getting user ID when context is provided."""
        mock_ctx = Mock()
        mock_request = Mock()
        mock_request.headers.get.return_value = "CTX-USER-456"
        mock_ctx.get_http_request.return_value = mock_request
        
        result = get_user_id_from_request(mock_ctx)
        
        self.assertEqual(result, "ctx-user-456")  # Should be lowercase
        mock_ctx.get_http_request.assert_called_once()
        mock_request.headers.get.assert_called_once_with("user-id")

    @patch('aixtools.server.utils.dependencies')
    def test_get_user_id_header_not_found(self, mock_dependencies):
        """Test getting user ID when header is not found."""
        mock_request = Mock()
        mock_request.headers.get.return_value = None
        mock_dependencies.get_http_request.return_value = mock_request
        
        result = get_user_id_from_request(None)
        
        self.assertIsNone(result)

    @patch('aixtools.server.utils.dependencies')
    def test_get_user_id_empty_string(self, mock_dependencies):
        """Test getting user ID when header is empty string."""
        mock_request = Mock()
        mock_request.headers.get.return_value = ""
        mock_dependencies.get_http_request.return_value = mock_request
        
        result = get_user_id_from_request(None)
        
        self.assertIsNone(result)

    @patch('aixtools.server.utils.dependencies')
    def test_get_user_id_value_error(self, mock_dependencies):
        """Test getting user ID when ValueError is raised."""
        mock_dependencies.get_http_request.side_effect = ValueError("Request error")
        
        result = get_user_id_from_request(None)
        
        self.assertIsNone(result)

    @patch('aixtools.server.utils.dependencies')
    def test_get_user_id_runtime_error(self, mock_dependencies):
        """Test getting user ID when RuntimeError is raised."""
        mock_dependencies.get_http_request.side_effect = RuntimeError("Runtime error")
        
        result = get_user_id_from_request(None)
        
        self.assertIsNone(result)

    @patch('aixtools.server.utils.dependencies')
    def test_get_user_id_attribute_error(self, mock_dependencies):
        """Test getting user ID when AttributeError is raised."""
        mock_dependencies.get_http_request.side_effect = AttributeError("Attribute error")
        
        result = get_user_id_from_request(None)
        
        self.assertIsNone(result)

    @patch('aixtools.server.utils.dependencies')
    def test_get_user_id_case_variations(self, mock_dependencies):
        """Test that user ID is always returned in lowercase."""
        test_cases = [
            ("UPPERCASE", "uppercase"),
            ("MixedCase", "mixedcase"),
            ("lowercase", "lowercase"),
            ("CamelCase", "camelcase"),
        ]
        
        for input_user_id, expected_output in test_cases:
            with self.subTest(input_user_id=input_user_id):
                mock_request = Mock()
                mock_request.headers.get.return_value = input_user_id
                mock_dependencies.get_http_request.return_value = mock_request
                
                result = get_user_id_from_request(None)
                
                self.assertEqual(result, expected_output)


class TestGetSessionIdTuple(unittest.TestCase):
    """Test cases for get_session_id_tuple function."""

    @patch('aixtools.server.utils.get_session_id_from_request')
    @patch('aixtools.server.utils.get_user_id_from_request')
    @patch('aixtools.server.utils.session_id_var')
    @patch('aixtools.server.utils.user_id_var')
    def test_get_session_id_tuple_with_headers(self, mock_user_var, mock_session_var, 
                                               mock_get_user, mock_get_session):
        """Test getting session ID tuple when headers are available."""
        mock_get_user.return_value = "header-user"
        mock_get_session.return_value = "header-session"
        
        result = get_session_id_tuple(None)
        
        self.assertEqual(result, ("header-user", "header-session"))
        mock_get_user.assert_called_once_with(None)
        mock_get_session.assert_called_once_with(None)

    @patch('aixtools.server.utils.get_session_id_from_request')
    @patch('aixtools.server.utils.get_user_id_from_request')
    @patch('aixtools.server.utils.session_id_var')
    @patch('aixtools.server.utils.user_id_var')
    def test_get_session_id_tuple_with_fallback(self, mock_user_var, mock_session_var,
                                                mock_get_user, mock_get_session):
        """Test getting session ID tuple with fallback to context variables."""
        mock_get_user.return_value = None
        mock_get_session.return_value = None
        mock_user_var.get.return_value = "context-user"
        mock_session_var.get.return_value = "context-session"
        
        result = get_session_id_tuple(None)
        
        self.assertEqual(result, ("context-user", "context-session"))
        mock_user_var.get.assert_called_once_with("default_user")
        mock_session_var.get.assert_called_once_with("default_session")

    @patch('aixtools.server.utils.get_session_id_from_request')
    @patch('aixtools.server.utils.get_user_id_from_request')
    @patch('aixtools.server.utils.session_id_var')
    @patch('aixtools.server.utils.user_id_var')
    def test_get_session_id_tuple_mixed_sources(self, mock_user_var, mock_session_var,
                                                mock_get_user, mock_get_session):
        """Test getting session ID tuple with mixed sources."""
        mock_get_user.return_value = "header-user"
        mock_get_session.return_value = None
        mock_session_var.get.return_value = "context-session"
        
        result = get_session_id_tuple(None)
        
        self.assertEqual(result, ("header-user", "context-session"))

    def test_get_session_id_tuple_with_context(self):
        """Test getting session ID tuple with provided context."""
        mock_ctx = Mock()
        
        with patch('aixtools.server.utils.get_user_id_from_request') as mock_get_user, \
             patch('aixtools.server.utils.get_session_id_from_request') as mock_get_session:
            
            mock_get_user.return_value = "ctx-user"
            mock_get_session.return_value = "ctx-session"
            
            result = get_session_id_tuple(mock_ctx)
            
            self.assertEqual(result, ("ctx-user", "ctx-session"))
            mock_get_user.assert_called_once_with(mock_ctx)
            mock_get_session.assert_called_once_with(mock_ctx)


class TestGetSessionIdStr(unittest.TestCase):
    """Test cases for get_session_id_str function."""

    @patch('aixtools.server.utils.get_session_id_tuple')
    def test_get_session_id_str(self, mock_get_tuple):
        """Test getting session ID string."""
        mock_get_tuple.return_value = ("test-user", "test-session")
        
        result = get_session_id_str(None)
        
        self.assertEqual(result, "test-user:test-session")
        mock_get_tuple.assert_called_once_with(None)

    @patch('aixtools.server.utils.get_session_id_tuple')
    def test_get_session_id_str_with_context(self, mock_get_tuple):
        """Test getting session ID string with context."""
        mock_ctx = Mock()
        mock_get_tuple.return_value = ("ctx-user", "ctx-session")
        
        result = get_session_id_str(mock_ctx)
        
        self.assertEqual(result, "ctx-user:ctx-session")
        mock_get_tuple.assert_called_once_with(mock_ctx)

    @patch('aixtools.server.utils.get_session_id_tuple')
    def test_get_session_id_str_special_characters(self, mock_get_tuple):
        """Test getting session ID string with special characters."""
        mock_get_tuple.return_value = ("user@domain.com", "session-123-abc")
        
        result = get_session_id_str(None)
        
        self.assertEqual(result, "user@domain.com:session-123-abc")


class TestRunInThread(unittest.IsolatedAsyncioTestCase):
    """Test cases for run_in_thread decorator."""

    async def test_run_in_thread_basic_function(self):
        """Test run_in_thread decorator with basic function."""
        @run_in_thread
        def sync_function(x, y):
            return x + y
        
        result = await sync_function(5, 3)  # type: ignore
        
        self.assertEqual(result, 8)

    async def test_run_in_thread_with_kwargs(self):
        """Test run_in_thread decorator with keyword arguments."""
        @run_in_thread
        def sync_function(x, y, multiplier=1):
            return (x + y) * multiplier
        
        result = await sync_function(5, 3, multiplier=2)  # type: ignore
        
        self.assertEqual(result, 16)

    async def test_run_in_thread_with_exception(self):
        """Test run_in_thread decorator when function raises exception."""
        @run_in_thread
        def failing_function():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError) as context:
            await failing_function()  # type: ignore
        
        self.assertEqual(str(context.exception), "Test error")

    async def test_run_in_thread_preserves_function_metadata(self):
        """Test that run_in_thread preserves function metadata."""
        @run_in_thread
        def documented_function(x):
            """This is a test function."""
            return x * 2
        
        self.assertEqual(documented_function.__name__, "documented_function")
        self.assertEqual(documented_function.__doc__, "This is a test function.")

    async def test_run_in_thread_with_no_args(self):
        """Test run_in_thread decorator with function that takes no arguments."""
        @run_in_thread
        def no_args_function():
            return "success"
        
        result = await no_args_function()  # type: ignore
        
        self.assertEqual(result, "success")

    async def test_run_in_thread_with_complex_return_type(self):
        """Test run_in_thread decorator with complex return type."""
        @run_in_thread
        def complex_function():
            return {"key": "value", "list": [1, 2, 3], "nested": {"inner": True}}
        
        result = await complex_function()  # type: ignore
        
        expected = {"key": "value", "list": [1, 2, 3], "nested": {"inner": True}}
        self.assertEqual(result, expected)

    @patch('asyncio.to_thread')
    async def test_run_in_thread_calls_asyncio_to_thread(self, mock_to_thread):
        """Test that run_in_thread actually calls asyncio.to_thread."""
        mock_to_thread.return_value = "mocked_result"
        
        @run_in_thread
        def test_function(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"
        
        result = await test_function("a", "b", kwarg1="c")  # type: ignore
        
        self.assertEqual(result, "mocked_result")
        mock_to_thread.assert_called_once()
        # Verify the original function and arguments were passed
        args, kwargs = mock_to_thread.call_args
        self.assertEqual(args[1:], ("a", "b"))  # Skip the function itself
        self.assertEqual(kwargs, {"kwarg1": "c"})


if __name__ == '__main__':
    unittest.main()