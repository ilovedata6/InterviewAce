from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in settings")
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 