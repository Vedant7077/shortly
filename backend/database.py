
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Primary database: handles writes
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://shortly_user:shortly_dev_password@localhost:5432/shortly"
)

# Read replica: handles read queries
READ_DATABASE_URL = os.getenv(
    "READ_DATABASE_URL",
    DATABASE_URL
)

# Primary engine
write_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=2,
    pool_timeout=30
)

# Read engine
read_engine = create_engine(
    READ_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=2,
    pool_timeout=30
)

# Database sessions
WriteSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=write_engine
)

ReadSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=read_engine
)

# Keep existing compatibility for migrations and other modules
engine = write_engine
SessionLocal = WriteSessionLocal

Base = declarative_base()


# Write database dependency
def get_write_db():
    db = WriteSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Read database dependency
def get_read_db():
    db = ReadSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Existing dependency compatibility
def get_db():
    yield from get_write_db()
