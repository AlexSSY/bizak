from typing import Optional, Sequence, Any, Dict
from dataclasses import dataclass
from fastapi import Request
from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import Query, Session
from .types import SQLAlchemyModel


@dataclass
class IndexList:
    """Retrieve records from DB to template context."""

    request: Request
    model: Any  # SQLAlchemy ORM model class
    queryset: Query
    column_names: Sequence[str]
    offset: int = 0
    limit: int = 8
    search: Optional[str] = None
    order: Optional[str] = None
    order_type: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None  # 👈 фильтры по полям

    def get_records(self) -> list:
        query = self.queryset

        # Фильтрация по конкретным полям
        if self.filters:
            for field, value in self.filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        # Поиск по строке (LIKE %search%)
        if self.search:
            search_clauses = [
                getattr(self.model, col).ilike(f"%{self.search}%")
                for col in self.column_names
                if hasattr(self.model, col)
            ]
            if search_clauses:
                query = query.filter(or_(*search_clauses))

        # Сортировка
        if self.order and hasattr(self.model, self.order):
            column = getattr(self.model, self.order)
            query = query.order_by(desc(column) if self.order_type == 'desc' else asc(column))

        # Лимит и оффсет
        return query.offset(self.offset).limit(self.limit).all()
