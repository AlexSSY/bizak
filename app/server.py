from contextlib import asynccontextmanager
from typing import Annotated, Any, Optional
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from admin.model import ModelAdminRegistry
from admin.form import Form, model_to_form
from app import model as app_model
from app.db import get_db, Base, engine
from app.form import LoginForm


@asynccontextmanager
async def liffespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(debug=True, lifespan=liffespan)
templating = Jinja2Templates('app/templates')


@app.get('/admin/{model}')
def index(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    model_admin = ModelAdminRegistry.get_instance_by(model)
    return model_admin.index_view(request=request, session=session)


@app.get('/admin/{model}/schema')
def schema(reques: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    # schema: SQLAlchemyAutoSchema = getattr(app_model, f'{model}Schema', None)
    user_instance = session.query(app_model.User).first()
    return app_model.UserSchema().dumps(user_instance)


@app.get('/admin/{model}/new')
def new(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    # schema_class = getattr(app_model, f'{model.capitalize()}Schema', None)
    # schema_instance: SQLAlchemyAutoSchema = schema_class()
    sqlalchemy_model_class = getattr(app_model, model.capitalize(), None)
    fields = model_to_form(sqlalchemy_model_class, session)
    context = {
        'method': 'post',
        'action': f'/{model}/create',
        "fields": fields,
    }
    return templating.TemplateResponse(request=request, name='add.html', context=context)


async def render_form(request: Request, session: Session, form: Form, old_values: dict[str, Any] = {}):
    fields = form.fields_html(templating=templating, old_values=old_values)
    context = {
        'fields': fields,
        'method': 'post',
        'action': '/admin/test/form',
    }
    return templating.TemplateResponse(request=request, name='form.html', context=context)


@app.get('/admin/test/form')
async def form(request: Request, session: Annotated[Session, Depends(get_db)]):
    form = LoginForm()
    return await render_form(request, session, form)


@app.post('/admin/test/form')
async def post_form(request: Request, session: Annotated[Session, Depends(get_db)]):
    form_data = await request.form()
    form=LoginForm()
    form.validate(form_data=form_data, session=session)
    if form.valid:
        return form.cleaned_data
    else:
        return await render_form(request=request, session=session, form=form)


@app.get('/admin/test/form/{model}')
async def form_model(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    model_cls = getattr(app_model, model)
    form = model_to_form(model_cls, session)
    return await render_form(request=request, session=session, form=form)


@app.get('/admin/')
def main(session: Annotated[Session, Depends(get_db)]):
    user_instance = session.query(app_model.User).first()
    return user_instance
