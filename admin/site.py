from typing import Dict, List, Tuple, Type
from .model import ModelAdmin
from .types import SQLAlchemyModel


__all__ = (
    'register',
    'get_model_class',
    'get_model_admin_instance',
)


storage: Dict[str, Tuple[Type[SQLAlchemyModel], Type[ModelAdmin]]] = dict()

# cached instances
instances: Dict[str, ModelAdmin] = dict()


def register(model_class: SQLAlchemyModel, model_admin_class: ModelAdmin):
    """
    Регистрирует модель алхимии 
    :param model_class: Класс модели DeclarativeBase
    :param model_admin_class: Класс модели ModelAdmin
    """
    normalized_model_name = model_class.__name__.lower()
    storage[normalized_model_name] = (model_class, model_admin_class)


def get_model_class(model_name: str) -> Type[SQLAlchemyModel]:
    normalized_model_name = model_name.lower()
    row = storage.get(normalized_model_name)

    if row == None:
        raise KeyError(f'Model "{normalized_model_name}" not registered')
    
    return row[0]


def get_model_admin_instance(model_name: str) -> ModelAdmin:
    normalized_model_name = model_name.lower()

    row = storage.get(normalized_model_name)
    if row == None:
        raise KeyError(f'model "{model_name}" not registered')
    
    model_class, model_admin_classs = row
    instance = instances.get(normalized_model_name)
    if instance == None:
        instance = model_admin_classs(model=model_class)
        instances[normalized_model_name] = instance
    return instance


def get_all_sqlalchemy_models() -> List[Type[SQLAlchemyModel]]:
    return list([m[0] for m in storage.values()])


# def get_sqlalchemy_model_class_by(name: str) -> Type[SQLAlchemyModel]:
#     name = name.lower()
#     return next(filter(lambda x: x.__name__.lower() == name, admin_model_storage.keys()))
