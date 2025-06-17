from typing import Type, Any, Union, Sequence, Literal, TypedDict
from sqlalchemy.orm import Session, DeclarativeMeta
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


class DeleteResult(TypedDict):
    success: bool
    reason: Union[Literal["not_found", "constraint_error", "unknown_error"], None]
    error: Union[str, None]


def delete_by_pk(
    model_cls: Type[DeclarativeMeta],
    pk_values: Union[Any, Sequence[Any]],
    session: Session,
    commit: bool = True
) -> DeleteResult:
    """
    Удаляет запись по PK (включая составной). Возвращает детальный результат.

    :param model_cls: Класс модели
    :param pk_values: Значение PK или кортеж значений
    :param session: SQLAlchemy session
    :param commit: Делать ли commit
    :return: Словарь с ключами: success, reason, error
    """
    try:
        mapper = inspect(model_cls)
        pk_columns = mapper.primary_key

        if not isinstance(pk_values, (tuple, list)):
            pk_values = (pk_values,)

        if len(pk_columns) != len(pk_values):
            return {
                "success": False,
                "reason": "unknown_error",
                "error": f"Expected {len(pk_columns)} PK values, got {len(pk_values)}"
            }

        filters = [col == val for col, val in zip(pk_columns, pk_values)]
        instance = session.query(model_cls).filter(*filters).first()

        if not instance:
            return {
                "success": False,
                "reason": "not_found",
                "error": None
            }

        session.delete(instance)
        if commit:
            session.commit()

        return {
            "success": True,
            "reason": None,
            "error": None
        }

    except IntegrityError as e:
        session.rollback()
        return {
            "success": False,
            "reason": "constraint_error",
            "error": str(e.orig)
        }
    except SQLAlchemyError as e:
        session.rollback()
        return {
            "success": False,
            "reason": "unknown_error",
            "error": str(e)
        }


class UpdateResult(TypedDict):
    success: bool
    reason: Union[Literal["not_found", "constraint_error", "unknown_error"], None]
    error: Union[str, None]


from typing import Type, Any, Union, Sequence, Mapping, Literal, TypedDict
from sqlalchemy.orm import Session, DeclarativeMeta
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class UpdateResult(TypedDict):
    success: bool
    reason: Union[Literal["not_found", "constraint_error", "unknown_error"], None]
    error: Union[str, None]
    updated: Union[dict[str, Any], None]


def update_by_pk(
    model_cls: Type[DeclarativeMeta],
    pk_values: Union[Any, Sequence[Any]],
    updates: Mapping[str, Any],
    session: Session,
    commit: bool = True
) -> UpdateResult:
    """
    Обновляет запись по первичному ключу (включая составной).
    Возвращает результат обновления и обновлённые данные.

    :param model_cls: Класс модели SQLAlchemy
    :param pk_values: Значение PK (или tuple значений, если составной ключ)
    :param updates: Словарь с полями и новыми значениями
    :param session: SQLAlchemy session
    :param commit: Делать ли commit
    :return: UpdateResult с флагом успеха, причиной и ошибкой
    """
    try:
        mapper = inspect(model_cls)
        pk_columns = mapper.primary_key

        if not isinstance(pk_values, (tuple, list)):
            pk_values = (pk_values,)

        if len(pk_columns) != len(pk_values):
            return {
                "success": False,
                "reason": "unknown_error",
                "error": f"Expected {len(pk_columns)} PK values, got {len(pk_values)}",
                "updated": None
            }

        filters = [col == val for col, val in zip(pk_columns, pk_values)]
        instance = session.query(model_cls).filter(*filters).first()

        if not instance:
            return {
                "success": False,
                "reason": "not_found",
                "error": None,
                "updated": None
            }

        for key, value in updates.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        if commit:
            session.commit()

        return {
            "success": True,
            "reason": None,
            "error": None,
            "updated": {k: getattr(instance, k) for k in updates.keys()}
        }

    except IntegrityError as e:
        session.rollback()
        return {
            "success": False,
            "reason": "constraint_error",
            "error": str(e.orig),
            "updated": None
        }
    except SQLAlchemyError as e:
        session.rollback()
        return {
            "success": False,
            "reason": "unknown_error",
            "error": str(e),
            "updated": None
        }


from typing import Type, Any, Union, Sequence, Literal, TypedDict
from sqlalchemy.orm import Session, DeclarativeMeta
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError


class RetrieveResult(TypedDict):
    success: bool
    reason: Union[Literal["not_found", "unknown_error"], None]
    error: Union[str, None]
    instance: Union[DeclarativeMeta, None]


def retrieve_by_pk(
    model_cls: Type[DeclarativeMeta],
    pk_values: Union[Any, Sequence[Any]],
    session: Session
) -> RetrieveResult:
    """
    Ищет запись по первичному ключу (включая составной). Возвращает объект или ошибку.

    :param model_cls: Класс модели SQLAlchemy
    :param pk_values: Значение PK или tuple значений (если составной ключ)
    :param session: SQLAlchemy session
    :return: RetrieveResult с success, reason, error и instance
    """
    try:
        mapper = inspect(model_cls)
        pk_columns = mapper.primary_key

        if not isinstance(pk_values, (tuple, list)):
            pk_values = (pk_values,)

        if len(pk_columns) != len(pk_values):
            return {
                "success": False,
                "reason": "unknown_error",
                "error": f"Expected {len(pk_columns)} PK values, got {len(pk_values)}",
                "instance": None
            }

        filters = [col == val for col, val in zip(pk_columns, pk_values)]
        instance = session.query(model_cls).filter(*filters).first()

        if not instance:
            return {
                "success": False,
                "reason": "not_found",
                "error": None,
                "instance": None
            }

        return {
            "success": True,
            "reason": None,
            "error": None,
            "instance": instance
        }

    except SQLAlchemyError as e:
        return {
            "success": False,
            "reason": "unknown_error",
            "error": str(e),
            "instance": None
        }
