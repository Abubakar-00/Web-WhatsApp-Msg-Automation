# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL (adjust as needed for your database)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Example: SQLite database

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# database.py (add this at the end of the file)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()