import datetime
import typing
from typing import TypedDict

import pydantic
import typing_extensions

DTOKwargs = typing.Any
BookID = int


@typing.final
class PydanticErrorDict(TypedDict):
    """Pydantic error type."""

    loc: tuple[str]
    msg: str
    type: str


def create_dto_safely(
    dto: type[pydantic.BaseModel],
    **dto_kwargs: DTOKwargs,
) -> tuple[pydantic.BaseModel | None, list[PydanticErrorDict] | None]:
    """Create a Pydantic DTO safely."""
    try:
        return dto(**dto_kwargs), None
    except pydantic.ValidationError as exc:
        return None, [
            PydanticErrorDict(
                loc=error["loc"],
                msg=error["msg"],
                type=error["type"],
            )
            for error in exc.errors()
        ]


@typing.final
class Book(pydantic.BaseModel):
    name: str
    author: str
    date_published: datetime.date

    genre: str = ""
    is_denied: bool = False

    url: pydantic.HttpUrl | None = None

    @pydantic.model_validator(mode="after")
    def validate_required_fields(self) -> typing_extensions.Self:
        """Validate required fields."""
        if not self.name or not self.author or not self.date_published:
            raise ValueError("Name, author and date_published are required")
        return self


@typing.final
class BookFilters(pydantic.BaseModel):
    name: str | None = None
    author: str | None = None
    date_published: datetime.date | None = None
    genre: str | None = None

    def filters_exist(self) -> bool:
        """Check if filters exist."""
        return not all((
            self.name is None,
            self.author is None,
            self.date_published is None,
            self.genre is None,
        ))
