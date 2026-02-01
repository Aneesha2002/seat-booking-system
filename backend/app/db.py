from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

#Database connection
DATABASE_URL = "sqlite:///./seats.db"

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread":False})

#Session factory
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)

#Base class for ORM models
Base = declarative_base()