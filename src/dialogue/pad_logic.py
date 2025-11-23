"""
PAD Emotional Logic Module.

This module handles the mathematical calculations for the Pleasure-Arousal-Dominance (PAD)
emotional model. It is purely functional and stateless.
"""

from typing import Dict, Tuple

class PADLogic:
    """
    Logic for calculating PAD emotional state updates.
    PAD Range: -1.0 (Low) to +1.0 (High)
    """
    
    # Base decay rate towards user's baseline (personality)
    DECAY_RATE = 0.05
    
    # Sensitivity to new inputs
    REACTIVITY = 0.2

    @staticmethod
    def calculate_update(
        current_pad: Dict[str, float],
        stimulus: Dict[str, float],
        baseline: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Calculate new PAD state based on current state, stimulus, and decay.
        
        Args:
            current_pad: Dict with 'pleasure', 'arousal', 'dominance'
            stimulus: Dict with impact values for p, a, d
            baseline: Target resting state (default: 0,0,0)
            
        Returns:
            New PAD state dictionary
        """
        if baseline is None:
            baseline = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}
            
        new_state = {}
        
        for dim in ['pleasure', 'arousal', 'dominance']:
            current = current_pad.get(dim, 0.0)
            impact = stimulus.get(dim, 0.0)
            base = baseline.get(dim, 0.0)
            
            # 1. Apply Stimulus (Reaction)
            # New input pulls the state towards the stimulus direction
            reaction = current + (impact * PADLogic.REACTIVITY)
            
            # 2. Apply Decay (Homeostasis)
            # State naturally drifts back towards baseline over time
            decay = (base - reaction) * PADLogic.DECAY_RATE
            
            # 3. Clamp to Valid Range [-1.0, 1.0]
            final_val = max(-1.0, min(1.0, reaction + decay))
            
            new_state[dim] = final_val
            
        return new_state

    @staticmethod
    def get_quadrant(pad: Dict[str, float]) -> str:
        """
        Determine emotional quadrant/label based on PAD values.
        Simplified mapping for high-level labels.
        """
        p, a, d = pad.get('pleasure', 0), pad.get('arousal', 0), pad.get('dominance', 0)
        
        if p > 0 and a > 0 and d > 0: return "Exuberant"
        if p > 0 and a > 0 and d < 0: return "Dependent"
        if p > 0 and a < 0 and d > 0: return "Relaxed"
        if p > 0 and a < 0 and d < 0: return "Docile"
        
        if p < 0 and a > 0 and d > 0: return "Hostile"
        if p < 0 and a > 0 and d < 0: return "Anxious"
        if p < 0 and a < 0 and d > 0: return "Disdainful"
        if p < 0 and a < 0 and d < 0: return "Bored"
        
        return "Neutral"



