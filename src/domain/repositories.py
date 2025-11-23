"""
Data Access Repositories for Marcus AI Avatar.

Implements the Repository pattern to abstract database operations
and decouple business logic from SQLAlchemy details.
"""

import uuid
from datetime import datetime
from typing import Generic, TypeVar, Type, Optional, List, Sequence, Any

from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.models import (
    Base, User, Session, Message, PADState, Pattern, Strategy, Event, BehavioralState
)

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Abstract base repository implementing common CRUD operations.
    """

    def __init__(self, session: AsyncSession, model_cls: Type[T]):
        self.session = session
        self.model_cls = model_cls

    async def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by primary key."""
        return await self.session.get(self.model_cls, id)

    async def get_all(self) -> Sequence[T]:
        """Get all entities."""
        stmt = select(self.model_cls)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    def add(self, entity: T) -> T:
        """Add entity to session (needs commit)."""
        self.session.add(entity)
        return entity

    async def save(self, entity: T) -> T:
        """Add and flush entity (updates ID but doesn't commit transaction)."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: Any) -> bool:
        """Delete entity by ID."""
        entity = await self.get_by_id(id)
        if entity:
            await self.session.delete(entity)
            return True
        return False


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_external_id(self, external_id: str) -> Optional[User]:
        """Find user by external identifier."""
        stmt = select(User).where(User.external_id == external_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_user(self, external_id: str, display_name: str = None) -> User:
        """Get existing user or create new one."""
        user = await self.get_by_external_id(external_id)
        if not user:
            user = User(external_id=external_id, display_name=display_name)
            await self.save(user)
        elif display_name and user.display_name != display_name:
            user.display_name = display_name
            user.last_active = datetime.utcnow()
            await self.session.flush()
        return user


class SessionRepository(BaseRepository[Session]):
    """Repository for Session operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Session)

    async def get_active_session(self, user_id: uuid.UUID) -> Optional[Session]:
        """Get the most recent active session for a user."""
        stmt = (
            select(Session)
            .where(Session.user_id == user_id)
            .where(Session.ended_at.is_(None))
            .order_by(desc(Session.started_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_session(self, user_id: uuid.UUID) -> Session:
        """Create a new session for the user."""
        # Close any existing open sessions first (optional, but good for hygiene)
        active = await self.get_active_session(user_id)
        if active:
            active.ended_at = datetime.utcnow()
            
        session = Session(user_id=user_id)
        return await self.save(session)

    async def get_user_sessions(self, user_id: uuid.UUID, limit: int = 10) -> Sequence[Session]:
        """Get recent sessions for a user."""
        stmt = (
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(desc(Session.started_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_full_history(self, session_id: uuid.UUID) -> Sequence[Message]:
        """Get all messages for a session including PAD states."""
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at)
            .options(
                selectinload(Message.pad_state),
                selectinload(Message.behavioral_state)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


class MessageRepository(BaseRepository[Message]):
    """Repository for Message operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def add_message(
        self, 
        session_id: uuid.UUID, 
        role: str, 
        content: str, 
        metadata: dict = None
    ) -> Message:
        """Add a message to the session."""
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            metadata_=metadata or {}
        )
        await self.save(message)
        
        # Update session turn count (if user message)
        if role == "user":
            stmt = (
                update(Session)
                .where(Session.session_id == session_id)
                .values(total_turns=Session.total_turns + 1)
            )
            await self.session.execute(stmt)
            
        return message


class PADStateRepository(BaseRepository[PADState]):
    """Repository for PAD State operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, PADState)

    async def record_state(
        self,
        session_id: uuid.UUID,
        pleasure: float,
        arousal: float,
        dominance: float,
        quadrant: str,
        message_id: uuid.UUID = None
    ) -> PADState:
        """Record a new PAD state."""
        state = PADState(
            session_id=session_id,
            message_id=message_id,
            pleasure=pleasure,
            arousal=arousal,
            dominance=dominance,
            quadrant=quadrant
        )
        return await self.save(state)

    async def get_latest(self, session_id: uuid.UUID) -> Optional[PADState]:
        """Get the most recent PAD state for a session."""
        stmt = (
            select(PADState)
            .where(PADState.session_id == session_id)
            .order_by(desc(PADState.recorded_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_history(self, session_id: uuid.UUID, limit: int = 10) -> Sequence[PADState]:
        """Get recent PAD history."""
        stmt = (
            select(PADState)
            .where(PADState.session_id == session_id)
            .order_by(desc(PADState.recorded_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        # Return reversed so it's chronological
        return list(reversed(result.scalars().all()))


class BehavioralRepository(BaseRepository[BehavioralState]):
    """Repository for Behavioral State operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, BehavioralState)

    async def record_state(
        self,
        session_id: uuid.UUID,
        relationship_stage: str,
        communication_style: str,
        crisis_level: int,
        flow_data: dict,
        message_id: uuid.UUID = None
    ) -> BehavioralState:
        """Record a new behavioral state."""
        state = BehavioralState(
            session_id=session_id,
            message_id=message_id,
            relationship_stage=relationship_stage,
            communication_style=communication_style,
            crisis_level=crisis_level,
            flow_data=flow_data
        )
        return await self.save(state)




