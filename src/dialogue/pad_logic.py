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
    
    # Default baseline (neutral state)
    BASELINE = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}
    
    def __init__(self, baseline: Dict[str, float] = None):
        """
        Initialize PAD logic with optional custom baseline.
        
        Args:
            baseline: Custom resting state (defaults to neutral)
        """
        self.baseline = baseline or self.BASELINE.copy()

    def calculate_update(
        self,
        current_pad: Dict[str, float],
        stimulus: Dict[str, float],
        baseline: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Calculate new PAD state based on current state, stimulus, and decay.
        
        Args:
            current_pad: Dict with 'pleasure', 'arousal', 'dominance'
            stimulus: Dict with impact values for p, a, d
            baseline: Target resting state (uses instance baseline if not provided)
            
        Returns:
            New PAD state dictionary
        """
        if baseline is None:
            baseline = self.baseline
            
        new_state = {}
        
        for dim in ['pleasure', 'arousal', 'dominance']:
            current = current_pad.get(dim, 0.0)
            impact = stimulus.get(dim, 0.0)
            base = baseline.get(dim, 0.0)
            
            # 1. Apply Stimulus (Reaction)
            # New input pulls the state towards the stimulus direction
            reaction = current + (impact * self.REACTIVITY)
            
            # 2. Apply Decay (Homeostasis)
            # State naturally drifts back towards baseline over time
            decay = (base - reaction) * self.DECAY_RATE
            
            # 3. Clamp to Valid Range [-1.0, 1.0]
            final_val = max(-1.0, min(1.0, reaction + decay))
            
            new_state[dim] = final_val
            
        return new_state

    @staticmethod
    def get_quadrant(pad: Dict[str, float]) -> str:
        """
        Determine emotional quadrant based on Pleasure and Arousal.
        
        Simplified 4-quadrant model (ignores dominance for MVP):
        - Exuberant: High pleasure, high arousal (happy, energetic)
        - Dependent: High pleasure, low arousal (content, calm)
        - Hostile: Low pleasure, high arousal (angry, anxious)
        - Bored: Low pleasure, low arousal (sad, withdrawn)
        """
        p = pad.get('pleasure', 0)
        a = pad.get('arousal', 0)
        
        # 4-quadrant classification based on pleasure and arousal
        if p > 0:
            if a > 0:
                return "Exuberant"  # High pleasure, high arousal
            else:
                return "Dependent"  # High pleasure, low arousal
        else:
            if a > 0:
                return "Hostile"    # Low pleasure, high arousal
            else:
                return "Bored"      # Low pleasure, low arousal











