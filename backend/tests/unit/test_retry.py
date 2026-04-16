"""Tests for exponential backoff retry policy."""

import pytest

from src.queue.retry import MAX_RETRIES, RETRY_DELAYS, get_retry_delay


@pytest.mark.unit
class TestRetryPolicy:
    def test_first_retry_delay(self):
        assert get_retry_delay(0) == 60

    def test_second_retry_delay(self):
        assert get_retry_delay(1) == 300

    def test_third_retry_delay(self):
        assert get_retry_delay(2) == 900

    def test_clamps_beyond_max(self):
        """Retries beyond the list length should use the last delay."""
        assert get_retry_delay(99) == 900
        assert get_retry_delay(3) == 900

    def test_retry_delays_are_increasing(self):
        for i in range(len(RETRY_DELAYS) - 1):
            assert RETRY_DELAYS[i] < RETRY_DELAYS[i + 1]

    def test_max_retries_matches_delays(self):
        assert MAX_RETRIES == len(RETRY_DELAYS)

    def test_delays_match_issue_spec(self):
        """Issue #25 specifies 60s/300s/900s delays."""
        assert RETRY_DELAYS == [60, 300, 900]
