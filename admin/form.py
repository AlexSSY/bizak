from typing import Any
from sqlalchemy.orm import Session
from .types import SQLAlchemyModel, PydanticShema


class Form:

    class Meta:
        model: SQLAlchemyModel = None
        schema: PydanticShema = None

    def save(self, data: dict[str, Any], session: Session):
        ...

    def validate(self, data: dict[str, Any], session: Session):
        ...