import io
import random

import pandas as pd
import pytest
from aiohttp import FormData
from aiohttp.test_utils import TestClient
from faker import Faker

from literaflow.utils import http_statuses

fake = Faker()


EXTERNAL_BOOKS_URLS = [
    "https://oldevgeny.github.io/cv/CV_Evgenii_Andreev.pdf",
    "http://flibusta.site/b/300929/epub",
    "http://flibusta.site/b/70332/fb2",
    "http://flibusta.site/b/138887/epub",
]


def get_fake_book_name() -> str:
    """Generate a fake book name."""
    return fake.sentence(nb_words=4)


def get_fake_author_name() -> str:
    """Generate a fake author name."""
    return fake.name()


def get_fake_date_published() -> str:
    """Generate a fake date published."""
    return fake.date()


def get_fake_genre() -> str:
    """Generate a fake genre."""
    return fake.word()


def get_real_external_file_url() -> str:
    """Generate a real external file URL."""
    return random.choice(EXTERNAL_BOOKS_URLS)  # noqa: S311


@pytest.fixture
def fake_book_data():
    """Generate fake book data."""
    return {
        "name": get_fake_book_name(),
        "author": get_fake_author_name(),
        "date_published": get_fake_date_published(),
        "genre": get_fake_genre(),
        "file_path": None,
    }


@pytest.mark.asyncio
async def test_create_book_without_url(client: TestClient, fake_book_data: dict):
    """Test creating a new book."""
    response = await client.post("/v1/books", json=fake_book_data)
    assert response.status == http_statuses.HTTP_201_CREATED
    data = await response.json()
    assert data["name"] == fake_book_data["name"]


@pytest.mark.asyncio
async def test_get_books(client: TestClient):
    """Test retrieving the list of books."""
    response = await client.get("/v1/books")
    assert response.status == http_statuses.HTTP_200_OK
    data = await response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_book_by_id(client: TestClient, fake_book_data: dict):
    """Test retrieving a book by ID."""
    # Create a book
    create_response = await client.post("/v1/books", json=fake_book_data)
    assert create_response.status == http_statuses.HTTP_201_CREATED
    book = await create_response.json()
    book_id = book["id"]

    # Retrieve the book
    get_response = await client.get(f"/v1/books/{book_id}")
    assert get_response.status == http_statuses.HTTP_200_OK
    retrieved_book = await get_response.json()
    assert retrieved_book["id"] == book_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_data",
    [
        {
            "name": "",
            "author": get_fake_author_name(),
            "date_published": get_fake_genre(),
        },
        {
            "name": get_fake_book_name(),
            "author": "",
            "date_published": get_fake_genre(),
        },
        {
            "name": get_fake_book_name(),
            "author": get_fake_author_name(),
            "date_published": "invalid-date",
        },
        {"name": "", "author": get_fake_author_name(), "": get_fake_genre()},
        {"name": "", "author": "", "date_published": get_fake_genre()},
        {"name": get_fake_book_name(), "author": "", "date_published": "invalid-date"},
        {"name": "", "author": "", "date_published": ""},
    ],
)
async def test_create_book_invalid_required_data(
    client: TestClient, invalid_data: dict
):
    """Test creating a book with invalid data."""
    response = await client.post("/v1/books", json=invalid_data)
    assert response.status == http_statuses.HTTP_400_BAD_REQUEST
    data = await response.json()
    assert "errors" in data


@pytest.mark.asyncio
async def test_upload_denied_books(client: TestClient):
    """Test uploading a denied books list via file upload."""
    # Create a book that might be denied
    book_data = {
        "name": fake.sentence(nb_words=4),
        "author": fake.name(),
        "date_published": fake.date(),
        "genre": fake.word(),
    }
    create_response = await client.post("/v1/books", json=book_data)
    assert create_response.status == http_statuses.HTTP_201_CREATED
    book = await create_response.json()

    # Prepare the denied books Excel file
    names_df = pd.DataFrame({"name": [book_data["name"]]})
    authors_df = pd.DataFrame({"author": [book_data["author"]]})

    # Do not use 'with' statement for BytesIO
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        names_df.to_excel(writer, sheet_name="name", index=False)
        authors_df.to_excel(writer, sheet_name="author", index=False)
    # Ensure all data is written to the buffer
    buffer.seek(0)
    excel_content = buffer.getvalue()

    # Simulate the file upload using FormData
    form = FormData()
    form.add_field(
        "file",
        excel_content,
        filename="denied_books.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Upload the denied books list
    response = await client.post("/v1/books/deny", data=form)
    assert response.status == http_statuses.HTTP_200_OK
    data = await response.json()
    assert data["message"] == "Denied books updated"

    # Check if the book is now denied
    get_response = await client.get(f"/v1/books/{book["id"]}")
    assert get_response.status == http_statuses.HTTP_200_OK
    updated_book = await get_response.json()
    assert updated_book["is_denied"] is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "valid_data",
    [
        {
            "name": get_fake_book_name(),
            "author": get_fake_author_name(),
            "date_published": get_fake_date_published(),
            "genre": get_fake_genre(),
            "url": None,
            "is_file_path": False,
        },
        {
            "name": get_fake_book_name(),
            "author": get_fake_author_name(),
            "date_published": get_fake_date_published(),
            "genre": "",
            "url": get_real_external_file_url(),
            "is_file_path": True,
        },
        {
            "name": get_fake_book_name(),
            "author": get_fake_author_name(),
            "date_published": get_fake_date_published(),
            "genre": get_fake_genre(),
            "url": get_real_external_file_url(),
            "is_file_path": True,
        },
    ],
)
async def test_create_book_with_valid_data(client: TestClient, valid_data: dict):
    """Test creating a book with valid data."""
    response = await client.post("/v1/books", json=valid_data)
    assert response.status == http_statuses.HTTP_201_CREATED
    data = await response.json()
    assert data["name"] == valid_data["name"]
    assert data["author"] == valid_data["author"]
    assert data["date_published"] == valid_data["date_published"]
    assert data["genre"] == valid_data["genre"]
    assert bool(data["file_path"]) is valid_data["is_file_path"]


@pytest.mark.asyncio
@pytest.mark.parametrize("book_count", [1, 3, 5])
async def test_get_multiple_books_by_id(client: TestClient, book_count: int):
    """Test retrieving multiple books by their IDs."""
    book_ids = []
    for _ in range(book_count):
        book_data = {
            "name": get_fake_book_name(),
            "author": get_fake_author_name(),
            "date_published": get_fake_date_published(),
            "genre": get_fake_genre(),
            "file_path": None,
        }
        create_response = await client.post("/v1/books", json=book_data)
        assert create_response.status == http_statuses.HTTP_201_CREATED
        book = await create_response.json()
        book_ids.append(book["id"])

    # Retrieve each book by ID
    for book_id in book_ids:
        get_response = await client.get(f"/v1/books/{book_id}")
        assert get_response.status == http_statuses.HTTP_200_OK
        retrieved_book = await get_response.json()
        assert retrieved_book["id"] == book_id


@pytest.mark.asyncio
async def test_download_book(client: TestClient, fake_book_data: dict):
    """Test downloading a book file."""
    # Assume file_path is valid and points to an existing file for testing
    fake_book_data["url"] = get_real_external_file_url()
    create_response = await client.post("/v1/books", json=fake_book_data)
    assert create_response.status == http_statuses.HTTP_201_CREATED
    book = await create_response.json()
    book_id = book["id"]

    # Attempt to download the book
    download_response = await client.get(f"/v1/books/{book_id}/download")
    assert download_response.status == http_statuses.HTTP_200_OK
    content = await download_response.read()

    # Ensure the content is not empty
    assert content


@pytest.mark.asyncio
async def test_download_denied_book(client: TestClient):
    """Test that downloading a denied book is forbidden."""
    # Create a book
    book_data = {
        "name": get_fake_book_name(),
        "author": get_fake_author_name(),
        "date_published": get_fake_date_published(),
        "genre": get_fake_genre(),
        "url": get_real_external_file_url(),
    }
    create_response = await client.post("/v1/books", json=book_data)
    assert create_response.status == http_statuses.HTTP_201_CREATED
    book = await create_response.json()
    book_id = book["id"]

    # Deny the book using the upload_denied_books endpoint
    names_df = pd.DataFrame({"name": [book_data["name"]]})
    authors_df = pd.DataFrame({"author": []})

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        names_df.to_excel(writer, sheet_name="name", index=False)
        authors_df.to_excel(writer, sheet_name="author", index=False)
    buffer.seek(0)
    excel_content = buffer.getvalue()

    form = FormData()
    form.add_field(
        "file",
        excel_content,
        filename="denied_books.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    response = await client.post("/v1/books/deny", data=form)
    assert response.status == http_statuses.HTTP_200_OK
    data = await response.json()
    assert data["message"] == "Denied books updated"

    # Attempt to download the denied book
    download_response = await client.get(f"/v1/books/{book_id}/download")
    assert download_response.status == http_statuses.HTTP_403_FORBIDDEN
    error_data = await download_response.json()
    assert error_data["error"] == "Book is denied for download"


@pytest.mark.parametrize(
    "invalid_id",
    ["abc", "-1", "0", "9999999"],
)
@pytest.mark.asyncio
async def test_get_book_invalid_id(client: TestClient, invalid_id: str):
    """Test retrieving a book with an invalid ID."""
    get_response = await client.get(f"/v1/books/{invalid_id}")
    if invalid_id.isdigit() and int(invalid_id) >= 0:
        # Assuming the book ID does not exist
        assert get_response.status == http_statuses.HTTP_404_NOT_FOUND
        data = await get_response.json()
        assert data["error"] == "Book not found"
    else:
        assert get_response.status == http_statuses.HTTP_400_BAD_REQUEST
        data = await get_response.json()
        assert data["error"] == "Invalid book ID"


@pytest.mark.asyncio
async def test_download_book_file_not_found(client: TestClient, fake_book_data: dict):
    """Test downloading a book when the file does not exist."""
    # Create a book without a file_path
    create_response = await client.post("/v1/books", json=fake_book_data)
    assert create_response.status == http_statuses.HTTP_201_CREATED
    book = await create_response.json()
    book_id = book["id"]

    # Attempt to download the book
    download_response = await client.get(f"/v1/books/{book_id}/download")
    assert download_response.status == http_statuses.HTTP_404_NOT_FOUND
    data = await download_response.json()
    assert data["error"] == "Book file not found"


@pytest.mark.asyncio
async def test_create_duplicate_book(client: TestClient, fake_book_data: dict):
    """Test creating a book that already exists."""
    # First creation
    response1 = await client.post("/v1/books", json=fake_book_data)
    assert response1.status == http_statuses.HTTP_201_CREATED
    await response1.json()

    # Second creation with the same data
    response2 = await client.post("/v1/books", json=fake_book_data)
    assert response2.status == http_statuses.HTTP_409_CONFLICT
    data2 = await response2.json()
    assert data2["error"] == "Book already exists"


@pytest.mark.asyncio
async def test_upload_empty_denied_books(client: TestClient):
    """Test uploading an empty denied books file."""
    # Prepare empty Excel file with the correct sheets but no data
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame().to_excel(writer, sheet_name="name", index=False)
        pd.DataFrame().to_excel(writer, sheet_name="author", index=False)
    buffer.seek(0)
    excel_content = buffer.getvalue()

    # Simulate the file upload using FormData
    form = FormData()
    form.add_field(
        "file",
        excel_content,
        filename="empty_denied_books.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Upload the denied books list
    response = await client.post("/v1/books/deny", data=form)
    assert response.status == http_statuses.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_upload_denied_books_invalid_format(client: TestClient):
    """Test uploading a denied books file with invalid format."""
    # Prepare an Excel file with incorrect sheet names
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame().to_excel(writer, sheet_name="InvalidSheet", index=False)
    buffer.seek(0)
    excel_content = buffer.getvalue()

    # Simulate the file upload using FormData
    form = FormData()
    form.add_field(
        "file",
        excel_content,
        filename="invalid_denied_books.xlsx",
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # Upload the denied books list
    response = await client.post("/v1/books/deny", data=form)
    assert response.status == http_statuses.HTTP_400_BAD_REQUEST
    data = await response.json()
    assert data["error"] == "Failed to parse the denied books file"


@pytest.mark.asyncio
async def test_download_book_missing_file_path(
    client: TestClient, fake_book_data: dict
):
    """Test downloading a book when file_path is missing."""
    # Create a book without a file_path
    fake_book_data.pop("file_path", None)
    create_response = await client.post("/v1/books", json=fake_book_data)
    assert create_response.status == http_statuses.HTTP_201_CREATED
    book = await create_response.json()
    book_id = book["id"]

    # Attempt to download the book
    download_response = await client.get(f"/v1/books/{book_id}/download")
    assert download_response.status == http_statuses.HTTP_404_NOT_FOUND
    data = await download_response.json()
    assert data["error"] == "Book file not found"
