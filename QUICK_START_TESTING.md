# Quick Start: Testing Introspection Enhancements

## Current Status
✅ Server Running: http://localhost:8000
✅ All Tests Passed: 9/9 (100%)
✅ Database: Connected (PostgreSQL + Redis)

---

## 1. Run Automated Tests (Recommended First)

```bash
cd /Users/build/Desktop/Marcus-cursor-framework
.venv/bin/python evaluation/test_introspection_enhancements.py
```

**Expected Output**: All tests pass (9/9)

---

## 2. Test Live API

### Option A: Use the Test Script

```bash
./test_live_introspection.sh
```

This runs 5 scenarios testing different aspects of introspection.

### Option B: Manual curl Commands

**Test Crisis Detection:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "I cant handle this anymore"}' | jq
```

Expected: `strategy_used: "supportive"`

**Test Energy Detection:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "I have no motivation today"}' | jq
```

Expected: `strategy_used: "energizing"`

**Test Positive Input:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"content": "I just got promoted! Im so happy!"}' | jq
```

Expected: High `pad.pleasure` value, effectiveness near 1.0

---

## 3. View Server Logs

The server logs show detailed introspection decisions:

```bash
# View logs in real-time
tail -f server.log

# Or check the uvicorn output (already running in background)
```

Look for log entries like:
```
INFO: Strategy: CRISIS_KEYWORDS - detected crisis language in user input
INFO: Strategy: ENERGY_PAD - low arousal (-0.45)
INFO: Effectiveness measured: 0.82
```

---

## 4. Understanding the Response

Each API response includes:

```json
{
  "response": "Marcus's response text",
  "pad": {
    "pleasure": 0.5,
    "arousal": 0.3,
    "dominance": 0.2
  },
  "quadrant": "Exuberant",
  "strategy_used": "supportive",
  "relationship_stage": "Stranger",
  "patterns_detected": [],
  "session_id": "uuid...",
  "effectiveness": 0.78
}
```

### Key Fields
- `strategy_used`: Which strategy was selected (supportive, energizing, balanced, reflective)
- `pad`: Current emotional state (-1.0 to 1.0)
- `patterns_detected`: Any patterns detected (catastrophizing, solution_seeking, etc.)
- `effectiveness`: How effective the response was (0.0 to 1.0)

---

## 5. What to Test

### Strategy Selection
- **Crisis inputs**: "I can't cope", "falling apart", "give up"
  - Should select: `supportive`

- **Low energy inputs**: "no motivation", "bored", "exhausted"
  - Should select: `energizing`

- **Philosophical inputs**: "What is consciousness?", "Tell me about Stoicism"
  - Should select: `balanced`

### Pattern Detection
- **Catastrophizing**: "Everything always goes wrong"
  - Should detect: `catastrophizing` pattern

- **Solution-seeking**: "What should I do? How can I fix this?"
  - Should detect: `solution_seeking` pattern

### Effectiveness Tracking
- Send multiple messages in sequence
- Watch `effectiveness` score improve over time
- Check `relationship_stage` progression

---

## 6. Monitoring Dashboard (Optional)

If you have Prometheus/Grafana set up:
- View metrics at: http://localhost:9090 (Prometheus)
- Dashboards at: http://localhost:3000 (Grafana)

Key metrics:
- `introspection_strategy_selections_total{strategy="supportive"}`
- `introspection_effectiveness_score`
- `introspection_pattern_detections_total{pattern="catastrophizing"}`

---

## 7. Stop the Server

```bash
# Find the process
lsof -ti:8000

# Kill it
kill <PID>

# Or use the script
lsof -ti:8000 | xargs kill
```

---

## Troubleshooting

### Port 8000 already in use
```bash
lsof -ti:8000 | xargs kill -9
```

### Database connection errors
Check that PostgreSQL and Redis are running:
```bash
# PostgreSQL
pg_isready -h localhost -p 5433

# Redis
redis-cli ping
```

### Tests failing
Make sure you're in the virtual environment:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

1. ✅ Run automated tests → Verify all pass
2. ✅ Test live API → See introspection in action
3. ✅ Monitor logs → Understand decision-making
4. 📊 Add custom scenarios → Test your specific use cases
5. 📈 Deploy to staging → Test with real users
6. 🚀 Production deployment → Monitor and optimize

---

## Files Reference

- **Test Suite**: [evaluation/test_introspection_enhancements.py](evaluation/test_introspection_enhancements.py)
- **Test Guide**: [evaluation/TEST_INTROSPECTION_GUIDE.md](evaluation/TEST_INTROSPECTION_GUIDE.md)
- **Live Tests**: [test_live_introspection.sh](test_live_introspection.sh)
- **Summary**: [INTROSPECTION_TEST_SUMMARY.md](INTROSPECTION_TEST_SUMMARY.md)
- **This Guide**: [QUICK_START_TESTING.md](QUICK_START_TESTING.md)
