import pytest
from src.dialogue.pad_logic import PADLogic

def test_pad_update_increases_pleasure_on_positive_stimulus():
    """Test that positive stimulus increases pleasure."""
    # current = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}
    # stimulus = {'pleasure': 0.5, 'arousal': 0.0, 'dominance': 0.0}
    
    # We can use the static method directly
    current = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}
    stimulus = {'pleasure': 0.5, 'arousal': 0.0, 'dominance': 0.0}
    
    new_state = PADLogic.calculate_update(current, stimulus)
    
    assert new_state['pleasure'] > current['pleasure']
    assert new_state['pleasure'] <= 1.0  # Respects bounds

def test_pad_decay_towards_baseline():
    """Test that emotional state decays towards baseline over time."""
    current = {'pleasure': 0.8, 'arousal': 0.0, 'dominance': 0.0}
    stimulus = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}  # No stimulus
    baseline = {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}
    
    new_state = PADLogic.calculate_update(current, stimulus, baseline)
    
    assert new_state['pleasure'] < current['pleasure']  # Decayed towards 0

def test_pad_quadrant_classification():
    """Test emotional quadrant labeling."""
    assert PADLogic.get_quadrant({'pleasure': 0.5, 'arousal': 0.5, 'dominance': 0.5}) == "Exuberant"
    assert PADLogic.get_quadrant({'pleasure': -0.5, 'arousal': -0.5, 'dominance': -0.5}) == "Bored"
    assert PADLogic.get_quadrant({'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0}) == "Neutral"


