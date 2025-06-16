from typing import Type
from sqlalchemy.orm import Session, DeclarativeMeta


def delete_record(model_cls: Type[DeclarativeMeta], pk_column_name: str, session: Session):
    session.query(model_cls).where()