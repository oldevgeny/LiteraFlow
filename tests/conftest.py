import asyncio
import typing
from collections.abc import Callable

import pytest
from aiohttp.test_utils import TestClient

from literaflow import utils


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client(aiohttp_client: Callable[..., typing.Any]) -> TestClient:
    """Create a test client for the application."""
    app = utils.create_app()
    return await aiohttp_client(app)
