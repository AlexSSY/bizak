from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import FastAPI, Request, Depends, Query
from admin.model import ModelAdminRegistry
from app.db import get_db
from app.model import User, UserAdmin


app = FastAPI(debug=True)


@app.get('/{model}')
def index(request: Request, model: str, session: Annotated[Session, Depends(get_db)]):
    model_admin = ModelAdminRegistry.get_instance_by(model)
    return model_admin.index_view(request=request, session=session)
