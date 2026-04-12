from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os
from dotenv import load_dotenv
load_dotenv()
#Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"} if DATABASE_URL.startswith("postgresql") else {},
    pool_pre_ping=True,
    pool_recycle=300
)

#Session factory
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)

#Base class for ORM models
Base = declarative_base()