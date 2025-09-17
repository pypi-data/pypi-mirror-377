"""
Asynchronous retry decorator with zero dependencies.
Compatible with mypy --strict.
Author: M. Andi Saputra <moehandi@gmail.com>
"""

import asyncio
import email.utils
import functools
import logging
import random
import time
from typing import Any, Callable, Coroutine, Optional, Tuple, Type, TypeVar

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


def aretry(
    max_attempts: int = 3,
    backoff: float = 1.0,
    jitter: bool = True,
    max_sleep: float = 300,
    retry_after: bool = False,
    break_on: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable[
    [Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]
]:
    """
    Asynchronous retry decorator.

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
    Decorated async function that retries on failure.

    Examples
    --------
    >>> @aretry(max_attempts=5, backoff=2.0)
    ... async def fetch(url):
    ...     async with aiohttp.ClientSession() as s:
    ...         async with s.get(url) as resp:
    ...             resp.raise_for_status()
    ...             return await resp.text()
    """
    _break: Tuple[Type[Exception], ...] = break_on or ()

    def deco(
        func: Callable[..., Coroutine[Any, Any, T]]
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
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
                    log.info("async sleeping %.1fs before retry", sleep_sec)
                    await asyncio.sleep(sleep_sec)
            # Unreachable but required for mypy --strict
            raise RuntimeError("Unreachable")

        return wrapper

    return deco
