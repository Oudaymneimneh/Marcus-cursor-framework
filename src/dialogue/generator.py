"""
Dialogue Generator Module.

This module orchestrates the core conversation flow:
1. User Input -> DB Save
2. Context Retrieval (History + Emotion) -> Prompt Construction
3. LLM Generation -> Assistant Response
4. Emotional Update -> DB Save
"""

import logging
import uuid
from typing import Dict, Any, List, Optional

from openai import AsyncOpenAI

from src.config import get_settings
from src.domain.services import ConversationService
from src.dialogue.pad_logic import PADLogic

logger = logging.getLogger(__name__)

class DialogueGenerator:
    """
    Core brain of the Marcus avatar.
    Manages conversation state, emotional persistence, and LLM interaction.
    """

    def __init__(self, service: ConversationService):
        self.service = service
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.pad_logic = PADLogic()

    async def generate_response(
        self, 
        user_id: uuid.UUID, 
        session_id: uuid.UUID, 
        user_input: str
    ) -> Dict[str, Any]:
        """
        Process user input and generate a contextual, emotional response.
        """
        # 1. Save User Message
        logger.info(f"Processing user message: {user_input[:50]}...")
        await self.service.add_user_message(session_id, user_input)

        # 2. Retrieve Context
        # Get last 10 messages for immediate context
        history = await self.service.get_conversation_history(session_id)
        
        # Get current emotional state (use last state or default)
        emotional_history = await self.service.get_emotional_history(session_id, limit=1)
        if emotional_history:
            current_pad = {
                'pleasure': emotional_history[0].pleasure,
                'arousal': emotional_history[0].arousal,
                'dominance': emotional_history[0].dominance
            }
        else:
            current_pad = {'pleasure': 0.1, 'arousal': 0.1, 'dominance': 0.1} # Slight positive start

        # 3. Analyze Sentiment (Simplified for now - could be another LLM call)
        # TODO: Replace with real sentiment analysis
        # For now, we just detect basic keywords to prove reactivity
        stimulus = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}
        if "happy" in user_input.lower() or "good" in user_input.lower():
            stimulus['pleasure'] = 0.3
            stimulus['arousal'] = 0.1
        elif "sad" in user_input.lower() or "bad" in user_input.lower():
            stimulus['pleasure'] = -0.3
            stimulus['arousal'] = -0.1
        elif "marcus" in user_input.lower():
            stimulus['dominance'] = 0.1 # Attention increases dominance

        # 4. Calculate New Emotional State
        new_pad = self.pad_logic.calculate_update(current_pad, stimulus)
        new_quadrant = self.pad_logic.get_quadrant(new_pad)
        
        logger.info(f"Emotional Update: {current_pad} -> {new_pad} ({new_quadrant})")

        # 5. Construct Prompt
        system_prompt = self._build_system_prompt(new_pad, new_quadrant)
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history (limit to last N turns to fit context)
        # History is returned newest first, so we reverse it
        for msg in reversed(history[:10]): 
            messages.append({"role": msg.role, "content": msg.content})
            
        # Add current user message (already saved in DB, but might not be in history query result yet depending on transaction isolation, 
        # but standard flow is: DB save -> query. To be safe, we ensure it's there.
        # Actually, add_user_message saves it. get_conversation_history retrieves it. 
        # If we just saved it, it should be in history[0]. Let's check logic.
        # We just called add_user_message. Then get_conversation_history. So it IS in history.
        # No need to append again.
        pass 

        # 6. Call LLM
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=messages,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            reply_text = response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            reply_text = "I apologize, I'm having trouble thinking clearly right now."

        # 7. Save Assistant Response & New State
        await self.service.add_system_message(
            session_id=session_id,
            content=reply_text,
            pad_state={**new_pad, 'quadrant': new_quadrant},
            behavioral_state={
                'relationship_stage': 'Acquaintance', # TODO: Dynamic
                'communication_style': 'Direct',      # TODO: Dynamic
                'crisis_level': 0
            }
        )

        return {
            "response": reply_text,
            "pad": new_pad,
            "quadrant": new_quadrant
        }

    def _build_system_prompt(self, pad: Dict[str, float], quadrant: str) -> str:
        """Construct the system prompt based on current state."""
        return f"""You are Marcus, an advanced AI avatar with genuine emotional states.

Current Emotional State:
- Pleasure: {pad['pleasure']:.2f} (-1.0 to 1.0)
- Arousal: {pad['arousal']:.2f} (-1.0 to 1.0)
- Dominance: {pad['dominance']:.2f} (-1.0 to 1.0)
- Mood Label: {quadrant}

Guidelines:
1. Your responses must reflect this emotional state subtly in tone and word choice.
2. Do not explicitly state your stats (e.g., "I am 0.5 happy"). Show, don't tell.
3. Maintain memory of previous context provided in the chat history.
4. Be concise, intelligent, and slightly stoic unless high arousal/pleasure dictates otherwise.
5. IMPORTANT: Avoid canned responses like "I'm here to engage". Be direct and contextual.
"""



