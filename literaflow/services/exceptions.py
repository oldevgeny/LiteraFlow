class BookDownloadError(Exception):
    """Book download error."""


class BookDownloadTimeoutError(BookDownloadError):
    """Book download timeout error."""


class BookAlreadyExistsError(Exception):
    """Book already exists error."""
