"""
SQLAlchemy Domain Models for Marcus AI Avatar.

Defines the database schema mappings for Users, Sessions, Messages,
and behavioral/emotional state tracking.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class User(Base):
    """
    Represents a human user interacting with Marcus.
    """
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSONB, server_default="{}", nullable=False
    )

    # Relationships
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    patterns: Mapped[List["Pattern"]] = relationship(
        "Pattern", back_populates="user", cascade="all, delete-orphan"
    )
    strategies: Mapped[List["Strategy"]] = relationship(
        "Strategy", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(user_id={self.user_id}, name={self.display_name})>"


class Session(Base):
    """
    Represents a conversation session between a User and Marcus.
    """
    __tablename__ = "sessions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_turns: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSONB, server_default="{}", nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[List["Message"]] = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at"
    )
    pad_states: Mapped[List["PADState"]] = relationship(
        "PADState", back_populates="session", cascade="all, delete-orphan"
    )
    behavioral_states: Mapped[List["BehavioralState"]] = relationship(
        "BehavioralState", back_populates="session", cascade="all, delete-orphan"
    )
    events: Mapped[List["Event"]] = relationship(
        "Event", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session(session_id={self.session_id}, turns={self.total_turns})>"


class Message(Base):
    """
    Represents a single message in a conversation (User or System).
    """
    __tablename__ = "messages"

    message_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSONB, server_default="{}", nullable=False
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="messages")
    pad_state: Mapped[Optional["PADState"]] = relationship(
        "PADState", back_populates="message", uselist=False, cascade="all, delete-orphan"
    )
    behavioral_state: Mapped[Optional["BehavioralState"]] = relationship(
        "BehavioralState", back_populates="message", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.message_id}, role={self.role}, length={len(self.content)})>"


class PADState(Base):
    """
    Represents the Pleasure-Arousal-Dominance emotional state
    associated with a specific message or moment in a session.
    """
    __tablename__ = "pad_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # BigSerial
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=True, unique=True
    )
    
    pleasure: Mapped[float] = mapped_column(Float, nullable=False)
    arousal: Mapped[float] = mapped_column(Float, nullable=False)
    dominance: Mapped[float] = mapped_column(Float, nullable=False)
    quadrant: Mapped[str] = mapped_column(String(50), nullable=False)
    
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="pad_states")
    message: Mapped["Message"] = relationship("Message", back_populates="pad_state")

    __table_args__ = (
        Index("idx_pad_session_recorded", "session_id", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<PADState(P={self.pleasure:.2f}, A={self.arousal:.2f}, D={self.dominance:.2f})>"


class Pattern(Base):
    """
    Represents a detected behavioral pattern for a user (e.g., "Catastrophizing").
    """
    __tablename__ = "patterns"

    pattern_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    pattern_name: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    first_noticed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_confirmed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    evidence: Mapped[List[str]] = mapped_column(JSONB, server_default="[]", nullable=False)
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSONB, server_default="{}", nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="patterns")

    def __repr__(self) -> str:
        return f"<Pattern(name={self.pattern_name}, confidence={self.confidence:.2f})>"


class Strategy(Base):
    """
    Represents a communication strategy attempted with a user.
    """
    __tablename__ = "strategies"

    strategy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    strategy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    effectiveness: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    times_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    last_used: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata", JSONB, server_default="{}", nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="strategies")

    def __repr__(self) -> str:
        return f"<Strategy(name={self.strategy_name}, effect={self.effectiveness:.2f})>"


class Event(Base):
    """
    Represents a significant system or interaction event (e.g., Crisis Alert).
    """
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # BigSerial
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, server_default="{}", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="events")

    __table_args__ = (
        Index("idx_event_type_created", "event_type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Event(type={self.event_type}, id={self.event_id})>"


class BehavioralState(Base):
    """
    Snapshots the full behavioral context (Relationship, Style, Flow)
    at a specific moment in time.
    """
    __tablename__ = "behavioral_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False
    )
    message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=True, unique=True
    )
    
    relationship_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    communication_style: Mapped[str] = mapped_column(String(50), nullable=False)
    crisis_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    flow_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, server_default="{}", nullable=False
    )  # Stores pacing, turn_count, topic_depth
    
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="behavioral_states")
    message: Mapped["Message"] = relationship("Message", back_populates="behavioral_state")

    def __repr__(self) -> str:
        return f"<BehavioralState(stage={self.relationship_stage}, crisis={self.crisis_level})>"




