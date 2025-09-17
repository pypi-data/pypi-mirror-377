import time

import pytest
import requests
import responses
from retrylite import retry


def test_success():
    @retry()
    def ok() -> int:
        return 42

    assert ok() == 42


def test_retries_exhausted(resp_mock):
    attempts = 0
    resp_mock.add(responses.GET, "http://test/fail", status=500)

    @retry(max_attempts=3, backoff=0.001)
    def get():
        nonlocal attempts
        attempts += 1
        resp = requests.get("http://test/fail")
        resp.raise_for_status()

    with pytest.raises(requests.HTTPError):
        get()
    assert attempts == 3


def test_circuit_breaker():
    class Fatal(Exception):
        pass

    calls = 0

    @retry(max_attempts=5, break_on=(Fatal,), backoff=0.001)
    def fail():
        nonlocal calls
        calls += 1
        raise Fatal("boom")

    with pytest.raises(Fatal):
        fail()
    assert calls == 1  # no retry


@responses.activate
def test_retry_after_header_seconds():
    # 1. Register mock
    responses.add(
        responses.GET,
        "http://test/retry",  # URL Full
        status=503,
        headers={"Retry-After": "0.5"},
    )

    # 2. Identic call
    start = time.perf_counter()

    @retry(max_attempts=2, retry_after=True, backoff=0.001)
    def get():
        requests.get("http://test/retry").raise_for_status()  # sama persis

    with pytest.raises(requests.HTTPError):
        get()

    elapsed = time.perf_counter() - start
    assert 0.4 < elapsed < 0.7


@responses.activate
def test_sync_retry_after_float():
    """Cover retry-after float branch (sync mirror)."""

    calls = 0
    start = time.perf_counter()

    # mock response with header float
    class FakeResp:
        headers = {"Retry-After": "0.25"}

    @retry(max_attempts=2, retry_after=True, backoff=0.001)
    def get():
        nonlocal calls
        calls += 1
        e = RuntimeError("boom")
        e.response = FakeResp()  # type: ignore
        raise e

    with pytest.raises(RuntimeError):
        get()
    elapsed = time.perf_counter() - start
    assert calls == 2
    assert 0.15 < elapsed < 0.5  # ⬅ toleran 0.15 s


@responses.activate
def test_sync_retry_after_float_branch():
    import time

    calls = 0
    start = time.perf_counter()

    # string float will enter float path
    class FakeResp:
        headers = {"Retry-After": "0.21"}  # float string

    @retry(max_attempts=2, retry_after=True, backoff=0.001)
    def get():
        nonlocal calls
        calls += 1
        e = RuntimeError("boom")
        e.response = FakeResp()  # type: ignore
        raise e

    with pytest.raises(RuntimeError):
        get()

    elapsed = time.perf_counter() - start
    assert calls == 2
    assert 0.15 < elapsed < 0.5  # ⬅ toleran 0.15 s


def test_sync_unreachable_final():
    """Cover unreachable raise di akhir loop (sync mirror)."""

    @retry(max_attempts=1, break_on=(ValueError,), backoff=0.001)
    def fail():
        raise RuntimeError("boom")  # not ValueError → enter retry

    with pytest.raises(RuntimeError):
        fail()


def test_sync_unreachable_final_cover():
    """Cover unreachable raise at end of loop."""

    @retry(max_attempts=1, break_on=(ValueError,), backoff=0.001)
    def fail():
        raise RuntimeError("boom")  # not ValueError → loop end

    with pytest.raises(RuntimeError, match="boom"):
        fail()
    # ➜ unreachable line 72 covered


def test_sync_break_on_exact_exception():
    """Cover 'except break_on:' branch."""
    calls = 0

    @retry(max_attempts=5, break_on=(ValueError,), backoff=0.001)
    def fail():
        nonlocal calls
        calls += 1
        raise ValueError("in break_on")  # ➜ enter line 21

    with pytest.raises(ValueError):
        fail()
    assert calls == 1  # no retry


@responses.activate
def test_break_on_exact_exception_sync():
    calls = 0

    @retry(max_attempts=5, break_on=(ValueError,), backoff=0.001)
    def fail():
        nonlocal calls
        calls += 1
        raise ValueError("in break_on")

    with pytest.raises(ValueError):
        fail()
    assert calls == 1


@responses.activate
def test_sync_retry_after_http_date():
    import time

    calls = 0
    start = time.perf_counter()

    # ⭐ register on BOTH attempts (not just first)
    responses.add(
        responses.GET, "http://test", status=503, headers={"Retry-After": "1.0"}
    )
    responses.add(
        responses.GET, "http://test", status=503, headers={"Retry-After": "1.0"}
    )

    @retry(max_attempts=2, retry_after=True, backoff=0.001)
    def get():
        nonlocal calls
        calls += 1
        resp = requests.get("http://test")
        resp.raise_for_status()

    with pytest.raises(requests.HTTPError):
        get()
    elapsed = time.perf_counter() - start
    assert calls == 2
    assert elapsed > 0.8  # ⬅ at least first 1.0 s sleep


@responses.activate
def test_sync_retry_after_float_all_attempts():
    """Cover float branch & sleep on every retry."""
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

    @retry(max_attempts=2, retry_after=True, backoff=0.001)
    def get():
        nonlocal calls
        calls += 1
        resp = requests.get("http://test")
        resp.raise_for_status()

    with pytest.raises(requests.HTTPError):
        get()
    elapsed = time.perf_counter() - start
    assert calls == 2
    assert elapsed > 0.8  # ⬅ at least first 1.0 s sleep


def test_sync_on_retry_callback():
    calls = []

    def my_hook(exc, attempt):
        calls.append((type(exc).__name__, attempt))

    @retry(max_attempts=2, backoff=0.001, on_retry=my_hook)
    def fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        fail()
    assert calls == [("RuntimeError", 1), ("RuntimeError", 2)]


def test_sync_keyboard_interrupt():

    calls = 0

    @retry(max_attempts=3, backoff=0.1)
    def fail():
        nonlocal calls
        calls += 1
        if calls == 2:
            raise KeyboardInterrupt  # ➜ line 68-72 covered
        raise RuntimeError("boom")

    with pytest.raises(KeyboardInterrupt):
        fail()
    assert calls == 2
