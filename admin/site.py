from typing import Dict, Tuple, Type
from .model import ModelAdmin
from .types import SQLAlchemyModel


__all__ = ('register', 'get_model_admin_instance')


admin_model_storage: dict[str, Tuple[Type[SQLAlchemyModel], ModelAdmin]] = dict()
storage: Dict[str, Type[ModelAdmin]] = dict()


def register(model_class: SQLAlchemyModel, model_admin_class: ModelAdmin):
    """
    Регистрирует модель алхимии 
    :param model_class: Класс модели DeclarativeBase
    :param model_admin_class: Класс модели ModelAdmin
    """
    admin_model_storage[model_class] = model_admin_class(model_class)
    storage[model_class.__name__] = (model_class, model_admin_class)


def get_model_admin_instance(model: SQLAlchemyModel) -> ModelAdmin:
    instance = admin_model_storage.get(model)
    if instance == None:
        raise ValueError(f'model: {model} is not registered in AdminModelRegistry')
    return instance


def get_instance_by( model_class_name: str) -> ModelAdmin:
    result = [v for k, v in admin_model_storage.items() if k.__name__ == model_class_name]
    if not result:
        raise ValueError(f'model: {model_class_name} is not registered in AdminModelRegistry')
    model_admin = result[-1]
    return model_admin


def get_all_sqlalchemy_models() -> Tuple[ModelAdmin]:
    return tuple([m for m in admin_model_storage.values()])


def get_sqlalchemy_model_class_by(name: str) -> Type[SQLAlchemyModel]:
    name = name.lower()
    return next(filter(lambda x: x.__name__.lower() == name, admin_model_storage.keys()))
