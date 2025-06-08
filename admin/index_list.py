from typing import Optional, Sequence
from dataclasses import dataclass
from fastapi import Request
from sqlalchemy.orm import Query, Session
from .types import SQLAlchemyModel


@dataclass
class IndexList:
    """Retrieve's records from DB to template context."""

    request: Request
    model: SQLAlchemyModel
    queryset: Query
    column_names: Sequence[str]
    offset: int = 0
    limit: int = 8
    search: Optional[str] = None
    order: Optional[str] = None
    order_type: Optional[str] = None

    def get_records(self) -> list:
        records = self.queryset.limit(self.limit).offset(self.offset).all()
        return records
