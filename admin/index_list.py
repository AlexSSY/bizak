from typing import Optional, Sequence, Any, Dict
from fastapi import Request
from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import Query, Session
from .types import SQLAlchemyModel


def index_list(
    request: Request,
    model: Any,  # SQLAlchemy ORM model class
    queryset: Query,
    column_names: Sequence[str],
    offset: int = 0,
    limit: int = 8,
    search: Optional[str] = None,
    order: Optional[str] = None,
    order_type: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None  # 👈 фильтры по полям
) -> list:
    """Retrieve records from DB to template context."""
    
    query = queryset

    # Фильтрация по конкретным полям
    if filters:
        for field, value in filters.items():
            if hasattr(model, field):
                query = query.filter(getattr(model, field) == value)

    # Поиск по строке (LIKE %search%)
    if search:
        search_clauses = [
            getattr(model, col).ilike(f"%{search}%")
            for col in column_names
            if hasattr(model, col)
        ]
        if search_clauses:
            query = query.filter(or_(*search_clauses))

    # Сортировка
    if order and hasattr(model, order):
        column = getattr(model, order)
        query = query.order_by(desc(column) if order_type == 'desc' else asc(column))

    # Лимит и оффсет
    return query.offset(offset).limit(limit).all()
