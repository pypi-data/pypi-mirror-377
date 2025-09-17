"""Unit tests for aixtools.google.client module."""

import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from aixtools.google.client import get_genai_client


class TestGetGenaiClient(unittest.TestCase):
    """Test cases for get_genai_client function."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original environment variables to restore later
        self.original_env = os.environ.copy()
        
    def tearDown(self):
        """Clean up after tests."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('aixtools.google.client.genai.Client')
    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    @patch('aixtools.google.client.GOOGLE_GENAI_USE_VERTEXAI', True)
    def test_get_genai_client_basic_success(self, mock_client):
        """Test get_genai_client with basic valid configuration."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        result = get_genai_client()
        
        mock_client.assert_called_once_with(
            vertexai=True,
            project='test-project',
            location='us-central1'
        )
        self.assertEqual(result, mock_client_instance)

    @patch('aixtools.google.client.genai.Client')
    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-west1')
    @patch('aixtools.google.client.GOOGLE_GENAI_USE_VERTEXAI', False)
    def test_get_genai_client_without_vertexai(self, mock_client):
        """Test get_genai_client with GOOGLE_GENAI_USE_VERTEXAI set to False."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        result = get_genai_client()
        
        mock_client.assert_called_once_with(
            vertexai=False,
            project='test-project',
            location='us-west1'
        )
        self.assertEqual(result, mock_client_instance)

    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', None)
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    def test_get_genai_client_missing_project(self):
        """Test get_genai_client raises AssertionError when GOOGLE_CLOUD_PROJECT is not set."""
        with self.assertRaises(AssertionError) as context:
            get_genai_client()
        
        self.assertIn("GOOGLE_CLOUD_PROJECT is not set", str(context.exception))

    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', None)
    def test_get_genai_client_missing_location(self):
        """Test get_genai_client raises AssertionError when GOOGLE_CLOUD_LOCATION is not set."""
        with self.assertRaises(AssertionError) as context:
            get_genai_client()
        
        self.assertIn("GOOGLE_CLOUD_LOCATION is not set", str(context.exception))

    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', '')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    def test_get_genai_client_empty_project(self):
        """Test get_genai_client raises AssertionError when GOOGLE_CLOUD_PROJECT is empty."""
        with self.assertRaises(AssertionError) as context:
            get_genai_client()
        
        self.assertIn("GOOGLE_CLOUD_PROJECT is not set", str(context.exception))

    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', '')
    def test_get_genai_client_empty_location(self):
        """Test get_genai_client raises AssertionError when GOOGLE_CLOUD_LOCATION is empty."""
        with self.assertRaises(AssertionError) as context:
            get_genai_client()
        
        self.assertIn("GOOGLE_CLOUD_LOCATION is not set", str(context.exception))

    @patch('aixtools.google.client.genai.Client')
    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    @patch('aixtools.google.client.GOOGLE_GENAI_USE_VERTEXAI', True)
    @patch('aixtools.google.client.logger')
    def test_get_genai_client_with_valid_service_account_key(self, mock_logger, mock_client):
        """Test get_genai_client with valid service account key file."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Create a temporary file path that exists
        with patch('pathlib.Path.exists', return_value=True):
            service_account_path = Path('/tmp/test-service-account.json')
            
            result = get_genai_client(service_account_path)
            
            # Verify the environment variable was set
            self.assertEqual(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), str(service_account_path))
            
            # Verify logging was called
            mock_logger.info.assert_called_once_with(f"✅ GCP Service Account Key File: {service_account_path}")
            
            # Verify client was created correctly
            mock_client.assert_called_once_with(
                vertexai=True,
                project='test-project',
                location='us-central1'
            )
            self.assertEqual(result, mock_client_instance)

    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    def test_get_genai_client_with_nonexistent_service_account_key(self):
        """Test get_genai_client raises FileNotFoundError for nonexistent service account key."""
        with patch('pathlib.Path.exists', return_value=False):
            service_account_path = Path('/tmp/nonexistent-service-account.json')
            
            with self.assertRaises(FileNotFoundError) as context:
                get_genai_client(service_account_path)
            
            self.assertIn(f"Service account key file not found: {service_account_path}", str(context.exception))

    @patch('aixtools.google.client.genai.Client')
    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    @patch('aixtools.google.client.GOOGLE_GENAI_USE_VERTEXAI', True)
    def test_get_genai_client_preserves_existing_credentials_env(self, mock_client):
        """Test get_genai_client preserves existing GOOGLE_APPLICATION_CREDENTIALS when no service account key provided."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Set existing credentials
        existing_credentials = '/existing/path/to/credentials.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = existing_credentials
        
        result = get_genai_client()
        
        # Verify existing credentials are preserved
        self.assertEqual(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), existing_credentials)
        
        mock_client.assert_called_once_with(
            vertexai=True,
            project='test-project',
            location='us-central1'
        )
        self.assertEqual(result, mock_client_instance)

    @patch('aixtools.google.client.genai.Client')
    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    @patch('aixtools.google.client.GOOGLE_GENAI_USE_VERTEXAI', True)
    @patch('aixtools.google.client.logger')
    def test_get_genai_client_overwrites_existing_credentials_env(self, mock_logger, mock_client):
        """Test get_genai_client overwrites existing GOOGLE_APPLICATION_CREDENTIALS when service account key provided."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        # Set existing credentials
        existing_credentials = '/existing/path/to/credentials.json'
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = existing_credentials
        
        with patch('pathlib.Path.exists', return_value=True):
            new_service_account_path = Path('/tmp/new-service-account.json')
            
            result = get_genai_client(new_service_account_path)
            
            # Verify new credentials overwrite existing ones
            self.assertEqual(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), str(new_service_account_path))
            
            # Verify logging was called
            mock_logger.info.assert_called_once_with(f"✅ GCP Service Account Key File: {new_service_account_path}")
            
            mock_client.assert_called_once_with(
                vertexai=True,
                project='test-project',
                location='us-central1'
            )
            self.assertEqual(result, mock_client_instance)

    @patch('aixtools.google.client.genai.Client')
    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    @patch('aixtools.google.client.GOOGLE_GENAI_USE_VERTEXAI', True)
    def test_get_genai_client_genai_client_exception(self, mock_client):
        """Test get_genai_client propagates exceptions from genai.Client."""
        mock_client.side_effect = Exception("GenAI client initialization failed")
        
        with self.assertRaises(Exception) as context:
            get_genai_client()
        
        self.assertIn("GenAI client initialization failed", str(context.exception))

    @patch('aixtools.google.client.genai.Client')
    @patch('aixtools.google.client.GOOGLE_CLOUD_PROJECT', 'test-project')
    @patch('aixtools.google.client.GOOGLE_CLOUD_LOCATION', 'us-central1')
    @patch('aixtools.google.client.GOOGLE_GENAI_USE_VERTEXAI', True)
    @patch('aixtools.google.client.logger')
    def test_get_genai_client_service_account_path_as_string(self, mock_logger, mock_client):
        """Test get_genai_client handles service account path as string correctly."""
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        
        with patch('pathlib.Path.exists', return_value=True):
            service_account_path = Path('/tmp/test-service-account.json')
            
            result = get_genai_client(service_account_path)
            
            # Verify the environment variable was set as string
            self.assertEqual(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), str(service_account_path))
            self.assertIsInstance(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), str)
            
            mock_client.assert_called_once()
            self.assertEqual(result, mock_client_instance)


if __name__ == '__main__':
    unittest.main()
