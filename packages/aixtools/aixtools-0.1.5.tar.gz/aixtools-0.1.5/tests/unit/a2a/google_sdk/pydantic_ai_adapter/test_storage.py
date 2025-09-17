"""Tests for the Pydantic AI adapter storage module."""

import unittest
from unittest.mock import MagicMock

from aixtools.a2a.google_sdk.pydantic_ai_adapter.storage import (
    PydanticAiAgentHistoryStorage,
    InMemoryHistoryStorage,
)


class TestInMemoryHistoryStorage(unittest.TestCase):
    """Tests for the InMemoryHistoryStorage class."""

    def setUp(self):
        self.storage = InMemoryHistoryStorage()

    def test_init(self):
        """Test InMemoryHistoryStorage initialization."""
        self.assertEqual(self.storage.storage, {})

    def test_get_nonexistent_task(self):
        """Test getting history for a task that doesn't exist."""
        result = self.storage.get("nonexistent_task")
        self.assertIsNone(result)

    def test_store_and_get_messages(self):
        """Test storing and retrieving messages."""
        task_id = "test_task_1"
        # Use simple mock objects that can be stored
        messages = [MagicMock(), MagicMock()]
        
        # Store the messages
        self.storage.store(task_id, messages)
        
        # Retrieve the messages
        result = self.storage.get(task_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, messages)
        self.assertEqual(len(result), 2)

    def test_store_overwrites_existing(self):
        """Test that storing overwrites existing messages for the same task."""
        task_id = "test_task_3"
        
        # Store initial messages
        initial_messages = [MagicMock()]
        self.storage.store(task_id, initial_messages)
        
        # Store new messages (should overwrite)
        new_messages = [MagicMock(), MagicMock()]
        self.storage.store(task_id, new_messages)
        
        # Retrieve and verify new messages are stored
        result = self.storage.get(task_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, new_messages)
        self.assertEqual(len(result), 2)
        self.assertNotEqual(result, initial_messages)

    def test_multiple_tasks(self):
        """Test storing and retrieving messages for multiple tasks."""
        task1_id = "task_1"
        task2_id = "task_2"
        
        task1_messages = [MagicMock()]
        task2_messages = [MagicMock(), MagicMock()]
        
        # Store messages for both tasks
        self.storage.store(task1_id, task1_messages)
        self.storage.store(task2_id, task2_messages)
        
        # Retrieve and verify both tasks' messages
        result1 = self.storage.get(task1_id)
        result2 = self.storage.get(task2_id)
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, task1_messages)
        self.assertEqual(result2, task2_messages)
        self.assertNotEqual(result1, result2)

    def test_store_empty_list(self):
        """Test storing an empty list of messages."""
        task_id = "empty_task"
        empty_messages = []
        
        self.storage.store(task_id, empty_messages)
        result = self.storage.get(task_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, empty_messages)
        self.assertEqual(len(result), 0)

    def test_get_after_multiple_stores(self):
        """Test that get returns the most recent store for a task."""
        task_id = "update_task"
        
        # Store multiple times
        messages1 = [MagicMock()]
        messages2 = [MagicMock()]
        messages3 = [MagicMock(), MagicMock()]
        
        self.storage.store(task_id, messages1)
        self.storage.store(task_id, messages2)
        self.storage.store(task_id, messages3)
        
        result = self.storage.get(task_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result, messages3)

    def test_storage_isolation(self):
        """Test that different storage instances are isolated."""
        storage1 = InMemoryHistoryStorage()
        storage2 = InMemoryHistoryStorage()
        
        task_id = "isolation_test"
        messages1 = [MagicMock()]
        messages2 = [MagicMock()]
        
        storage1.store(task_id, messages1)
        storage2.store(task_id, messages2)
        
        result1 = storage1.get(task_id)
        result2 = storage2.get(task_id)
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1, messages1)
        self.assertEqual(result2, messages2)
        self.assertNotEqual(result1, result2)


class TestPydanticAiAgentHistoryStorageInterface(unittest.TestCase):
    """Tests for the PydanticAiAgentHistoryStorage abstract interface."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that the abstract base class cannot be instantiated."""
        with self.assertRaises(TypeError):
            PydanticAiAgentHistoryStorage()

    def test_inmemory_implements_interface(self):
        """Test that InMemoryHistoryStorage properly implements the interface."""
        storage = InMemoryHistoryStorage()
        
        # Verify it's an instance of the abstract base class
        self.assertIsInstance(storage, PydanticAiAgentHistoryStorage)
        
        # Verify it has the required methods
        self.assertTrue(hasattr(storage, 'get'))
        self.assertTrue(hasattr(storage, 'store'))
        self.assertTrue(callable(getattr(storage, 'get')))
        self.assertTrue(callable(getattr(storage, 'store')))
