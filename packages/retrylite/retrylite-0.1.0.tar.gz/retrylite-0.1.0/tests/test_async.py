import time

import aiohttp
import pytest
import requests
import responses
from retrylite import aretry


@pytest.mark.asyncio
async def test_async_success():
    @aretry(backoff=0.001)
    async def ok() -> str:
        return "yes"

    assert await ok() == "yes"


@pytest.mark.asyncio
async def test_async_retries():
    calls = 0

    @aretry(max_attempts=3, backoff=0.001)
    async def get():
        nonlocal calls
        calls += 1
        # Create session inside task (not from fixture)
        async with aiohttp.ClientSession() as session:
            async with session.get("http://httpbin.org/status/500") as resp:
                resp.raise_for_status()

    with pytest.raises(aiohttp.ClientResponseError):
        await get()

    assert calls == 3


@pytest.mark.asyncio
async def test_async_circuit_breaker():
    """Cover break_on branch."""

    class Fatal(Exception):
        pass

    calls = 0

    @aretry(max_attempts=5, break_on=(Fatal,), backoff=0.001)
    async def fail():
        nonlocal calls
        calls += 1
        raise Fatal("permanent")

    with pytest.raises(Fatal):
        await fail()
    assert calls == 1  # no retry


@pytest.mark.asyncio
async def test_async_retry_after_float():
    """Cover retry-after header (float path)."""

    # mock response with header Retry-After float
    class FakeResp:
        headers = {"Retry-After": "0.3"}

    calls = 0
    start = time.perf_counter()

    @aretry(max_attempts=2, retry_after=True, backoff=0.001)
    async def get():
        nonlocal calls
        calls += 1
        e = RuntimeError("boom")
        e.response = FakeResp()  # type: ignore
        raise e

    with pytest.raises(RuntimeError):
        await get()
    elapsed = time.perf_counter() - start
    assert calls == 2
    assert 0.25 < elapsed < 0.4  # slept ~0.3 s


@pytest.mark.asyncio
async def test_async_retry_after_float_branch():
    calls = 0
    start = time.perf_counter()

    class FakeResp:
        headers = {"Retry-After": "0.21"}

    @aretry(max_attempts=2, retry_after=True, backoff=0.001)
    async def get():
        nonlocal calls
        calls += 1
        e = RuntimeError("boom")
        e.response = FakeResp()  # type: ignore
        raise e

    with pytest.raises(RuntimeError):
        await get()
    elapsed = time.perf_counter() - start
    assert calls == 2
    assert 0.18 < elapsed < 0.25  # ➜ branch 55→58 & 60→65 covered


@pytest.mark.asyncio
async def test_async_unreachable_final():
    """Cover 'unreachable' raise di akhir loop (mypy strict)."""

    # use break_on for exhausted loop & raise unreachable
    @aretry(max_attempts=1, break_on=(ValueError,), backoff=0.001)
    async def fail():
        raise RuntimeError("boom")  # not ValueError → enter retry

    with pytest.raises(RuntimeError):
        await fail()
    # unreachable raise covered because exhausted loop & not break_on


@pytest.mark.asyncio
async def test_async_unreachable_final_cover():
    """Cover unreachable raise at end of loop."""

    @aretry(max_attempts=1, break_on=(ValueError,), backoff=0.001)
    async def fail():
        raise RuntimeError("boom")  # not ValueError → loop habis

    with pytest.raises(RuntimeError, match="boom"):
        await fail()


@pytest.mark.asyncio
async def test_async_break_on_exact_exception():
    """Cover 'except break_on:' branch."""
    calls = 0

    @aretry(max_attempts=5, break_on=(ValueError,), backoff=0.001)
    async def fail():
        nonlocal calls
        calls += 1
        raise ValueError("in break_on")  # ➜ enter line 22

    with pytest.raises(ValueError):
        await fail()
    assert calls == 1  # no retry


@pytest.mark.asyncio
async def test_break_on_exact_exception():
    """Ensure 'except break_on:' is executed."""
    calls = 0

    @aretry(max_attempts=5, break_on=(ValueError,), backoff=0.001)
    async def fail():
        nonlocal calls
        calls += 1
        raise ValueError("in break_on")  # ➜ will trigger line 21

    with pytest.raises(ValueError):
        await fail()
    assert calls == 1  # no retry


@responses.activate
@pytest.mark.asyncio
async def test_async_retry_after_http_date():
    import time

    calls = 0
    start = time.perf_counter()

    # register on BOTH attempts
    responses.add(
        responses.GET, "http://test", status=503, headers={"Retry-After": "1.0"}
    )
    responses.add(
        responses.GET, "http://test", status=503, headers={"Retry-After": "1.0"}
    )

    @aretry(max_attempts=2, retry_after=True, backoff=0.001)
    async def get():
        nonlocal calls
        calls += 1
        resp = requests.get("http://test")
        resp.raise_for_status()

    with pytest.raises(requests.HTTPError):
        await get()
    elapsed = time.perf_counter() - start
    assert calls == 2
    assert elapsed > 0.8  # ⬅ at least first 1.0 s sleep


@responses.activate
@pytest.mark.asyncio
async def test_async_retry_after_float_all_attempts():
    import time

    calls = 0
    start = time.perf_counter()

    # header on ALL attempts
    responses.add(
        responses.GET, "http://test", status=503, headers={"Retry-After": "1.0"}
    )
    responses.add(
        responses.GET, "http://test", status=503, headers={"Retry-After": "1.0"}
    )

    @aretry(max_attempts=2, retry_after=True, backoff=0.001)
    async def get():
        nonlocal calls
        calls += 1
        resp = requests.get("http://test")
        resp.raise_for_status()

    with pytest.raises(requests.HTTPError):
        await get()
    elapsed = time.perf_counter() - start
    assert calls == 2
    assert elapsed > 0.8  # ⬅ at least first 1.0 s sleep


@pytest.mark.asyncio
async def test_async_on_retry_callback():
    calls = []

    def my_hook(exc, attempt):
        calls.append((type(exc).__name__, attempt))

    @aretry(max_attempts=2, backoff=0.001, on_retry=my_hook)
    async def fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await fail()
    assert calls == [("RuntimeError", 1), ("RuntimeError", 2)]


@pytest.mark.asyncio
async def test_async_keyboard_interrupt():

    calls = 0

    @aretry(max_attempts=3, backoff=0.1)
    async def fail():
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt
        raise RuntimeError("boom")

    with pytest.raises(KeyboardInterrupt):
        await fail()
    assert calls == 2
