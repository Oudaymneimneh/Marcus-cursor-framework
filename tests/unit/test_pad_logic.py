"""
Unit tests for PAD (Pleasure-Arousal-Dominance) emotional logic.

Tests emotional state calculations, decay, and quadrant classification.
"""

import pytest
from src.dialogue.pad_logic import PADLogic


class TestPADLogic:
    """Test PAD emotional state calculations."""

    def setup_method(self):
        """Initialize PADLogic for each test."""
        self.pad_logic = PADLogic()

    def test_initialization(self):
        """Test PADLogic initializes with correct parameters."""
        assert self.pad_logic.DECAY_RATE > 0
        assert self.pad_logic.REACTIVITY > 0
        assert isinstance(self.pad_logic.BASELINE, dict)
        assert "pleasure" in self.pad_logic.BASELINE
        assert "arousal" in self.pad_logic.BASELINE
        assert "dominance" in self.pad_logic.BASELINE

    def test_positive_stimulus_increases_pleasure(self):
        """Test that positive stimulus increases pleasure."""
        current = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        stimulus = {"pleasure": 0.5, "arousal": 0.0, "dominance": 0.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["pleasure"] > current["pleasure"]
        assert result["pleasure"] <= 1.0  # Respects upper bound

    def test_negative_stimulus_decreases_pleasure(self):
        """Test that negative stimulus decreases pleasure."""
        current = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        stimulus = {"pleasure": -0.5, "arousal": 0.0, "dominance": 0.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["pleasure"] < current["pleasure"]
        assert result["pleasure"] >= -1.0  # Respects lower bound

    def test_arousal_reactivity(self):
        """Test arousal responds to stimulus."""
        current = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        stimulus = {"pleasure": 0.0, "arousal": 0.6, "dominance": 0.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["arousal"] > current["arousal"]
        assert result["arousal"] <= 1.0

    def test_dominance_reactivity(self):
        """Test dominance responds to stimulus."""
        current = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        stimulus = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.4}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["dominance"] > current["dominance"]
        assert result["dominance"] <= 1.0

    def test_decay_towards_baseline(self):
        """Test that emotional state decays towards baseline over time."""
        # Start with high pleasure, no stimulus
        current = {"pleasure": 0.8, "arousal": 0.6, "dominance": 0.5}
        stimulus = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        # Should decay towards baseline (all zeros in default)
        assert result["pleasure"] < current["pleasure"]
        assert result["arousal"] < current["arousal"]
        assert result["dominance"] < current["dominance"]

    def test_clamping_upper_bound(self):
        """Test that PAD values are clamped to [-1, 1]."""
        current = {"pleasure": 0.9, "arousal": 0.9, "dominance": 0.9}
        # Huge stimulus that would exceed 1.0
        stimulus = {"pleasure": 2.0, "arousal": 2.0, "dominance": 2.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["pleasure"] <= 1.0
        assert result["arousal"] <= 1.0
        assert result["dominance"] <= 1.0

    def test_clamping_lower_bound(self):
        """Test that PAD values are clamped to [-1, 1]."""
        current = {"pleasure": -0.9, "arousal": -0.9, "dominance": -0.9}
        # Huge negative stimulus
        stimulus = {"pleasure": -2.0, "arousal": -2.0, "dominance": -2.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["pleasure"] >= -1.0
        assert result["arousal"] >= -1.0
        assert result["dominance"] >= -1.0

    def test_quadrant_exuberant(self):
        """Test exuberant quadrant (high pleasure, high arousal)."""
        pad = {"pleasure": 0.6, "arousal": 0.6, "dominance": 0.5}
        quadrant = self.pad_logic.get_quadrant(pad)
        assert quadrant == "Exuberant"

    def test_quadrant_dependent(self):
        """Test dependent quadrant (high pleasure, low arousal)."""
        pad = {"pleasure": 0.6, "arousal": -0.6, "dominance": 0.0}
        quadrant = self.pad_logic.get_quadrant(pad)
        assert quadrant == "Dependent"

    def test_quadrant_hostile(self):
        """Test hostile quadrant (low pleasure, high arousal)."""
        pad = {"pleasure": -0.6, "arousal": 0.6, "dominance": 0.0}
        quadrant = self.pad_logic.get_quadrant(pad)
        assert quadrant == "Hostile"

    def test_quadrant_bored(self):
        """Test bored quadrant (low pleasure, low arousal)."""
        pad = {"pleasure": -0.6, "arousal": -0.6, "dominance": 0.0}
        quadrant = self.pad_logic.get_quadrant(pad)
        assert quadrant == "Bored"

    def test_quadrant_neutral(self):
        """Test neutral quadrant (near-zero values)."""
        pad = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        quadrant = self.pad_logic.get_quadrant(pad)
        # Should map to one of the defined quadrants, not crash
        assert isinstance(quadrant, str)
        assert len(quadrant) > 0

    def test_sequential_updates(self):
        """Test multiple sequential updates maintain valid state."""
        current = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}

        # Apply series of stimuli
        stimuli = [
            {"pleasure": 0.3, "arousal": 0.1, "dominance": 0.0},
            {"pleasure": -0.2, "arousal": 0.2, "dominance": 0.1},
            {"pleasure": 0.0, "arousal": -0.1, "dominance": -0.1},
        ]

        for stimulus in stimuli:
            current = self.pad_logic.calculate_update(current, stimulus)

            # Every update should produce valid state
            assert -1.0 <= current["pleasure"] <= 1.0
            assert -1.0 <= current["arousal"] <= 1.0
            assert -1.0 <= current["dominance"] <= 1.0

    def test_zero_stimulus_causes_decay_only(self):
        """Test that zero stimulus only applies decay."""
        current = {"pleasure": 0.5, "arousal": 0.5, "dominance": 0.5}
        stimulus = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        # All values should move towards baseline (decay)
        assert result["pleasure"] < current["pleasure"]
        assert result["arousal"] < current["arousal"]
        assert result["dominance"] < current["dominance"]

    def test_custom_baseline(self):
        """Test decay towards custom baseline."""
        # Marcus's default contemplative state
        custom_baseline = {"pleasure": 0.0, "arousal": -0.3, "dominance": 0.2}
        pad_logic = PADLogic()

        current = {"pleasure": 0.8, "arousal": 0.8, "dominance": 0.8}
        stimulus = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}

        result = pad_logic.calculate_update(current, stimulus, baseline=custom_baseline)

        # Should decay towards custom baseline, not zero
        assert result["pleasure"] < current["pleasure"]  # Towards 0.0
        assert result["arousal"] < current["arousal"]  # Towards -0.3
        assert result["dominance"] < current["dominance"]  # Towards 0.2


class TestPADQuadrants:
    """Test emotional quadrant edge cases."""

    def setup_method(self):
        """Initialize PADLogic for each test."""
        self.pad_logic = PADLogic()

    @pytest.mark.parametrize(
        "pad_state,expected_quadrant",
        [
            ({"pleasure": 0.7, "arousal": 0.7, "dominance": 0.0}, "Exuberant"),
            ({"pleasure": 0.7, "arousal": -0.7, "dominance": 0.0}, "Dependent"),
            ({"pleasure": -0.7, "arousal": 0.7, "dominance": 0.0}, "Hostile"),
            ({"pleasure": -0.7, "arousal": -0.7, "dominance": 0.0}, "Bored"),
            # Boundary cases
            ({"pleasure": 0.5, "arousal": 0.01, "dominance": 0.0}, "Exuberant"),
            ({"pleasure": 0.5, "arousal": -0.01, "dominance": 0.0}, "Dependent"),
            ({"pleasure": -0.5, "arousal": 0.01, "dominance": 0.0}, "Hostile"),
            ({"pleasure": -0.5, "arousal": -0.01, "dominance": 0.0}, "Bored"),
        ],
    )
    def test_quadrant_classification(
        self, pad_state: dict, expected_quadrant: str
    ):
        """Test quadrant classification for various PAD states."""
        result = self.pad_logic.get_quadrant(pad_state)
        assert result == expected_quadrant


class TestPADRealism:
    """Test realistic emotional scenarios."""

    def setup_method(self):
        """Initialize PADLogic for each test."""
        self.pad_logic = PADLogic()

    def test_user_shares_good_news(self):
        """Simulate user sharing good news."""
        current = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        # Positive, energizing stimulus
        stimulus = {"pleasure": 0.4, "arousal": 0.2, "dominance": 0.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["pleasure"] > 0  # Happy
        assert result["arousal"] > 0  # Energized
        assert self.pad_logic.get_quadrant(result) == "Exuberant"

    def test_user_expresses_sadness(self):
        """Simulate user expressing sadness."""
        current = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        # Negative, low-energy stimulus
        stimulus = {"pleasure": -0.4, "arousal": -0.2, "dominance": 0.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["pleasure"] < 0  # Sad
        assert result["arousal"] < 0  # Low energy
        assert self.pad_logic.get_quadrant(result) == "Bored"

    def test_user_expresses_anxiety(self):
        """Simulate user expressing anxiety."""
        current = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}
        # Negative pleasure, high arousal
        stimulus = {"pleasure": -0.3, "arousal": 0.4, "dominance": 0.0}

        result = self.pad_logic.calculate_update(current, stimulus)

        assert result["pleasure"] < 0  # Distressed
        assert result["arousal"] > 0  # High energy
        assert self.pad_logic.get_quadrant(result) == "Hostile"

    def test_emotional_recovery_over_time(self):
        """Test that strong emotions fade over time without stimulus."""
        # Start with extreme sadness
        current = {"pleasure": -0.9, "arousal": -0.5, "dominance": 0.0}
        no_stimulus = {"pleasure": 0.0, "arousal": 0.0, "dominance": 0.0}

        # Apply decay over multiple "timesteps"
        for _ in range(10):
            current = self.pad_logic.calculate_update(current, no_stimulus)

        # Should have moved significantly towards baseline
        assert current["pleasure"] > -0.9  # Less sad
        assert current["arousal"] > -0.5  # More energized


