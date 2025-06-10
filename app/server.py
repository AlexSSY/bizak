from contextlib import asynccontextmanager
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from admin.model import ModelAdminRegistry
from admin.form import get_model_fields
from app import model as app_model
from app.db import get_db, Base, engine
from app.form import LoginForm
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


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
    fields = get_model_fields(sqlalchemy_model_class)
    context = {
        'method': 'post',
        'action': f'/{model}/create',
        "fields": fields,
        "old": {},
    }
    return templating.TemplateResponse(request=request, name='add.html', context=context)


@app.get('/admin/test/form')
def form(request: Request):
    form = LoginForm()
    fields = form.fields_html(templating=templating)
    context = {
        'fields': fields
    }
    return templating.TemplateResponse(request=request, name='form.html', context=context)


@app.get('/admin/')
def main(session: Annotated[Session, Depends(get_db)]):
    user_instance = session.query(app_model.User).first()
    return user_instance
