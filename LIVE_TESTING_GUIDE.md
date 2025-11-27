# Live Testing & Monitoring Guide

## See Marcus's Brain in Action! 🧠

This guide shows you how to test Marcus live and see **exactly** how he makes decisions using introspection, memory, emotions, and logic.

---

## Quick Start (3 Steps)

### Step 1: Start the Backend Server

```bash
cd /Users/build/Desktop/Marcus-cursor-framework

# Activate virtual environment (if using one)
source .venv/bin/activate  # or: python -m venv .venv && source .venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt

# Start the server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
INFO:     [Marcus] SENTIMENT ANALYSIS: ADVANCED MODE (Transformer)
```

### Step 2: Open the Monitoring Dashboard

Open `marcus_monitor.html` in your browser:

```bash
# On macOS:
open marcus_monitor.html

# Or just double-click the file in Finder
```

**What you'll see:**
- **Left Panel**: Live conversation with Marcus
- **Right Panels**: Real-time introspection data showing:
  - Strategy selection (supportive, energizing, balanced, etc.)
  - Effectiveness scores (0.0-1.0)
  - Pattern detection (catastrophizing, solution-seeking)
  - Warning flags (crisis, low arousal, etc.)
  - Emotional state (PAD values)
  - Decision tree (how Marcus chose his strategy)

### Step 3: Test Different Scenarios

Try these messages to see Marcus's decision-making:

#### Crisis Detection Test
```
"I can't handle this anymore, everything is falling apart"
```
**Expected:** Strategy = `supportive`, Warning flags = `crisis_detected`

#### Energy Detection Test
```
"I have no motivation to do anything today"
```
**Expected:** Strategy = `energizing`, Warning flags = `low_arousal`

#### Pattern Detection Test
```
"Everything always goes wrong for me. Nothing ever works out."
```
**Expected:** Patterns = `catastrophizing`, Strategy = `reflective`

#### Solution-Seeking Test
```
"What should I do? How can I fix this situation?"
```
**Expected:** Patterns = `solution_seeking`, Strategy = `balanced`

#### Positive Achievement Test
```
"I finally finished that difficult project I've been working on!"
```
**Expected:** Effectiveness = `0.7-1.0`, Pleasure increases

---

## What You're Observing

### 1. **Strategy Selection** (Top Right Panel)
Shows which strategy Marcus chose and why:
- `CRISIS_KEYWORDS` → supportive (keyword detected)
- `CRISIS_PAD` → supportive (pleasure < -0.5)
- `ENERGY_KEYWORDS` → energizing (low energy detected)
- `ENERGY_PAD` → energizing (arousal < -0.3)
- `PATTERN` → reflective/balanced (pattern-based)
- `DATA-DRIVEN` → best strategy from history

### 2. **Effectiveness Measurement** (Top Right Panel)
Shows how effective Marcus thinks his response was:
- **0.7-1.0**: Excellent (positive scenarios, breaking negative streaks)
- **0.4-0.7**: Good (neutral scenarios, appropriate strategy)
- **0.0-0.4**: Poor (negative scenarios, wrong strategy)

### 3. **Pattern Detection** (Middle Right Panel)
Shows what behavioral patterns Marcus detected:
- `catastrophizing`: Extreme negative thinking
- `solution_seeking`: User wants advice/guidance
- `None`: No clear pattern (balanced statement)

### 4. **Warning Flags** (Middle Right Panel)
Shows concerns Marcus detected:
- `crisis_detected`: Severe negative pleasure (< -0.5)
- `low_arousal`: User is lethargic (< -0.3)
- `prolonged_negative_state`: 3+ consecutive negative states
- `engagement_dropping`: Arousal trending down

### 5. **Emotional State (PAD)** (Bottom Right Panel)
Shows Marcus's emotional model:
- **Pleasure**: -1.0 (very negative) to +1.0 (very positive)
- **Arousal**: -1.0 (calm) to +1.0 (excited)
- **Dominance**: -1.0 (submissive) to +1.0 (dominant)
- **Quadrant**: Emotional classification (e.g., "Anxious", "Content")

### 6. **Memory & Learning** (Bottom Right Panel)
Shows Marcus's learning progress:
- **Total Interactions**: How many messages exchanged
- **Learning Stage**: 
  - `Cold Start` (0 interactions)
  - `Warming Up` (1-10 interactions)
  - `Learning` (10-50 interactions)
  - `Proficient` (50-100 interactions)
  - `Expert` (100+ interactions)

---

## Viewing Server Logs

To see detailed introspection logs, watch the terminal where the server is running:

```bash
# You'll see logs like:
[Marcus] Introspecting...
[Marcus] Strategy: CRISIS_KEYWORDS - detected crisis language in user input
[Marcus] Strategy selected: supportive
[Marcus] Sentiment: sadness (confidence: 0.85)
[Marcus] Emotional: {'pleasure': -0.3, 'arousal': 0.2} -> {'pleasure': -0.5, 'arousal': 0.15} (Anxious)
[Marcus] Effectiveness measured: 0.65
Pattern: catastrophizing detected (indicators=3, balance=0, delta=0.15)
```

---

## Alternative: Simple Chat Interface

If you prefer a simpler interface, use `chat.html`:

```bash
open chat.html
```

This shows:
- Basic conversation
- PAD emotional state visualization
- No introspection details (cleaner UI)

---

## Testing Learning Over Time

To see Marcus learn and adapt:

1. **Start a conversation** with 5-10 messages
2. **Watch the effectiveness scores** - they should improve as Marcus learns what works
3. **Check the relationship stage** - should progress from "Stranger" → "Acquaintance"
4. **Try the same scenario twice** - Marcus should adapt based on what worked before

Example learning conversation:
```
Turn 1: "I'm feeling anxious" → Effectiveness: 0.45
Turn 5: "I'm still anxious" → Effectiveness: 0.55 (learning what works)
Turn 10: "The anxiety is better" → Effectiveness: 0.70 (found effective approach)
```

---

## Troubleshooting

### "Cannot connect to backend"
- Make sure the server is running on port 8000
- Check: `curl http://localhost:8000/health`

### "No introspection data showing"
- Check server logs for errors
- Verify database is connected
- Check that introspection service is being called

### "Strategy always shows 'balanced'"
- This is normal for first few interactions (cold start)
- After 5+ interactions, Marcus will use data-driven strategies
- Try different message types to trigger keyword-based strategies

### "Effectiveness scores seem wrong"
- Check the test scenarios in `evaluation/test_introspection_enhancements.py`
- Verify PAD values are changing correctly
- Review server logs for effectiveness calculation details

---

## Next Steps

1. **Run the test suite** to verify everything works:
   ```bash
   python evaluation/test_introspection_enhancements.py
   ```

2. **Try your own scenarios** and see how Marcus responds

3. **Monitor the logs** to understand the decision-making process

4. **Check the database** to see stored patterns and strategies:
   ```bash
   # If using SQLite:
   sqlite3 your_database.db
   SELECT * FROM strategies;
   SELECT * FROM patterns;
   ```

---

## What You're Seeing

Every message you send triggers:

1. **Introspection** → Marcus asks: "What do I know about this user?"
2. **Pattern Detection** → Marcus asks: "Is this a recurring behavior?"
3. **Strategy Selection** → Marcus asks: "What approach should I use?"
4. **Emotional Calculation** → Marcus asks: "How should I feel about this?"
5. **Response Generation** → Marcus generates context-aware reply
6. **Effectiveness Measurement** → Marcus asks: "Did that work?"
7. **Learning** → Marcus updates his memory with what worked

**This is Marcus's "brain" in action!** 🧠
