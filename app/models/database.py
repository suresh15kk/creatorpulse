from sqlalchemy import (
    create_engine, Column, String,
    Text, DateTime, Boolean, Integer
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email         = Column(String(255), unique=True, nullable=False)
    name          = Column(String(255))
    hashed_password = Column(String(255))
    created_at    = Column(DateTime, default=datetime.utcnow)
    is_active     = Column(Boolean, default=True)

class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = Column(UUID(as_uuid=True), nullable=False)
    platform            = Column(String(50), nullable=False)
    access_token        = Column(Text, nullable=False)
    refresh_token       = Column(Text)
    expires_at          = Column(DateTime)
    platform_user_id    = Column(String(255))
    platform_username   = Column(String(255))
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow)

class Digest(Base):
    __tablename__ = "digests"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = Column(UUID(as_uuid=True), nullable=False)
    date                = Column(DateTime, default=datetime.utcnow)
    summary             = Column(Text)
    sentiment           = Column(String(20))
    total_comments      = Column(Integer, default=0)
    top_topics          = Column(Text)
    platforms_included  = Column(Text)
    raw_data            = Column(Text)
    created_at          = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), nullable=False)
    platform     = Column(String(50))
    external_id  = Column(String(255))
    author       = Column(String(255))
    content      = Column(Text)
    sentiment    = Column(String(20))
    topic        = Column(String(100))
    post_id      = Column(String(255))
    fetched_at   = Column(DateTime, default=datetime.utcnow)

def create_tables():
    Base.metadata.create_all(bind=engine)