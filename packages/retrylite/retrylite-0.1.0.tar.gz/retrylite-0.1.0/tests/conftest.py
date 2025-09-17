from collections.abc import Generator

import pytest
import responses


@pytest.fixture
def resp_mock() -> Generator[responses.RequestsMock, None, None]:
    with responses.RequestsMock() as rsps:
        yield rsps
