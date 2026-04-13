import json
from datetime import datetime
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from .config import settings

# Primary engine (Admin level - for system tasks and saving history)
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Reader engine (Restricted - for executing LLM-generated SQL)
reader_engine = create_engine(settings.reader_database_url)

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String) # 'user' or 'ai'
    content = Column(String)
    sql_query = Column(String, nullable=True) # If it's an AI message
    geojson = Column(JSON, nullable=True)     # If it's an AI message
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="messages")

def execute_read_only_query(query: str):
    """Executes a query using the RESTRICTED reader account."""
    with reader_engine.connect() as conn:
        result = conn.execute(text(query))
        columns = result.keys()
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]

def get_db():
    """Admin DB session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create tables (Should be run by the Admin engine)."""
    Base.metadata.create_all(bind=engine)
