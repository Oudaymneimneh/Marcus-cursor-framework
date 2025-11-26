"""
Marcus Introspection Service.

This is Marcus's self-awareness layer - queries data to inform real-time decisions.
MANDATORY: Called before every response generation.

INTROSPECTION QUESTIONS THIS SERVICE ANSWERS:
1. What emotional state am I in?
2. What patterns have I detected about this user?
3. What strategies work best with this user?
4. Is engagement trending up or down?
5. What relationship stage are we at?
6. Should I pivot my approach?
7. How effective was my last strategy?
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories import (
    PatternRepository,
    StrategyRepository,
    PADStateRepository,
    BehavioralRepository,
    SessionRepository
)

logger = logging.getLogger(__name__)


class IntrospectionService:
    """
    Marcus's nervous system - provides context for decision-making.
    
    This service is the bridge between stored data and real-time decisions.
    It transforms historical patterns into actionable intelligence.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.session = db_session
        self.patterns = PatternRepository(db_session)
        self.strategies = StrategyRepository(db_session)
        self.pad_states = PADStateRepository(db_session)
        self.behavioral = BehavioralRepository(db_session)
        self.sessions_repo = SessionRepository(db_session)
    
    async def prepare_response_context(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        MANDATORY call before generating response.
        Gathers all introspection data to inform strategy selection.
        
        This is Marcus asking himself:
        - What do I know about this user?
        - How is this conversation going?
        - What should I do differently?
        
        Args:
            user_id: User being responded to
            session_id: Current conversation session
        
        Returns:
            Dictionary with keys:
            - patterns: List of detected patterns (confidence >= 0.5)
            - top_strategies: Most effective strategies (top 5)
            - emotional_trend: "increasing"/"decreasing"/"stable"/"insufficient_data"
            - current_emotion: Latest PADState or None
            - relationship_stage: Current stage or "Stranger"
            - warning_flags: List of concerns requiring attention
            - negative_streak: Consecutive negative pleasure states
        """
        logger.info(f"Introspecting for user={user_id}, session={session_id}")
        
        # Gather all context in parallel for speed
        patterns = await self.patterns.get_active_patterns(user_id, min_confidence=0.5)
        strategies = await self.strategies.get_ranked_strategies(user_id, limit=5)
        trend = await self.pad_states.engagement_trend(session_id)
        current_emotion = await self.pad_states.get_latest(session_id)
        behavioral = await self.behavioral.get_latest(session_id)
        negative_streak = await self.pad_states.time_in_negative_state(session_id)
        
        # Generate warning flags based on data
        warnings = []
        if trend == "decreasing":
            warnings.append("engagement_dropping")
        if negative_streak >= 3:
            warnings.append("prolonged_negative_state")
        if not strategies:
            warnings.append("no_strategy_history")
        if current_emotion and current_emotion.arousal < -0.5:
            warnings.append("low_arousal")
        
        context = {
            "patterns": patterns,
            "top_strategies": strategies,
            "emotional_trend": trend,
            "current_emotion": current_emotion,
            "relationship_stage": behavioral.relationship_stage if behavioral else "Stranger",
            "warning_flags": warnings,
            "negative_streak": negative_streak
        }
        
        logger.info(
            f"Introspection complete: "
            f"patterns={len(patterns)}, "
            f"strategies={len(strategies)}, "
            f"trend={trend}, "
            f"warnings={warnings}"
        )
        
        return context
    
    async def select_strategy(
        self,
        context: Dict[str, Any],
        user_id: uuid.UUID
    ) -> str:
        """
        Q: What strategy should I use right now?
        
        Decision tree:
        1. Crisis handling - If prolonged negative or severe drop
        2. Engagement recovery - If engagement dropping
        3. Data-driven normal - Use highest effectiveness strategy
        4. Variety check - Avoid overusing same strategy
        5. Default fallback - "balanced" if no data
        
        Args:
            context: Output from prepare_response_context()
            user_id: User for checking recent strategy usage
        
        Returns:
            Strategy name (e.g., "supportive", "energizing", "balanced")
        """
        warnings = context.get("warning_flags", [])
        
        # Crisis handling takes priority
        if "prolonged_negative_state" in warnings:
            logger.info("Strategy: CRISIS - prolonged negative state detected")
            return "supportive"
        
        if "engagement_dropping" in warnings:
            logger.info("Strategy: RECOVERY - engagement dropping")
            return "energizing"
        
        if "low_arousal" in warnings:
            logger.info("Strategy: STIMULATION - arousal too low")
            return "engaging"
        
        # Normal operation - use data
        strategies = context.get("top_strategies", [])
        
        if not strategies:
            logger.info("Strategy: DEFAULT - no history available")
            return "balanced"
        
        # Get top strategy
        top_strategy = strategies[0].strategy_name
        
        # Check if overused recently (avoid repetition)
        times_recent = await self.strategies.get_recent_usage_count(
            user_id, 
            top_strategy, 
            hours=1
        )
        
        if times_recent >= 3 and len(strategies) > 1:
            # Try second-best to avoid repetition
            second_strategy = strategies[1].strategy_name
            logger.info(
                f"Strategy: VARIETY - {top_strategy} overused ({times_recent}x), "
                f"using {second_strategy} instead"
            )
            return second_strategy
        
        logger.info(f"Strategy: DATA-DRIVEN - {top_strategy} (eff={strategies[0].effectiveness:.2f})")
        return top_strategy
    
    async def measure_effectiveness(
        self,
        before_context: Dict[str, Any],
        after_pad: Dict[str, float]
    ) -> float:
        """
        Q: How effective was my response?
        
        Measures multiple factors:
        1. Pleasure improvement (+0.3 per 0.1 gain)
        2. Arousal improvement if was too low (+0.2 per 0.1 gain)
        3. Breaking negative streak (+0.5 bonus)
        4. Engagement trend improvement (+0.3 bonus)
        
        Args:
            before_context: Context from prepare_response_context() before response
            after_pad: PAD state after the response
        
        Returns:
            Effectiveness score 0.0 to 1.0
        """
        score = 0.5  # Baseline neutral
        
        before_emotion = before_context.get("current_emotion")
        if not before_emotion:
            # No baseline to compare - return neutral
            return score
        
        # Factor 1: Pleasure improvement
        pleasure_delta = after_pad["pleasure"] - before_emotion.pleasure
        score += pleasure_delta * 3  # Weight: 3x
        
        # Factor 2: Arousal improvement (if was too low)
        if before_emotion.arousal < 0:
            arousal_delta = after_pad["arousal"] - before_emotion.arousal
            if arousal_delta > 0:
                score += arousal_delta * 2  # Weight: 2x
        
        # Factor 3: Negative streak break
        if before_context.get("negative_streak", 0) >= 3 and after_pad["pleasure"] > 0:
            score += 0.5  # Significant bonus for breaking negative cycle
            logger.info("Effectiveness bonus: broke negative streak")
        
        # Factor 4: Engagement trend
        trend = before_context.get("emotional_trend")
        if trend == "increasing":
            score += 0.1  # Small bonus for maintaining positive trend
        elif trend == "decreasing":
            # No penalty - already captured in arousal/pleasure changes
            pass
        
        # Clamp to valid range
        final_score = max(0.0, min(1.0, score))
        
        logger.info(
            f"Effectiveness measured: {final_score:.2f} "
            f"(pleasure_delta={pleasure_delta:.2f}, "
            f"negative_streak_broken={before_context.get('negative_streak', 0) >= 3})"
        )
        
        return final_score
    
    async def detect_new_patterns(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        user_input: str
    ) -> List[str]:
        """
        Q: Should I detect any new patterns from this interaction?
        
        Simple pattern detection based on keywords and sentiment.
        In production, this would use ML/NLP for better detection.
        
        Args:
            user_id: User to track patterns for
            session_id: Current session
            user_input: User's message content
        
        Returns:
            List of newly detected or reinforced pattern names
        """
        detected = []
        
        # Simple keyword-based detection (placeholder for ML)
        lower_input = user_input.lower()
        
        # Catastrophizing pattern
        if any(word in lower_input for word in ["always", "never", "worst", "terrible", "disaster"]):
            pattern = await self.patterns.get_or_create_pattern(
                user_id, 
                "catastrophizing",
                initial_confidence=0.3
            )
            await self.patterns.update_pattern_confidence(
                pattern.pattern_id,
                f"Detected in: '{user_input[:50]}...'",
                confidence_delta=0.1
            )
            detected.append("catastrophizing")
        
        # Solution-seeking pattern
        if any(word in lower_input for word in ["how", "what should", "help me", "advice"]):
            pattern = await self.patterns.get_or_create_pattern(
                user_id,
                "solution_seeking",
                initial_confidence=0.4
            )
            await self.patterns.update_pattern_confidence(
                pattern.pattern_id,
                f"Detected in: '{user_input[:50]}...'",
                confidence_delta=0.1
            )
            detected.append("solution_seeking")
        
        if detected:
            logger.info(f"Patterns detected: {detected}")
        
        return detected
