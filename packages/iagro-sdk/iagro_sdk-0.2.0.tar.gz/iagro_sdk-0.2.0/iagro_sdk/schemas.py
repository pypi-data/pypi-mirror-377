from datetime import datetime
from typing import Generic, List
from typing import TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        arbitrary_types_allowed=True,
        populate_by_name=True,
        from_attributes=True,
    )

class BaseSchemaOut(BaseSchema):
    id: str
    created_at: datetime
    updated_at: datetime


class PaginationMeta(BaseModel):
    current_page: int
    per_page: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    pagination: PaginationMeta

class Paginator(BaseModel):
    skip: int = 0
    limit: int = 100