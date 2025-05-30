from sqlalchemy import create_engine, Column, String, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

print("SQLALCHEMY_DATABASE_URL:")
print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class TableMetadata(Base):
    __tablename__ = "table_metadata"

    table_name = Column(String, primary_key=True)
    column_names = Column(ARRAY(String))
    column_descriptions = Column(ARRAY(String))
    table_description = Column(String)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine) 