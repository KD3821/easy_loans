import sys
from contextlib import contextmanager

sys.path = ['', '..'] + sys.path[1:]
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from settings import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
Session = sessionmaker(bind=engine)
db_session = Session()


@contextmanager
def session_scope() -> Session:
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
