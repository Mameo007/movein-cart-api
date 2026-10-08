import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load the database password
load_dotenv()
# No default on purpose: a missing URL should crash at startup, not silently
# fall back to a local database that Render wipes on every redeploy
DATABASE_URL = os.environ["DATABASE_URL"]


# Setup the Database Engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Helper function to open and close database connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()