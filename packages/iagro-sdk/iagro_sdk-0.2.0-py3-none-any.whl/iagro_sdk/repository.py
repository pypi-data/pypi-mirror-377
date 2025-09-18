from math import ceil
from typing import TypeVar, Generic, Any, Union, Optional, List, Dict

from sqlalchemy import select, and_, Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from iagro_sdk.model import BaseModelMixin
from iagro_sdk.schemas import PaginationMeta, PaginatedResponse

ModelType = TypeVar("ModelType", bound=BaseModelMixin)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModelMixin)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModelMixin)


class BaseRepository(Generic[ModelType]):
    def __init__(self: 'BaseRepository', model: type[ModelType]):
        self.model = model

    def add_eager_join_fields(
        self: "BaseRepository",
        stmt: Select,
        eager_join_fields: List[str],
    ) -> Select:
        for field in eager_join_fields:
            stmt = stmt.options(joinedload(getattr(self.model, field)))

        return stmt

    async def create(
        self: "BaseRepository",
        item: ModelType,
        session: AsyncSession
    ) -> ModelType:
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def get(
        self: "BaseRepository",
        id: str,
        session: AsyncSession,
        eager_join_fields: List[str] | None = None,
    ) -> Union[ModelType, None]:
        statement = select(self.model).where(and_(self.model.id == id))

        statement = (
            self.add_eager_join_fields(statement, eager_join_fields)
            if eager_join_fields
            else statement
        )

        record = await session.execute(statement)

        return record.scalar_one_or_none()

    async def list(
            self: 'BaseRepository',
            session: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[dict[str, Any]] = None,
            eager_join_fields: Optional[list[str]] = None,
    ) -> PaginatedResponse[ModelType]:
        base_statement = select(self.model)

        # aplica filtros
        if filters:
            conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]
            if conditions:
                base_statement = base_statement.where(and_(*conditions))

        # total de registros (sem paginação)
        count_statement = select(func.count()).select_from(base_statement.subquery())
        total_items = (await session.execute(count_statement)).scalar_one()

        # aplica eager joins
        statement = base_statement
        if eager_join_fields:
            statement = self.add_eager_join_fields(statement, eager_join_fields)

        # aplica paginação
        statement = statement.offset(skip).limit(limit)

        results = await session.scalars(statement)
        records = results.unique().all()

        # calcula metadados
        current_page = (skip // limit) + 1 if limit else 1
        total_pages = ceil(total_items / limit) if limit else 1

        pagination = PaginationMeta(
            current_page=current_page,
            per_page=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=current_page < total_pages,
            has_prev=current_page > 1,
        )

        return PaginatedResponse(
            data=list(records),
            pagination=pagination,
        )

    async def update(
        self: 'BaseRepository',
        session: AsyncSession,
        item: ModelType,
        updated_item: ModelType,
    ) -> ModelType:
        update_data = updated_item.model_dump(exclude_unset=True, exclude={"updated_at", "created_at"})

        for field, value in update_data.items():
            setattr(item, field, value)

        item = await session.merge(item)
        await session.flush()
        await session.refresh(item)

        return item

    async def delete(
        self,
        session: AsyncSession,
        id: str
    ) -> None:
        item = await self.get(id=id, session=session)

        await session.delete(item)
        await session.flush()

    async def first(
        self,
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        eager_join_fields: Optional[List[str]] = None,
    ) -> ModelType:
        statement = select(self.model)

        if filters:
            conditions = [
                getattr(self.model, key) == value
                for key, value in filters.items()
                if hasattr(self.model, key)
            ]
            if conditions:
                statement = statement.where(and_(*conditions))

        if eager_join_fields:
            statement = self.add_eager_join_fields(statement, eager_join_fields)

        result = await session.scalars(statement)
        record = result.unique().first()

        return record

