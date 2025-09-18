import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from pydantic import ConfigDict
from sqlalchemy import TIMESTAMP
from sqlmodel import SQLModel, Field

UTC = ZoneInfo("UTC")

class BaseModelMixin(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=TIMESTAMP(timezone=True), # Type: ignore
        sa_column_kwargs={
            "server_default": "CURRENT_TIMESTAMP",
        },
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=TIMESTAMP(timezone=True), # Type: ignore
        sa_column_kwargs={
            "server_default": "CURRENT_TIMESTAMP",
            "onupdate": "CURRENT_TIMESTAMP",
        },
        nullable=False,
    )

    model_config = ConfigDict(
        extra='forbid',
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )