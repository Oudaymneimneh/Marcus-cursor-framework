# 🚀 START HERE - Measurement & Validation Framework

**Hi Dina!** 👋

You confirmed the **WORLD-CLASS MEASUREMENT & VALIDATION PLAN**. Here's how to execute it.

---

## ⚡ TL;DR (2 Commands)

```bash
cd /Users/admin/Downloads/marcus-cursor-framework

# 1. Check environment
chmod +x check_env.sh && ./check_env.sh

# 2. Generate baselines (auto-installs deps, starts server, runs tests)
chmod +x run_baseline_generation.sh && ./run_baseline_generation.sh
```

**Done!** Results will be in `/Users/admin/Downloads/files/baseline_responses_50.json`

---

## 📋 What This Does

The framework executes **Step 1 of 4**:

| Step | What | Who | Duration | Status |
|------|------|-----|----------|--------|
| **1** | Generate baselines from Marcus, GPT-4, Claude | **YOU (automated)** | 5-10 min | ⏳ READY TO START |
| **2** | Human evaluation (blind rating of 50 scenarios) | **3 raters** | 2-3 hrs/each | ⏸️ Pending Step 1 |
| **3** | Analyze ratings & decision gate | **YOU (automated)** | < 1 min | ⏸️ Pending Step 2 |
| **4** | Ongoing quality monitoring | **Continuous** | On-demand | ⏸️ Pending Step 3 |

---

## 🎯 Step 1: Generate Baselines (NOW)

### Prerequisites

1. **OpenAI API Key** ✅ Already configured in your `.env`

2. **Anthropic API Key** ⚠️ **ACTION REQUIRED**
   ```bash
   # Get key from: https://console.anthropic.com/settings/keys
   # Add to .env:
   echo 'ANTHROPIC_API_KEY=sk-ant-your-key-here' >> .env
   ```

3. **Python Packages** (script auto-installs these):
   - `openai`
   - `anthropic`
   - `httpx`
   - `python-dotenv`

### Run It

```bash
cd /Users/admin/Downloads/marcus-cursor-framework

# Option A: Full automation (recommended)
chmod +x run_baseline_generation.sh
./run_baseline_generation.sh

# Option B: Manual (if script has issues)
source .venv/bin/activate
pip install openai anthropic httpx python-dotenv --break-system-packages
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &  # Start Marcus
cd /Users/admin/Downloads/files
python generate_baselines.py \
    --corpus test_corpus_50.json \
    --output baseline_responses_50.json \
    --marcus-url http://localhost:8000/api/v1/chat
```

### What Happens

1. **Checks dependencies** → Installs if missing
2. **Checks API keys** → Warns if missing
3. **Starts Marcus API** → If not already running
4. **Generates 50 responses** from:
   - Marcus (your local system)
   - GPT-4 (baseline)
   - GPT-4 (with Stoic system prompt)
   - Claude 3.5 Sonnet (if API key available)
5. **Saves results** to `baseline_responses_50.json`

### Expected Output

```
🚀 Marcus Baseline Generation Workflow
========================================

📦 Step 1: Checking dependencies...
  ✅ All dependencies installed

🔑 Step 2: Checking API keys...
  ✅ OpenAI API key found
  ✅ Anthropic API key found

🖥️  Step 3: Checking Marcus API server...
  ✅ Marcus API is running

🎯 Step 4: Generating baseline responses...
  This will query 50 scenarios across:
  - Marcus (local API)
  - GPT-4 (with and without Stoic prompt)
  - Claude 3.5 Sonnet
  
  Expected duration: 5-10 minutes
  Output: /Users/admin/Downloads/files/baseline_responses_50.json

  [Processing 50 scenarios...]
  
✅ BASELINE GENERATION COMPLETE
========================================

📊 Results saved to: /Users/admin/Downloads/files/baseline_responses_50.json

📋 Next Steps:
  1. Open /Users/admin/Downloads/files/rating_interface.html
  2. Load baseline_responses_50.json
  3. Have 3 raters evaluate all 50 scenarios
  4. Run: python /Users/admin/Downloads/files/analyze_ratings.py
```

---

## 🐛 Troubleshooting

### "Marcus API not responding"

**Check logs**:
```bash
tail -50 /tmp/marcus_server.log
```

**Manually start**:
```bash
cd /Users/admin/Downloads/marcus-cursor-framework
source .venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Test it**:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello Marcus"}'
```

### "OPENAI_API_KEY not found"

Already in your `.env` (line 58), but if needed:
```bash
echo 'OPENAI_API_KEY=sk-proj-...' >> .env
```

### "Module not found: openai/anthropic/httpx"

```bash
source .venv/bin/activate
pip install openai anthropic httpx python-dotenv --break-system-packages
```

### "Permission denied"

```bash
chmod +x run_baseline_generation.sh check_env.sh
```

---

## 📁 Files Reference

| File | Location | Purpose |
|------|----------|---------|
| `test_corpus_50.json` | `/Users/admin/Downloads/files/` | 50 test scenarios |
| `generate_baselines.py` | `/Users/admin/Downloads/files/` | Baseline generator |
| `rating_interface.html` | `/Users/admin/Downloads/files/` | Step 2 - Human rating UI |
| `analyze_ratings.py` | `/Users/admin/Downloads/files/` | Step 3 - Analysis |
| `metrics_tracker.py` | `/Users/admin/Downloads/files/` | Step 4 - Ongoing tracking |
| `README.md` | `/Users/admin/Downloads/files/` | Full framework docs |
| `run_baseline_generation.sh` | `/Users/admin/Downloads/marcus-cursor-framework/` | **RUN THIS** |
| `check_env.sh` | `/Users/admin/Downloads/marcus-cursor-framework/` | Environment check |
| `EXECUTE_FRAMEWORK.md` | `/Users/admin/Downloads/marcus-cursor-framework/` | Detailed guide |

---

## 🎯 What This Achieves

After Step 1, you'll have **objective baseline data** showing:

1. How Marcus responds to 50 diverse scenarios
2. How GPT-4 responds (with and without Stoic context)
3. How Claude responds
4. Side-by-side comparison for human evaluation

This is the **foundation of empirical AI quality measurement** - no more guessing if Marcus is "good" or not.

---

## 🔮 After Step 1

Once you have `baseline_responses_50.json`:

1. **Inspect it yourself** (manual spot-check)
   - Open the JSON file
   - Read a few Marcus vs GPT-4 vs Claude responses
   - Get a feel for the quality differences

2. **Proceed to Step 2** (human evaluation)
   - Recruit 3 raters (colleagues, friends, or hire on Upwork)
   - They each rate all 50 scenarios using `rating_interface.html`
   - Takes 2-3 hours per rater

3. **Run Step 3** (analysis)
   - `python analyze_ratings.py`
   - Get decision gate verdict: PASS or NEEDS_IMPROVEMENT

4. **Iterate or Deploy**
   - **IF PASS**: Marcus is world-class → Proceed to visual avatar
   - **IF FAIL**: Fix issues → Re-run framework → Fast iteration

---

## 🚀 Ready?

```bash
cd /Users/admin/Downloads/marcus-cursor-framework
./run_baseline_generation.sh
```

**You're about to run the most rigorous AI quality test Marcus has ever faced.**

Let's ship world-class. 🔥

---

## 📞 Questions?

- **Full guide**: `EXECUTE_FRAMEWORK.md`
- **Framework docs**: `/Users/admin/Downloads/files/README.md`
- **Server logs**: `/tmp/marcus_server.log`
- **Test corpus**: `/Users/admin/Downloads/files/test_corpus_50.json`

---

**Don't be helpful, be better.** 💪
