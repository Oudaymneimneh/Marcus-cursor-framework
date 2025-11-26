# Quick Start: AI Evaluation

## The Path Issue (Resolved)

**Problem:** Running `python ai_raters.py` from the evaluation directory needs the venv from the parent directory.

**Solution:** Use the run script (handles paths automatically)

---

## How to Run

### Option 1: Run Script (Easiest)

```bash
# From anywhere
cd /Users/admin/Downloads/marcus-cursor-framework/evaluation
./run_ai_evaluation.sh --limit 5
```

### Option 2: Manual (If script doesn't work)

```bash
# From project root
cd /Users/admin/Downloads/marcus-cursor-framework
source .venv/bin/activate
python evaluation/ai_raters.py --limit 5
```

### Option 3: Direct Python (Advanced)

```bash
# From evaluation directory
cd /Users/admin/Downloads/marcus-cursor-framework/evaluation
../.venv/bin/python ai_raters.py --limit 5
```

---

## Commands

### Test (5 scenarios, 2 min, ~$0.15)

```bash
./run_ai_evaluation.sh --limit 5
```

### Full Run (50 scenarios, 20 min, ~$1.60)

```bash
./run_ai_evaluation.sh
```

### Analyze Results

```bash
source ../.venv/bin/activate
python compare_ratings.py --ai ai_ratings.json
```

---

## Prerequisites

✅ Virtual environment activated (script does this automatically)
✅ Packages installed:
- openai
- anthropic  
- google-generativeai ✅ (just installed)

✅ API keys in `.env`:
- OPENAI_API_KEY ✅
- ANTHROPIC_API_KEY ✅
- GEMINI_API_KEY ⚠️ (needs your key)

---

## Add Gemini Key

1. Get key: https://aistudio.google.com/app/apikey
2. Edit `.env` in project root
3. Add: `GEMINI_API_KEY=your_key_here`

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'google.generativeai'"

✅ Fixed! Just installed it.

### "API key not found"

Check `.env` file:
```bash
cat ../.env | grep GEMINI_API_KEY
```

Add if missing:
```bash
echo "GEMINI_API_KEY=your_key" >> ../.env
```

### "Permission denied: ./run_ai_evaluation.sh"

Make executable:
```bash
chmod +x run_ai_evaluation.sh
```

---

## What Happens When You Run

```
🔧 Activating virtual environment...
✅ Environment activated
📍 Working from: /Users/admin/Downloads/marcus-cursor-framework/evaluation

🤖 AI EVALUATION SYSTEM
============================================================
Input: /Users/admin/Downloads/files/baseline_responses_50.json
Output: ai_ratings.json
Raters: claude, gpt4, gemini
============================================================

[1/5] PHIL-001 (philosophy)
  Evaluating 6 pairs with 3 AI raters...
  ✅ Claude rated
  ✅ GPT-4 rated
  ✅ Gemini rated

...

✅ Saved AI evaluations to: ai_ratings.json
```

---

## Next Steps

1. Add Gemini API key to `.env`
2. Run test: `./run_ai_evaluation.sh --limit 5`
3. If successful, run full: `./run_ai_evaluation.sh`
4. Analyze: `python compare_ratings.py --ai ai_ratings.json`
5. See which model ranks #1!


