from aiohttp import web
from aiohttp.web_request import Request

import literaflow.services.exceptions as s_exceptions
from literaflow.core import dto, logger
from literaflow.services.book import BookService
from literaflow.services.denied_list import DeniedListService
from literaflow.utils import http_statuses
from literaflow.utils.denied_books_parser import (
    parse_denied_books,
)

routes = web.RouteTableDef()


@routes.post("/v1/books")
async def create_book(request: Request) -> web.Response:
    """Endpoint to create a new book."""
    if not request.body_exists:
        raise web.HTTPBadRequest(reason="No request body provided")

    try:
        body = await request.json()
    except Exception as exc:
        raise web.HTTPBadRequest(reason="Invalid JSON body") from exc

    book_dto: dto.Book
    book_dto, errors = dto.create_dto_safely(dto.Book, **body)

    if errors:
        return web.json_response(
            {"errors": errors}, status=http_statuses.HTTP_400_BAD_REQUEST
        )

    book_service = BookService()

    try:
        book_model = await book_service.create_book(book_dto=book_dto)
    except s_exceptions.BookDownloadError:
        return web.json_response(
            {"error": "Failed to download book file"},
            status=http_statuses.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except s_exceptions.BookAlreadyExistsError:
        return web.json_response(
            {"error": "Book already exists"},
            status=http_statuses.HTTP_409_CONFLICT,
        )

    return web.json_response(
        book_model.to_dict(), status=http_statuses.HTTP_201_CREATED
    )


@routes.get("/v1/books")
async def get_books(request: Request) -> web.Response:
    """Endpoint to retrieve books based on query parameters."""
    query_params = dict(request.query)

    boot_filters_dto: dto.BookFilters
    boot_filters_dto, errors = dto.create_dto_safely(dto.BookFilters, **query_params)

    if errors:
        return web.json_response(
            {"errors": errors}, status=http_statuses.HTTP_400_BAD_REQUEST
        )

    book_service = BookService()
    books = await book_service.get_books(filters_dto=boot_filters_dto)
    return web.json_response([book.to_dict() for book in books])


@routes.get("/v1/books/{book_id}")
async def get_book(request: Request) -> web.Response:
    """Endpoint to retrieve a book by ID."""
    raw_book_id = request.match_info["book_id"]
    book_id = int(raw_book_id) if raw_book_id.isdigit() else None

    if book_id is None:
        return web.json_response(
            {"error": "Invalid book ID"}, status=http_statuses.HTTP_400_BAD_REQUEST
        )

    book_service = BookService()
    book = await book_service.get_book_by_id(book_id)
    if book is None:
        return web.json_response(
            {"error": "Book not found"}, status=http_statuses.HTTP_404_NOT_FOUND
        )

    return web.json_response(book.to_dict())


@routes.get("/v1/books/{book_id}/download")
async def download_book(request: Request) -> web.FileResponse | web.Response:
    """Endpoint to download a book file."""
    book_id = int(request.match_info["book_id"])
    book_service = BookService()
    book = await book_service.get_book_by_id(book_id)
    if book is None:
        return web.json_response(
            {"error": "Book not found"}, status=http_statuses.HTTP_404_NOT_FOUND
        )
    if book.is_denied:
        return web.json_response(
            {"error": "Book is denied for download"},
            status=http_statuses.HTTP_403_FORBIDDEN,
        )
    if not book.file_path:
        return web.json_response(
            {"error": "Book file not found"}, status=http_statuses.HTTP_404_NOT_FOUND
        )
    return web.FileResponse(path=book.file_path)


@routes.post("/v1/books/deny")
async def upload_denied_books(request: Request) -> web.Response:
    """Endpoint to upload and process denied books list."""
    reader = await request.multipart()
    field = await reader.next()

    if field.name != "file":
        return web.json_response(
            {"error": "Expected a file upload"},
            status=http_statuses.HTTP_400_BAD_REQUEST,
        )
    data = await field.read()

    try:
        denied_books = parse_denied_books(data)
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Failed to parse the denied books file: {exc}")
        return web.json_response(
            {"error": "Failed to parse the denied books file"},
            status=http_statuses.HTTP_400_BAD_REQUEST,
        )

    denied_list_service = DeniedListService()
    await denied_list_service.update_denied_books(denied_books)
    return web.json_response({"message": "Denied books updated"})
