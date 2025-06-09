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

# if __name__ == '__main__':
#     from pprint import pprint
#     create_all_tables()
#     with SessionLocal() as session:
#         pprint(ModelAdminRegistry.get_instance(User).index_view(None, session))
