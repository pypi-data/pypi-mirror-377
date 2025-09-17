"""Unit tests for aixtools.agents.prompt module."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from pydantic_ai import BinaryContent

from aixtools.agents.prompt import (
    CLAUDE_IMAGE_MAX_FILE_SIZE_IN_CONTEXT,
    CLAUDE_MAX_FILE_SIZE_IN_CONTEXT,
    build_user_input,
    file_to_binary_content,
    should_be_included_into_context,
)


class TestShouldBeIncludedIntoContext(unittest.TestCase):
    """Test cases for should_be_included_into_context function."""

    def test_non_binary_content_returns_false(self):
        """Test that non-BinaryContent returns False."""
        result = should_be_included_into_context("text content", 100)
        self.assertFalse(result)
        
        result = should_be_included_into_context(None, 100)
        self.assertFalse(result)

    def test_text_media_type_returns_false(self):
        """Test that text media types return False."""
        binary_content = BinaryContent(data=b"test", media_type="text/plain")
        result = should_be_included_into_context(binary_content, 100)
        self.assertFalse(result)
        
        binary_content = BinaryContent(data=b"test", media_type="text/html")
        result = should_be_included_into_context(binary_content, 100)
        self.assertFalse(result)

    def test_archive_types_return_false(self):
        """Test that archive media types return False."""
        archive_types = [
            "application/zip",
            "application/x-tar",
            "application/gzip",
            "application/x-gzip",
            "application/x-rar-compressed",
            "application/x-7z-compressed",
        ]
        
        for media_type in archive_types:
            binary_content = BinaryContent(data=b"test", media_type=media_type)
            result = should_be_included_into_context(binary_content, 100)
            self.assertFalse(result, f"Archive type {media_type} should return False")

    def test_image_within_size_limit_returns_true(self):
        """Test that images within size limit return True."""
        with patch.object(BinaryContent, 'is_image', new_callable=lambda: True):
            binary_content = BinaryContent(data=b"image_data", media_type="image/png")
            
            # Test with size under limit
            result = should_be_included_into_context(binary_content, 1024)
            self.assertTrue(result)

    def test_image_over_size_limit_returns_false(self):
        """Test that images over size limit return False."""
        with patch.object(BinaryContent, 'is_image', new_callable=lambda: True):
            binary_content = BinaryContent(data=b"image_data", media_type="image/png")
            
            # Test with size over limit
            result = should_be_included_into_context(binary_content, CLAUDE_IMAGE_MAX_FILE_SIZE_IN_CONTEXT + 1)
            self.assertFalse(result)

    def test_non_image_within_size_limit_returns_true(self):
        """Test that non-images within size limit return True."""
        with patch.object(BinaryContent, 'is_image', new_callable=lambda: False):
            binary_content = BinaryContent(data=b"pdf_data", media_type="application/pdf")
            
            # Test with size under limit
            result = should_be_included_into_context(binary_content, 1024)
            self.assertTrue(result)

    def test_non_image_over_size_limit_returns_false(self):
        """Test that non-images over size limit return False."""
        with patch.object(BinaryContent, 'is_image', new_callable=lambda: False):
            binary_content = BinaryContent(data=b"pdf_data", media_type="application/pdf")
            
            # Test with size over limit
            result = should_be_included_into_context(binary_content, CLAUDE_MAX_FILE_SIZE_IN_CONTEXT + 1)
            self.assertFalse(result)

    def test_custom_size_limits(self):
        """Test with custom size limits."""
        # Test non-image content with custom limits (since image detection is complex)
        pdf_content = BinaryContent(data=b"pdf_data", media_type="application/pdf")
        
        # Test non-image over custom file limit
        result = should_be_included_into_context(
            pdf_content, 5000, max_img_size_bytes=1024, max_file_size_bytes=4096
        )
        self.assertFalse(result)
        
        # Test non-image under custom file limit
        result = should_be_included_into_context(
            pdf_content, 2000, max_img_size_bytes=1024, max_file_size_bytes=4096
        )
        self.assertTrue(result)
        
        # Test with very small custom limits
        result = should_be_included_into_context(
            pdf_content, 100, max_img_size_bytes=50, max_file_size_bytes=80
        )
        self.assertFalse(result)
        
        # Test with very large custom limits
        result = should_be_included_into_context(
            pdf_content, 100, max_img_size_bytes=200, max_file_size_bytes=200
        )
        self.assertTrue(result)


class TestFileToBinaryContent(unittest.TestCase):
    """Test cases for file_to_binary_content function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    @patch('aixtools.agents.prompt.is_text_content')
    @patch('mimetypes.guess_type')
    def test_text_file_returns_string(self, mock_guess_type, mock_is_text):
        """Test that text files return decoded strings."""
        mock_guess_type.return_value = ("text/plain", None)
        mock_is_text.return_value = True
        
        test_file = self.temp_path / "test.txt"
        test_content = "Hello, world!"
        test_file.write_text(test_content, encoding="utf-8")
        
        result = file_to_binary_content(test_file)
        
        self.assertEqual(result, test_content)
        mock_is_text.assert_called_once()

    @patch('aixtools.agents.prompt.is_text_content')
    @patch('mimetypes.guess_type')
    def test_binary_file_returns_binary_content(self, mock_guess_type, mock_is_text):
        """Test that binary files return BinaryContent."""
        mock_guess_type.return_value = ("image/png", None)
        mock_is_text.return_value = False
        
        test_file = self.temp_path / "test.png"
        test_data = b'\x89PNG\r\n\x1a\n'
        test_file.write_bytes(test_data)
        
        result = file_to_binary_content(test_file)
        
        self.assertIsInstance(result, BinaryContent)
        if isinstance(result, BinaryContent):
            self.assertEqual(result.data, test_data)
            self.assertEqual(result.media_type, "image/png")

    @patch('aixtools.agents.prompt.is_text_content')
    @patch('mimetypes.guess_type')
    def test_unknown_mime_type_defaults_to_octet_stream(self, mock_guess_type, mock_is_text):
        """Test that unknown mime types default to application/octet-stream."""
        mock_guess_type.return_value = (None, None)
        mock_is_text.return_value = False
        
        test_file = self.temp_path / "test.unknown"
        test_data = b'unknown data'
        test_file.write_bytes(test_data)
        
        result = file_to_binary_content(test_file)
        
        self.assertIsInstance(result, BinaryContent)
        if isinstance(result, BinaryContent):
            self.assertEqual(result.media_type, "application/octet-stream")

    @patch('aixtools.agents.prompt.is_text_content')
    def test_explicit_mime_type(self, mock_is_text):
        """Test with explicitly provided mime type."""
        mock_is_text.return_value = False
        
        test_file = self.temp_path / "test.data"
        test_data = b'test data'
        test_file.write_bytes(test_data)
        
        result = file_to_binary_content(test_file, "application/custom")
        
        self.assertIsInstance(result, BinaryContent)
        if isinstance(result, BinaryContent):
            self.assertEqual(result.media_type, "application/custom")


class TestBuildUserInput(unittest.TestCase):
    """Test cases for build_user_input function."""

    def setUp(self):
        """Set up test fixtures."""
        self.session_tuple = ("user123", "session456")
        self.user_text = "Please analyze these files"

    def test_no_file_paths_returns_text_only(self):
        """Test that no file paths returns just the user text."""
        result = build_user_input(self.session_tuple, self.user_text, [])
        
        self.assertEqual(result, self.user_text)

    @patch('aixtools.agents.prompt.should_be_included_into_context')
    @patch('aixtools.agents.prompt.file_to_binary_content')
    @patch('aixtools.agents.prompt.container_to_host_path')
    @patch('mimetypes.guess_type')
    def test_single_file_not_included_in_context(
        self, mock_guess_type, mock_container_to_host,
        mock_file_to_binary, mock_should_include
    ):
        """Test with single file that should not be included in context."""
        # Setup mocks
        mock_guess_type.return_value = ("text/plain", None)
        mock_should_include.return_value = False
        
        mock_host_path = Mock()
        mock_host_path.stat.return_value.st_size = 1024
        mock_container_to_host.return_value = mock_host_path
        
        mock_file_to_binary.return_value = "file content"
        
        file_paths = [Path("/workspace/test.txt")]
        
        result = build_user_input(self.session_tuple, self.user_text, file_paths)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)  # Only the prompt, no binary attachments
        self.assertIsInstance(result[0], str)
        prompt_text = str(result[0])
        self.assertIn("Please analyze these files", prompt_text)
        self.assertIn("Attachments:", prompt_text)
        self.assertIn("test.txt", prompt_text)
        self.assertIn("file_size=1024 bytes", prompt_text)

    @patch('aixtools.agents.prompt.should_be_included_into_context')
    @patch('aixtools.agents.prompt.file_to_binary_content')
    @patch('aixtools.agents.prompt.container_to_host_path')
    @patch('mimetypes.guess_type')
    def test_single_file_included_in_context(
        self, mock_guess_type, mock_container_to_host,
        mock_file_to_binary, mock_should_include
    ):
        """Test with single file that should be included in context."""
        # Setup mocks
        mock_guess_type.return_value = ("image/png", None)
        mock_should_include.return_value = True
        
        mock_host_path = Mock()
        mock_host_path.stat.return_value.st_size = 2048
        mock_container_to_host.return_value = mock_host_path
        
        mock_binary_content = BinaryContent(data=b"image data", media_type="image/png")
        mock_file_to_binary.return_value = mock_binary_content
        
        file_paths = [Path("/workspace/image.png")]
        
        result = build_user_input(self.session_tuple, self.user_text, file_paths)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # Prompt + 1 binary attachment
        self.assertIsInstance(result[0], str)
        prompt_text = str(result[0])
        self.assertIn("Please analyze these files", prompt_text)
        self.assertIn("Attachments:", prompt_text)
        self.assertIn("image.png", prompt_text)
        self.assertIn("file_size=2048 bytes", prompt_text)
        self.assertIn("provided to model context at index 0", prompt_text)
        self.assertEqual(result[1], mock_binary_content)

    @patch('aixtools.agents.prompt.should_be_included_into_context')
    @patch('aixtools.agents.prompt.file_to_binary_content')
    @patch('aixtools.agents.prompt.container_to_host_path')
    @patch('mimetypes.guess_type')
    def test_multiple_files_mixed_inclusion(
        self, mock_guess_type, mock_container_to_host,
        mock_file_to_binary, mock_should_include
    ):
        """Test with multiple files, some included in context, some not."""
        # Setup mocks
        mock_guess_type.side_effect = [("text/plain", None), ("image/png", None)]
        mock_should_include.side_effect = [False, True]  # First file not included, second included
        
        mock_host_path1 = Mock()
        mock_host_path1.stat.return_value.st_size = 1024
        mock_host_path2 = Mock()
        mock_host_path2.stat.return_value.st_size = 2048
        mock_container_to_host.side_effect = [mock_host_path1, mock_host_path2]
        
        mock_text_content = "text content"
        mock_binary_content = BinaryContent(data=b"image data", media_type="image/png")
        mock_file_to_binary.side_effect = [mock_text_content, mock_binary_content]
        
        file_paths = [Path("/workspace/text.txt"), Path("/workspace/image.png")]
        
        result = build_user_input(self.session_tuple, self.user_text, file_paths)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)  # Prompt + 1 binary attachment
        self.assertIsInstance(result[0], str)
        prompt_text = str(result[0])
        self.assertIn("Please analyze these files", prompt_text)
        self.assertIn("Attachments:", prompt_text)
        self.assertIn("text.txt", prompt_text)
        self.assertIn("image.png", prompt_text)
        self.assertIn("file_size=1024 bytes", prompt_text)
        self.assertIn("file_size=2048 bytes", prompt_text)
        self.assertIn("provided to model context at index 0", prompt_text)
        self.assertEqual(result[1], mock_binary_content)

    def test_non_workspace_path_raises_error(self):
        """Test that non-workspace paths raise ValueError."""
        file_paths = [Path("/invalid/path.txt")]
        
        with self.assertRaises(ValueError) as context:
            build_user_input(self.session_tuple, self.user_text, file_paths)
        
        self.assertIn(
            "Container path must be a subdir of '/workspace', got '/invalid/path.txt' instead",
            str(context.exception),
        )

    @patch('aixtools.agents.prompt.should_be_included_into_context')
    @patch('aixtools.agents.prompt.file_to_binary_content')
    @patch('aixtools.agents.prompt.container_to_host_path')
    @patch('mimetypes.guess_type')
    def test_unknown_mime_type_defaults(
        self, mock_guess_type, mock_container_to_host,
        mock_file_to_binary, mock_should_include
    ):
        """Test that unknown mime types default to application/octet-stream."""
        # Setup mocks
        mock_guess_type.return_value = (None, None)  # Unknown mime type
        mock_should_include.return_value = False
        
        mock_host_path = Mock()
        mock_host_path.stat.return_value.st_size = 1024
        mock_container_to_host.return_value = mock_host_path
        
        mock_file_to_binary.return_value = "file content"
        
        file_paths = [Path("/workspace/unknown.dat")]
        
        build_user_input(self.session_tuple, self.user_text, file_paths)
        
        # Verify that file_to_binary_content was called with the default mime type
        mock_file_to_binary.assert_called_once_with(mock_host_path, "application/octet-stream")


if __name__ == '__main__':
    unittest.main()
