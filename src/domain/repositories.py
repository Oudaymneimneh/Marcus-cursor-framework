"""
Data Access Repositories for Marcus AI Avatar.

Implements the Repository pattern to abstract database operations
and decouple business logic from SQLAlchemy details.
"""

import uuid
from datetime import datetime, timezone
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
            user.last_active = datetime.now(timezone.utc)
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
            active.ended_at = datetime.now(timezone.utc)
            
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

    async def close_session(self, session_id: uuid.UUID) -> Optional[Session]:
        """Close a session by setting ended_at timestamp."""
        session = await self.get_by_id(session_id)
        if session and not session.ended_at:
            session.ended_at = datetime.now(timezone.utc)
            return await self.save(session)
        return session

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
    """
    Repository for PAD State operations.
    
    INTROSPECTION QUERIES THIS SUPPORTS:
    1. What's my current emotional state?
    2. Is engagement increasing or decreasing?
    3. How long have I been in negative state?
    4. What's the emotional trajectory this session?
    """

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
        """Q: What's my current emotional state?"""
        stmt = (
            select(PADState)
            .where(PADState.session_id == session_id)
            .order_by(desc(PADState.recorded_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_history(self, session_id: uuid.UUID, limit: int = 10) -> Sequence[PADState]:
        """Q: How has emotion evolved this session?"""
        stmt = (
            select(PADState)
            .where(PADState.session_id == session_id)
            .order_by(desc(PADState.recorded_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        # Return reversed so it's chronological
        return list(reversed(result.scalars().all()))
    
    async def engagement_trend(self, session_id: uuid.UUID) -> str:
        """
        Q: Is engagement increasing, decreasing, or stable?
        
        Analyzes arousal levels (engagement proxy) over recent history.
        Compares last 3 states vs previous 3 states.
        
        Returns:
            "increasing" | "decreasing" | "stable" | "insufficient_data"
        """
        history = await self.get_history(session_id, limit=6)
        
        if len(history) < 3:
            return "insufficient_data"
        
        # Compare recent 3 vs older states
        recent_arousal = sum(s.arousal for s in history[-3:]) / 3
        
        if len(history) >= 6:
            older_arousal = sum(s.arousal for s in history[:3]) / 3
        else:
            # Use baseline of 0 if not enough history
            older_arousal = 0.0
        
        diff = recent_arousal - older_arousal
        
        if diff > 0.2:
            return "increasing"
        elif diff < -0.2:
            return "decreasing"
        else:
            return "stable"
    
    async def time_in_negative_state(self, session_id: uuid.UUID) -> int:
        """
        Q: How many consecutive turns have I been in negative pleasure?
        
        Used to detect prolonged negative states that require intervention.
        
        Returns:
            Number of consecutive states with pleasure < 0
        """
        history = await self.get_history(session_id, limit=10)
        
        consecutive = 0
        for state in reversed(history):
            if state.pleasure < 0:
                consecutive += 1
            else:
                break
        
        return consecutive


class BehavioralRepository(BaseRepository[BehavioralState]):
    """
    Repository for Behavioral State operations.
    
    INTROSPECTION QUERIES THIS SUPPORTS:
    1. What relationship stage am I at with this user?
    2. What communication style am I using?
    3. Is there a crisis signal?
    """

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
    
    async def get_latest(self, session_id: uuid.UUID) -> Optional[BehavioralState]:
        """Q: What's the current behavioral context?"""
        stmt = (
            select(BehavioralState)
            .where(BehavioralState.session_id == session_id)
            .order_by(desc(BehavioralState.recorded_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class PatternRepository(BaseRepository[Pattern]):
    """
    Repository for Pattern detection and tracking.
    
    INTROSPECTION QUERIES THIS SUPPORTS:
    1. What behavioral patterns have I detected for this user?
    2. What's my confidence level in each pattern?
    3. What evidence supports these patterns?
    4. Should I adjust pattern confidence?
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Pattern)

    async def get_active_patterns(
        self, 
        user_id: uuid.UUID, 
        min_confidence: float = 0.5
    ) -> Sequence[Pattern]:
        """
        Q: What patterns am I tracking for this user?
        
        Returns patterns above confidence threshold, ordered by most recent.
        """
        stmt = (
            select(Pattern)
            .where(Pattern.user_id == user_id)
            .where(Pattern.confidence >= min_confidence)
            .order_by(desc(Pattern.last_confirmed))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_or_create_pattern(
        self,
        user_id: uuid.UUID,
        pattern_name: str,
        initial_confidence: float = 0.5
    ) -> Pattern:
        """Get existing pattern or create new one."""
        stmt = (
            select(Pattern)
            .where(Pattern.user_id == user_id)
            .where(Pattern.pattern_name == pattern_name)
        )
        result = await self.session.execute(stmt)
        pattern = result.scalar_one_or_none()
        
        if not pattern:
            pattern = Pattern(
                user_id=user_id,
                pattern_name=pattern_name,
                confidence=initial_confidence,
                evidence=[]
            )
            await self.save(pattern)
        
        return pattern
    
    async def update_pattern_confidence(
        self,
        pattern_id: uuid.UUID,
        new_evidence: str,
        confidence_delta: float
    ):
        """
        Q: How should I adjust confidence based on new evidence?
        
        Updates pattern confidence and adds evidence.
        Confidence is clamped to [0.0, 1.0] range.
        """
        pattern = await self.get_by_id(pattern_id)
        if pattern:
            # Adjust confidence within valid range
            pattern.confidence = max(0.0, min(1.0, pattern.confidence + confidence_delta))
            pattern.last_confirmed = datetime.now(timezone.utc)
            
            # Add evidence to list
            if isinstance(pattern.evidence, list):
                pattern.evidence.append(new_evidence)
            else:
                pattern.evidence = [new_evidence]
            
            await self.session.flush()


class StrategyRepository(BaseRepository[Strategy]):
    """
    Repository for Strategy effectiveness tracking.
    
    INTROSPECTION QUERIES THIS SUPPORTS:
    1. Which strategies have highest effectiveness with this user?
    2. Am I overusing a strategy?
    3. What should I try next based on data?
    4. How do I update effectiveness after each use?
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Strategy)

    async def get_ranked_strategies(
        self,
        user_id: uuid.UUID,
        limit: int = 5
    ) -> Sequence[Strategy]:
        """
        Q: What strategies work best with this user?
        
        Returns top strategies by effectiveness score.
        """
        stmt = (
            select(Strategy)
            .where(Strategy.user_id == user_id)
            .order_by(desc(Strategy.effectiveness))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def record_outcome(
        self,
        user_id: uuid.UUID,
        strategy_name: str,
        outcome_score: float,
        context: str = None
    ) -> Strategy:
        """
        Q: How effective was the strategy I just used?
        
        Updates effectiveness using weighted average:
        new_eff = (old_eff * times_used + outcome_score) / (times_used + 1)
        
        Args:
            user_id: User this strategy was used with
            strategy_name: Name of strategy (e.g., "supportive", "energizing")
            outcome_score: Effectiveness score 0.0 to 1.0
            context: Optional context about this use
        
        Returns:
            Updated or newly created Strategy record
        """
        # Check if strategy exists
        stmt = (
            select(Strategy)
            .where(Strategy.user_id == user_id)
            .where(Strategy.strategy_name == strategy_name)
        )
        result = await self.session.execute(stmt)
        strategy = result.scalar_one_or_none()
        
        if strategy:
            # Update with weighted average
            total = strategy.times_used
            old_eff = strategy.effectiveness
            new_eff = ((old_eff * total) + outcome_score) / (total + 1)
            
            strategy.effectiveness = new_eff
            strategy.times_used += 1
            strategy.last_used = datetime.now(timezone.utc)
            
            if context:
                strategy.context = context
        else:
            # Create new strategy record
            strategy = Strategy(
                user_id=user_id,
                strategy_name=strategy_name,
                effectiveness=outcome_score,
                times_used=1,
                context=context or f"First use, outcome: {outcome_score:.2f}"
            )
            self.session.add(strategy)
        
        await self.session.flush()
        return strategy
    
    async def get_recent_usage_count(
        self,
        user_id: uuid.UUID,
        strategy_name: str,
        hours: int = 1
    ) -> int:
        """
        Q: Have I overused this strategy recently?
        
        Checks if strategy was used recently (within specified hours).
        Returns usage count if recent, 0 otherwise.
        """
        stmt = (
            select(Strategy)
            .where(Strategy.user_id == user_id)
            .where(Strategy.strategy_name == strategy_name)
        )
        result = await self.session.execute(stmt)
        strategy = result.scalar_one_or_none()
        
        if not strategy:
            return 0
        
        # Check if used recently
        if not strategy.last_used:
            return 0
        
        # Ensure both datetimes are timezone-aware
        now = datetime.now(timezone.utc)
        last_used = strategy.last_used
        if last_used.tzinfo is None:
            # If naive, assume UTC
            last_used = last_used.replace(tzinfo=timezone.utc)
        
        time_since_use = (now - last_used).total_seconds()
        if time_since_use < (hours * 3600):
            return strategy.times_used
        
        return 0
    
    async def get_overall_effectiveness(self, user_id: uuid.UUID) -> float:
        """
        Q: What's the overall effectiveness across all strategies?
        
        Returns weighted average effectiveness considering usage count.
        """
        stmt = (
            select(Strategy)
            .where(Strategy.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        strategies = result.scalars().all()
        
        if not strategies:
            return 0.5  # Neutral baseline
        
        total_weight = sum(s.times_used for s in strategies)
        if total_weight == 0:
            return 0.5
        
        weighted_sum = sum(s.effectiveness * s.times_used for s in strategies)
        return weighted_sum / total_weight
    
    async def get_learning_metrics(self, user_id: uuid.UUID) -> dict:
        """
        Q: What's the learning curve for this user?
        
        Returns metrics showing effectiveness improvement over time.
        """
        stmt = (
            select(Strategy)
            .where(Strategy.user_id == user_id)
            .order_by(desc(Strategy.last_used))
        )
        result = await self.session.execute(stmt)
        strategies = result.scalars().all()
        
        total_interactions = sum(s.times_used for s in strategies)
        best_strategy = max(strategies, key=lambda s: s.effectiveness) if strategies else None
        overall_effectiveness = await self.get_overall_effectiveness(user_id)
        
        return {
            'total_interactions': total_interactions,
            'strategies_tried': len(strategies),
            'overall_effectiveness': overall_effectiveness,
            'best_strategy': best_strategy.strategy_name if best_strategy else None,
            'best_strategy_effectiveness': best_strategy.effectiveness if best_strategy else 0.0,
            'strategies': [
                {
                    'name': s.strategy_name,
                    'effectiveness': s.effectiveness,
                    'times_used': s.times_used
                }
                for s in strategies
            ]
        }




