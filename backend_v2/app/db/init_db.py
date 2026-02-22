from app.models.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.security import LoginAttempt, TokenBlacklist, UserSession, PasswordHistory
from app.models.resume import Resume
from app.models.interview import InterviewSession, InterviewQuestion
from app.models.security import LoginAttempt, TokenBlacklist, UserSession
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def drop_db() -> None:
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        drop_db()
    init_db() 