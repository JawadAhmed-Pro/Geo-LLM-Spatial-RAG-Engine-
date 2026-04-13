import asyncio
import json
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

from .spatial_chain import process_spatial_query
from .database import get_db, Conversation, Message, init_db

app = FastAPI(title="Geo-LLM Spatial RAG Engine")

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = 1

class HistoryResponse(BaseModel):
    role: str
    content: str
    sql_query: Optional[str] = None
    geojson: Optional[dict] = None

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/history", response_model=List[HistoryResponse])
def get_chat_history(conversation_id: int = 1, db: Session = Depends(get_db)):
    """Fetch all previous messages for a specific conversation."""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        return []
    
    return [
        HistoryResponse(
            role=msg.role,
            content=msg.content,
            sql_query=msg.sql_query,
            geojson=msg.geojson
        ) for msg in conversation.messages
    ]

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Standard JSON endpoint that now persists history.
    """
    # 1. Get or Create Conversation
    conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
    if not conversation:
        conversation = Conversation(id=request.conversation_id)
        db.add(conversation)
        db.commit()

    # 2. Save User Message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_msg)
    db.commit()

    # 3. Process AI Response
    result = process_spatial_query(request.message)
    
    # 4. Save AI Response
    ai_msg = Message(
        conversation_id=conversation.id,
        role="ai",
        content=result.get("answer"),
        sql_query=result.get("sql"),
        geojson=result.get("geojson")
    )
    db.add(ai_msg)
    db.commit()

    return result

@app.post("/api/chat/clear")
def clear_history(conversation_id: int = 1, db: Session = Depends(get_db)):
    """Wipes the history for a conversation."""
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    db.commit()
    return {"status": "History cleared"}
