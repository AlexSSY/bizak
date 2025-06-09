from typing import Optional, Sequence, Any, Dict
from fastapi import Request
from sqlalchemy import or_, asc, desc, and_
from sqlalchemy.orm import Query
from .types import SQLAlchemyModel


OPERATORS = {
    "eq": lambda col, val: col == val,
    "gt": lambda col, val: col > val,
    "lt": lambda col, val: col < val,
    "gte": lambda col, val: col >= val,
    "lte": lambda col, val: col <= val,
    "like": lambda col, val: col.like(val),
    "ilike": lambda col, val: col.ilike(val),
    "ne": lambda col, val: col != val,
}


def parse_filters(request: Request) -> Dict[str, Any]:
    filters = {}
    for key, value in request.query_params.multi_items():
        if key.startswith("filters[") and key.endswith("]"):
            actual_key = key[len("filters["):-1]
            filters[actual_key] = value
    return filters


def index_list(
    request: Request,
    model: SQLAlchemyModel,  # SQLAlchemy ORM model class
    queryset: Query,
    search_column_names: Sequence[str],
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
    for raw_key, value in filters.items():
        if "__" in raw_key:
            field, op = raw_key.split("__", 1)
        else:
            field, op = raw_key, "eq"

        if field in model.__table__.columns and op in OPERATORS:
            column = getattr(model, field)
            query = query.filter(OPERATORS[op](column, value))

    # Поиск по строке (LIKE %search%)
    if search:
        search_clauses = [
            getattr(model, col).ilike(f"%{search}%")
            for col in search_column_names
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
