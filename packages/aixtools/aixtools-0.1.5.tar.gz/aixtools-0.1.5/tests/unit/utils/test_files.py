"""Unit tests for aixtools.utils.files module."""

import unittest

from aixtools.utils.files import is_text_content


class TestIsTextContent(unittest.TestCase):
    """Test cases for is_text_content function."""

    def test_text_mime_types_return_true(self):
        """Test that text mime types return True."""
        text_mime_types = [
            "text/plain",
            "text/html",
            "text/css",
            "text/javascript",
            "text/csv",
            "text/xml",
            "text/markdown",
        ]
        
        for mime_type in text_mime_types:
            with self.subTest(mime_type=mime_type):
                result = is_text_content(b"some content", mime_type)
                self.assertTrue(result, f"MIME type {mime_type} should be detected as text")

    def test_application_text_mime_types_return_true(self):
        """Test that application text-like mime types return True."""
        app_text_mime_types = [
            "application/json",
            "application/xml",
            "application/javascript",
        ]
        
        for mime_type in app_text_mime_types:
            with self.subTest(mime_type=mime_type):
                result = is_text_content(b"some content", mime_type)
                self.assertTrue(result, f"MIME type {mime_type} should be detected as text")

    def test_binary_mime_types_with_valid_utf8_return_true(self):
        """Test that binary mime types with valid UTF-8 content return True."""
        binary_mime_types = [
            "application/octet-stream",
            "image/png",
            "video/mp4",
            "application/pdf",
        ]
        
        utf8_content = "Hello, world! 🌍".encode("utf-8")
        
        for mime_type in binary_mime_types:
            with self.subTest(mime_type=mime_type):
                result = is_text_content(utf8_content, mime_type)
                self.assertTrue(result, f"Valid UTF-8 content should be detected as text even with {mime_type}")

    def test_binary_mime_types_with_invalid_utf8_return_false(self):
        """Test that binary mime types with invalid UTF-8 content return False."""
        binary_mime_types = [
            "application/octet-stream",
            "image/png",
            "video/mp4",
            "application/pdf",
        ]
        
        # Create invalid UTF-8 bytes
        invalid_utf8_content = b'\x80\x81\x82\x83'
        
        for mime_type in binary_mime_types:
            with self.subTest(mime_type=mime_type):
                result = is_text_content(invalid_utf8_content, mime_type)
                self.assertFalse(result, f"Invalid UTF-8 content should not be detected as text with {mime_type}")

    def test_empty_mime_type_with_valid_utf8_return_true(self):
        """Test that empty mime type with valid UTF-8 content returns True."""
        utf8_content = "Hello, world!".encode("utf-8")
        
        result = is_text_content(utf8_content, "")
        self.assertTrue(result)

    def test_empty_mime_type_with_invalid_utf8_return_false(self):
        """Test that empty mime type with invalid UTF-8 content returns False."""
        invalid_utf8_content = b'\x80\x81\x82\x83'
        
        result = is_text_content(invalid_utf8_content, "")
        self.assertFalse(result)

    def test_none_mime_type_with_valid_utf8_return_true(self):
        """Test that None mime type with valid UTF-8 content returns True."""
        utf8_content = "Hello, world!".encode("utf-8")
        
        result = is_text_content(utf8_content, None)  # type: ignore
        self.assertTrue(result)

    def test_none_mime_type_with_invalid_utf8_return_false(self):
        """Test that None mime type with invalid UTF-8 content returns False."""
        invalid_utf8_content = b'\x80\x81\x82\x83'
        
        result = is_text_content(invalid_utf8_content, None)  # type: ignore
        self.assertFalse(result)

    def test_empty_content_with_text_mime_type_return_true(self):
        """Test that empty content with text mime type returns True."""
        result = is_text_content(b"", "text/plain")
        self.assertTrue(result)

    def test_empty_content_with_binary_mime_type_return_true(self):
        """Test that empty content with binary mime type returns True (empty is valid UTF-8)."""
        result = is_text_content(b"", "application/octet-stream")
        self.assertTrue(result)

    def test_unicode_content_return_true(self):
        """Test that Unicode content is properly detected as text."""
        unicode_strings = [
            "Hello, 世界!",
            "Café ☕",
            "🚀 Rocket",
            "Здравствуй мир",
            "مرحبا بالعالم",
        ]
        
        for unicode_str in unicode_strings:
            with self.subTest(content=unicode_str):
                utf8_content = unicode_str.encode("utf-8")
                result = is_text_content(utf8_content, "application/octet-stream")
                self.assertTrue(result, f"Unicode string '{unicode_str}' should be detected as text")

    def test_binary_image_data_return_false(self):
        """Test that actual binary image data returns False."""
        # PNG file header
        png_header = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        
        result = is_text_content(png_header, "image/png")
        self.assertFalse(result)

    def test_binary_executable_data_return_false(self):
        """Test that binary executable data returns False."""
        # Binary data with invalid UTF-8 sequences
        binary_data = b'\x7f\x80\x81\x82\x83\x84\x85\x86'
        
        result = is_text_content(binary_data, "application/octet-stream")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()