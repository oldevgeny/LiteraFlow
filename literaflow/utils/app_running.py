import typing

import aiohttp
import aiohttp_cors

from literaflow.api.routes import setup_routes
from literaflow.core.db import create_tables

OnStartUpArgs = typing.Any


async def setup_database(*_: OnStartUpArgs) -> None:
    """Set up the database."""
    await create_tables()


def create_app() -> aiohttp.web.Application:
    """Create the application."""
    app = aiohttp.web.Application()
    setup_routes(app)

    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )
    for route in list(app.router.routes()):
        cors.add(route)

    app.on_startup.append(setup_database)
    return app
