from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


# Determine the absolute path for the API directory.
# __file__ is infrastructure/database.py, so we need to go up two levels.
api_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if "pytest" in os.environ.get("ENV", "development"):
    db_path = os.path.join(api_dir, 'test.db')
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URL = DATABASE_URL
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
    else:
        db_path = os.path.join(api_dir, 'dev.db')
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
