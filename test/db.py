from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DB_FILE_NAME = 'test.sqlite3'
engine = create_engine(f'sqlite:///{DB_FILE_NAME}', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
