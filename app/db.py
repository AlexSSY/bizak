from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeMeta


engine = create_engine('sqlite:///database.sqlite3')
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base: DeclarativeMeta = declarative_base()


def create_all_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
