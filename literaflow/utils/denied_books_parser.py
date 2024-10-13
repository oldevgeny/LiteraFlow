from io import BytesIO

import pandas as pd
from typing_extensions import TypedDict


class DeniedBooksDict(TypedDict):
    """Denied books dictionary."""

    names: tuple[str, ...]
    authors: tuple[str, ...]


def parse_denied_books(file_content: bytes) -> DeniedBooksDict:
    """Parse the denied books from an XLS file."""
    f = BytesIO(file_content)
    try:
        sheets = pd.read_excel(f, sheet_name=["name", "author"], engine="openpyxl")
    except Exception as exc:
        raise ValueError(f"Failed to read Excel file: {exc}") from exc

    names_df = sheets["name"]
    authors_df = sheets["author"]

    names_series = names_df.iloc[:, 0].dropna().astype(str)
    authors_series = authors_df.iloc[:, 0].dropna().astype(str)

    names = tuple(names_series.tolist())
    authors = tuple(authors_series.tolist())

    return DeniedBooksDict(names=names, authors=authors)
