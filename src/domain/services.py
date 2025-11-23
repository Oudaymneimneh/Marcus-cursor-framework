"""
Domain Services for Marcus AI Avatar.

Orchestrates business logic and data persistence using Repositories.
Serves as the bridge between the API layer and the Data Access layer.
"""

import uuid
from typing import Optional, Tuple, Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import User, Session, Message, PADState
from src.domain.repositories import (
    UserRepository,
    SessionRepository,
    MessageRepository,
    PADStateRepository,
    BehavioralRepository
)


class ConversationService:
    """
    Service for managing conversation flow and persistence.
    """

    def __init__(self, db_session: AsyncSession):
        self.session = db_session
        self.users = UserRepository(db_session)
        self.sessions = SessionRepository(db_session)
        self.messages = MessageRepository(db_session)
        self.pad_states = PADStateRepository(db_session)
        self.behavioral = BehavioralRepository(db_session)

    async def get_or_create_user(self, external_id: str, display_name: str = None) -> User:
        """Identify and retrieve a user, creating if necessary."""
        return await self.users.ensure_user(external_id, display_name)

    async def start_session(self, user_id: uuid.UUID) -> Session:
        """Start a new conversation session for the user."""
        return await self.sessions.create_session(user_id)

    async def get_active_session(self, user_id: uuid.UUID) -> Optional[Session]:
        """Get the current active session for the user."""
        return await self.sessions.get_active_session(user_id)

    async def get_user_sessions(self, user_id: uuid.UUID, limit: int = 10) -> Sequence[Session]:
        """Get user's recent sessions."""
        return await self.sessions.get_user_sessions(user_id, limit)

    async def add_user_message(
        self, 
        session_id: uuid.UUID, 
        content: str
    ) -> Message:
        """Record a user message."""
        message = await self.messages.add_message(
            session_id=session_id,
            role="user",
            content=content
        )
        return message

    async def add_system_message(
        self, 
        session_id: uuid.UUID, 
        content: str,
        pad_state: dict = None,
        behavioral_state: dict = None
    ) -> Message:
        """
        Record a system (Marcus) response, including emotional state.
        
        Args:
            session_id: UUID of the session.
            content: The text response.
            pad_state: Dict with keys 'pleasure', 'arousal', 'dominance', 'quadrant'.
            behavioral_state: Dict with keys 'relationship_stage', 'communication_style', etc.
        """
        # 1. Save Message
        message = await self.messages.add_message(
            session_id=session_id,
            role="assistant",
            content=content
        )

        # 2. Save PAD State if provided
        if pad_state:
            await self.pad_states.record_state(
                session_id=session_id,
                message_id=message.message_id,
                pleasure=pad_state.get("pleasure", 0.0),
                arousal=pad_state.get("arousal", 0.0),
                dominance=pad_state.get("dominance", 0.0),
                quadrant=pad_state.get("quadrant", "Neutral")
            )

        # 3. Save Behavioral State if provided
        if behavioral_state:
            await self.behavioral.record_state(
                session_id=session_id,
                message_id=message.message_id,
                relationship_stage=behavioral_state.get("relationship_stage", "Stranger"),
                communication_style=behavioral_state.get("communication_style", "Stoic"),
                crisis_level=int(behavioral_state.get("crisis_level", 0)),
                flow_data=behavioral_state.get("flow_data", {})
            )

        return message

    async def get_conversation_history(self, session_id: uuid.UUID) -> Sequence[Message]:
        """Get full conversation history."""
        return await self.sessions.get_full_history(session_id)

    async def get_emotional_history(self, session_id: uuid.UUID, limit: int = 10) -> Sequence[PADState]:
        """Get recent emotional states."""
        return await self.pad_states.get_history(session_id, limit)




