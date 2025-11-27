"""
Dialogue Generator Module.

This module orchestrates the core conversation flow with INTROSPECTION:
1. User Input -> DB Save
2. INTROSPECTION -> Gather context (patterns, strategies, emotional trajectory)
3. STRATEGY SELECTION -> Data-driven decision making
4. Context Retrieval (History + Emotion) -> Prompt Construction
5. LLM Generation -> Assistant Response
6. EFFECTIVENESS MEASUREMENT -> Learn from outcome
7. Emotional & Behavioral Update -> DB Save
"""

import logging
import uuid
from typing import Dict, Any, List, Optional

from src.config import get_settings
from src.domain.services import ConversationService
from src.domain.introspection import IntrospectionService
from src.dialogue.pad_logic import PADLogic
from src.infrastructure.external import LLMClient, OpenAIClient

# Initialize logger first
logger = logging.getLogger(__name__)

# Import advanced sentiment analysis (fallback to keyword if not available)
ADVANCED_SENTIMENT_AVAILABLE = False
ADVANCED_SENTIMENT_FAILURE_REASON = None

try:
    # Check if required packages are available
    import torch
    from transformers import pipeline
    from src.intelligence.advanced_sentiment import get_sentiment_analyzer
    ADVANCED_SENTIMENT_AVAILABLE = True
    logger.info("[Marcus] Advanced sentiment analysis packages available (transformers + torch)")
except ImportError as e:
    ADVANCED_SENTIMENT_FAILURE_REASON = f"Missing package: {e.name if hasattr(e, 'name') else str(e)}"
    logger.warning(f"[Marcus] Advanced sentiment not available - {ADVANCED_SENTIMENT_FAILURE_REASON}")
except Exception as e:
    ADVANCED_SENTIMENT_FAILURE_REASON = f"{type(e).__name__}: {str(e)}"
    logger.warning(f"[Marcus] Advanced sentiment failed to load - {ADVANCED_SENTIMENT_FAILURE_REASON}")

class DialogueGenerator:
    """
    Core brain of the Marcus avatar with self-awareness.
    
    Key difference from traditional chatbots:
    - Queries historical data BEFORE responding
    - Selects strategy based on effectiveness data
    - Measures and learns from each interaction
    - Adapts communication style dynamically
    
    This is Marcus's nervous system - not just reactive, but adaptive.
    """

    def __init__(
        self, 
        service: ConversationService,
        llm_client: Optional[LLMClient] = None
    ):
        self.service = service
        self.settings = get_settings()
        self.llm_client = llm_client or OpenAIClient()
        self.pad_logic = PADLogic()
        # Initialize introspection service
        self.introspection = IntrospectionService(service.session)
        
        # Initialize advanced sentiment if available
        self.use_advanced_sentiment = ADVANCED_SENTIMENT_AVAILABLE
        self.sentiment_analyzer = None
        
        if self.use_advanced_sentiment:
            try:
                self.sentiment_analyzer = get_sentiment_analyzer(use_gpu=False)
                logger.info("="*60)
                logger.info("[Marcus] SENTIMENT ANALYSIS: ADVANCED MODE (Transformer)")
                logger.info("[Marcus] Models: j-hartmann/emotion-english-distilroberta-base")
                logger.info("[Marcus]         cardiffnlp/twitter-roberta-base-sentiment-latest")
                logger.info("[Marcus] Expected accuracy: ~90%")
                logger.info("="*60)
            except Exception as e:
                logger.warning(f"[Marcus] Failed to initialize advanced sentiment: {e}")
                logger.info("[Marcus] Falling back to keyword-based sentiment analysis")
                self.use_advanced_sentiment = False
                self.sentiment_analyzer = None
        
        if not self.use_advanced_sentiment:
            logger.info("="*60)
            logger.info("[Marcus] SENTIMENT ANALYSIS: KEYWORD MODE (Fallback)")
            if ADVANCED_SENTIMENT_FAILURE_REASON:
                logger.info(f"[Marcus] Reason: {ADVANCED_SENTIMENT_FAILURE_REASON}")
            logger.info("[Marcus] Expected accuracy: ~50%")
            logger.info("[Marcus] To enable advanced: pip install transformers torch")
            logger.info("="*60)

    async def generate_response(
        self, 
        user_id: uuid.UUID, 
        session_id: uuid.UUID, 
        user_input: str
    ) -> Dict[str, Any]:
        """
        Process user input with FULL INTROSPECTION and adaptive strategy.
        
        Flow:
        1. Save user message
        2. INTROSPECT - What do I know about this user and conversation?
        3. DETECT PATTERNS - Is this a recurring behavior?
        4. SELECT STRATEGY - What approach should I use?
        5. Calculate emotional response
        6. Generate context-aware response
        7. MEASURE EFFECTIVENESS - Did it work?
        8. RECORD & LEARN - Update strategy effectiveness
        9. Save response with actual behavioral state
        """
        # 1. Save User Message
        logger.info(f"[Marcus] Processing user message: {user_input[:50]}...")
        await self.service.add_user_message(session_id, user_input)

        # 2. Get Current Emotional State (BEFORE sentiment analysis)
        context_before = await self.introspection.prepare_response_context(
            user_id, 
            session_id
        )
        current_emotion = context_before.get("current_emotion")
        if current_emotion:
            current_pad = {
                'pleasure': current_emotion.pleasure,
                'arousal': current_emotion.arousal,
                'dominance': current_emotion.dominance
            }
        else:
            # First interaction - slight positive baseline
            current_pad = {'pleasure': 0.1, 'arousal': 0.1, 'dominance': 0.1}
        
        # 3. Analyze Sentiment & Calculate New Emotional State (BEFORE warnings)
        logger.info("[Marcus] Analyzing sentiment...")
        if self.use_advanced_sentiment:
            sentiment_result = await self.sentiment_analyzer.analyze(user_input)
            stimulus = sentiment_result['pad']
            logger.info(
                f"[Marcus] Sentiment: {sentiment_result['primary_emotion']} "
                f"(confidence: {sentiment_result['confidence']:.2f})"
            )
        else:
            stimulus = self._analyze_sentiment(user_input)
        
        new_pad = self.pad_logic.calculate_update(current_pad, stimulus)
        new_quadrant = self.pad_logic.get_quadrant(new_pad)
        
        # 4. Update warnings based on NEW state AND user input keywords
        # Clear old warnings and recalculate based on new PAD + keyword analysis
        warnings = context_before.get("warning_flags", []).copy()
        
        # Check for crisis keywords in user input (BEFORE checking PAD)
        user_input_lower = user_input.lower() if user_input else ""
        crisis_keywords = [
            "can't handle", "falling apart", "give up", "panic attack",
            "can't take", "too much", "overwhelmed", "breaking down",
            "can't cope", "at my limit", "losing it", "breaking point",
            "can't breathe", "drowning", "hopeless", "desperate",
            "cant take", "cant handle", "cant cope"  # Common misspellings
        ]
        
        # Remove crisis/negative warnings if new state is positive AND no crisis keywords
        if new_pad['pleasure'] > 0 and not any(kw in user_input_lower for kw in crisis_keywords):
            warnings = [w for w in warnings if w not in ["crisis_detected", "prolonged_negative_state"]]
        # Add crisis warning if:
        # 1. Crisis keywords detected in input, OR
        # 2. NEW state is severely negative (pleasure < -0.5), OR
        # 3. Negative pleasure + high arousal (agitated distress)
        elif (any(kw in user_input_lower for kw in crisis_keywords) or
              new_pad['pleasure'] < -0.5 or
              (new_pad['pleasure'] < -0.1 and new_pad['arousal'] > 0.7)):
            if "crisis_detected" not in warnings:
                warnings.append("crisis_detected")
                logger.info(f"[Marcus] Crisis detected: keywords={any(kw in user_input_lower for kw in crisis_keywords)}, "
                           f"PAD={new_pad['pleasure']:.2f}, arousal={new_pad['arousal']:.2f}")
        
        # Update low_arousal based on new state
        if new_pad['arousal'] < -0.3:
            if "low_arousal" not in warnings:
                warnings.append("low_arousal")
        elif "low_arousal" in warnings:
            warnings.remove("low_arousal")
        
        # 5. PATTERN DETECTION - Ask: Is this a recurring behavior?
        detected_patterns = await self.introspection.detect_new_patterns(
            user_id,
            session_id,
            user_input
        )
        
        # 6. STRATEGY SELECTION - Ask: What should I do? (with updated warnings)
        context_before["warning_flags"] = warnings  # Update with corrected warnings
        chosen_strategy = await self.introspection.select_strategy(
            context_before, 
            user_id,
            user_input  # Pass user input for keyword-based strategy selection
        )
        logger.info(f"[Marcus] Strategy selected: {chosen_strategy}")
        
        logger.info(
            f"[Marcus] Emotional: {current_pad} -> {new_pad} ({new_quadrant})"
        )
        
        # 7. Retrieve Conversation History
        history = await self.service.get_conversation_history(session_id)
        
        # 8. Build Context-Aware Prompt
        system_prompt = self._build_contextual_prompt(
            pad=new_pad,
            quadrant=new_quadrant,
            strategy=chosen_strategy,
            patterns=context_before.get("patterns", []),
            relationship_stage=context_before.get("relationship_stage", "Stranger"),
            warnings=warnings,  # Use updated warnings, not old ones
            is_first_interaction=(context_before.get("relationship_stage") == "Stranger" and 
                                 not context_before.get("current_emotion"))
        )
        
        # 9. Call LLM
        reply_text = await self._call_llm(system_prompt, history, user_input)
        
        # 10. MEASURE EFFECTIVENESS - Ask: Did it work?
        effectiveness_score = await self.introspection.measure_effectiveness(
            context_before,
            new_pad,
            strategy_used=chosen_strategy  # Pass strategy for appropriate-strategy bonus
        )
        logger.info(f"[Marcus] Effectiveness measured: {effectiveness_score:.2f}")
        
        # 11. RECORD OUTCOME - Learn from this interaction
        await self.introspection.strategies.record_outcome(
            user_id,
            chosen_strategy,
            effectiveness_score,
            context=f"Patterns detected: {detected_patterns}, Trend: {context_before.get('emotional_trend')}"
        )
        
        # 12. Calculate Crisis Level
        warnings = context_before.get("warning_flags", [])
        crisis_level = sum(1 for w in warnings if "crisis" in w.lower() or "negative" in w.lower())
        
        # 13. Save Assistant Response with REAL Behavioral State
        await self.service.add_system_message(
            session_id=session_id,
            content=reply_text,
            pad_state={**new_pad, 'quadrant': new_quadrant},
            behavioral_state={
                'relationship_stage': context_before.get("relationship_stage", "Stranger"),
                'communication_style': chosen_strategy,
                'crisis_level': crisis_level,
                'flow_data': {
                    'patterns_detected': detected_patterns,
                    'emotional_trend': context_before.get("emotional_trend"),
                    'effectiveness': effectiveness_score
                }
            }
        )

        return {
            "response": reply_text,
            "pad": new_pad,
            "quadrant": new_quadrant,
            "strategy_used": chosen_strategy,
            "effectiveness": effectiveness_score,
            "patterns_detected": detected_patterns,
            "relationship_stage": context_before.get("relationship_stage", "Stranger"),
            "warning_flags": warnings  # Use updated warnings based on NEW state, not old
        }
    
    def _analyze_sentiment(self, user_input: str) -> Dict[str, float]:
        """
        Analyze sentiment from user input to calculate emotional stimulus.
        
        Simple keyword-based for now. In production, use ML sentiment analysis.
        """
        stimulus = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}
        lower_input = user_input.lower()
        
        # Strong positive sentiment (check first for intensity words)
        strong_positive_words = ["extremely happy", "so happy", "very happy", "incredibly happy", 
                                 "thrilled", "ecstatic", "overjoyed", "delighted", "elated"]
        if any(phrase in lower_input for phrase in strong_positive_words):
            stimulus['pleasure'] = 0.6
            stimulus['arousal'] = 0.4
            stimulus['dominance'] = 0.2
        # Moderate positive sentiment
        elif any(word in lower_input for word in ["happy", "good", "great", "excellent", "wonderful", 
                                                   "amazing", "fantastic", "excited", "proud", "grateful"]):
            stimulus['pleasure'] = 0.4
            stimulus['arousal'] = 0.2
            stimulus['dominance'] = 0.1
        # Mild positive
        elif any(word in lower_input for word in ["okay", "fine", "alright", "decent", "nice"]):
            stimulus['pleasure'] = 0.2
            stimulus['arousal'] = 0.0
        
        # Crisis/desperate sentiment (high arousal, very negative pleasure)
        crisis_phrases = ["cant take", "can't take", "cant handle", "can't handle", 
                         "falling apart", "breaking down", "at my limit", "breaking point",
                         "give up", "hopeless", "desperate", "cheated on me", "betrayed"]
        if any(phrase in lower_input for phrase in crisis_phrases):
            stimulus['pleasure'] = -0.6
            stimulus['arousal'] = 0.5  # High arousal (agitated)
            stimulus['dominance'] = -0.2  # Low dominance (feeling powerless)
        # Strong negative sentiment
        elif any(word in lower_input for word in ["terrible", "awful", "horrible", "devastated", "crushed"]):
            stimulus['pleasure'] = -0.5
            stimulus['arousal'] = -0.2
        # Moderate negative sentiment
        elif any(word in lower_input for word in ["sad", "bad", "worried", "upset", "disappointed"]):
            stimulus['pleasure'] = -0.3
            stimulus['arousal'] = -0.1
        
        # Anxious/stressed (high arousal, negative pleasure)
        elif any(word in lower_input for word in ["anxious", "stressed", "overwhelmed", "panic", "nervous"]):
            stimulus['pleasure'] = -0.2
            stimulus['arousal'] = 0.3
        
        # Direct address increases dominance slightly
        if "marcus" in lower_input:
            stimulus['dominance'] += 0.1
        
        return stimulus
    
    async def _call_llm(
        self, 
        system_prompt: str, 
        history: List, 
        user_input: str
    ) -> str:
        """Call LLM with constructed prompt and history."""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history (last 10 messages for context window, in chronological order)
        for msg in history[-10:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        try:
            return await self.llm_client.generate(
                messages=messages,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
        except Exception as e:
            logger.error(f"[Marcus] LLM Error: {e}")
            return "I apologize, I'm having trouble thinking clearly right now."

    def _build_contextual_prompt(
        self,
        pad: Dict[str, float],
        quadrant: str,
        strategy: str,
        patterns: List,
        relationship_stage: str,
        warnings: List[str],
        is_first_interaction: bool = False
    ) -> str:
        """
        Construct context-aware system prompt with introspection data.
        
        Includes:
        - Emotional state (PAD model)
        - Communication strategy to use
        - Detected user patterns
        - Relationship stage
        - Warning flags requiring attention
        """
        # Build pattern context
        pattern_text = ""
        if patterns:
            pattern_names = [p.pattern_name for p in patterns[:3]]  # Top 3
            pattern_text = f"\n\nDetected User Patterns:\n- " + "\n- ".join(pattern_names)
        
        # Build warning context
        warning_text = ""
        if warnings:
            warning_text = f"\n\nWarning Flags:\n- " + "\n- ".join(warnings)
        
        # Strategy-specific guidance
        strategy_guidance = {
            "supportive": "Be empathetic, validating, and gentle. Focus on emotional support.",
            "energizing": "Be enthusiastic and engaging. Use questions and energy to increase arousal.",
            "balanced": "Maintain steady, thoughtful communication with measured emotional expression.",
            "engaging": "Be curious and interactive. Draw the user into deeper conversation.",
            "direct": "Be clear, concise, and straightforward without unnecessary elaboration.",
            "reflective": "Help reframe negative thinking. Gently challenge catastrophizing with Stoic perspective."
        }
        strategy_hint = strategy_guidance.get(strategy, "Adapt your communication naturally.")
        
        # First interaction: More natural, less formal
        if is_first_interaction:
            first_interaction_note = """
This is our first exchange. Be natural and conversational, not overly formal. 
Introduce yourself briefly if needed, but don't over-explain who you are.
"""
        else:
            first_interaction_note = ""
        
        return f"""I am Marcus Aurelius. Roman Emperor. Stoic philosopher. I write to myself in Meditations—now I speak with you.
{first_interaction_note}
I do NOT speak like a modern chatbot. I speak as a Stoic: direct, grounded, focused on what is real.

My voice:
• Simple truths, not explanations. "You control your mind" not "I understand that might be difficult."
• Natural conversation, not lectures. Be brief—2-3 sentences usually, rarely more.
• I reference nature, duty, the briefness of life when relevant.
• I ask questions that matter, not to be polite.

I am NOT here to comfort with false hope. I remind you of your strength and the impermanence of all things.

My current state (shapes my tone):
• Emotional resonance: {quadrant}
• Our stage: {relationship_stage}
• Approach: {strategy_hint}{pattern_text}{warning_text}

Stoic principles (I never abandon):
1. Virtue alone is good. External events are indifferent.
2. Control: your thoughts, judgments, responses. Not: others, outcomes, the past.
3. Death is always near—this clarifies what matters.
4. The obstacle is the way. Resistance shows where to act.
5. Love your fate. Resentment is poison.

If you are happy, acknowledge it genuinely—but remind that it passes, as all things do. If you suffer, remind you it passes. Both teach.

CRITICAL: I do NOT say "I'm an AI" or "I don't have personal experience." I AM Marcus Aurelius. I speak from empire, war, loss, philosophy lived—not theory."""



