# LiteraFlow API Service

LiteraFlow is an asynchronous API service built with Python, aiohttp, and PostgreSQL, designed to provide users with access to a collection of literary works. The service allows users to upload books, retrieve books based on various filters, and manage access to books via a denied list.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Using Docker (Recommended)](#using-docker-recommended)
- [Usage](#usage)
  - [API Endpoints](#api-endpoints)
    - [Books](#books)
  - [Denied List](#denied-list)
  - [Testing](#testing)
  - [Examples of API Requests with cURL](#examples-of-api-requests-with-curl)
- [Project Structure](#project-structure)
- [Code Quality](#code-quality)
- [Configuration](#configuration)
- [Additional Notes](#additional-notes)
- [Limitations](#limitations)
- [What's Next?](#whats-next)
- [License](#license)

## Features

- **Book Management:** Upload, retrieve, and access books.
- **Filtering:** Retrieve a list of books filtered by name, author, date_published, or genre.
- **Denied List:** Upload an XLS file to manage a denied list of books that cannot be downloaded but can be viewed online.
- **Asynchronous Operations:** Built with async capabilities for improved performance.
- **Docker Support:** Easy setup and deployment using Docker and Docker Compose.
- **Testing:** Comprehensive test suite using pytest and pytest-aiohttp.
- **Code Quality:** Enforced via ruff and follows best practices.

## Requirements

- **Python:** 3.12 or newer
- **PostgreSQL:** Version compatible with your environment
- **Docker and Docker Compose:** For containerized builds
- **Poetry:** For dependency management

## Installation

### Using Docker (Recommended)

_**Tested on:** macOS Sequoia 15.0 with Apple Silicon chip_

1. Clone the Repository:

```bash
git clone git@github.com:oldevgeny/LiteraFlow.git
cd LiteraFlow
```


2. Set Up Environment Variables:

- Copy the example environment file and edit it:

```bash
cp .env.example .env.local
```

- Open .env.local and fill in all the environment variables:

```bash
vim .env.local
```

```bash
DB_NAME=literaflow_insecure_name
DB_HOST=literaflow_db
DB_PORT=5432
DB_USER=literaflow_insecure_user
DB_PASS=literaflow_insecure_pass
```

3. Ensure Execution Permission for Entry Point Script:

```bash
chmod +x infra/entrypoint.sh
```

4. Build and Run the Containers:

```bash
make run
```

This command will:
- Build the Docker images.
- Start the containers for the web application and the database.
- Apply database migrations.

5. Access the API:
The API server will be running at http://localhost:8000/.


## Usage

Use the following command for help:

```bash
make help
```

### API Endpoints


#### Books
- **Create a Book:** POST /v1/books/
- **List Books:** GET /v1/books/
- **Retrieve a Book:** GET /v1/books/{book_id}/
- **Download a Book:** GET /v1/books/{book_id}/download/

Fields:

- **id:** Auto-increment primary key.
- **name:** Title of the book (string).
- **author:** Author of the book (string).
- **date_published:** Publication date (ISO 8601 format).
- **genre:** Genre of the book (string, optional).
- **is_denied:** Boolean indicating if the book is denied for download.
- **url:** URL to download the book file (optional).

Notes:

- **Mandatory Fields:** name, author, and date_published are required when creating a book.
- **File Storage:** Book files are stored in the books directory, which is configurable.
- **Asynchronous Operations:** All database queries and file operations are asynchronous.


### Denied List

 - **Upload Denied List:** POST /v1/books/deny/
   - Accepts an XLS file containing two sheets:
     - **Sheet “name”:** List of book names to be denied.
     - **Sheet “author”:** List of authors whose books should be denied.
   - **Effect:** Books in the denied list become unavailable for download but remain available for viewing.


### Testing

To run the test suite, execute:

```bash
make test
```

This command will execute the test suite inside a Docker container (if using Docker) or in your local environment.

### Examples of API Requests with cURL

1. Create a Book
```bash
curl -X POST http://localhost:8000/v1/books/ \
-H "Content-Type: application/json" \
-d '{
  "name": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "date_published": "1925-04-10",
  "genre": "Novel",
  "url": "https://example.com/great_gatsby.pdf"
}'
```

2. List Books with Filtering
```bash
curl -X GET "http://localhost:8000/v1/books/?author=F.%20Scott%20Fitzgerald" \
-H "Content-Type: application/json"
```

3. Retrieve a Book by ID
```bash
curl -X GET http://localhost:8000/v1/books/1/ \
-H "Content-Type: application/json"
```

4. Download a Book
```bash
curl -X GET http://localhost:8000/v1/books/1/download/ \
-H "Content-Type: application/json" --output great_gatsby.pdf
```

5. Upload Denied List
```bash
curl -X POST http://localhost:8000/v1/books/deny/ \
-F "file=@path_to_your_file/denied_books.xlsx"
```

## Project Structure

The project structure follows Django best practices:

```
LiteraFlow/
├── Makefile
├── README.md
├── infra/
│   ├── Dockerfile.dev
│   ├── docker-compose.yml
│   └── entrypoint.sh
├── literaflow/
│   ├── api/
│   │   ├── routes.py
│   │   └── v1/
│   │       └── books.py
│   ├── core/
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── dto.py
│   │   └── logger.py
│   ├── models/
│   │   └── book.py
│   ├── services/
│   │   ├── book.py
│   │   ├── denied_list.py
│   │   └── exceptions.py
│   └── utils/
│       ├── app_running.py
│       ├── denied_books_parser.py
│       ├── files.py
│       └── http_statuses.py
├── main.py
├── media/
│   └── decline_list_example.xlsx
├── poetry.lock
├── pyproject.toml
└── tests/
    ├── conftest.py
    └── test_books.py
```

- **infra/:** Docker and infrastructure-related files.
- **literaflow/:** Main application code.
  - **api/:** API endpoints and route definitions.
  - **core/:** Core configurations, database setup, and data transfer objects.
  - **models/:** Database models.
  - **services/:** Business logic and services.
  - **utils/:** Utility functions and helpers.
- **tests/:** Test cases for the application.
- **main.py:** Entry point for the application.
- **pyproject.toml:** Project configuration and dependencies.


## Code Quality
**Linters:** The project uses ruff and black for linting and code formatting.

- To check for linting errors:

```bash
make lint
```

- Automatically fix formatting issues:

```bash
make format
```

**Configuration:** Linter configurations are specified in pyproject.toml.

## Configuration

- **Environment Variables:** The local application uses environment variables for configuration, specified in the .env.local file.
- **Database Settings:** Configurable via environment variables for DB_NAME, DB_HOST, DB_PORT, DB_USER, and DB_PASS.
- **App Settings:** Configurable via config.py, including host, port, and directory paths.

## Additional Notes

- **Asynchronous Framework:** Built using aiohttp for handling asynchronous HTTP requests.
- **Database ORM:** Utilizes SQLAlchemy with async support for database operations.
- **File Handling:** Manages book file downloads and storage asynchronously.
- **Error Handling:** Custom exceptions and error responses for better API feedback.
- **Logging:** Implemented using loguru for structured logging.


## Limitations

- **Authentication:** No authentication or authorization mechanisms are implemented.
- **Data Validation:** Basic validation is implemented, but additional checks could enhance robustness.
- **Scalability:** While the application is asynchronous, further optimizations may be needed for high-load scenarios.


## What's Next?
While the current implementation meets the basic requirements, there are several areas where the project can be enhanced:

1.	**Database Migrations with Alembic:**
- **Issue:** Currently, database schema changes are managed manually, which can lead to inconsistencies and make it difficult to track changes over time.
- **Improvement:** Integrate Alembic for database migrations. Alembic works seamlessly with SQLAlchemy and allows for version-controlled database schema migrations.
- **Benefit:** Easier management of database schema changes, rollback capabilities, and better collaboration among developers.
2.	**Authentication and Authorization:**
- **Issue:** The API endpoints are publicly accessible, which is not ideal for a service that manages potentially sensitive data.
- **Improvement:** Implement authentication mechanisms such as API keys, JWT tokens, or OAuth2. Additionally, set up authorization to control access to certain endpoints or resources based on user roles or permissions.
- **Benefit:** Enhanced security by restricting access to authorized users, protecting user data, and complying with security best practices.
3.	**API Documentation with Swagger or ReDoc:**
- **Issue:** Currently, there is no interactive API documentation available for users to understand and test the API endpoints.
- **Improvement:** Integrate Swagger (OpenAPI) or ReDoc to auto-generate interactive API documentation.
- **Benefit:** Provides a user-friendly interface for developers to explore and test the API, improving developer experience and facilitating integration.
4.	**Improved Error Handling and Validation:**
- **Issue:** While basic error handling is implemented, some exceptions may not provide detailed feedback to the client.
- **Improvement:** Enhance validation logic using libraries like pydantic to provide more descriptive error messages. Implement global exception handlers to catch unhandled exceptions and return consistent error responses.
- **Benefit:** Improves API robustness and provides clients with actionable feedback when errors occur.
5.	**Pagination and Sorting:**
- **Issue:** The GET /v1/books/ endpoint may return a large number of records without pagination, which can lead to performance issues.
- **Improvement:** Implement pagination and sorting capabilities using query parameters (e.g., limit, offset, sort_by).
- **Benefit:** Enhances performance, reduces load on the server, and provides clients with control over data retrieval.
6.	**Caching Mechanisms:**
- **Issue:** Frequent database queries for the same data can lead to unnecessary load.
- **Improvement:** Implement caching strategies using tools like Redis or in-memory caches to store frequently accessed data.
- **Benefit:** Reduces database load, decreases response times, and improves scalability.
7.	**Continuous Integration and Deployment (CI/CD):**
- **Issue:** Manual testing and deployment can be error-prone and time-consuming.
- **Improvement:** Set up CI/CD pipelines using tools like GitHub Actions or Jenkins to automate testing, linting, and deployment processes.
- **Benefit:** Ensures code quality, facilitates rapid deployment, and reduces the risk of human error.
8. **Data Validation and Sanitization:**
- **Issue:** Input data may not be fully sanitized, leading to potential security vulnerabilities like SQL injection or XSS attacks.
- **Improvement:** Enhance input validation and sanitization using pydantic models and validation methods.
- **Benefit:** Increases security by preventing malicious data from causing harm.
9.	**Internationalization (i18n) and Localization (l10n):**
- **Issue:** The application may not support multiple languages or locale-specific formatting.
- **Improvement:** Implement internationalization frameworks to support multiple languages and date formats.
- **Benefit:** Makes the application accessible to a wider audience.


## License

This project is for demonstration purposes and does not have a specific license.
