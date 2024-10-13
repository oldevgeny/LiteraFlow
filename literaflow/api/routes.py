from aiohttp import web

from literaflow.api.v1 import books


def setup_routes(app: web.Application) -> None:
    """Set up application routes."""
    app.add_routes(books.routes)
