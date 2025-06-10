from contextlib import asynccontextmanager
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, Depends
from admin.model import ModelAdminRegistry
from app import model as app_model
from app.db import get_db, Base, engine
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


@asynccontextmanager
async def liffespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(debug=True, lifespan=liffespan)


@app.get('/{model}')
def index(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    model_admin = ModelAdminRegistry.get_instance_by(model)
    return model_admin.index_view(request=request, session=session)


@app.get('/{model}/schema')
def schema(reques: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    # schema: SQLAlchemyAutoSchema = getattr(app_model, f'{model}Schema', None)
    user_instance = session.query(app_model.User).first()
    return app_model.UserSchema().dumps(user_instance)


@app.get('/')
def main(session: Annotated[Session, Depends(get_db)]):
    user_instance = session.query(app_model.User).first()
    return user_instance
