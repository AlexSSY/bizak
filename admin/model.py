from sqlalchemy import inspect
from sqlalchemy.orm import Query
from sqlalchemy.orm import Session
from fastapi import Request
from .types import SQLAlchemyModel
from .index_list import IndexList


class ModelAdmin:
    def __init__(self, model: SQLAlchemyModel):
        self.model = model

    def get_queryset(self, request: Request, session: Session) -> Query:
        return session.query(self.model)
    
    def get_name(self) -> str:
        return self.model.__class__.__name__
    
    def get_name_plural(self) -> str:
        return self.model.__class__.__name__
    
    def index_view(self, request: Request, session: Session) -> dict:
        inspected_model = inspect(self.model)
        sql_columns = inspected_model.columns
        name = self.__class__.__name__

        ctx_columns = list()

        def customize_column(column):
            get_column_display = getattr(self, f'get_{column.name}_display', None)
            if get_column_display:
                ctx_columns.append(get_column_display())
            else:
                ctx_columns.append(column.name)
                
        for column in sql_columns:
            # check if column name in the list_display
            if isinstance(self.list_display, str):
                if self.list_display != '__all__':
                    error_msg = f'The get_list_display method of a {name} - invalid'
                    raise ValueError(error_msg)
                else:
                    customize_column(column)

            elif isinstance(self.list_display, list):
                if len(self.list_display) == 0:
                    error_msg = f'The get_list_display method of a {name} returns empty list'
                    raise ValueError(error_msg)
                else:
                    if column.name not in self.list_display:
                        continue
                    customize_column(column)
                    
            else:
                error_msg = f'The get_list_display method of a {name} must return list or str'
                raise ValueError(error_msg)
            
        index_list = IndexList(request, self.model, self.get_queryset(request, session), [])
        
        return {
            'columns': ctx_columns,
            'records': index_list.get_context()['records']
        }

    
    list_display = '__all__'
    fields = '__all__'
    exclude_fields = []


class ModelAdminRegistry:
    admin_model_storage: dict[SQLAlchemyModel, ModelAdmin] = dict()

    @classmethod
    def register(cls, model: SQLAlchemyModel, model_admin_class: ModelAdmin):
        cls.admin_model_storage[model] = model_admin_class

    @classmethod
    def get_instance(cls, model: SQLAlchemyModel) -> ModelAdmin:
        model_admin_class = cls.admin_model_storage.get(model)
        if model_admin_class == None:
            raise ValueError(f'model: {model} is not registered in AdminModelRegistry')
        return model_admin_class(model)
