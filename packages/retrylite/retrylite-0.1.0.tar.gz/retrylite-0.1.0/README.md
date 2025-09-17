# retrylite

[![CI](https://github.com/moehandi/retrylite/actions/workflows/ci.yml/badge.svg)](https://github.com/moehandi/retrylite/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/moehandi/retrylite/branch/main/graph/badge.svg)](https://codecov.io/gh/moehandi/retrylite)
[![PyPI version](https://badge.fury.io/py/retrylite.svg)](https://badge.fury.io/py/retrylite)
[![Python versions](https://img.shields.io/pypi/pyversions/retrylite.svg)](https://pypi.org/project/retrylite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/deps-none-success.svg)](https://github.com/moehandi/retrylite)

Zero-dependency retry decorator for Python (sync & async) with circuit-breaker, retry-after, and full type safety.

## Features
- Zero runtime dependencies – <b>only std-lib</b>.
- Sync & Async support. 
- Exponential backoff & full jitter.
- Circuit-breaker support.  
- Respects Retry-After header.  
- Test coverage & mypy strict. 
- PyPI wheel <b>&lt; 10 kB</b>.

## Installation
```bash
pip install retrylite
```

## Quick Start

### Synchronous

```python
from retrylite import retry
import requests

@retry(max_attempts=3, backoff=1.5)
def fetch(url):
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    return resp.json()

try:
    data = fetch("https://httpbin.org/json")
except requests.HTTPError:
    print("Final failure after 3 retries")
```

### Asynchronous

```python
import aiohttp
from retrylite import aretry

@aretry(max_attempts=3, backoff=1.5)
async def fetch(url):
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

html = asyncio.run(fetch("https://httpbin.org/json"))
```
### Advanced

### Circuit-breaker
```python
from retrylite import retry

@retry(break_on=(ValueError,))
def risky():
    raise ValueError("permanent")  # no retry
```

### Retry-After header
```python
from retrylite import retry
import requests

@retry(retry_after=True)
def api_call():
    resp = requests.get(url)
    resp.raise_for_status()  # respects 503 + Retry-After
```

### Sample:
```python
import time
import requests
import aiohttp
import asyncio
from retrylite import retry, aretry

# 1. Sync retry ---------------------------------
print("=== Sync Retry ===")
calls = 0

@retry(max_attempts=3, backoff=0.5, retry_after=True)
def fetch_sync(url: str) -> str:
    global calls
    calls += 1
    print(f"[Sync] attempt {calls}")
    resp = requests.get(url, timeout=3)
    resp.raise_for_status()
    return resp.text

try:
    html = fetch_sync("https://httpbin.org/status/503")
except requests.HTTPError:
    print("[Sync] Final failure (expected)")
print(f"[Sync] Total calls: {calls}\n")

# 2. Async retry --------------------------------
print("=== Async Retry ===")
calls = 0

@aretry(max_attempts=3, backoff=0.5, retry_after=True)
async def fetch_async(url: str) -> str:
    global calls
    calls += 1
    print(f"[Async] attempt {calls}")
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

try:
    html = asyncio.run(fetch_async("https://httpbin.org/status/503"))
except aiohttp.ClientResponseError:
    print("[Async] Final failure (expected)")
print(f"[Async] Total calls: {calls}\n")

# 3. Circuit-breaker demo ----------------------
print("=== Circuit-Breaker Demo ===")

@retry(max_attempts=5, break_on=(ValueError,), backoff=0.1)
def always_fail():
    raise ValueError("permanent")

try:
    always_fail()
except ValueError as e:
    print(f"[Circuit] Immediately raised: {e} (no retry)")
```

### Development
```sh
git clone https://github.com/moehandi/retrylite.git
cd retrylite
poetry install
poetry run pre-commit install
poetry run pytest --cov
poetry build
```

### License

MIT - see [LICENSE](LICENSE)