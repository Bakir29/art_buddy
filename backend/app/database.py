from sqlalchemy import create_engine, TypeDecorator, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from app.config import settings
import uuid

from sqlalchemy import create_engine, TypeDecorator, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from app.config import settings
import uuid

# PostgreSQL-optimized UUID type
class UUID(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL's UUID type, otherwise uses String(36).
    """
    impl = PostgresUUID(as_uuid=True)
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        else:
            return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)

# Configure PostgreSQL engine
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
