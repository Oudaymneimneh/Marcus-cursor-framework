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
        # Lower threshold for low_arousal to -0.3 (more sensitive)
        if current_emotion and current_emotion.arousal < -0.3:
            warnings.append("low_arousal")
        # Add crisis warning for severe negative pleasure
        if current_emotion and current_emotion.pleasure < -0.5:
            warnings.append("crisis_detected")
        
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
    
    # Crisis keywords that should trigger supportive strategy
    CRISIS_KEYWORDS = [
        "can't handle", "falling apart", "give up", "panic attack",
        "can't take", "too much", "overwhelmed", "breaking down",
        "can't cope", "at my limit", "losing it", "breaking point",
        "can't breathe", "drowning", "hopeless", "desperate"
    ]
    
    # Low energy keywords that should trigger energizing strategy
    ENERGY_KEYWORDS = [
        "no motivation", "bored", "stuck in rut", "nothing excites",
        "sluggish", "can't get started", "unmotivated", "apathetic",
        "no energy", "exhausted", "drained", "listless", "numb",
        "disconnected", "empty", "going through the motions"
    ]
    
    async def select_strategy(
        self,
        context: Dict[str, Any],
        user_id: uuid.UUID,
        user_input: Optional[str] = None
    ) -> str:
        """
        Q: What strategy should I use right now?
        
        Decision tree (PRIORITY ORDER):
        1. Keyword-based crisis detection - Immediate supportive response
        2. PAD-based crisis detection - If pleasure very negative
        3. Keyword-based energy detection - If user shows low energy
        4. PAD-based energy detection - If arousal very low
        5. Pattern-based selection - Catastrophizing → reflective
        6. Warning flag handling - Prolonged negative, engagement dropping
        7. Data-driven normal - Use highest effectiveness strategy
        8. Variety check - Avoid overusing same strategy
        9. Default fallback - "balanced" if no data
        
        Args:
            context: Output from prepare_response_context()
            user_id: User for checking recent strategy usage
            user_input: Current user message for keyword analysis
        
        Returns:
            Strategy name (e.g., "supportive", "energizing", "balanced", "reflective")
        """
        warnings = context.get("warning_flags", [])
        current_emotion = context.get("current_emotion")
        patterns = context.get("patterns", [])
        
        # Normalize user input for keyword matching
        user_input_lower = user_input.lower() if user_input else ""
        
        # PRIORITY 1: Keyword-based crisis detection (most sensitive)
        if user_input_lower and any(kw in user_input_lower for kw in self.CRISIS_KEYWORDS):
            logger.info("Strategy: CRISIS_KEYWORDS - detected crisis language in user input")
            return "supportive"
        
        # PRIORITY 2: PAD-based crisis detection (pleasure < -0.5)
        if current_emotion and current_emotion.pleasure < -0.5:
            logger.info(f"Strategy: CRISIS_PAD - severe negative pleasure ({current_emotion.pleasure:.2f})")
            return "supportive"
        
        # PRIORITY 3: Warning flag crisis handling
        if "prolonged_negative_state" in warnings:
            logger.info("Strategy: CRISIS - prolonged negative state detected")
            return "supportive"
        
        # PRIORITY 4: Keyword-based energy detection
        if user_input_lower and any(kw in user_input_lower for kw in self.ENERGY_KEYWORDS):
            logger.info("Strategy: ENERGY_KEYWORDS - detected low energy language in user input")
            return "energizing"
        
        # PRIORITY 5: PAD-based energy detection (arousal < -0.3)
        if current_emotion and current_emotion.arousal < -0.3:
            logger.info(f"Strategy: ENERGY_PAD - low arousal ({current_emotion.arousal:.2f})")
            return "energizing"
        
        # PRIORITY 6: Warning flag energy handling
        if "engagement_dropping" in warnings:
            logger.info("Strategy: RECOVERY - engagement dropping")
            return "energizing"
        
        if "low_arousal" in warnings:
            logger.info("Strategy: STIMULATION - arousal too low")
            return "engaging"
        
        # PRIORITY 7: Pattern-based strategy selection
        pattern_names = [p.pattern_name for p in patterns] if patterns else []
        
        if "catastrophizing" in pattern_names:
            logger.info("Strategy: PATTERN - catastrophizing detected, using reflective")
            return "reflective"
        
        if "solution_seeking" in pattern_names:
            logger.info("Strategy: PATTERN - solution-seeking detected, using balanced")
            return "balanced"
        
        # PRIORITY 8: Normal operation - use data
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
        after_pad: Dict[str, float],
        strategy_used: Optional[str] = None
    ) -> float:
        """
        Q: How effective was my response?
        
        CALIBRATED effectiveness formula based on test scenarios:
        
        Factors (in priority order):
        1. Pleasure improvement - Weight: 2.5x (calibrated from 3.0)
        2. Arousal improvement - Always contributes, not just when negative
        3. Strategy-appropriate bonus - Reward correct strategy for context
        4. Negative streak break - Higher bonus (0.3) for breaking cycle
        5. Engagement trend bonus - Maintain momentum
        
        Expected ranges (from test scenarios):
        - Positive achievement: 0.7-1.0
        - Negative situations: 0.0-0.4
        - Neutral baseline: 0.4-0.6
        - Breaking negative streak: 0.75-1.0
        
        Args:
            before_context: Context from prepare_response_context() before response
            after_pad: PAD state after the response
            strategy_used: Strategy that was applied (for appropriate-strategy bonus)
        
        Returns:
            Effectiveness score 0.0 to 1.0
        """
        score = 0.5  # Baseline neutral
        
        before_emotion = before_context.get("current_emotion")
        if not before_emotion:
            # No baseline to compare - return neutral
            return score
        
        # Factor 1: Pleasure improvement (CALIBRATED weight: 2.5x)
        pleasure_delta = after_pad["pleasure"] - before_emotion.pleasure
        score += pleasure_delta * 2.5
        
        # Factor 2: Arousal improvement (now always contributes)
        arousal_delta = after_pad["arousal"] - before_emotion.arousal
        
        # If arousal was too low (user lethargic), reward increasing it
        if before_emotion.arousal < -0.3:
            if arousal_delta > 0:
                score += arousal_delta * 1.5  # Weight: 1.5x for energy boost
                logger.debug(f"Effectiveness: arousal boost bonus +{arousal_delta * 1.5:.2f}")
        
        # If arousal was too high (user anxious), reward decreasing it
        elif before_emotion.arousal > 0.5:
            if arousal_delta < 0:
                score += abs(arousal_delta) * 1.0  # Weight: 1.0x for calming
                logger.debug(f"Effectiveness: calming bonus +{abs(arousal_delta) * 1.0:.2f}")
        
        # Factor 3: Strategy-appropriate bonus
        if strategy_used:
            # Supportive strategy in crisis (pleasure < -0.5)
            if strategy_used == "supportive" and before_emotion.pleasure < -0.5:
                score += 0.2
                logger.debug("Effectiveness: appropriate supportive strategy +0.2")
            
            # Energizing strategy for low energy (arousal < -0.3)
            elif strategy_used == "energizing" and before_emotion.arousal < -0.3:
                score += 0.2
                logger.debug("Effectiveness: appropriate energizing strategy +0.2")
            
            # Reflective strategy for catastrophizing pattern
            elif strategy_used == "reflective":
                pattern_names = [p.pattern_name for p in before_context.get("patterns", [])]
                if "catastrophizing" in pattern_names:
                    score += 0.15
                    logger.debug("Effectiveness: appropriate reflective strategy +0.15")
        
        # Factor 4: Negative streak break (ENHANCED bonus)
        negative_streak = before_context.get("negative_streak", 0)
        if negative_streak >= 3 and after_pad["pleasure"] > 0:
            # Higher bonus for longer streaks
            streak_bonus = min(0.4, 0.2 + (negative_streak - 3) * 0.05)
            score += streak_bonus
            logger.info(f"Effectiveness bonus: broke negative streak ({negative_streak} turns) +{streak_bonus:.2f}")
        
        # Factor 5: Engagement trend maintenance
        trend = before_context.get("emotional_trend")
        if trend == "increasing":
            score += 0.1  # Bonus for maintaining positive trend
        elif trend == "stable":
            score += 0.05  # Small bonus for stability
        
        # Clamp to valid range
        final_score = max(0.0, min(1.0, score))
        
        logger.info(
            f"Effectiveness measured: {final_score:.2f} "
            f"(pleasure_delta={pleasure_delta:.2f}, arousal_delta={arousal_delta:.2f}, "
            f"strategy={strategy_used}, streak={negative_streak})"
        )
        
        return final_score
    
    async def get_learning_metrics(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Q: How am I learning what works for this user?
        
        Returns comprehensive metrics about learning progress:
        - Overall effectiveness trend
        - Best performing strategies
        - Total interactions
        - Estimated learning stage
        
        Args:
            user_id: User to get metrics for
        
        Returns:
            Dictionary with learning metrics
        """
        metrics = await self.strategies.get_learning_metrics(user_id)
        total = metrics['total_interactions']
        
        # Determine learning stage
        if total == 0:
            learning_stage = "cold_start"
            stage_description = "No data yet - will use defaults"
        elif total < 10:
            learning_stage = "warming_up"
            stage_description = "Building initial understanding"
        elif total < 50:
            learning_stage = "learning"
            stage_description = "Patterns emerging, adapting strategies"
        elif total < 100:
            learning_stage = "proficient"
            stage_description = "Good understanding of user preferences"
        else:
            learning_stage = "expert"
            stage_description = "Deep personalization active"
        
        metrics['learning_stage'] = learning_stage
        metrics['stage_description'] = stage_description
        
        # Log learning status
        logger.info(
            f"Learning metrics for user {user_id}: "
            f"stage={learning_stage}, "
            f"interactions={total}, "
            f"effectiveness={metrics['overall_effectiveness']:.2f}"
        )
        
        return metrics
    
    async def calculate_learning_curve(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Q: Am I getting better at helping this user over time?
        
        Calculates the learning curve by comparing early effectiveness
        to recent effectiveness within the current session and across sessions.
        
        Args:
            user_id: User to analyze
            session_id: Current session
        
        Returns:
            Dictionary with:
            - session_improvement: Change in effectiveness this session
            - overall_improvement: Change in effectiveness overall
            - is_improving: Boolean indicating positive trend
            - recommendation: Suggestion for next steps
        """
        # Get session history
        pad_history = await self.pad_states.get_history(session_id, limit=20)
        
        if len(pad_history) < 4:
            return {
                'session_improvement': 0.0,
                'overall_improvement': 0.0,
                'is_improving': None,  # Not enough data
                'recommendation': "Continue gathering data - need at least 4 interactions",
                'data_points': len(pad_history)
            }
        
        # Calculate session improvement (compare first half vs second half)
        mid_point = len(pad_history) // 2
        early_pleasure = sum(s.pleasure for s in pad_history[:mid_point]) / mid_point
        recent_pleasure = sum(s.pleasure for s in pad_history[mid_point:]) / (len(pad_history) - mid_point)
        
        session_improvement = recent_pleasure - early_pleasure
        
        # Get overall strategy metrics
        overall_effectiveness = await self.strategies.get_overall_effectiveness(user_id)
        
        # Determine if improving
        is_improving = session_improvement > 0.1 or overall_effectiveness > 0.6
        
        # Generate recommendation
        if session_improvement > 0.2:
            recommendation = "Excellent progress! Current approach is working well."
        elif session_improvement > 0:
            recommendation = "Positive trend detected. Continue with current strategies."
        elif session_improvement > -0.1:
            recommendation = "Stable session. Consider trying different strategies."
        else:
            recommendation = "Declining trend. May need to pivot strategy or approach."
        
        logger.info(
            f"Learning curve for user {user_id}: "
            f"session_improvement={session_improvement:.2f}, "
            f"overall_effectiveness={overall_effectiveness:.2f}, "
            f"improving={is_improving}"
        )
        
        return {
            'session_improvement': session_improvement,
            'overall_effectiveness': overall_effectiveness,
            'is_improving': is_improving,
            'recommendation': recommendation,
            'data_points': len(pad_history),
            'early_avg_pleasure': early_pleasure,
            'recent_avg_pleasure': recent_pleasure
        }
    
    # Catastrophizing pattern keywords (absolute/extreme language)
    CATASTROPHIZING_KEYWORDS = [
        "always", "never", "worst", "terrible", "disaster",
        "everything", "nothing", "ruined", "falling apart",
        "can't do anything right", "completely", "totally",
        "no one", "everyone hates", "always fail", "never works",
        "my whole life", "entire", "all the time", "every time"
    ]
    
    # False positive indicators (balanced language that contradicts catastrophizing)
    BALANCE_INDICATORS = [
        "but", "however", "although", "sometimes", "occasionally",
        "usually", "mostly", "often", "managing", "coping",
        "getting better", "improving", "trying", "working on",
        "know it will pass", "temporary", "for now"
    ]
    
    # Solution-seeking keywords
    SOLUTION_KEYWORDS = [
        "what should", "how can", "how do", "help me",
        "advice", "plan", "steps", "options", "recommend",
        "suggestion", "what would you", "think through",
        "figure out", "decide", "approach", "strategy",
        "solution", "fix", "resolve", "handle"
    ]
    
    async def detect_new_patterns(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        user_input: str
    ) -> List[str]:
        """
        Q: Should I detect any new patterns from this interaction?
        
        Enhanced pattern detection with:
        1. Expanded keyword lists
        2. Multi-indicator confidence scoring
        3. False positive prevention via balance indicators
        
        Args:
            user_id: User to track patterns for
            session_id: Current session
            user_input: User's message content
        
        Returns:
            List of newly detected or reinforced pattern names
        """
        detected = []
        lower_input = user_input.lower()
        
        # Count catastrophizing indicators
        catastrophizing_count = sum(
            1 for kw in self.CATASTROPHIZING_KEYWORDS if kw in lower_input
        )
        
        # Count balance indicators (reduces catastrophizing confidence)
        balance_count = sum(
            1 for bi in self.BALANCE_INDICATORS if bi in lower_input
        )
        
        # Catastrophizing pattern detection with false positive prevention
        # Require at least 2 indicators and more catastrophizing than balance
        if catastrophizing_count >= 2 and catastrophizing_count > balance_count:
            # Higher confidence for more indicators
            confidence_delta = min(0.2, catastrophizing_count * 0.05)
            # Reduce confidence if balance indicators present
            if balance_count > 0:
                confidence_delta *= 0.5
            
            pattern = await self.patterns.get_or_create_pattern(
                user_id, 
                "catastrophizing",
                initial_confidence=0.3
            )
            await self.patterns.update_pattern_confidence(
                pattern.pattern_id,
                f"Detected {catastrophizing_count} indicators (balance: {balance_count}) in: '{user_input[:50]}...'",
                confidence_delta=confidence_delta
            )
            detected.append("catastrophizing")
            logger.info(
                f"Pattern: catastrophizing detected "
                f"(indicators={catastrophizing_count}, balance={balance_count}, delta={confidence_delta:.2f})"
            )
        
        # Solution-seeking pattern detection
        solution_count = sum(
            1 for kw in self.SOLUTION_KEYWORDS if kw in lower_input
        )
        
        # Require at least 1 solution indicator
        if solution_count >= 1:
            # Higher confidence for more indicators
            confidence_delta = min(0.15, solution_count * 0.05)
            
            pattern = await self.patterns.get_or_create_pattern(
                user_id,
                "solution_seeking",
                initial_confidence=0.4
            )
            await self.patterns.update_pattern_confidence(
                pattern.pattern_id,
                f"Detected {solution_count} indicators in: '{user_input[:50]}...'",
                confidence_delta=confidence_delta
            )
            detected.append("solution_seeking")
            logger.info(
                f"Pattern: solution_seeking detected "
                f"(indicators={solution_count}, delta={confidence_delta:.2f})"
            )
        
        if detected:
            logger.info(f"Patterns detected: {detected}")
        else:
            logger.debug(f"No patterns detected (catastrophizing={catastrophizing_count}, balance={balance_count}, solution={solution_count})")
        
        return detected
