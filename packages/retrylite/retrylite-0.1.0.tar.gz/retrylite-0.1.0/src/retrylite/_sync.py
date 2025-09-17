"""
Synchronous retry decorator with zero dependencies.
Compatible with mypy --strict.
Author: M. Andi Saputra <moehandi@gmail.com>
"""

import email.utils
import functools
import logging
import random
import time
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, cast

log = logging.getLogger(__name__)

T = TypeVar("T")


def _parse_retry_after(value: str) -> float:
    """Convert Retry-After header (seconds or HTTP-date) → float seconds."""
    try:
        return int(value)
    except ValueError:
        pass
    try:
        ts = email.utils.parsedate_to_datetime(value).timestamp()
        return max(0, ts - time.time())
    except (TypeError, ValueError):
        return float(value)


def retry(
    max_attempts: int = 3,
    backoff: float = 1.0,
    jitter: bool = True,
    max_sleep: float = 300,
    retry_after: bool = False,
    break_on: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Synchronous retry decorator.

    Parameters
    ----------
    max_attempts   : total tries (first + retries)
    backoff        : base sleep multiplier (seconds)
    jitter         : add random 0.5-1.0 multiplier
    max_sleep      : cap sleep time
    retry_after    : respect Retry-After header if exception has `.response.headers`
    break_on       : tuple of exceptions → immediately re-raise without retry
    on_retry       : callback(exc, attempt) for metrics / logging

    Returns
    -------
    Decorated function that retries on failure.

    Examples
    --------
    >>> @retry(max_attempts=5, backoff=2.0)
    ... def fetch(url):
    ...     resp = requests.get(url)
    ...     resp.raise_for_status()
    ...     return resp.json()
    """
    _break: Tuple[Type[Exception], ...] = break_on or ()

    def deco(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except _break:
                    raise
                except Exception as exc:
                    if on_retry:
                        on_retry(exc, attempt)
                    log.warning(
                        "%s: %s  (attempt %s/%s)",
                        type(exc).__name__,
                        exc,
                        attempt,
                        max_attempts,
                    )
                    if attempt == max_attempts:
                        raise

                    sleep_sec = backoff * (2 ** (attempt - 1))
                    if jitter:
                        sleep_sec *= random.uniform(0.5, 1.0)

                    if retry_after:
                        resp = getattr(exc, "response", None)
                        if resp is not None:
                            retry_after_hdr = resp.headers.get("Retry-After")
                            if retry_after_hdr:
                                sleep_sec = _parse_retry_after(retry_after_hdr)

                    sleep_sec = min(sleep_sec, max_sleep)
                    log.info("sleeping %.1fs before retry", sleep_sec)
                    try:
                        time.sleep(sleep_sec)
                    except KeyboardInterrupt:
                        log.warning("KeyboardInterrupt – aborting retry")
                        raise
            # Unreachable but required for mypy --strict
            return cast(T, None)

        return wrapper

    return deco
