from app.db import SessionLocal
from admin.model import ModelAdminRegistry
from app.model import User
from app.db import create_all_tables


if __name__ == '__main__':
    from pprint import pprint
    create_all_tables()
    with SessionLocal() as session:
        pprint(ModelAdminRegistry.get_instance(User).index_view(None, session))
