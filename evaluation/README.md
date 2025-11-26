# Evaluation System

Two-track validation approach for Marcus AI.

## Files

- **`ai_raters.py`** - Automated AI evaluation (Claude, GPT-4, Gemini)
- **`compare_ratings.py`** - Combined AI + Human analysis
- **`AI_EVALUATION_GUIDE.md`** - Complete setup and usage guide
- **`baseline_comparison.py`** - Original baseline generator (legacy)

## Quick Start

### 1. Get Gemini API Key

Visit: https://aistudio.google.com/app/apikey

Add to `.env`:
```
GEMINI_API_KEY=your_key_here
```

### 2. Test AI Evaluation (5 scenarios)

```bash
cd evaluation
python ai_raters.py --limit 5
```

### 3. Run Full Evaluation (50 scenarios)

```bash
python ai_raters.py
```

### 4. Analyze Results

```bash
python compare_ratings.py --ai ai_ratings.json
```

## What You Get

**AI Evaluation Results:**
- Which model wins most battles
- Performance by category (philosophy, crisis, etc.)
- AI rater agreement metrics
- Detailed scores (wisdom, empathy, actionability)

**After Human Collection:**
- AI vs Human agreement rates
- Where judgments diverge
- Actionable improvement insights

## Cost

**AI Evaluation (50 scenarios):**
- ~900 API calls total
- ~$1.60 total cost
- ~15-20 minutes runtime

**Free Alternative:**
- Use `--limit 10` for smaller sample
- Comment out expensive raters (GPT-4)
- Still get valid results for ~$0.20

## Next Steps

See `AI_EVALUATION_GUIDE.md` for:
- Detailed setup instructions
- Troubleshooting
- Interpretation guide
- Human rating collection strategy


