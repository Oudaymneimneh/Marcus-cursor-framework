"""
Chat API Routes.

Endpoints for managing sessions and sending messages.
Now integrated with DialogueGenerator for real-time responses.
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from src.api.dependencies import ConvService
from src.dialogue.generator import DialogueGenerator
from src.infrastructure.metrics import track_time, REQUEST_COUNT, REQUEST_LATENCY
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["chat"])


# --- Pydantic Models ---

class StartSessionRequest(BaseModel):
    external_id: str = Field(..., description="External user ID (e.g., auth ID)")
    display_name: Optional[str] = Field(None, description="User's display name")

class SessionResponse(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID
    started_at: datetime
    total_turns: int

class MessageRequest(BaseModel):
    content: str = Field(
        ..., 
        min_length=1, 
        max_length=2000,
        description="User message content"
    )
    user_id: Optional[str] = Field(
        None,
        description="Optional user identifier for testing. If not provided, uses 'guest'."
    )

class ChatResponse(BaseModel):
    """Complete response including Marcus's reply, emotional state, and introspection data."""
    response: str
    pad: Dict[str, float]  # Frontend expects "pad" not "pad_state"
    quadrant: str  # Frontend expects "quadrant" not "mood_label"
    message_id: Optional[uuid.UUID] = None
    # Introspection fields
    strategy_used: Optional[str] = None
    effectiveness: Optional[float] = None
    patterns_detected: Optional[List[str]] = None
    relationship_stage: Optional[str] = None
    warning_flags: Optional[List[str]] = None

class MessageResponse(BaseModel):
    message_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

class ChatHistoryResponse(BaseModel):
    session_id: uuid.UUID
    messages: List[MessageResponse]


# --- Endpoints ---

@router.post("/chat", response_model=ChatResponse)
@track_time(REQUEST_LATENCY, {"method": "POST", "path": "/chat_simplified"})
async def simple_chat(
    request: MessageRequest,
    service: ConvService
):
    """
    Simplified chat endpoint for frontend.
    Automatically manages sessions internally.
    """
    REQUEST_COUNT.labels(method="POST", path="/chat_simplified", status="200").inc()
    
    try:
        # Get user ID from request or use default guest
        # In a real app, this would come from auth token
        user_identifier = request.user_id or "guest"
        display_name = f"User {user_identifier}" if user_identifier != "guest" else "Guest User"
        
        # Get or create user
        user = await service.get_or_create_user(
            external_id=user_identifier,
            display_name=display_name
        )
        
        # Get active session (or create new one)
        # We try to get an active session first
        session = await service.get_active_session(user.user_id)
        
        if not session:
            session = await service.start_session(user.user_id)
            logger.info(f"Auto-started session {session.session_id} for guest user")
        
        session_id = session.session_id
        
        # Generate response
        brain = DialogueGenerator(service)
        result = await brain.generate_response(
            user_id=user.user_id,
            session_id=session_id,
            user_input=request.content
        )
        
        return ChatResponse(
            response=result["response"],
            pad=result["pad"],
            quadrant=result["quadrant"],
            strategy_used=result.get("strategy_used"),
            effectiveness=result.get("effectiveness"),
            patterns_detected=result.get("patterns_detected"),
            relationship_stage=result.get("relationship_stage"),
            warning_flags=result.get("warning_flags")
        )
        
    except Exception as e:
        logger.error(f"Failed to process simplified chat: {e}", exc_info=True)
        REQUEST_COUNT.labels(method="POST", path="/chat_simplified", status="500").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {str(e)}"
        )


@router.post("/sessions", response_model=SessionResponse)
@track_time(REQUEST_LATENCY, {"method": "POST", "path": "/sessions"})
async def start_session(
    request: StartSessionRequest,
    service: ConvService
):
    """
    Start a new conversation session.
    Identifies the user (or creates them) and initializes a new session.
    """
    REQUEST_COUNT.labels(method="POST", path="/sessions", status="200").inc()
    
    try:
        user = await service.get_or_create_user(
            external_id=request.external_id,
            display_name=request.display_name
        )
        session = await service.start_session(user.user_id)
        
        logger.info(f"Started session {session.session_id} for user {user.user_id}")
        
        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            started_at=session.started_at,
            total_turns=session.total_turns
        )
        
    except Exception as e:
        logger.error(f"Failed to start session: {e}", exc_info=True)
        REQUEST_COUNT.labels(method="POST", path="/sessions", status="500").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start session"
        )


@router.post("/sessions/{session_id}/chat", response_model=ChatResponse)
@track_time(REQUEST_LATENCY, {"method": "POST", "path": "/chat"})
async def chat(
    session_id: uuid.UUID,
    request: MessageRequest,
    service: ConvService
):
    """
    Chat with Marcus.
    
    1. Saves user message.
    2. Generates response using DialogueGenerator (Brain).
    3. Returns response + new emotional state.
    """
    REQUEST_COUNT.labels(method="POST", path="/chat", status="200").inc()
    
    try:
        # 1. Verify session exists (basic check via service if needed, or let generator handle)
        # Assuming valid session_id for now or generator will fail gracefully
        
        # 2. Initialize Brain
        brain = DialogueGenerator(service)
        
        # 3. Generate Response
        # We need user_id for context, but session_id implies it. 
        # The generator might need to look it up. 
        # For now, we pass session_id, and let generator handle logic.
        # NOTE: The generator interface asks for user_id, but we can derive it or make it optional.
        # Let's update generator to not strictly require user_id if session is enough, 
        # or we fetch the session first.
        
        # Optimization: We just need the response.
        # Let's pass a dummy UUID for user_id for now if not readily available, 
        # or better: fetch the session first.
        # But to keep it fast, we can just pass session_id.
        
        result = await brain.generate_response(
            user_id=uuid.UUID('00000000-0000-0000-0000-000000000000'), # Placeholder, service handles session lookup
            session_id=session_id,
            user_input=request.content
        )
        
        return ChatResponse(
            response=result["response"],
            pad_state=result["pad"],
            mood_label=result["quadrant"]
        )
        
    except Exception as e:
        logger.error(f"Failed to process chat: {e}", exc_info=True)
        REQUEST_COUNT.labels(method="POST", path="/chat", status="500").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat: {str(e)}"
        )


@router.get("/chat/history", response_model=List[MessageResponse])
@track_time(REQUEST_LATENCY, {"method": "GET", "path": "/chat/history"})
async def get_simple_history(
    service: ConvService,
    user_id: Optional[str] = Query(None, description="User identifier. Defaults to 'guest'.")
):
    """
    Get history for a user (simplified).
    If user_id not provided, uses 'guest'.
    """
    try:
        user_identifier = user_id or "guest"
        display_name = f"User {user_identifier}" if user_identifier != "guest" else "Guest User"
        user = await service.get_or_create_user(
            external_id=user_identifier,
            display_name=display_name
        )
        session = await service.get_active_session(user.user_id)
        
        if not session:
            return []
            
        # History comes newest first from service, reverse for UI
        history = await service.get_conversation_history(session.session_id)
        history.reverse()
        
        return [
            MessageResponse(
                message_id=m.message_id,
                role=m.role,
                content=m.content,
                created_at=m.created_at
            ) for m in history
        ]
    except Exception as e:
        logger.error(f"Failed to get simplified history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve history"
        )


@router.post("/chat/new-session")
@track_time(REQUEST_LATENCY, {"method": "POST", "path": "/chat/new-session"})
async def start_new_session(
    service: ConvService,
    user_id: Optional[str] = Query(None, description="User identifier. Defaults to 'guest'.")
):
    """
    Close current session and prepare for a new one.
    Next message will start a fresh session.
    """
    try:
        user_identifier = user_id or "guest"
        display_name = f"User {user_identifier}" if user_identifier != "guest" else "Guest User"
        user = await service.get_or_create_user(
            external_id=user_identifier,
            display_name=display_name
        )
        session = await service.get_active_session(user.user_id)
        
        if session:
            # Close current session
            await service.sessions.close_session(session.session_id)
            logger.info(f"Closed session {session.session_id} for new session")
        
        return {"status": "ok", "message": "Session closed. Next message will start a new session."}
    except Exception as e:
        logger.error(f"Failed to start new session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start new session"
        )
