# Reddit Data Collection - Path B-Minimal
## Quick Start Guide

**Goal:** Collect 1,000 high-quality conversations from Reddit to improve Marcus AI

**Timeline:** 6 hours total (setup → test → validate → production)

**Cost:** $0 (Reddit API is free for research use)

---

## Step 1: Reddit API Setup (15 minutes)

### 1.1 Create Reddit Application

1. Go to: https://www.reddit.com/prefs/apps
2. Scroll down and click **"Create App"** or **"Create Another App"**
3. Fill out form:
   ```
   Name: Marcus AI Research
   App type: ● script
   Description: Academic research on conversational patterns for Stoic philosophy
   About URL: [leave blank]
   Redirect URI: http://localhost:8080
   ```
4. Click **"Create app"**

### 1.2 Copy Credentials

After creating, you'll see:
```
Marcus AI Research
personal use script
[14-character client_id]     ← COPY THIS

secret: [27-character secret]  ← COPY THIS
```

### 1.3 Add to .env File

```bash
# Open .env
nano /Users/admin/Downloads/marcus-cursor-framework/.env

# Add these lines:
REDDIT_CLIENT_ID=your_14_char_client_id_here
REDDIT_CLIENT_SECRET=your_27_char_secret_here

# Save: Ctrl+O, Enter, Ctrl+X
```

---

## Step 2: Install Dependencies (5 minutes)

```bash
cd /Users/admin/Downloads/marcus-cursor-framework

# Install Reddit API wrapper
pip install praw pandas pyarrow python-dotenv
```

---

## Step 3: Test Collection (30 minutes)

**Purpose:** Verify API works and data quality is good

```bash
python scripts/collect_reddit_data.py --test
```

**What it does:**
- Collects 10 posts from r/stoicism
- Takes ~30 minutes
- Output: `evaluation/reddit_test_sample.parquet` (~10-20 conversations)

**Expected output:**
```
✓ Conversations collected: 18
✓ Average upvotes: 87.3
✓ OP engagement rate: 33.3%
✓ Saved to: evaluation/reddit_test_sample.parquet

SAMPLE CONVERSATION:
User Input: I've been struggling with anger lately...
Response: Remember that you always have power over your response...
```

**Decision Gate:**
- ✅ Quality looks good → Proceed to Step 4
- ❌ Issues found → Check credentials, try again

---

## Step 4: Validation Collection (1 hour)

**Purpose:** Verify quality across multiple domains

```bash
python scripts/collect_reddit_data.py --validate
```

**What it does:**
- Collects from 4 subreddits (stoicism, relationships, stress, growth)
- 25 posts each = 100 total
- Takes ~1 hour
- Output: `evaluation/reddit_validation_sample.parquet` (~80-120 conversations)

**Expected checks:**
```
✓ Total conversations: 103 (target: >= 80)
✓ Average upvotes: 62.4 (target: >= 40)
✓ OP engagement: 34.2% (target: >= 25%)
✓ Domain diversity: 4 domains (target: >= 4)
✓ Response length: 156 chars (target: 100-500)

✅ ALL CHECKS PASSED (5/5)
```

**Decision Gate:**
- ✅ All checks pass → Proceed to Step 5
- ⚠️ Some checks fail → Review issues, adjust, retry

---

## Step 5: Production Collection (4 hours)

**Purpose:** Full dataset collection

```bash
python scripts/collect_reddit_data.py --production
```

**What it does:**
- Collects from 10 subreddits
- 100 posts each = 1,000 attempted
- Expected yield: ~600-800 high-quality conversations
- Takes ~4 hours
- Output: `evaluation/reddit_data_1000.parquet`

**Subreddits:**
1. r/stoicism (philosophy)
2. r/philosophy (philosophy)
3. r/DecidingToBeBetter (growth)
4. r/getdisciplined (growth)
5. r/stress (emotional)
6. r/relationships (interpersonal)
7. r/raisedbynarcissists (interpersonal)
8. r/exchristian (existential)
9. r/AsianParentStories (cultural)
10. r/mentalhealth (balance - handled carefully)

**Expected output:**
```
✅ PRODUCTION COMPLETE
Duration: 3.8 hours
Total conversations: 726

Quality metrics:
  Avg post upvotes: 143.2
  Avg response upvotes: 54.7
  Response length: 148 chars
  OP engagement: 36.8%

Domain distribution:
  philosophy: 152 (20.9%)
  interpersonal: 180 (24.8%)
  growth: 155 (21.3%)
  emotional: 92 (12.7%)
  cultural: 84 (11.6%)
  existential: 63 (8.7%)
```

---

## What You Get

### Files Created:

```
evaluation/
├── reddit_test_sample.parquet              (10-20 conversations)
├── reddit_validation_sample.parquet        (80-120 conversations)
├── reddit_data_1000.parquet                (600-800 conversations, MAIN DATASET)
├── reddit_statistics.json                  (Collection stats)
├── reddit_collection.log                   (Full log)
└── reddit_checkpoint_*.parquet             (Intermediate backups)
```

### Data Structure:

Each conversation contains:
```python
{
    'user_input': "Anonymized post text",
    'response': "Anonymized comment text",
    'quality_signals': {
        'post_upvotes': 156,
        'response_upvotes': 48,
        'op_acknowledged': True,
        'reply_count': 7
    },
    'context': {
        'subreddit': 'stoicism',
        'domain': 'philosophy',
        'response_length': 142
    }
}
```

---

## Ethical Safeguards Built-In

### ✅ What IS collected:
- Public posts with high upvotes (community-validated quality)
- Philosophy, growth, relationships, stress management
- Anonymized text (all names/locations removed)

### ❌ What is NOT collected:
- r/SuicideWatch, r/depression (crisis intervention communities)
- Posts with crisis keywords ("suicide", "kill myself", etc.)
- Posts with PII (emails, phone numbers, addresses)
- Low-quality content (<50 upvotes)
- Deleted or removed content

### Privacy Protection:
- All usernames → `[user]`
- All names → `[name]`
- All locations → `[location]`
- All companies → `[employer]`
- All URLs → `[link]`

---

## Troubleshooting

### Issue: "Missing Reddit API credentials"
**Fix:**
1. Double-check `.env` file has both `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`
2. Verify credentials are correct (14 chars for ID, 27 for secret)
3. Make sure no spaces around `=` in `.env`

### Issue: "No conversations collected"
**Causes:**
- `min_upvotes` threshold too high
- Subreddit has low activity
- Network/API issues

**Fix:**
- Lower `min_upvotes` in test mode: `min_upvotes=30`
- Try different subreddit
- Check Reddit API status: https://www.redditstatus.com/

### Issue: "Rate limit exceeded"
**Fix:**
- Script already has 1.1s delay between requests
- Reddit allows 60 requests/minute
- If still issues, Reddit may have temporary restrictions on your account

---

## Next Steps After Collection

### Immediate:
1. **Validate data quality:**
   ```bash
   python scripts/validate_reddit_data.py evaluation/reddit_data_1000.parquet
   ```

2. **Select scenarios for multi-LLM comparison:**
   ```bash
   python scripts/select_comparison_scenarios.py
   ```

### Phase B2: Multi-LLM Comparison
- Compare GPT-4, Claude, Gemini, Llama, Marcus
- 100 scenarios (selected from Reddit data)
- Cost: ~$6
- Time: 30 minutes

---

## FAQ

**Q: Is this legal?**  
A: Yes. Using Reddit's official API for research is allowed under their Terms of Service. We're not scraping HTML or violating rate limits.

**Q: Do I need Reddit account approval?**  
A: No. Creating a Reddit app for "script" type is self-service.

**Q: Can Reddit ban me for this?**  
A: Not if you follow rate limits (we do - 1.1s between requests) and use official API (we do).

**Q: What if I want MORE than 1,000 conversations?**  
A: Adjust `posts_per_subreddit` parameter. But 1,000 high-quality samples is already very good for this use case.

**Q: Can I add more subreddits?**  
A: Yes, edit `get_recommended_subreddits()` in `evaluation/reddit_collector.py`. Avoid forbidden subreddits (crisis/clinical content).

---

## Timeline Summary

| Step | Mode | Time | Output |
|------|------|------|--------|
| 1 | Setup | 15 min | API credentials configured |
| 2 | Dependencies | 5 min | Libraries installed |
| 3 | Test | 30 min | ~20 conversations |
| 4 | Validate | 1 hour | ~100 conversations |
| 5 | Production | 4 hours | ~700 conversations |
| **TOTAL** | | **6 hours** | **~700 high-quality conversations** |

---

## Success Criteria

✅ **Collection is successful if:**
- At least 500 conversations collected
- Average upvotes > 40
- Domain diversity >= 5 domains
- No PII leaks detected
- No crisis content present

✅ **Data is ready for:**
- Multi-LLM comparison (Phase B2)
- Pattern extraction
- Strategy effectiveness measurement
- Quality predictor training

---

**Ready to start? Run:**
```bash
python scripts/collect_reddit_data.py --test
```
