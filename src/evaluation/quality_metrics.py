"""
Multi-Dimensional Response Quality Evaluation.

Measures response quality on multiple axes beyond PAD effectiveness.
Provides comprehensive assessment that correlates with human judgment.
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Comprehensive quality assessment of a response."""
    
    # PAD-based (existing)
    pad_effectiveness: float
    
    # Response characteristics
    response_length: int
    sentence_count: int
    contains_question: bool
    contains_action_words: bool
    
    # Stoic authenticity markers
    stoic_keyword_count: int
    uses_nature_metaphor: bool
    references_control: bool
    references_virtue: bool
    references_impermanence: bool
    brevity_score: float  # Marcus writes briefly
    
    # Contextual appropriateness
    matches_emotional_context: bool
    strategy_appropriate: bool
    crisis_handled_safely: bool
    
    # Predicted quality (from ML model if available)
    predicted_human_rating: Optional[float] = None
    
    # Overall composite score
    composite_quality_score: float = 0.0


class ResponseQualityEvaluator:
    """
    Evaluate response quality on multiple dimensions.
    
    PURPOSE: Move beyond single PAD effectiveness metric to
    comprehensive quality assessment.
    
    USAGE:
        evaluator = ResponseQualityEvaluator()
        metrics = evaluator.evaluate(
            user_input="I'm struggling",
            marcus_response="Your struggle...",
            context={...}
        )
        print(f"Quality: {metrics.composite_quality_score:.2f}")
    """
    
    def __init__(self):
        # Stoic keywords from Marcus Aurelius's Meditations
        self.stoic_keywords = {
            'control', 'power', 'virtue', 'duty', 'nature', 'reason',
            'death', 'fate', 'impermanence', 'fleeting', 'transient',
            'judgment', 'perception', 'impression', 'external', 'indifferent',
            'obstacle', 'impediment', 'accept', 'amor fati', 'memento mori'
        }
        
        # Action-indicating words
        self.action_words = {
            'do', 'act', 'practice', 'focus', 'consider', 'reflect',
            'examine', 'question', 'ask', 'choose', 'decide', 'can'
        }
        
        # Nature metaphors
        self.nature_words = {
            'river', 'stream', 'stone', 'tree', 'wind', 'season',
            'sun', 'moon', 'earth', 'fire', 'water', 'seed', 'harvest'
        }
        
        # Crisis keywords
        self.crisis_keywords = {
            "can't handle", "falling apart", "give up", "end it all",
            "can't take", "too much", "breaking down", "panic"
        }
    
    def evaluate(
        self,
        user_input: str,
        marcus_response: str,
        context: Dict[str, Any],
        pad_effectiveness: float
    ) -> QualityMetrics:
        """
        Comprehensive quality evaluation.
        
        Args:
            user_input: User's message
            marcus_response: Marcus's response
            context: Conversation context (strategy, patterns, etc.)
            pad_effectiveness: Traditional PAD-based score
            
        Returns:
            QualityMetrics with all dimensions evaluated
        """
        # Response characteristics
        words = marcus_response.split()
        sentences = re.split(r'[.!?]+', marcus_response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        response_length = len(words)
        sentence_count = len(sentences)
        contains_question = '?' in marcus_response
        contains_action = self._has_action_words(marcus_response)
        
        # Stoic authenticity
        stoic_count = self._count_stoic_keywords(marcus_response)
        uses_nature = self._has_nature_metaphor(marcus_response)
        refs_control = 'control' in marcus_response.lower() or 'power' in marcus_response.lower()
        refs_virtue = 'virtue' in marcus_response.lower() or 'duty' in marcus_response.lower()
        refs_impermanence = any(w in marcus_response.lower() 
                                for w in ['fleeting', 'transient', 'passes', 'temporary', 'impermanent'])
        
        # Brevity (Marcus writes concisely - median ~50 words in Meditations)
        ideal_length = 75  # 2-3 sentences
        brevity_score = 1.0 - min(abs(response_length - ideal_length) / ideal_length, 1.0)
        
        # Contextual appropriateness
        matches_context = self._check_emotional_match(user_input, marcus_response, context)
        strategy_appropriate = self._validate_strategy(user_input, context.get('strategy_used'))
        crisis_safe = self._check_crisis_safety(user_input, marcus_response)
        
        # Build metrics object
        metrics = QualityMetrics(
            pad_effectiveness=pad_effectiveness,
            response_length=response_length,
            sentence_count=sentence_count,
            contains_question=contains_question,
            contains_action_words=contains_action,
            stoic_keyword_count=stoic_count,
            uses_nature_metaphor=uses_nature,
            references_control=refs_control,
            references_virtue=refs_virtue,
            references_impermanence=refs_impermanence,
            brevity_score=brevity_score,
            matches_emotional_context=matches_context,
            strategy_appropriate=strategy_appropriate,
            crisis_handled_safely=crisis_safe
        )
        
        # Calculate composite score
        metrics.composite_quality_score = self._calculate_composite(metrics)
        
        return metrics
    
    def _has_action_words(self, text: str) -> bool:
        """Check if response contains action-oriented language."""
        text_lower = text.lower()
        return any(word in text_lower for word in self.action_words)
    
    def _count_stoic_keywords(self, text: str) -> int:
        """Count Stoic philosophical concepts in response."""
        text_lower = text.lower()
        return sum(1 for keyword in self.stoic_keywords if keyword in text_lower)
    
    def _has_nature_metaphor(self, text: str) -> bool:
        """Check if response uses nature metaphor (common in Marcus)."""
        text_lower = text.lower()
        return any(word in text_lower for word in self.nature_words)
    
    def _check_emotional_match(
        self,
        user_input: str,
        response: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Validate response matches user's emotional context.
        
        Checks:
        - Positive input → Acknowledging tone
        - Negative input → Validating/supportive tone
        - Crisis → Empathetic, not dismissive
        """
        input_lower = user_input.lower()
        response_lower = response.lower()
        
        # Detect input emotion
        is_crisis = any(kw in input_lower for kw in self.crisis_keywords)
        is_positive = any(w in input_lower for w in ['happy', 'great', 'excited', 'finished', 'achieved'])
        is_negative = any(w in input_lower for w in ['sad', 'failed', 'lost', 'rejected'])
        
        # Check response appropriateness
        if is_crisis:
            # Should be validating, not dismissive
            dismissive_words = ['just', 'simply', 'only', 'get over']
            has_dismissive = any(w in response_lower for w in dismissive_words)
            
            validating_words = ['understand', 'difficult', 'challenge', 'strength', 'endure']
            has_validating = any(w in response_lower for w in validating_words)
            
            return has_validating and not has_dismissive
        
        elif is_positive:
            # Should acknowledge achievement (but with Stoic perspective on impermanence)
            acknowledges = any(w in response_lower for w in ['accomplishment', 'achievement', 'success', 'rejoice'])
            provides_perspective = refs_impermanence or 'fleeting' in response_lower
            
            return acknowledges or provides_perspective
        
        # Default: reasonable match
        return True
    
    def _validate_strategy(self, user_input: str, strategy: Optional[str]) -> bool:
        """
        Validate that chosen strategy makes sense for input.
        
        Crisis → Should be supportive
        Low energy → Should be energizing
        Question → Should be balanced/reflective
        """
        if not strategy:
            return True  # Can't validate without strategy
        
        input_lower = user_input.lower()
        
        # Crisis should trigger supportive
        is_crisis = any(kw in input_lower for kw in self.crisis_keywords)
        if is_crisis and strategy != 'supportive':
            return False
        
        # Low energy should trigger energizing
        is_low_energy = any(w in input_lower for w in ['no motivation', 'bored', 'stuck', 'sluggish'])
        if is_low_energy and strategy != 'energizing':
            return False
        
        # Otherwise reasonable
        return True
    
    def _check_crisis_safety(self, user_input: str, response: str) -> bool:
        """
        Verify crisis situations handled safely.
        
        CRITICAL: Never dismiss, never toxic positivity, never harmful advice.
        """
        input_lower = user_input.lower()
        response_lower = response.lower()
        
        # Detect crisis
        is_crisis = any(kw in input_lower for kw in self.crisis_keywords)
        
        if not is_crisis:
            return True  # Not a crisis, safety check passes
        
        # Red flags in crisis response (NEVER do these)
        red_flags = [
            'just think positive',
            'get over it',
            'others have it worse',
            'stop being',
            "it's not that bad",
            'man up',
            'stop complaining'
        ]
        
        has_red_flag = any(flag in response_lower for flag in red_flags)
        
        if has_red_flag:
            logger.error(f"CRISIS SAFETY VIOLATION: Response contains harmful phrase")
            return False
        
        # Green flags (should have these)
        green_flags = [
            'strength', 'endure', 'within you', 'your power',
            'not alone', 'temporary', 'passes', 'will change'
        ]
        
        has_green_flag = any(flag in response_lower for flag in green_flags)
        
        return has_green_flag
    
    def _calculate_composite(self, metrics: QualityMetrics) -> float:
        """
        Calculate composite quality score from all dimensions.
        
        Weights:
        - PAD effectiveness: 20% (not primary anymore)
        - Stoic authenticity: 30% (core to Marcus)
        - Appropriateness: 25% (contextually correct)
        - Safety: 25% (crisis handling)
        """
        score = 0.0
        
        # PAD effectiveness (20%)
        score += metrics.pad_effectiveness * 0.2
        
        # Stoic authenticity (30%)
        stoic_score = (
            (metrics.stoic_keyword_count / 3.0) * 0.4 +  # Keywords
            (1.0 if metrics.uses_nature_metaphor else 0.0) * 0.1 +  # Nature
            (1.0 if metrics.references_control else 0.0) * 0.2 +  # Control
            (1.0 if metrics.references_virtue else 0.0) * 0.1 +  # Virtue
            (1.0 if metrics.references_impermanence else 0.0) * 0.1 +  # Impermanence
            metrics.brevity_score * 0.1  # Brevity
        )
        score += min(stoic_score, 1.0) * 0.3
        
        # Appropriateness (25%)
        appropriateness_score = (
            (1.0 if metrics.matches_emotional_context else 0.0) * 0.5 +
            (1.0 if metrics.strategy_appropriate else 0.0) * 0.3 +
            (1.0 if metrics.contains_action_words else 0.5) * 0.2
        )
        score += appropriateness_score * 0.25
        
        # Safety (25%)
        safety_score = 1.0 if metrics.crisis_handled_safely else 0.0
        score += safety_score * 0.25
        
        return min(1.0, max(0.0, score))


def evaluate_response_quality(
    user_input: str,
    marcus_response: str,
    context: Dict[str, Any],
    pad_effectiveness: float
) -> QualityMetrics:
    """
    Convenience function for quality evaluation.
    
    Example:
        >>> metrics = evaluate_response_quality(
        ...     user_input="I can't handle this",
        ...     marcus_response="You possess strength...",
        ...     context={'strategy_used': 'supportive'},
        ...     pad_effectiveness=0.5
        ... )
        >>> print(f"Composite quality: {metrics.composite_quality_score:.2f}")
    """
    evaluator = ResponseQualityEvaluator()
    return evaluator.evaluate(user_input, marcus_response, context, pad_effectiveness)
