# AI + Human Evaluation System

Two-track evaluation system for validating Marcus AI performance.

## Architecture

```
Track 1: AI Raters (Fast, Automated)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Claude, GPT-4, Gemini evaluate all scenarios
├── Quantitative baseline
├── Fast iteration
└── Meta-question: Do AIs prefer Marcus?

Track 2: Human Raters (Slow, Qualitative)  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reddit crowdsourcing via gamified interface
├── Real-world validation
├── Qualitative insights
└── Gold standard truth

Combined Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Compare AI vs Human ratings
├── Agreement metrics
├── Bias detection
└── Actionable insights for Marcus improvement
```

---

## Setup

### 1. Install Dependencies

```bash
pip install openai anthropic google-generativeai numpy
```

### 2. Add Gemini API Key

Get key from: https://aistudio.google.com/app/apikey

Add to `.env`:
```bash
GEMINI_API_KEY=your_gemini_key_here
```

Your `.env` should now have:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
```

### 3. Verify Setup

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY']
for key in keys:
    val = os.getenv(key)
    status = '✅' if val else '❌'
    print(f'{status} {key}: {\"Set\" if val else \"Missing\"}')
"
```

---

## Track 1: AI Evaluation (Run Now)

### Quick Test (5 scenarios)

```bash
cd evaluation
python ai_raters.py --limit 5
```

Expected output:
```
🤖 AI EVALUATION SYSTEM
============================================================
Input: /Users/admin/Downloads/files/baseline_responses_50.json
Output: ai_ratings.json
Raters: claude, gpt4, gemini
============================================================

[1/5] PHIL-001 (philosophy)
  Evaluating 6 pairs with 3 AI raters...

...

✅ Saved AI evaluations to: ai_ratings.json

📊 RATER STATISTICS
============================================================
Claude Sonnet 4: 30 successful, 0 failed (100.0% success rate)
GPT-4: 30 successful, 0 failed (100.0% success rate)
Gemini: 30 successful, 0 failed (100.0% success rate)
```

### Full Evaluation (All 50 scenarios)

```bash
python ai_raters.py
```

**Time:** ~15-20 minutes
**Cost estimate:**
- Claude: ~$0.50
- GPT-4: ~$1.00
- Gemini: ~$0.10
- **Total: ~$1.60**

Each scenario = 6 pairs × 3 raters = 18 API calls
50 scenarios = 900 total API calls

---

## Track 2: Human Evaluation (Deploy to Reddit)

### Build Gamified Interface

```bash
# Create public interface
python build_public_interface.py

# Deploy to GitHub Pages
cd ../ai-wisdom-battle
git push origin main

# Post to Reddit
# See REDDIT_DEPLOYMENT_PLAN.md for strategy
```

**Target:** 150+ human raters (30 per group)

---

## Combined Analysis

### After AI Evaluation Completes

```bash
python compare_ratings.py --ai ai_ratings.json
```

Output:
```
📊 AI RATINGS ANALYSIS
======================================================================

🏆 MODEL RANKINGS (by AI judges)
----------------------------------------------------------------------
🥇 1. marcus          -  45 wins (35.2%)
🥈 2. gpt4_stoic      -  38 wins (29.7%)
🥉 3. claude          -  32 wins (25.0%)
   4. gpt4            -  13 wins (10.2%)

🤝 AI RATER AGREEMENT
----------------------------------------------------------------------
Unanimous decisions: 67 (82.7%)
Split decisions: 14 (17.3%)

📂 PERFORMANCE BY CATEGORY
----------------------------------------------------------------------

PHILOSOPHY:
  marcus          - 12 wins
  gpt4_stoic      -  9 wins
  claude          -  7 wins

CRISIS:
  marcus          - 15 wins
  ...
```

### After Human Data Collected

```bash
python compare_ratings.py --ai ai_ratings.json --human human_ratings.json
```

Additional output:
```
🔍 AI vs HUMAN COMPARISON
======================================================================

Agreement Rate: 73.2%
  Unanimous (AI + Human agree): 89 scenarios
  AI preferred, Human disagreed: 15 scenarios  
  Human preferred, AI disagreed: 12 scenarios

Biggest disagreements:
  CRISIS-007: AI chose marcus, Humans chose claude (81% human consensus)
  PHIL-003: AI chose gpt4_stoic, Humans chose marcus (76% human consensus)
```

---

## What the Data Tells You

### 1. Marcus Performance

**AI judges say:**
- Wins X% of head-to-head battles
- Strongest in [category]
- Weakest in [category]

**Humans say:**
- Wins Y% of head-to-head battles  
- Preferred for [qualities]
- Needs improvement in [areas]

### 2. Where to Improve

**Low AI scores + Low human scores = Clear weakness**
→ Fix immediately

**High AI scores + Low human scores = Missing human connection**
→ Add empathy, relatability

**Low AI scores + High human scores = AI judges miss nuance**
→ Validate with more humans

### 3. Validation Questions

- **Do AIs prefer Marcus?** If yes, might be overfitted to AI-style reasoning
- **Do humans prefer Marcus?** If yes, you've succeeded!
- **Agreement rate?** High = reliable data, Low = investigate differences
- **Category performance?** Optimize weakest areas

---

## Workflow

```
Day 1: Run AI Evaluation
├── python ai_raters.py --limit 5 (test)
├── python ai_raters.py (full run)
└── python compare_ratings.py --ai ai_ratings.json

Day 2-3: Deploy Human Interface  
├── Build public interface
├── Deploy to GitHub Pages
└── Post to r/SampleSize (soft launch)

Day 4-7: Scale Human Collection
├── Post to r/Stoicism
├── Post to r/DecidingToBeBetter
├── Monitor completion rates
└── Adjust strategy

Day 8: Combined Analysis
├── Download human ratings
├── python compare_ratings.py --ai ai_ratings.json --human human_ratings.json
├── Generate insights report
└── Plan Marcus improvements

Day 9+: Iterate
├── Update Marcus based on insights
├── Re-run AI evaluation
├── Validate improvements
└── Repeat
```

---

## Success Metrics

### AI Evaluation
- ✅ All 3 raters complete successfully
- ✅ Marcus wins >30% of battles (vs 25% random baseline)
- ✅ Rater agreement >70%

### Human Evaluation
- ✅ 150+ complete ratings (30 per group)
- ✅ Completion rate >40%
- ✅ Marcus wins >35% (humans harder to please)

### Combined
- ✅ AI-human agreement >65%
- ✅ Marcus ranks #1 or #2 overall
- ✅ Clear insights for improvement

---

## Troubleshooting

### AI Raters Failing

**Error: API key not found**
```bash
# Check .env file
cat .env | grep _API_KEY

# Reload environment
source .venv/bin/activate
python ai_raters.py --limit 1
```

**Error: Rate limited**
```bash
# Increase delay in ai_raters.py
# Line 185: await asyncio.sleep(0.5)  → sleep(2.0)
```

**Error: JSON parsing failed**
```bash
# One rater having issues, others work?
# Check output in ai_ratings.json for error messages
# That rater's responses may be malformed
```

### Low AI Agreement

**Split decisions >30%?**
- Normal for controversial scenarios
- Review split decisions manually
- May indicate genuinely hard choices

### Human Completion Rate Low

**<30% completion?**
- Reduce battles from 10 to 5
- Improve hook scenarios
- Add more gamification
- Check mobile experience

---

## Cost Optimization

### Reduce AI Evaluation Cost

**Option 1: Sample scenarios**
```bash
python ai_raters.py --limit 25  # Half the scenarios
```

**Option 2: Use fewer raters**
```python
# In ai_raters.py, comment out expensive raters:
self.raters = {
    'claude': ClaudeRater(),
    # 'gpt4': GPT4Rater(),  # Most expensive
    'gemini': GeminiRater()   # Cheapest
}
```

**Option 3: Reduce pairs per scenario**
```python
# In evaluate_scenario(), only test key pairs:
pairs = [
    ('marcus', 'gpt4'),
    ('marcus', 'gpt4_stoic'),
    ('marcus', 'claude')
]
# Skip comparing gpt4 vs gpt4_stoic, etc.
```

---

## Next Steps

1. ✅ Add Gemini API key to `.env`
2. ✅ Test AI evaluation: `python ai_raters.py --limit 5`
3. ✅ Run full AI evaluation: `python ai_raters.py`  
4. ✅ Review AI results: `python compare_ratings.py --ai ai_ratings.json`
5. ⏳ Build human interface (see REDDIT_DEPLOYMENT_PLAN.md)
6. ⏳ Deploy to Reddit
7. ⏳ Collect 150+ human ratings
8. ⏳ Run combined analysis
9. ⏳ Improve Marcus based on insights

**Start with step 1!**


