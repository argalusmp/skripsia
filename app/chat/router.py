from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List

from app.auth.dependencies import get_current_user
from app.chat.models import (
    Conversation, Message, ConversationCreate, ConversationResponse,
    ConversationWithMessages, ChatRequest, ChatResponse, MessageResponse
)
from app.chat.service import generate_response
from app.database import get_db
from app.users.models import User
from app.utils.timezone import get_utc_now  # Import utility function

router = APIRouter()

@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use utility function for consistent UTC time
    current_utc = get_utc_now()
    
    # Check if conversation exists or create a new one
    if chat_request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation with default title (first message content)
        title_preview = chat_request.message[:30] + "..." if len(chat_request.message) > 30 else chat_request.message
        conversation = Conversation(
            user_id=current_user.id, 
            title=title_preview,
            created_at=current_utc,
            updated_at=current_utc
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_request.message,
        created_at=current_utc
    )
    db.add(user_message)
    db.commit()
    
    # Get conversation history for context
    conversation_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).all()
    
    # Generate response using RAG
    history = [(msg.role, msg.content) for msg in conversation_messages]
    response_text = generate_response(chat_request.message, history)
    
    # Save assistant message with same timestamp
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        created_at=current_utc  # Use same timestamp
    )
    db.add(assistant_message)
    
    # Update conversation's updated_at timestamp
    conversation.updated_at = current_utc
    db.commit()
    db.refresh(assistant_message)
    
    return {
        "message": assistant_message,
        "conversation_id": conversation.id
    }

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    
    return conversations

@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@router.delete("/conversations/{conversation_id}", status_code=200)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete all messages in the conversation
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    
    # Delete the conversation
    db.delete(conversation)
    db.commit()
    
    return {"detail": "Conversation deleted successfully"}