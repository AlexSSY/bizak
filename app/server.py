from contextlib import asynccontextmanager
from typing import Annotated, Any, Optional, Type
from sqlalchemy.orm import Session, ColumnProperty
from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from admin import site
from wtforms import Form
from admin.utils import form_for_model, AdminForm
from app import model as app_model
from app.db import get_db, Base, engine
from app.form import LoginForm
from wtforms_sqlalchemy.orm import model_form
from wtforms_alchemy import ModelForm
from wtforms_sqlalchemy.orm import ModelConverter
from wtforms.validators import ValidationError, StopValidation
from app import crud
from admin.types import SQLAlchemyModel
from admin.validators import Unique


site.register(app_model.User, app_model.UserAdmin)
site.register(app_model.Flower, app_model.FlowerAdmin)
site.register(app_model.Post, app_model.PostAdmin)


@asynccontextmanager
async def liffespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(debug=True, lifespan=liffespan)


@app.middleware("http")
async def add_models_to_request(request: Request, call_next):
    """
    Добавляет в [response.state] аттрибут-массив [models_sizes]
    каждый элемент которого содержит название модели и к-во зарисей
    """
    models_sizes = []
    models = site.get_all_sqlalchemy_models()
    session = next(get_db())
    for model in models:
        size = session.query(model).count()
        models_sizes.append((model.__name__, size))
    request.state.models_sizes = models_sizes
    response = await call_next(request)
    return response


def global_context_processor(request: Request) -> dict:
    context = {
        "site_name": "MyApp",
        "models_sizes": getattr(request.state, "models_sizes", None),
    }
    return context


templating = Jinja2Templates('app/templates', context_processors=[global_context_processor])


def get_model_class(model_class_name: str) -> Type[SQLAlchemyModel]:
    return getattr(app_model, model_class_name.capitalize(), None)


@app.get('/admin/{model_name}', name='admin-model-index')
def index(request: Request, model_name: str, session: Annotated[Session, Depends(get_db)]):
    """
    Точка входа для спска записей модели
    """
    model_admin = site.get_model_admin_instance(model_name)
    return model_admin.index_view(templating, request, session)


@app.get('/admin/{model}/new')
async def new(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    sqlalchemy_model_class = getattr(app_model, model.capitalize(), None)
    if sqlalchemy_model_class == None:
        return templating.TemplateResponse(request, '404.html', {}, 404)

    readonly_fields = ['created_at', 'updated_at']
    # form = form_for_model(sqlalchemy_model_class, Base, session)()
    form = model_form(sqlalchemy_model_class, session, AdminForm, converter=MyModelConverter(), exclude=readonly_fields)()
    # form = PostForm()
    ctx = {
        'form': form,
        'model': model,
        'method': 'post',
        'action': f'/admin/{model}/'
    }
    return templating.TemplateResponse(request=request, name='add.html', context=ctx)


@app.post('/admin/{model}')
async def create_model(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    sqlalchemy_model_class = getattr(app_model, model.capitalize(), None)
    if sqlalchemy_model_class == None:
        return templating.TemplateResponse(request, '404.html', {}, 404)

    readonly_fields = ['created_at', 'updated_at']
    form_data = await request.form()
    # form = form_for_model(sqlalchemy_model_class, Base, session)(f)
    form = model_form(sqlalchemy_model_class, session, AdminForm, converter=MyModelConverter(), exclude=readonly_fields)(formdata=form_data)
    if form.validate():
        instance = sqlalchemy_model_class(**form.data)
        session.add(instance)
        session.commit()
        return RedirectResponse(f'/admin/{model}', 301)
    else:
        ctx = {
            'form': form,
            'model': model,
            'method': 'post',
            'action': f'/admin/{model}/'
        }
        return templating.TemplateResponse(request=request, name='add.html', context=ctx, status_code=400)


@app.get('/admin/')
def main(session: Annotated[Session, Depends(get_db)]):
    return 'PLEASE FOLLOW DEEPLINK'


@app.post('/admin/{model_name}/delete/')
async def delete(
    request: Request,
    model_name: str,
    session: Annotated[Session, Depends(get_db)]
):
    form_data = await request.form()
    sqlalchemy_model_class = getattr(app_model, model_name.capitalize(), None)
    pk_values = list([v for _, v in form_data.items()])
    result: crud.DeleteResult = crud.delete_by_pk(sqlalchemy_model_class, pk_values, session)

    if result.get('success'):
        return Response(content='', status_code=200)
    return Response(content=result.get('reason'), status_code=400)


@app.get('/admin/{model_name}/{id}/edit')
async def edit(
    request: Request,
    model_name: str,
    id: int,
    session: Annotated[Session, Depends(get_db)]
):
    sqlalchemy_model_class = getattr(app_model, model_name.capitalize(), None)
    if sqlalchemy_model_class == None:
        return templating.TemplateResponse(request, '404.html', {}, 404)

    readonly_fields = ['created_at', 'updated_at']
    # form = form_for_model(sqlalchemy_model_class, Base, session)()
    form_data = await request.form()
    form = model_form(sqlalchemy_model_class, session, AdminForm, converter=MyModelConverter(), exclude=readonly_fields)(formdata=form_data)
    # form = PostForm()
    ctx = {
        'form': form,
        'model': model_name,
        'method': 'post',
        'action': f'/admin/{model_name}/update/'
    }
    return templating.TemplateResponse(request=request, name='add.html', context=ctx)


@app.post('/admin/{model_name}/{id}/update/')
async def update(
    request: Request,
    model_name: str,
    id: int,
    session: Annotated[Session, Depends(get_db)]
):
    return None