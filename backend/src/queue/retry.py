"""Exponential backoff retry policy for Celery tasks.

Delays: 60s -> 300s -> 900s (max 3 retries as specified in Issue #25).
"""

RETRY_DELAYS: list[int] = [60, 300, 900]
MAX_RETRIES: int = 3


def get_retry_delay(retries: int) -> int:
    """Return the delay in seconds for the given retry attempt.

    Clamps to the last delay value if retries exceeds the list length.
    """
    index = min(retries, len(RETRY_DELAYS) - 1)
    return RETRY_DELAYS[index]
