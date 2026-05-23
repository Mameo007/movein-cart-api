import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load the database password
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Setup the Database Engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Helper function to open and close database connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()