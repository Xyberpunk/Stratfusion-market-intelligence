from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter

T = TypeVar("T")


def async_retry(max_attempts: int) -> Callable[[Callable[..., T]], Callable[..., T]]:
    return retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential_jitter(initial=1, max=60),
        stop=stop_after_attempt(max_attempts),
        reraise=True,
    )
