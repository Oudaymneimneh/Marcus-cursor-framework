# Testing Introspection Enhancements

## Quick Start

Run the test suite:

```bash
cd /Users/build/Desktop/Marcus-cursor-framework
python evaluation/test_introspection_enhancements.py
```

## What Gets Tested

### 1. Strategy Selection
- **Keyword-based crisis detection**: "I can't handle this" → `supportive`
- **Keyword-based energy detection**: "I have no motivation" → `energizing`
- **PAD-based thresholds**: Pleasure < -0.5 → `supportive`, Arousal < -0.3 → `energizing`
- **Pattern-based selection**: Catastrophizing → `reflective`, Solution-seeking → `balanced`

### 2. Effectiveness Formula
- **Pleasure weight**: Calibrated to 2.5x (was 3.0)
- **Arousal contribution**: Now handles both high and low arousal
- **Strategy bonus**: +0.2 for appropriate strategy in context
- **Negative streak break**: Enhanced bonus for breaking cycles

### 3. Pattern Detection
- **Catastrophizing**: Detects "always", "never", "everything", etc.
- **Solution-seeking**: Detects "what should", "how can", "help me", etc.
- **False positive prevention**: Balance indicators prevent over-detection

### 4. Learning Tracking
- **20-turn simulation**: Tests improvement over conversation
- **Learning stages**: cold_start → warming_up → learning → proficient → expert
- **Learning curve**: Measures effectiveness improvement

## Adding Your Test Scenarios

To test with your actual scenarios, create JSON files:

### `evaluation/test_scenarios/strategy_selection.json`
```json
[
  {
    "scenario_id": "strat_crisis_001",
    "category": "strategy_selection",
    "user_input": "Everything is falling apart and I can't handle this anymore",
    "expected_strategy": "supportive",
    "baseline_pad": {"pleasure": -0.6, "arousal": 0.3, "dominance": -0.2}
  }
]
```

### `evaluation/test_scenarios/effectiveness.json`
```json
[
  {
    "scenario_id": "eff_pleasure_increase_001",
    "category": "effectiveness_formula",
    "user_input": "I finally finished that difficult project!",
    "baseline_pad": {"pleasure": 0.1, "arousal": 0.3, "dominance": 0.2},
    "expected_pad_direction": {"pleasure": "increase"},
    "expected_effectiveness_range": [0.7, 1.0],
    "expected_strategy": "supportive"
  }
]
```

### `evaluation/test_scenarios/pattern_detection.json`
```json
[
  {
    "scenario_id": "pattern_catastrophizing_001",
    "category": "pattern_detection",
    "user_input": "Everything always goes wrong for me. Nothing ever works out.",
    "expected_pattern": "catastrophizing"
  }
]
```

Then modify `test_introspection_enhancements.py` to load from these files:

```python
async def load_test_scenarios() -> Dict[str, List[Dict]]:
    scenarios = {}
    
    # Load from JSON files
    for category in ['strategy_selection', 'effectiveness', 'pattern_detection']:
        file_path = Path(f"evaluation/test_scenarios/{category}.json")
        if file_path.exists():
            with open(file_path) as f:
                scenarios[category] = json.load(f)
    
    return scenarios
```

## Expected Results

### Strategy Selection
- **Crisis detection**: 95%+ accuracy
- **Energy detection**: 75%+ accuracy
- **Pattern-based**: Should match expected strategies

### Effectiveness Formula
- **Positive scenarios**: 0.7-1.0 range
- **Negative scenarios**: 0.0-0.4 range
- **Neutral scenarios**: 0.4-0.6 range

### Pattern Detection
- **Catastrophizing**: 90%+ accuracy
- **Solution-seeking**: 90%+ accuracy
- **False positives**: <10% (balanced statements shouldn't trigger)

### Learning Tracking
- **Improvement**: Should show 0.15+ improvement over 20 turns
- **Learning stage**: Should progress from cold_start → warming_up

## Troubleshooting

### Tests fail with "No module named 'src'"
Make sure you're running from the project root:
```bash
cd /Users/build/Desktop/Marcus-cursor-framework
python evaluation/test_introspection_enhancements.py
```

### Database errors
The test uses in-memory SQLite. If you see errors, check that `aiosqlite` is installed:
```bash
pip install aiosqlite
```

### Strategy selection not matching
Check logs to see which detection method triggered:
- `CRISIS_KEYWORDS` - keyword-based crisis
- `CRISIS_PAD` - PAD-based crisis (pleasure < -0.5)
- `ENERGY_KEYWORDS` - keyword-based energy
- `ENERGY_PAD` - PAD-based energy (arousal < -0.3)
- `PATTERN` - pattern-based selection

## Next Steps

1. **Run the test suite** to verify improvements
2. **Add your actual scenarios** to JSON files
3. **Review failures** and adjust thresholds if needed
4. **Test with real API** by running the server and sending requests

## Integration with Real API

To test with the actual running server:

```bash
# Start the server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# In another terminal, test a scenario
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "I can'\''t handle this anymore"
  }'

# Check logs for:
# - Strategy selected: supportive
# - Effectiveness measured: X.XX
# - Patterns detected: [...]
```
