"""Tests for the remote agent connection module."""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch, call

from a2a.client import Client
from a2a.types import AgentCard, Message, Task, TaskState, TaskStatus, TaskQueryParams

from aixtools.a2a.google_sdk.remote_agent_connection import (
    RemoteAgentConnection,
    is_in_terminal_state,
    is_in_terminal_or_interrupted_state,
)


class TestRemoteAgentConnection(unittest.IsolatedAsyncioTestCase):
    """Tests for the RemoteAgentConnection class."""

    def setUp(self):
        self.mock_card = MagicMock(spec=AgentCard)
        self.mock_client = AsyncMock(spec=Client)
        self.connection = RemoteAgentConnection(self.mock_card, self.mock_client)

    def test_get_agent_card(self):
        """Test that get_agent_card returns the stored card."""
        result = self.connection.get_agent_card()
        self.assertEqual(result, self.mock_card)

    async def test_send_message_returns_message(self):
        """Test send_message when it receives a Message response."""
        mock_message = MagicMock(spec=Message)
        mock_task = MagicMock(spec=Task)
        
        # Mock the async generator to yield a message
        async def mock_generator():
            yield mock_message
            yield (mock_task,)
        
        self.mock_client.send_message.return_value = mock_generator()
        
        test_message = MagicMock(spec=Message)
        result = await self.connection.send_message(test_message)
        
        self.assertEqual(result, mock_message)
        self.mock_client.send_message.assert_called_once_with(test_message)

    async def test_send_message_returns_terminal_task(self):
        """Test send_message when it receives a task in terminal state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.completed
        
        # Mock the async generator to yield a terminal task
        async def mock_generator():
            yield (mock_task,)
        
        self.mock_client.send_message.return_value = mock_generator()
        
        test_message = MagicMock(spec=Message)
        result = await self.connection.send_message(test_message)
        
        self.assertEqual(result, mock_task)

    async def test_send_message_returns_interrupted_task(self):
        """Test send_message when it receives a task in interrupted state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.input_required
        
        # Mock the async generator to yield an interrupted task
        async def mock_generator():
            yield (mock_task,)
        
        self.mock_client.send_message.return_value = mock_generator()
        
        test_message = MagicMock(spec=Message)
        result = await self.connection.send_message(test_message)
        
        self.assertEqual(result, mock_task)

    async def test_send_message_returns_last_task(self):
        """Test send_message returns the last task when no terminal/interrupted state is reached."""
        mock_task1 = MagicMock(spec=Task)
        mock_task1.status = MagicMock(spec=TaskStatus)
        mock_task1.status.state = TaskState.working
        
        mock_task2 = MagicMock(spec=Task)
        mock_task2.status = MagicMock(spec=TaskStatus)
        mock_task2.status.state = TaskState.working
        
        # Mock the async generator to yield multiple running tasks
        async def mock_generator():
            yield (mock_task1,)
            yield (mock_task2,)
        
        self.mock_client.send_message.return_value = mock_generator()
        
        test_message = MagicMock(spec=Message)
        result = await self.connection.send_message(test_message)
        
        self.assertEqual(result, mock_task2)

    async def test_send_message_handles_exception(self):
        """Test send_message properly handles and re-raises exceptions."""
        test_error = Exception("Test error")
        self.mock_client.send_message.side_effect = test_error
        
        test_message = MagicMock(spec=Message)
        
        with self.assertRaises(Exception) as context:
            await self.connection.send_message(test_message)
        
        self.assertEqual(context.exception, test_error)

    async def test_send_message_returns_none_when_no_events(self):
        """Test send_message returns None when no events are yielded."""
        # Mock empty async generator
        async def mock_generator():
            return
            yield  # This line will never be reached
        
        self.mock_client.send_message.return_value = mock_generator()
        
        test_message = MagicMock(spec=Message)
        result = await self.connection.send_message(test_message)
        
        self.assertIsNone(result)

    async def test_send_message_with_polling_returns_message(self):
        """Test send_message_with_polling when send_message returns a Message."""
        mock_message = MagicMock(spec=Message)
        
        # Mock send_message to return a Message
        self.connection.send_message = AsyncMock(return_value=mock_message)
        
        test_message = MagicMock(spec=Message)
        result = await self.connection.send_message_with_polling(test_message)
        
        self.assertEqual(result, mock_message)
        self.connection.send_message.assert_called_once_with(test_message)

    async def test_send_message_with_polling_returns_terminal_task(self):
        """Test send_message_with_polling when send_message returns a task in terminal state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.completed
        
        # Mock send_message to return a terminal task
        self.connection.send_message = AsyncMock(return_value=mock_task)
        
        test_message = MagicMock(spec=Message)
        result = await self.connection.send_message_with_polling(test_message)
        
        self.assertEqual(result, mock_task)
        self.connection.send_message.assert_called_once_with(test_message)

    async def test_send_message_with_polling_polls_until_terminal(self):
        """Test send_message_with_polling polls until task reaches terminal state."""
        # Create initial task in working state
        initial_task = MagicMock(spec=Task)
        initial_task.id = "task123"
        initial_task.status = MagicMock(spec=TaskStatus)
        initial_task.status.state = TaskState.working
        
        # Create intermediate task still in working state
        intermediate_task = MagicMock(spec=Task)
        intermediate_task.status = MagicMock(spec=TaskStatus)
        intermediate_task.status.state = TaskState.working
        
        # Create final task in completed state
        final_task = MagicMock(spec=Task)
        final_task.status = MagicMock(spec=TaskStatus)
        final_task.status.state = TaskState.completed
        
        # Mock send_message to return initial working task
        self.connection.send_message = AsyncMock(return_value=initial_task)
        
        # Mock get_task to return intermediate task first, then final task
        self.mock_client.get_task.side_effect = [intermediate_task, final_task]
        
        test_message = MagicMock(spec=Message)
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await self.connection.send_message_with_polling(
                test_message, sleep_time=0.1, max_iter=10
            )
        
        self.assertEqual(result, final_task)
        self.connection.send_message.assert_called_once_with(test_message)
        
        # Verify get_task was called with correct parameters
        expected_calls = [
            call(TaskQueryParams(id="task123")),
            call(TaskQueryParams(id="task123"))
        ]
        self.mock_client.get_task.assert_has_calls(expected_calls)
        
        # Verify sleep was called twice (once for each polling iteration)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(0.1)

    async def test_send_message_with_polling_polls_until_interrupted(self):
        """Test send_message_with_polling polls until task reaches interrupted state."""
        # Create initial task in working state
        initial_task = MagicMock(spec=Task)
        initial_task.id = "task456"
        initial_task.status = MagicMock(spec=TaskStatus)
        initial_task.status.state = TaskState.working
        
        # Create final task in input_required state (interrupted)
        final_task = MagicMock(spec=Task)
        final_task.status = MagicMock(spec=TaskStatus)
        final_task.status.state = TaskState.input_required
        
        # Mock send_message to return initial working task
        self.connection.send_message = AsyncMock(return_value=initial_task)
        
        # Mock get_task to return final task
        self.mock_client.get_task.return_value = final_task
        
        test_message = MagicMock(spec=Message)
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await self.connection.send_message_with_polling(
                test_message, sleep_time=0.05, max_iter=5
            )
        
        self.assertEqual(result, final_task)
        self.mock_client.get_task.assert_called_once_with(TaskQueryParams(id="task456"))
        mock_sleep.assert_called_once_with(0.05)

    async def test_send_message_with_polling_timeout_exception(self):
        """Test send_message_with_polling raises exception when max_iter is reached."""
        # Create initial task in working state
        initial_task = MagicMock(spec=Task)
        initial_task.id = "task789"
        initial_task.status = MagicMock(spec=TaskStatus)
        initial_task.status.state = TaskState.working
        
        # Create task that stays in working state
        working_task = MagicMock(spec=Task)
        working_task.status = MagicMock(spec=TaskStatus)
        working_task.status.state = TaskState.working
        
        # Mock send_message to return initial working task
        self.connection.send_message = AsyncMock(return_value=initial_task)
        
        # Mock get_task to always return working task
        self.mock_client.get_task.return_value = working_task
        
        test_message = MagicMock(spec=Message)
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            with self.assertRaises(Exception) as context:
                await self.connection.send_message_with_polling(
                    test_message, sleep_time=0.1, max_iter=3
                )
        
        expected_timeout = 3 * 0.1  # max_iter * sleep_time
        self.assertIn(f"Task did not complete in {expected_timeout} seconds", str(context.exception))
        
        # Verify get_task was called max_iter times
        self.assertEqual(self.mock_client.get_task.call_count, 3)

    async def test_send_message_with_polling_no_task_returned(self):
        """Test send_message_with_polling raises ValueError when send_message returns None."""
        # Mock send_message to return None
        self.connection.send_message = AsyncMock(return_value=None)
        
        test_message = MagicMock(spec=Message)
        
        with self.assertRaises(ValueError) as context:
            await self.connection.send_message_with_polling(test_message)
        
        self.assertEqual(str(context.exception), "No task or message returned from send_message")
        self.connection.send_message.assert_called_once_with(test_message)

    async def test_send_message_with_polling_custom_parameters(self):
        """Test send_message_with_polling with custom sleep_time and max_iter."""
        # Create initial task in working state
        initial_task = MagicMock(spec=Task)
        initial_task.id = "custom_task"
        initial_task.status = MagicMock(spec=TaskStatus)
        initial_task.status.state = TaskState.working
        
        # Create final task in completed state
        final_task = MagicMock(spec=Task)
        final_task.status = MagicMock(spec=TaskStatus)
        final_task.status.state = TaskState.completed
        
        # Mock send_message to return initial working task
        self.connection.send_message = AsyncMock(return_value=initial_task)
        
        # Mock get_task to return final task
        self.mock_client.get_task.return_value = final_task
        
        test_message = MagicMock(spec=Message)
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await self.connection.send_message_with_polling(
                test_message, sleep_time=0.5, max_iter=100
            )
        
        self.assertEqual(result, final_task)
        mock_sleep.assert_called_once_with(0.5)

    async def test_send_message_with_polling_default_parameters(self):
        """Test send_message_with_polling uses default parameters correctly."""
        # Create initial task in working state
        initial_task = MagicMock(spec=Task)
        initial_task.id = "default_task"
        initial_task.status = MagicMock(spec=TaskStatus)
        initial_task.status.state = TaskState.working
        
        # Create final task in failed state (terminal)
        final_task = MagicMock(spec=Task)
        final_task.status = MagicMock(spec=TaskStatus)
        final_task.status.state = TaskState.failed
        
        # Mock send_message to return initial working task
        self.connection.send_message = AsyncMock(return_value=initial_task)
        
        # Mock get_task to return final task
        self.mock_client.get_task.return_value = final_task
        
        test_message = MagicMock(spec=Message)
        
        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await self.connection.send_message_with_polling(test_message)
        
        self.assertEqual(result, final_task)
        # Default sleep_time is 0.2
        mock_sleep.assert_called_once_with(0.2)


class TestHelperFunctions(unittest.TestCase):
    """Tests for helper functions in the remote agent connection module."""

    def test_is_in_terminal_state_completed(self):
        """Test is_in_terminal_state returns True for completed state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.completed
        
        result = is_in_terminal_state(mock_task)
        self.assertTrue(result)

    def test_is_in_terminal_state_canceled(self):
        """Test is_in_terminal_state returns True for canceled state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.canceled
        
        result = is_in_terminal_state(mock_task)
        self.assertTrue(result)

    def test_is_in_terminal_state_failed(self):
        """Test is_in_terminal_state returns True for failed state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.failed
        
        result = is_in_terminal_state(mock_task)
        self.assertTrue(result)

    def test_is_in_terminal_state_running(self):
        """Test is_in_terminal_state returns False for running state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.working
        
        result = is_in_terminal_state(mock_task)
        self.assertFalse(result)

    def test_is_in_terminal_or_interrupted_state_input_required(self):
        """Test is_in_terminal_or_interrupted_state returns True for input_required state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.input_required
        
        result = is_in_terminal_or_interrupted_state(mock_task)
        self.assertTrue(result)

    def test_is_in_terminal_or_interrupted_state_unknown(self):
        """Test is_in_terminal_or_interrupted_state returns True for unknown state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.unknown
        
        result = is_in_terminal_or_interrupted_state(mock_task)
        self.assertTrue(result)

    def test_is_in_terminal_or_interrupted_state_completed(self):
        """Test is_in_terminal_or_interrupted_state returns True for terminal states."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.completed
        
        result = is_in_terminal_or_interrupted_state(mock_task)
        self.assertTrue(result)

    def test_is_in_terminal_or_interrupted_state_running(self):
        """Test is_in_terminal_or_interrupted_state returns False for running state."""
        mock_task = MagicMock(spec=Task)
        mock_task.status = MagicMock(spec=TaskStatus)
        mock_task.status.state = TaskState.working
        
        result = is_in_terminal_or_interrupted_state(mock_task)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
