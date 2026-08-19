from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = 'sqlite:///./blog.db'

engine = create_engine(
    DATABASE_URL,
    # You'll only need to do this when you're using sqlalchemy
    connect_args={"check_same_thread" :False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db