"""Unit tests for aixtools.server.path module."""

import unittest
from pathlib import Path, PurePath, PurePosixPath
from unittest.mock import Mock, patch

from aixtools.server.path import (
    CONTAINER_WORKSPACE_PATH,
    WORKSPACES_ROOT_DIR,
    container_to_host_path,
    get_workspace_path,
    host_to_container_path,
)


class TestGetWorkspacePath(unittest.TestCase):
    """Test cases for get_workspace_path function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ctx = ("test_user", "test_session")

    def test_sandbox_path_without_service_name(self):
        """Test getting sandbox path without service name."""
        result = get_workspace_path(in_sandbox=True)
        
        self.assertEqual(result, CONTAINER_WORKSPACE_PATH)
        self.assertIsInstance(result, PurePath)

    def test_sandbox_path_with_service_name(self):
        """Test getting sandbox path with service name."""
        result = get_workspace_path("mcp_server", in_sandbox=True)
        
        expected = CONTAINER_WORKSPACE_PATH / "mcp_server"
        self.assertEqual(result, expected)

    @patch('aixtools.server.path.get_session_id_tuple')
    def test_host_path_without_service_name(self, mock_get_session):
        """Test getting host path without service name."""
        mock_get_session.return_value = ("test_user", "test_session")
        
        result = get_workspace_path(in_sandbox=False)
        
        expected = WORKSPACES_ROOT_DIR / "test_user" / "test_session"
        self.assertEqual(result, expected)

    @patch('aixtools.server.path.get_session_id_tuple')
    def test_host_path_with_service_name(self, mock_get_session):
        """Test getting host path with service name."""
        mock_get_session.return_value = ("test_user", "test_session")
        
        result = get_workspace_path("mcp_server", in_sandbox=False)
        
        expected = WORKSPACES_ROOT_DIR / "test_user" / "test_session" / "mcp_server"
        self.assertEqual(result, expected)

    def test_host_path_with_tuple_context(self):
        """Test getting host path with tuple context."""
        result = get_workspace_path("service", in_sandbox=False, ctx=self.mock_ctx)
        
        expected = WORKSPACES_ROOT_DIR / "test_user" / "test_session" / "service"
        self.assertEqual(result, expected)

    @patch('aixtools.server.path.get_session_id_tuple')
    def test_host_path_with_context_object(self, mock_get_session):
        """Test getting host path with context object."""
        mock_ctx = Mock()
        mock_get_session.return_value = ("ctx_user", "ctx_session")
        
        result = get_workspace_path("service", in_sandbox=False, ctx=mock_ctx)
        
        expected = WORKSPACES_ROOT_DIR / "ctx_user" / "ctx_session" / "service"
        self.assertEqual(result, expected)
        mock_get_session.assert_called_once_with(mock_ctx)

    def test_default_parameters(self):
        """Test function with default parameters."""
        with patch('aixtools.server.path.get_session_id_tuple') as mock_get_session:
            mock_get_session.return_value = ("default_user", "default_session")
            
            result = get_workspace_path()
            
            expected = WORKSPACES_ROOT_DIR / "default_user" / "default_session"
            self.assertEqual(result, expected)


class TestContainerToHostPath(unittest.TestCase):
    """Test cases for container_to_host_path function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ctx = ("test_user", "test_session")

    @patch('aixtools.server.path.get_workspace_path')
    def test_valid_container_path_conversion(self, mock_get_workspace):
        """Test valid container path conversion."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        container_path = PurePosixPath("/workspace/file.txt")
        result = container_to_host_path(container_path, ctx=self.mock_ctx)
        
        expected = Path("/data/workspaces/user/session/file.txt")
        self.assertEqual(result, expected)

    @patch('aixtools.server.path.get_workspace_path')
    def test_container_root_path_conversion(self, mock_get_workspace):
        """Test container root path conversion."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        container_path = PurePosixPath("/workspace")
        result = container_to_host_path(container_path, ctx=self.mock_ctx)
        
        expected = Path("/data/workspaces/user/session")
        self.assertEqual(result, expected)

    @patch('aixtools.server.path.get_workspace_path')
    def test_nested_container_path_conversion(self, mock_get_workspace):
        """Test nested container path conversion."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        container_path = PurePosixPath("/workspace/subdir/nested/file.txt")
        result = container_to_host_path(container_path, ctx=self.mock_ctx)
        
        expected = Path("/data/workspaces/user/session/subdir/nested/file.txt")
        self.assertEqual(result, expected)

    def test_invalid_container_path_raises_error(self):
        """Test that invalid container paths raise ValueError."""
        invalid_paths = [
            PurePosixPath("/tmp/file.txt"),
            PurePosixPath("/home/user/file.txt"),
            PurePosixPath("/workspace_other/file.txt"),
        ]
        
        for invalid_path in invalid_paths:
            with self.subTest(path=invalid_path):
                with self.assertRaises(ValueError) as context:
                    container_to_host_path(invalid_path, ctx=self.mock_ctx)
                
                self.assertIn("Container path must be a subdir", str(context.exception))
                self.assertIn(str(invalid_path), str(context.exception))

    @patch('aixtools.server.path.get_workspace_path')
    def test_context_passed_to_get_workspace_path(self, mock_get_workspace):
        """Test that context is properly passed to get_workspace_path."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        container_path = PurePosixPath("/workspace/file.txt")
        container_to_host_path(container_path, ctx=self.mock_ctx)
        
        mock_get_workspace.assert_called_once_with(ctx=self.mock_ctx)


class TestHostToContainerPath(unittest.TestCase):
    """Test cases for host_to_container_path function."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_ctx = ("test_user", "test_session")

    @patch('aixtools.server.path.get_workspace_path')
    def test_valid_host_path_conversion(self, mock_get_workspace):
        """Test valid host path conversion."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        host_path = Path("/data/workspaces/user/session/file.txt")
        result = host_to_container_path(host_path, ctx=self.mock_ctx)
        
        expected = PurePosixPath("/workspace/file.txt")
        self.assertEqual(result, expected)

    @patch('aixtools.server.path.get_workspace_path')
    def test_host_root_path_conversion(self, mock_get_workspace):
        """Test host root path conversion."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        host_path = Path("/data/workspaces/user/session")
        result = host_to_container_path(host_path, ctx=self.mock_ctx)
        
        expected = PurePosixPath("/workspace")
        self.assertEqual(result, expected)

    @patch('aixtools.server.path.get_workspace_path')
    def test_nested_host_path_conversion(self, mock_get_workspace):
        """Test nested host path conversion."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        host_path = Path("/data/workspaces/user/session/subdir/nested/file.txt")
        result = host_to_container_path(host_path, ctx=self.mock_ctx)
        
        expected = PurePosixPath("/workspace/subdir/nested/file.txt")
        self.assertEqual(result, expected)

    @patch('aixtools.server.path.get_workspace_path')
    def test_invalid_host_path_raises_error(self, mock_get_workspace):
        """Test that invalid host paths raise ValueError."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        invalid_paths = [
            Path("/tmp/file.txt"),
            Path("/home/user/file.txt"),
            Path("/data/other/file.txt"),
        ]
        
        for invalid_path in invalid_paths:
            with self.subTest(path=invalid_path):
                with self.assertRaises(ValueError) as context:
                    host_to_container_path(invalid_path, ctx=self.mock_ctx)
                
                self.assertIn("Host path must be a subdir", str(context.exception))
                self.assertIn(str(invalid_path), str(context.exception))

    @patch('aixtools.server.path.get_workspace_path')
    def test_context_passed_to_get_workspace_path(self, mock_get_workspace):
        """Test that context is properly passed to get_workspace_path."""
        mock_get_workspace.return_value = Path("/data/workspaces/user/session")
        
        host_path = Path("/data/workspaces/user/session/file.txt")
        host_to_container_path(host_path, ctx=self.mock_ctx)
        
        mock_get_workspace.assert_called_once_with(ctx=self.mock_ctx)


if __name__ == '__main__':
    unittest.main()