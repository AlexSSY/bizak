from contextlib import asynccontextmanager
from typing import Annotated, Any, Optional
from sqlalchemy.orm import Session, ColumnProperty
from fastapi import FastAPI, Request, Depends
from fastapi.responses import Response, RedirectResponse
from fastapi.templating import Jinja2Templates
from admin.model import ModelAdminRegistry
from wtforms import Form
from admin.utils import form_for_model, AdminForm
from app import model as app_model
from app.db import get_db, Base, engine
from app.form import LoginForm
from wtforms_sqlalchemy.orm import model_form
from wtforms_alchemy import ModelForm
from wtforms_sqlalchemy.orm import ModelConverter
from wtforms.validators import ValidationError, StopValidation

class Unique:
    def __init__(self, model, field, session, message="Must be unique"):
        self.model = model
        self.field = field
        self.session = session
        self.message = message

    def __call__(self, form, field):
        query = self.session.query(self.model).filter(getattr(self.model, self.field) == field.data)

        # При редактировании — не считаем текущий объект за дубликат
        if hasattr(form, 'obj'):
            existing_value = getattr(form.obj, self.field, None)
            if existing_value == field.data:
                return

        if query.first():
            raise StopValidation(self.message)

class MyModelConverter(ModelConverter):
    def convert(self, model, mapper, prop, field_args, db_session=None):
        if not field_args:
            field_args = {}
        render_kw = field_args.setdefault("render_kw", {})
        render_kw.setdefault("class", "form-control")

        field = super().convert(model, mapper, prop, field_args, db_session=db_session)

        if isinstance(prop, ColumnProperty):
            column = prop.columns[0]

            if getattr(column, 'unique', False):
                validators = field.kwargs.get('validators', [])
                if not any(isinstance(v, Unique) for v in validators):
                    validators.insert(0, Unique(model=model, field=column.name, session=db_session))
                    field.kwargs['validators'] = validators

        return field


@asynccontextmanager
async def liffespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(debug=True, lifespan=liffespan)


@app.middleware("http")
async def add_models_to_request(request: Request, call_next):
    models_sizes = []
    admin_models = ModelAdminRegistry.get_all()
    session = next(get_db())
    for amodel in admin_models:
        size = session.query(amodel.model).count()
        models_sizes.append((amodel.model.__name__, size))
    request.state.models_sizes = models_sizes
    response = await call_next(request)
    return response


def global_context(request: Request) -> dict:
    context = {
        "site_name": "MyApp",
        "models_sizes": getattr(request.state, "models_sizes", None),
    }
    return context

templating = Jinja2Templates('app/templates', context_processors=[global_context])


@app.get('/admin/{model}/json')
def index_json(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    model_admin = ModelAdminRegistry.get_instance_by(model)
    return model_admin.index_view(templating=templating, request=request, session=session)


@app.get('/admin/{model}', name='admin-model-index')
def index(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    model_admin = ModelAdminRegistry.get_instance_by(model)
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


@app.delete('/admin/{model_name}/')
def delete(
    request: Request,
    model_name: str,
    session: Annotated[Session, Depends(get_db)]
):
    pass