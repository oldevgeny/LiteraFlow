import datetime
import typing

import sqlalchemy
import sqlalchemy.orm as sa_orm

int_pk = typing.Annotated[int, sa_orm.mapped_column(primary_key=True)]
created_at = typing.Annotated[
    datetime.datetime,
    sa_orm.mapped_column(
        server_default=sqlalchemy.text("TIMEZONE('utc', now())"),
    ),
]
updated_at = typing.Annotated[
    datetime.datetime,
    sa_orm.mapped_column(
        server_default=sqlalchemy.text("TIMEZONE('utc', now())"),
        onupdate=sqlalchemy.text("TIMEZONE('utc', now())"),
    ),
]
