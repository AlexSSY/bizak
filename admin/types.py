from typing import TypeAlias
from sqlalchemy.orm import DeclarativeMeta


SQLAlchemyModel: TypeAlias = DeclarativeMeta


class Renderable:
    def render(self, request, templating, session):
        ...
