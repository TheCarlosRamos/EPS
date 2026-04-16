"""Tests for Dead Letter Queue manager using fakeredis."""

import pytest
from fakeredis import FakeRedis

from src.queue.dlq import DLQ_KEY, DLQManager


@pytest.fixture
def dlq(fake_redis: FakeRedis) -> DLQManager:
    return DLQManager(fake_redis)


@pytest.mark.unit
class TestDLQManager:
    def test_send_to_dlq(self, dlq, fake_redis):
        entry_id = dlq.send_to_dlq(
            task_name="test_task",
            task_id="abc-123",
            args=["arg1"],
            kwargs={"key": "value"},
            exception="ValueError: something went wrong",
        )
        assert entry_id is not None
        assert fake_redis.llen(DLQ_KEY) == 1

    def test_list_dlq_empty(self, dlq):
        entries = dlq.list_dlq()
        assert entries == []

    def test_list_dlq_returns_entries(self, dlq):
        dlq.send_to_dlq("task1", "id1", [], {}, "error1")
        dlq.send_to_dlq("task2", "id2", [], {}, "error2")
        entries = dlq.list_dlq()
        assert len(entries) == 2
        assert entries[0]["task_name"] == "task2"  # LPUSH: newest first
        assert entries[1]["task_name"] == "task1"

    def test_list_dlq_pagination(self, dlq):
        for i in range(5):
            dlq.send_to_dlq(f"task{i}", f"id{i}", [], {}, f"error{i}")

        page = dlq.list_dlq(limit=2, offset=0)
        assert len(page) == 2

        page2 = dlq.list_dlq(limit=2, offset=2)
        assert len(page2) == 2

    def test_count(self, dlq):
        assert dlq.count() == 0
        dlq.send_to_dlq("task1", "id1", [], {}, "error")
        assert dlq.count() == 1
        dlq.send_to_dlq("task2", "id2", [], {}, "error")
        assert dlq.count() == 2

    def test_get_entry_found(self, dlq):
        entry_id = dlq.send_to_dlq("task1", "id1", ["a"], {"b": "c"}, "err")
        entry = dlq.get_entry(entry_id)
        assert entry is not None
        assert entry["task_name"] == "task1"
        assert entry["args"] == ["a"]
        assert entry["kwargs"] == {"b": "c"}
        assert entry["exception"] == "err"
        assert "timestamp" in entry

    def test_get_entry_not_found(self, dlq):
        assert dlq.get_entry("nonexistent") is None

    def test_purge(self, dlq, fake_redis):
        dlq.send_to_dlq("task1", "id1", [], {}, "error")
        dlq.send_to_dlq("task2", "id2", [], {}, "error")
        count = dlq.purge()
        assert count == 2
        assert dlq.count() == 0
        assert fake_redis.llen(DLQ_KEY) == 0

    def test_purge_empty(self, dlq):
        count = dlq.purge()
        assert count == 0

    def test_entry_contains_required_fields(self, dlq):
        dlq.send_to_dlq("my_task", "task-uuid", [1, 2], {"k": "v"}, "RuntimeError")
        entry = dlq.list_dlq()[0]
        assert "id" in entry
        assert "task_name" in entry
        assert "task_id" in entry
        assert "args" in entry
        assert "kwargs" in entry
        assert "exception" in entry
        assert "timestamp" in entry

    def test_replay_removes_entry(self, dlq):
        """After replay, the entry should be removed from the DLQ."""
        from unittest.mock import MagicMock

        entry_id = dlq.send_to_dlq("task1", "id1", ["arg"], {}, "error")
        assert dlq.count() == 1

        mock_app = MagicMock()
        mock_app.send_task.return_value.id = "new-task-id"

        new_id = dlq.replay_task(entry_id, celery_app=mock_app)
        assert new_id == "new-task-id"
        assert dlq.count() == 0
        mock_app.send_task.assert_called_once_with("task1", args=["arg"], kwargs={})

    def test_replay_nonexistent_returns_none(self, dlq):
        from unittest.mock import MagicMock

        mock_app = MagicMock()
        result = dlq.replay_task("nonexistent", celery_app=mock_app)
        assert result is None
        mock_app.send_task.assert_not_called()
