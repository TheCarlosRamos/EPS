"""Integration tests for DLQ against real Redis."""

import pytest

from src.queue.dlq import DLQManager


@pytest.mark.integration
class TestDLQRealRedis:
    def test_send_and_retrieve(self, redis_client):
        dlq = DLQManager(redis_client)
        entry_id = dlq.send_to_dlq(
            task_name="real_scraper",
            task_id="real-123",
            args=["query"],
            kwargs={"source": "portal"},
            exception="ConnectionError: timeout",
        )
        entries = dlq.list_dlq()
        assert len(entries) == 1
        assert entries[0]["id"] == entry_id
        assert entries[0]["task_name"] == "real_scraper"

    def test_purge_clears_all(self, redis_client):
        dlq = DLQManager(redis_client)
        dlq.send_to_dlq("t1", "id1", [], {}, "err")
        dlq.send_to_dlq("t2", "id2", [], {}, "err")
        count = dlq.purge()
        assert count == 2
        assert dlq.count() == 0

    def test_multiple_entries_ordering(self, redis_client):
        dlq = DLQManager(redis_client)
        dlq.send_to_dlq("first", "id1", [], {}, "err")
        dlq.send_to_dlq("second", "id2", [], {}, "err")
        dlq.send_to_dlq("third", "id3", [], {}, "err")
        entries = dlq.list_dlq()
        assert entries[0]["task_name"] == "third"  # LPUSH: newest first
        assert entries[2]["task_name"] == "first"
