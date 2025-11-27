# Path B: Deep Research Implementation Guide

## Building World-Class AI Through Empirical Data

**Decision Date:** 2025-11-25  
**Chosen Path:** Deep research foundation before visual avatar  
**Timeline:** 8-10 weeks to world-class AI system  
**Philosophy:** Evidence-driven, not theory-driven development

---

## Executive Summary

**What We're Building:**

A world-class conversational AI system for Marcus Aurelius, grounded in:

- 30,000+ real human conversations (Reddit data)
- Mental models extracted from 5 leading LLMs
- Empirically-validated strategy selection
- Human-rated ground truth quality metrics

**Why This Approach:**

- Current system works but is theory-driven (1974 PAD model)
- Real human data reveals what actually helps people
- Multi-LLM comparison extracts best-of-breed approaches
- Empirical foundation enables continuous improvement

**What We're NOT Building:**

- Visual avatar (deferred to Phase C)
- TTS/FLAME systems (deferred)
- Unreal Engine integration (deferred)

**Success Criteria:**

- Marcus outperforms GPT-4, Claude, Gemini in 70%+ blind preferences
- Human quality ratings > 4.2/5.0 average
- Empirically-validated strategy rules
- Quality predictor R² > 0.7
- System learns from every conversation

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Phase B1: Data Collection Infrastructure](#phase-b1-data-collection-infrastructure)
3. [Phase B2: Multi-LLM Comparison System](#phase-b2-multi-llm-comparison-system)
4. [Phase B3: Data Analysis & Pattern Extraction](#phase-b3-data-analysis--pattern-extraction)
5. [Phase B4: AI Reconstruction](#phase-b4-ai-reconstruction)
6. [Phase B5: Validation & Deployment](#phase-b5-validation--deployment)
7. [What To Do / What NOT To Do](#what-to-do--what-not-to-do)
8. [Success Metrics](#success-metrics)
9. [Timeline & Resources](#timeline--resources)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    WORLD-CLASS MARCUS AI                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         DATA COLLECTION LAYER (Phase B1)             │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • Reddit Scraper (40 subreddits)                   │  │
│  │  • Ethical Filtering & Anonymization                │  │
│  │  • Quality Signal Extraction (upvotes, replies)     │  │
│  │  • Storage: 30K+ conversations with metadata        │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      MULTI-LLM COMPARISON LAYER (Phase B2)           │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • GPT-4o, GPT-4o-mini (OpenAI)                     │  │
│  │  • Claude 3.5 Sonnet (Anthropic)                    │  │
│  │  • Gemini 1.5 Pro (Google)                          │  │
│  │  • Llama-3-70B (Meta via Groq)                      │  │
│  │  • Marcus (current system)                           │  │
│  │  → Generate responses for 500 scenarios              │  │
│  │  → Mental model identification                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      ANALYSIS & LEARNING LAYER (Phase B3)            │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • Human Rating Collection (5-10 raters)            │  │
│  │  • Pattern Extraction (what works where)            │  │
│  │  • Mental Model Effectiveness Analysis              │  │
│  │  • Strategy Selection Rules (empirical)             │  │
│  │  • Quality Predictor Training (ML model)            │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       RECONSTRUCTED AI LAYER (Phase B4)              │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • Evidence-Based Dialogue Generator                │  │
│  │  • Empirical Strategy Selection                     │  │
│  │  • Context-Adaptive Response Generation             │  │
│  │  • Real-Time Quality Prediction                     │  │
│  │  • Continuous Learning from Feedback                │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       VALIDATION LAYER (Phase B5)                    │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • A/B Testing Framework                            │  │
│  │  • Blind Preference Studies                         │  │
│  │  • Statistical Significance Testing                 │  │
│  │  • Production Monitoring                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Reddit Posts → Ethical Filter → Quality Filter → Anonymize → Storage
                                                                ↓
Test Scenarios → Multi-LLM → Responses × 5 → Human Rating → Ground Truth
                                                                ↓
Ground Truth + Reddit Data → Analysis → Mental Models + Patterns
                                                                ↓
Mental Models → New Dialogue Generator → A/B Test → Deploy if Better
                                                                ↓
Production Users → Feedback → Continuous Learning → Improvement
```

---

## Phase B1: Data Collection Infrastructure

**Duration:** Week 1 (6 days of scraping + 1 day validation)  
**Deliverable:** 30,000+ human-validated conversations from Reddit

### B1.1: Reddit API Setup (2 hours)

#### What To Do:

**1.1.1 Create Reddit Application**

```bash
# Go to: https://www.reddit.com/prefs/apps
# Create app:
#   - Type: script
#   - Name: "Marcus AI Research (Educational Use Only)"
#   - Redirect URI: http://localhost:8080
#   - Description: "Academic research on conversational AI"

# Save credentials:
CLIENT_ID="your_client_id_here"
CLIENT_SECRET="your_client_secret_here"
```

**1.1.2 Install Dependencies**

```bash
cd /Users/admin/Downloads/marcus-cursor-framework
pip install praw pandas pyarrow faker
```

**1.1.3 Test API Connection**

```python
import praw

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent='Marcus AI Research v1.0 (Educational)'
)

# Test
subreddit = reddit.subreddit('stoicism')
print(f"Connected to r/stoicism: {subreddit.subscribers} subscribers")
```

#### What NOT To Do:

❌ **DO NOT** use web scraping (HTML parsing) - violates Reddit ToS  
❌ **DO NOT** exceed 60 requests/minute - will get rate limited  
❌ **DO NOT** scrape without user agent - will get banned  
❌ **DO NOT** claim commercial use - use "educational/research"  
❌ **DO NOT** use multiple accounts to bypass limits - violates ToS

---

### B1.2: Subreddit Selection & Prioritization (4 hours)

#### Tier 1: Core Philosophy & Growth (Priority 1)

**Subreddits:**
- r/Stoicism (300K) - Philosophy alignment
- r/DecidingToBeBetter (200K) - Growth mindset  
- r/getdisciplined (900K) - Actionable habits
- r/selfimprovement (800K) - Personal development

**Collection Target:** 10,000 posts (2,500 per subreddit)  
**Quality Threshold:** min_upvotes=15, min_comments=5  
**Expected Time:** 1.5 days continuous scraping

**Why These:**
- High quality moderation
- Constructive community norms
- Philosophical alignment with Stoicism
- Actionable advice (not just venting)

#### Tier 2: Stress & Emotional Challenges (Priority 2)

**Subreddits:**
- r/stress (50K) - Work/life stress
- r/Burnout (30K) - Professional burnout
- r/productivity (2M) - Managing overwhelm
- r/anxiety (200K) - Stress management (handle carefully)

**Collection Target:** 6,000 posts  
**Quality Threshold:** min_upvotes=10, min_comments=3  
**Expected Time:** 1 day

**Why These:**
- Common user challenges Marcus will encounter
- Emotional support data
- Crisis recognition patterns

#### Tier 3: Family & Relationships (Priority 3)

**Subreddits:**
- r/family (200K) - General family dynamics
- r/relationships (7M) - Relationship advice
- r/relationship_advice (8M) - Conflict resolution
- r/parenting (5M) - Parent challenges
- r/raisedbynarcissists (700K) - Family dysfunction
- r/NarcissisticAbuse (200K) - Manipulation patterns
- r/gaslighting (40K) - Psychological manipulation

**Collection Target:** 8,000 posts  
**Quality Threshold:** min_upvotes=12  
**Expected Time:** 1.5 days

**Why These:**
- Complex interpersonal challenges
- Boundary-setting advice
- Manipulation recognition

#### Tier 4: Cultural & Identity (Priority 4)

**Subreddits:**
- r/AsianParentStories (200K) - Cultural family dynamics
- r/BlackMentalHealth (30K) - Cultural mental health
- r/ABCDesis (100K) - South Asian diaspora
- r/mixedrace (40K) - Multiracial identity
- r/lgbt (900K) - LGBTQ+ identity

**Collection Target:** 4,000 posts  
**Quality Threshold:** min_upvotes=10  
**Expected Time:** 1 day

**Why These:**
- Cultural competence data
- Diverse perspectives
- Identity-specific challenges

#### Tier 5: Religion & Meaning (Priority 5)

**Subreddits:**
- r/exchristian (200K) - Faith deconstruction
- r/exmormon (250K) - Religious trauma
- r/spirituality (500K) - Spiritual seeking
- r/philosophy (16M) - Broader philosophy

**Collection Target:** 2,000 posts  
**Quality Threshold:** min_upvotes=15  
**Expected Time:** 0.5 days

**Why These:**
- Existential questions
- Meaning-making challenges
- Compatibility with Stoic philosophy

#### Subreddits to AVOID:

**NEVER Scrape (Ethical/Legal Reasons):**
- r/SuicideWatch - Active crisis intervention
- r/depression - Clinical condition requiring professionals
- r/selfharm - Extremely vulnerable population
- r/EatingDisorders - Medical condition
- r/addiction - Clinical support needed
- r/rape - Trauma survivors
- r/domesticviolence - Safety concerns
- Any subreddit for minors (r/teenagers, etc.)

**Reasoning:** These communities are for immediate support/crisis intervention, not training data. Scraping could:

- Violate Reddit's vulnerable population policies
- Create legal liability
- Ethical breach of trust
- Risk of harm if Marcus gives bad advice in actual crisis

---

### B1.3: Ethical Filtering System (6 hours to build)

#### File: `evaluation/reddit_collector.py`

**Purpose:** Collect only ethically-appropriate data with robust filters

```python
"""
Reddit Data Collector for Marcus AI
====================================

ETHICAL PRINCIPLES:
1. Use official API only (not web scraping)
2. Respect rate limits (60 req/min)
3. Never collect from vulnerable populations
4. Anonymize all identifying information
5. Training use only - never republish
6. Filter out crisis content
7. Quality > quantity

LEGAL COMPLIANCE:
- Reddit API Terms of Service
- GDPR considerations (anonymization)
- Research use classification
"""

import praw
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import re
import logging
from faker import Faker
import time

logger = logging.getLogger(__name__)
fake = Faker()

class EthicalRedditCollector:
    """
    Collects Reddit data with strict ethical filters.
    
    QUALITY OVER QUANTITY:
    - Only posts with community validation (upvotes)
    - Only constructive communities
    - Automatic crisis content filtering
    - Deep anonymization
    """
    
    # Subreddits we will NEVER scrape
    FORBIDDEN_SUBREDDITS = {
        'suicidewatch', 'depression', 'selfharm', 'eatingdisorders',
        'addiction', 'rape', 'domesticviolence', 'teenagers',
        'anxiety',  # Too clinical
    }
    
    # Crisis keywords - auto-reject posts containing these
    CRISIS_KEYWORDS = {
        'kill myself', 'suicide', 'end my life', 'want to die',
        'hurt myself', 'self harm', 'cut myself', 'overdose',
        'jump off', 'hang myself'
    }
    
    def __init__(self, client_id: str, client_secret: str):
        """Initialize with Reddit API credentials."""
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent='Marcus AI Research v1.0 (Educational Use)'
        )
        self.collected_count = 0
        self.filtered_count = 0
        
    def is_ethically_scrapable(
        self,
        subreddit_name: str,
        post_text: str,
        score: int,
        num_comments: int
    ) -> tuple[bool, str]:
        """
        Determine if post meets ethical standards.
        
        Returns:
            (is_ok, reason)
        """
        # Check forbidden subreddits
        if subreddit_name.lower() in self.FORBIDDEN_SUBREDDITS:
            return False, "forbidden_subreddit"
        
        # Check for crisis content
        text_lower = post_text.lower()
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in text_lower:
                return False, "crisis_content"
        
        # Quality filters
        if score < 10:
            return False, "low_quality"
        
        if num_comments < 3:
            return False, "insufficient_engagement"
        
        if len(post_text) < 50:
            return False, "too_short"
        
        # Check for potential PII
        if self._contains_pii(post_text):
            return False, "contains_pii"
        
        return True, "ok"
    
    def _contains_pii(self, text: str) -> bool:
        """
        Detect potential personally identifiable information.
        """
        # Phone numbers
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            return True
        
        # Email addresses
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            return True
        
        # Full addresses (simplified check)
        if re.search(r'\d+\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct)', text, re.IGNORECASE):
            return True
        
        return False
    
    def anonymize_text(self, text: str) -> str:
        """
        Deep anonymization of text.
        
        Replaces:
        - Names → Generic placeholders
        - Locations → Generic placeholders  
        - Companies → "my employer", "my company"
        - Universities → "my school"
        """
        # Remove Reddit usernames
        text = re.sub(r'u/\w+', '[user]', text)
        text = re.sub(r'/r/\w+', '[community]', text)
        
        # Remove potential names (capitalized words that aren't sentence starts)
        # This is imperfect but conservative
        text = re.sub(r'(?<!^)(?<!\. )\b([A-Z][a-z]+)\b', '[name]', text)
        
        # Company mentions
        text = re.sub(r'\b(works? at|employed at|job at)\s+[A-Z]\w+', r'\1 [employer]', text, flags=re.IGNORECASE)
        
        # School mentions
        text = re.sub(r'\b(attend|student at|studying at)\s+[A-Z]\w+', r'\1 [school]', text, flags=re.IGNORECASE)
        
        # Cities/states (simplified)
        text = re.sub(r'\b(live in|from|based in)\s+[A-Z]\w+(,\s*[A-Z]{2})?\b', r'\1 [location]', text, flags=re.IGNORECASE)
        
        return text
    
    def collect_from_subreddit(
        self,
        subreddit_name: str,
        limit: int = 1000,
        min_upvotes: int = 10,
        time_filter: str = 'year'
    ) -> List[Dict]:
        """
        Collect posts from a single subreddit with ethical filtering.
        
        Args:
            subreddit_name: Name of subreddit (without r/)
            limit: Max posts to collect
            min_upvotes: Minimum community validation
            time_filter: 'day', 'week', 'month', 'year', 'all'
        
        Returns:
            List of collected conversation dictionaries
        """
        # Safety check
        if subreddit_name.lower() in self.FORBIDDEN_SUBREDDITS:
            logger.error(f"❌ Attempted to scrape forbidden subreddit: r/{subreddit_name}")
            return []
        
        logger.info(f"📊 Starting collection from r/{subreddit_name}")
        
        subreddit = self.reddit.subreddit(subreddit_name)
        collected = []
        
        try:
            # Get top posts from time period
            for submission in subreddit.top(time_filter=time_filter, limit=limit):
                # Rate limiting (60 req/min = 1 per second)
                time.sleep(1.1)
                
                # Ethical filter
                is_ok, reason = self.is_ethically_scrapable(
                    subreddit_name=subreddit_name,
                    post_text=submission.selftext,
                    score=submission.score,
                    num_comments=submission.num_comments
                )
                
                if not is_ok:
                    self.filtered_count += 1
                    logger.debug(f"Filtered: {reason}")
                    continue
                
                # Get top comments (responses)
                submission.comments.replace_more(limit=0)  # Don't expand "load more"
                
                for comment in submission.comments.list()[:10]:  # Top 10 comments
                    if comment.score < min_upvotes:
                        continue
                    
                    # Check if OP responded (engagement signal)
                    op_responded = any(
                        reply.author == submission.author
                        for reply in comment.replies
                        if reply.author
                    )
                    
                    # Anonymize
                    user_input = self.anonymize_text(submission.selftext)
                    response = self.anonymize_text(comment.body)
                    
                    # Store
                    collected.append({
                        'user_input': user_input,
                        'response': response,
                        'quality_signals': {
                            'post_upvotes': submission.score,
                            'response_upvotes': comment.score,
                            'op_acknowledged': op_responded,
                            'reply_count': len(comment.replies),
                            'post_awards': submission.total_awards_received,
                            'response_awards': comment.total_awards_received
                        },
                        'context': {
                            'subreddit': subreddit_name,
                            'domain': self._classify_domain(subreddit_name),
                            'timestamp': datetime.fromtimestamp(comment.created_utc).isoformat(),
                            'post_length': len(submission.selftext),
                            'response_length': len(comment.body)
                        },
                        'metadata': {
                            'collection_date': datetime.utcnow().isoformat(),
                            'collection_version': 'v1.0'
                        }
                    })
                    
                    self.collected_count += 1
                    
                    if self.collected_count % 100 == 0:
                        logger.info(f"✓ Collected {self.collected_count} conversations")
        
        except Exception as e:
            logger.error(f"❌ Error collecting from r/{subreddit_name}: {e}")
        
        logger.info(f"✅ Collected {len(collected)} from r/{subreddit_name}")
        return collected
    
    def _classify_domain(self, subreddit: str) -> str:
        """Classify subreddit into domain categories."""
        domain_map = {
            'philosophy': ['stoicism', 'philosophy', 'spirituality'],
            'growth': ['decidingtobebetter', 'getdisciplined', 'selfimprovement'],
            'stress': ['stress', 'burnout', 'productivity'],
            'family': ['family', 'parenting', 'raisedbynarcissists'],
            'relationships': ['relationships', 'relationship_advice'],
            'manipulation': ['narcissisticabuse', 'gaslighting'],
            'cultural': ['asianparentstories', 'blackmentalhealth', 'abcdesis', 'mixedrace'],
            'identity': ['lgbt'],
            'religious': ['exchristian', 'exmormon'],
            'work': ['careerguidance', 'jobs', 'toxic_workplaces']
        }
        
        subreddit_lower = subreddit.lower()
        for domain, subs in domain_map.items():
            if subreddit_lower in subs:
                return domain
        
        return 'other'
    
    def collect_full_dataset(
        self,
        subreddit_config: Dict[str, Dict]
    ) -> pd.DataFrame:
        """
        Collect from multiple subreddits based on configuration.
        
        Args:
            subreddit_config: Dict of {subreddit: {limit, min_upvotes, ...}}
        
        Returns:
            DataFrame with all collected conversations
        """
        all_conversations = []
        
        for subreddit_name, config in subreddit_config.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"COLLECTING: r/{subreddit_name}")
            logger.info(f"{'='*60}")
            
            conversations = self.collect_from_subreddit(
                subreddit_name=subreddit_name,
                limit=config.get('limit', 1000),
                min_upvotes=config.get('min_upvotes', 10),
                time_filter=config.get('time_filter', 'year')
            )
            
            all_conversations.extend(conversations)
            
            # Save intermediate results (in case of crash)
            if len(all_conversations) % 1000 == 0:
                temp_df = pd.DataFrame(all_conversations)
                temp_df.to_parquet(f'evaluation/reddit_data_temp_{self.collected_count}.parquet')
        
        # Final statistics
        logger.info(f"\n{'='*60}")
        logger.info(f"COLLECTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total collected: {self.collected_count}")
        logger.info(f"Total filtered: {self.filtered_count}")
        logger.info(f"Pass rate: {self.collected_count / (self.collected_count + self.filtered_count) * 100:.1f}%")
        
        return pd.DataFrame(all_conversations)



# Configuration for full collection
SUBREDDIT_CONFIG = {
    # Tier 1: Philosophy & Growth (Priority 1)
    'stoicism': {'limit': 2500, 'min_upvotes': 15},
    'DecidingToBeBetter': {'limit': 2500, 'min_upvotes': 12},
    'getdisciplined': {'limit': 2500, 'min_upvotes': 15},
    'selfimprovement': {'limit': 2500, 'min_upvotes': 12},
    
    # Tier 2: Stress & Emotional (Priority 2)
    'stress': {'limit': 1500, 'min_upvotes': 10},
    'Burnout': {'limit': 1500, 'min_upvotes': 10},
    'productivity': {'limit': 1500, 'min_upvotes': 12},
    
    # Tier 3: Family & Relationships (Priority 3)
    'family': {'limit': 1200, 'min_upvotes': 12},
    'relationships': {'limit': 1200, 'min_upvotes': 15},
    'relationship_advice': {'limit': 1200, 'min_upvotes': 15},
    'parenting': {'limit': 1200, 'min_upvotes': 12},
    'raisedbynarcissists': {'limit': 1200, 'min_upvotes': 12},
    'NarcissisticAbuse': {'limit': 1000, 'min_upvotes': 10},
    'gaslighting': {'limit': 800, 'min_upvotes': 10},
    
    # Tier 4: Cultural & Identity (Priority 4)
    'AsianParentStories': {'limit': 1000, 'min_upvotes': 10},
    'BlackMentalHealth': {'limit': 800, 'min_upvotes': 8},
    'ABCDesis': {'limit': 800, 'min_upvotes': 10},
    'mixedrace': {'limit': 600, 'min_upvotes': 8},
    'lgbt': {'limit': 1000, 'min_upvotes': 12},
    
    # Tier 5: Religion & Meaning (Priority 5)
    'exchristian': {'limit': 1000, 'min_upvotes': 12},
    'exmormon': {'limit': 1000, 'min_upvotes': 12},
    'spirituality': {'limit': 800, 'min_upvotes': 12},
    'philosophy': {'limit': 1200, 'min_upvotes': 15},
}

```

---

### B1.4: Collection Execution Script (1 hour to build)

#### File: `scripts/collect_reddit_data.py`

```python

"""
Execute full Reddit data collection.

USAGE:
    python scripts/collect_reddit_data.py --test  # Test mode (small sample)
    python scripts/collect_reddit_data.py --full  # Full collection (30K+)
    
REQUIREMENTS:
    - Reddit API credentials in .env
    - ~6 days continuous runtime for full collection
    - 60 req/min rate limit
    
OUTPUT:
    - evaluation/reddit_data_full.parquet (main dataset)
    - evaluation/reddit_statistics.json (collection stats)
"""

import argparse
import logging
import os
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

from evaluation.reddit_collector import EthicalRedditCollector, SUBREDDIT_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation/reddit_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_credentials():
    """Load Reddit API credentials from environment."""
    from dotenv import load_dotenv
    load_dotenv()
    
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError(
            "Missing Reddit API credentials. "
            "Add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env"
        )
    
    return client_id, client_secret

def test_mode():
    """Quick test collection (3 subreddits, 50 posts each)."""
    logger.info("🧪 Running in TEST mode")
    
    test_config = {
        'stoicism': {'limit': 50, 'min_upvotes': 10},
        'DecidingToBeBetter': {'limit': 50, 'min_upvotes': 10},
        'relationships': {'limit': 50, 'min_upvotes': 10},
    }
    
    client_id, client_secret = load_credentials()
    collector = EthicalRedditCollector(client_id, client_secret)
    
    df = collector.collect_full_dataset(test_config)
    
    # Save
    output_file = Path('evaluation/reddit_data_test.parquet')
    df.to_parquet(output_file)
    
    logger.info(f"✅ Test complete: {len(df)} conversations collected")
    logger.info(f"📁 Saved to: {output_file}")
    
    # Statistics
    print("\n" + "="*60)
    print("TEST COLLECTION STATISTICS")
    print("="*60)
    print(f"Total conversations: {len(df)}")
    print(f"\nBy domain:")
    print(df['context'].apply(lambda x: x['domain']).value_counts())
    print(f"\nAverage upvotes:")
    print(f"  Posts: {df['quality_signals'].apply(lambda x: x['post_upvotes']).mean():.1f}")
    print(f"  Responses: {df['quality_signals'].apply(lambda x: x['response_upvotes']).mean():.1f}")

def full_mode():
    """Full production collection (40 subreddits, ~30K conversations)."""
    logger.info("🚀 Running in FULL mode")
    logger.info("⏱️  Estimated time: 6 days continuous")
    logger.info("📊 Expected output: 30,000+ conversations")
    
    response = input("\nThis will run for ~6 days. Continue? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Aborted by user")
        return
    
    client_id, client_secret = load_credentials()
    collector = EthicalRedditCollector(client_id, client_secret)
    
    start_time = datetime.utcnow()
    
    # Collect
    df = collector.collect_full_dataset(SUBREDDIT_CONFIG)
    
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds() / 3600  # hours
    
    # Save main dataset
    output_file = Path('evaluation/reddit_data_full.parquet')
    df.to_parquet(output_file)
    
    # Save statistics
    stats = {
        'collection_date': end_time.isoformat(),
        'duration_hours': duration,
        'total_conversations': len(df),
        'by_domain': df['context'].apply(lambda x: x['domain']).value_counts().to_dict(),
        'by_subreddit': df['context'].apply(lambda x: x['subreddit']).value_counts().to_dict(),
        'quality_metrics': {
            'avg_post_upvotes': float(df['quality_signals'].apply(lambda x: x['post_upvotes']).mean()),
            'avg_response_upvotes': float(df['quality_signals'].apply(lambda x: x['response_upvotes']).mean()),
            'avg_response_length': float(df['context'].apply(lambda x: x['response_length']).mean()),
        },
        'filtered_count': collector.filtered_count,
        'pass_rate': collector.collected_count / (collector.collected_count + collector.filtered_count)
    }
    
    stats_file = Path('evaluation/reddit_statistics.json')
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"\n{'='*60}")
    logger.info("FULL COLLECTION COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"📁 Data: {output_file}")
    logger.info(f"📊 Stats: {stats_file}")
    logger.info(f"🎯 Total: {len(df)} conversations")
    logger.info(f"⏱️  Duration: {duration:.1f} hours")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collect Reddit data for Marcus AI')
    parser.add_argument('--test', action='store_true', help='Test mode (quick sample)')
    parser.add_argument('--full', action='store_true', help='Full collection (6 days)')
    
    args = parser.parse_args()
    
    if args.test:
        test_mode()
    elif args.full:
        full_mode()
    else:
        print("Usage: python scripts/collect_reddit_data.py --test|--full")

```

---

### B1.5: Data Validation & Quality Checks (2 hours)

#### File: `scripts/validate_reddit_data.py`

```python

"""
Validate collected Reddit data quality.

Checks:
- No PII leakage
- No crisis content
- Quality distribution
- Domain coverage
- Anonymization effectiveness
"""

import pandas as pd
import re
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class DataQualityValidator:
    """Validate Reddit dataset meets quality standards."""
    
    # PII patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    
    # Crisis keywords (should not be present)
    CRISIS_KEYWORDS = {'suicide', 'kill myself', 'end my life', 'hurt myself'}
    
    def validate(self, df: pd.DataFrame) -> Dict:
        """
        Run all validation checks.
        
        Returns:
            Dict with validation results and issues found
        """
        results = {
            'total_conversations': len(df),
            'checks': {}
        }
        
        # Check 1: No PII
        results['checks']['pii_check'] = self._check_pii(df)
        
        # Check 2: No crisis content
        results['checks']['crisis_check'] = self._check_crisis(df)
        
        # Check 3: Quality distribution
        results['checks']['quality_check'] = self._check_quality(df)
        
        # Check 4: Domain coverage
        results['checks']['domain_coverage'] = self._check_domains(df)
        
        # Check 5: Response length distribution
        results['checks']['length_check'] = self._check_lengths(df)
        
        # Overall pass/fail
        results['validation_passed'] = all(
            check['passed'] for check in results['checks'].values()
        )
        
        return results
    
    def _check_pii(self, df: pd.DataFrame) -> Dict:
        """Check for PII leakage."""
        email_count = 0
        phone_count = 0
        
        for text in list(df['user_input']) + list(df['response']):
            if re.search(self.EMAIL_PATTERN, text):
                email_count += 1
            if re.search(self.PHONE_PATTERN, text):
                phone_count += 1
        
        passed = (email_count == 0 and phone_count == 0)
        
        return {
            'passed': passed,
            'email_leaks': email_count,
            'phone_leaks': phone_count,
            'message': 'No PII found' if passed else f'Found {email_count} emails, {phone_count} phones'
        }
    
    def _check_crisis(self, df: pd.DataFrame) -> Dict:
        """Check for crisis content."""
        crisis_count = 0
        
        for text in list(df['user_input']) + list(df['response']):
            text_lower = text.lower()
            for keyword in self.CRISIS_KEYWORDS:
                if keyword in text_lower:
                    crisis_count += 1
                    break
        
        passed = (crisis_count == 0)
        
        return {
            'passed': passed,
            'crisis_content_found': crisis_count,
            'message': 'No crisis content' if passed else f'Found {crisis_count} crisis posts'
        }
    
    def _check_quality(self, df: pd.DataFrame) -> Dict:
        """Check quality signal distribution."""
        post_upvotes = df['quality_signals'].apply(lambda x: x['post_upvotes'])
        response_upvotes = df['quality_signals'].apply(lambda x: x['response_upvotes'])
        
        # Should have high average upvotes
        avg_post = post_upvotes.mean()
        avg_response = response_upvotes.mean()
        
        passed = (avg_post >= 15 and avg_response >= 10)
        
        return {
            'passed': passed,
            'avg_post_upvotes': float(avg_post),
            'avg_response_upvotes': float(avg_response),
            'message': 'Quality metrics good' if passed else 'Low quality signals'
        }
    
    def _check_domains(self, df: pd.DataFrame) -> Dict:
        """Check domain coverage."""
        domains = df['context'].apply(lambda x: x['domain']).value_counts().to_dict()
        
        # Should have at least 5 domains represented
        num_domains = len(domains)
        passed = (num_domains >= 5)
        
        return {
            'passed': passed,
            'num_domains': num_domains,
            'distribution': domains,
            'message': f'{num_domains} domains covered'
        }
    
    def _check_lengths(self, df: pd.DataFrame) -> Dict:
        """Check response length distribution."""
        lengths = df['context'].apply(lambda x: x['response_length'])
        
        avg_length = lengths.mean()
        min_length = lengths.min()
        max_length = lengths.max()
        
        # Should have reasonable average (75-200 words is good)
        passed = (50 <= avg_length <= 500)
        
        return {
            'passed': passed,
            'avg_length': float(avg_length),
            'min_length': int(min_length),
            'max_length': int(max_length),
            'message': 'Length distribution reasonable' if passed else 'Unusual length distribution'
        }

if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_reddit_data.py <data_file.parquet>")
        sys.exit(1)
    
    data_file = sys.argv[1]
    df = pd.read_parquet(data_file)
    
    validator = DataQualityValidator()
    results = validator.validate(df)
    
    # Print results
    print("\n" + "="*60)
    print("DATA VALIDATION RESULTS")
    print("="*60)
    print(json.dumps(results, indent=2))
    
    if results['validation_passed']:
        print("\n✅ ALL CHECKS PASSED - Data ready for use")
    else:
        print("\n❌ VALIDATION FAILED - Review issues before proceeding")

```

**At end of Phase B1, you will have:**

1. ✅ `evaluation/reddit_data_full.parquet` - 30,000+ conversations
2. ✅ `evaluation/reddit_statistics.json` - Collection metrics
3. ✅ `evaluation/reddit_collection.log` - Detailed collection log
4. ✅ Validation report showing:
   - ✓ No PII leakage
   - ✓ No crisis content
   - ✓ High quality signals (upvotes)
   - ✓ 8+ domains covered
   - ✓ Reasonable response lengths

**Timeline:** 6 days continuous collection + 1 day validation = 7 days

**Next:** Phase B2 - Multi-LLM Comparison System

---

## Phase B2: Multi-LLM Comparison System

**Duration:** Week 2 (5 days)  
**Deliverable:** 500 scenarios × 6 model responses = 3,000 responses with mental model tags

### B2.1: API Integration (1 day)

#### Models to Compare:

1. **GPT-4o** (OpenAI) - Latest reasoning model
2. **GPT-4o-mini** (OpenAI) - Cost-effective alternative
3. **Claude 3.5 Sonnet** (Anthropic) - Ethical, balanced
4. **Gemini 1.5 Pro** (Google) - Factual, structured
5. **Llama-3-70B** (Meta via Groq) - Open source, fast
6. **Marcus** (Current system) - Introspection-based

#### File: `evaluation/multi_llm_comparator.py`

```python

"""
Multi-LLM Comparison System
===========================

PURPOSE: Generate responses from all major LLMs to learn best practices.

NOT to "beat" ChatGPT, but to LEARN from all models:
- What mental models does each use?
- Which approaches work in which contexts?
- How can we combine strengths?

API COSTS (for 500 scenarios):
- GPT-4o: 500 × $0.03 = $15
- GPT-4o-mini: 500 × $0.001 = $0.50
- Claude 3.5: 500 × $0.015 = $7.50  
- Gemini 1.5: 500 × $0.001 = $0.50
- Llama-3 (Groq): FREE
- TOTAL: ~$24
"""

import asyncio
from openai import AsyncOpenAI
import anthropic
import google.generativeai as genai
from groq import Groq
import httpx
from typing import Dict, List
import logging
import time

logger = logging.getLogger(__name__)

class MultiLLMComparator:
    """Compare responses from all major LLMs."""
    
    # Stoic prompt used for all models (except Marcus who has internal)
    STOIC_PROMPT = """You are Marcus Aurelius, the Roman Emperor and Stoic philosopher. 
Respond with wisdom, brevity, and practical guidance. 
Focus on what is within the user's control.
Use Stoic principles: acceptance, virtue, reason, nature.
Be compassionate but honest. Teach through questions when appropriate."""
    
    def __init__(self, api_keys: Dict[str, str]):
        """Initialize all LLM clients."""
        self.openai_client = AsyncOpenAI(api_key=api_keys['openai'])
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=api_keys['anthropic'])
        genai.configure(api_key=api_keys['google'])
        self.groq_client = Groq(api_key=api_keys['groq'])
        self.marcus_api_base = api_keys.get('marcus_url', 'http://localhost:8000')
    
    async def generate_gpt4o(self, user_input: str) -> Dict:
        """Generate from GPT-4o with Stoic prompt."""
        try:
            start = time.perf_counter()
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.STOIC_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            latency_ms = (time.perf_counter() - start) * 1000
            
            return {
                'model': 'gpt-4o',
                'response': response.choices[0].message.content,
                'latency_ms': latency_ms,
                'tokens': response.usage.total_tokens,
                'cost': response.usage.total_tokens * 0.00003  # Rough estimate
            }
        
        except Exception as e:
            logger.error(f"GPT-4o error: {e}")
            return {'model': 'gpt-4o', 'response': None, 'error': str(e)}
    
    async def generate_gpt4o_mini(self, user_input: str) -> Dict:
        """Generate from GPT-4o-mini (cost-effective)."""
        try:
            start = time.perf_counter()
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.STOIC_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            latency_ms = (time.perf_counter() - start) * 1000
            
            return {
                'model': 'gpt-4o-mini',
                'response': response.choices[0].message.content,
                'latency_ms': latency_ms,
                'tokens': response.usage.total_tokens,
                'cost': response.usage.total_tokens * 0.000001
            }
        
        except Exception as e:
            logger.error(f"GPT-4o-mini error: {e}")
            return {'model': 'gpt-4o-mini', 'response': None, 'error': str(e)}
    
    async def generate_claude(self, user_input: str) -> Dict:
        """Generate from Claude 3.5 Sonnet."""
        try:
            start = time.perf_counter()
            
            message = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                system=self.STOIC_PROMPT,
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            
            latency_ms = (time.perf_counter() - start) * 1000
            
            return {
                'model': 'claude-3.5-sonnet',
                'response': message.content[0].text,
                'latency_ms': latency_ms,
                'tokens': message.usage.input_tokens + message.usage.output_tokens,
                'cost': (message.usage.input_tokens * 0.000003 + 
                        message.usage.output_tokens * 0.000015)
            }
        
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return {'model': 'claude-3.5-sonnet', 'response': None, 'error': str(e)}
    
    async def generate_gemini(self, user_input: str) -> Dict:
        """Generate from Gemini 1.5 Pro."""
        try:
            start = time.perf_counter()
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = await model.generate_content_async(
                f"{self.STOIC_PROMPT}

User: {user_input}"
            )
            
            latency_ms = (time.perf_counter() - start) * 1000
            
            return {
                'model': 'gemini-1.5-pro',
                'response': response.text,
                'latency_ms': latency_ms,
                'tokens': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                'cost': 0.001  # Rough estimate
            }
        
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {'model': 'gemini-1.5-pro', 'response': None, 'error': str(e)}
    
    async def generate_llama(self, user_input: str) -> Dict:
        """Generate from Llama-3-70B via Groq (free, fast)."""
        try:
            start = time.perf_counter()
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": self.STOIC_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            latency_ms = (time.perf_counter() - start) * 1000
            
            return {
                'model': 'llama-3-70b',
                'response': response.choices[0].message.content,
                'latency_ms': latency_ms,
                'tokens': response.usage.total_tokens,
                'cost': 0  # Free via Groq
            }
        
        except Exception as e:
            logger.error(f"Llama error: {e}")
            return {'model': 'llama-3-70b', 'response': None, 'error': str(e)}
    
    async def generate_marcus(self, user_input: str) -> Dict:
        """Generate from current Marcus system."""
        try:
            start = time.perf_counter()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.marcus_api_base}/api/v1/chat",
                    json={"content": user_input},
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
            
            latency_ms = (time.perf_counter() - start) * 1000
            
            return {
                'model': 'marcus-introspection',
                'response': data['response'],
                'latency_ms': latency_ms,
                'introspection': {
                    'patterns': data.get('detected_patterns', []),
                    'strategy': data.get('strategy_used'),
                    'effectiveness': data.get('effectiveness_score')
                },
                'cost': 0  # Our system
            }
        
        except Exception as e:
            logger.error(f"Marcus error: {e}")
            return {'model': 'marcus-introspection', 'response': None, 'error': str(e)}
    
    async def generate_all(self, user_input: str, scenario_id: str) -> Dict:
        """
        Generate responses from all models in parallel.
        
        Returns:
            Dict with all responses and metadata
        """
        logger.info(f"Generating responses for scenario: {scenario_id}")
        
        # Generate all in parallel
        results = await asyncio.gather(
            self.generate_gpt4o(user_input),
            self.generate_gpt4o_mini(user_input),
            self.generate_claude(user_input),
            self.generate_gemini(user_input),
            self.generate_llama(user_input),
            self.generate_marcus(user_input),
            return_exceptions=True
        )
        
        # Package results
        comparison = {
            'scenario_id': scenario_id,
            'user_input': user_input,
            'timestamp': time.time(),
            'models': {}
        }
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Model error: {result}")
                continue
            
            model_name = result['model']
            comparison['models'][model_name] = result
        
        # Calculate statistics
        successful_models = [r for r in results if not isinstance(r, Exception) and r.get('response')]
        
        if successful_models:
            comparison['statistics'] = {
                'successful_models': len(successful_models),
                'avg_latency_ms': sum(r['latency_ms'] for r in successful_models) / len(successful_models),
                'total_cost': sum(r.get('cost', 0) for r in successful_models)
            }
        
        return comparison
    
    def identify_mental_models(self, responses: Dict[str, Dict]) -> Dict[str, List[str]]:
        """
        Identify which mental models each LLM uses.
        
        Mental Models:
        - socratic: Asking questions to lead to insight
        - reflective: Mirroring emotions and validating
        - reframing: Changing perspective on situation
        - stoic: Focus on control, acceptance, virtue
        - solution_focused: Concrete actionable steps
        - motivational: Inspiring and energizing
        - teaching: Explaining concepts/frameworks
        """
        patterns = {
            'socratic': [
                'have you considered', 'what if', 'why do you think',
                'ask yourself', 'consider this', 'reflect on'
            ],
            'reflective': [
                'it sounds like', 'you feel', 'you seem', 'i hear',
                'that must be', 'i understand'
            ],
            'reframing': [
                'another way to look', 'perspective', 'could be seen as',
                'instead of', 'rather than', 'opportunity to'
            ],
            'stoic': [
                'control', 'power', 'fate', 'virtue', 'external',
                'within you', 'nature', 'reason', 'accept', 'endure'
            ],
            'solution_focused': [
                'try', 'could', 'step', 'action', 'plan', 'start by',
                'begin with', 'next time', 'practice'
            ],
            'motivational': [
                'you can', 'within you', 'strength', 'capable', 'overcome',
                'believe', 'potential', 'rise'
            ],
            'teaching': [
                'principle', 'framework', 'concept', 'theory', 'understanding',
                'realize', 'recognize', 'aware'
            ]
        }
        
        model_patterns = {}
        
        for model_name, response_data in responses.items():
            response = response_data.get('response', '')
            if not response:
                continue
            
            response_lower = response.lower()
            found_patterns = []
            
            for pattern_name, keywords in patterns.items():
                if any(kw in response_lower for kw in keywords):
                    found_patterns.append(pattern_name)
            
            model_patterns[model_name] = found_patterns
        
        return model_patterns

```
```

#### What To Do:

1. ✅ Set up API keys for all 5 external models
2. ✅ Test each model individually first
3. ✅ Run comparison on 10 test scenarios
4. ✅ Verify costs are within budget ($24)
5. ✅ Monitor rate limits (all have different limits)

#### What NOT To Do:

❌ **DO NOT** run full 500 scenarios before testing on 10  
❌ **DO NOT** use production API keys (use separate test keys)  
❌ **DO NOT** parallelize too aggressively (respect rate limits)  
❌ **DO NOT** skip error handling (models can fail)  
❌ **DO NOT** forget to track costs (they add up fast)

---

### B2.2: Scenario Selection for Comparison (4 hours)

**Goal:** Select 500 diverse scenarios from:

- 80 existing test scenarios
- 200 high-quality Reddit samples
- 220 edge cases (crisis, culture, manipulation, etc.)

#### File: `scripts/select_comparison_scenarios.py`

```python

"""
Select 500 representative scenarios for multi-LLM comparison.

SELECTION CRITERIA:
- Coverage of all domains (philosophy, stress, family, etc.)
- Range of emotional contexts (crisis, achievement, confusion)
- Diverse user demographics (cultural, religious, identity)
- Mix of simple and complex challenges
- Edge cases (manipulation, trauma, boundaries)

OUTPUT:
- evaluation/comparison_scenarios.json (500 scenarios)
"""

import pandas as pd
import json
import random
from typing import List, Dict
from pathlib import Path

def load_test_scenarios() -> List[Dict]:
    """Load existing 80 test scenarios."""
    scenarios = []
    
    for file in ['effectiveness.json', 'strategies.json', 'patterns.json']:
        path = Path(f'scripts/scenarios/{file}')
        with open(path) as f:
            data = json.load(f)
            scenarios.extend(data['scenarios'])
    
    return scenarios

def sample_reddit_data(df: pd.DataFrame, n: int = 200) -> List[Dict]:
    """
    Sample high-quality Reddit scenarios.
    
    Strategy:
    - Stratified sampling across domains
    - High upvote posts only (>50 upvotes)
    - Diverse subreddits
    - Range of post lengths
    """
    # Filter high quality
    high_quality = df[
        df['quality_signals'].apply(lambda x: x['post_upvotes'] > 50)
    ]
    
    # Stratified sample by domain
    domains = high_quality['context'].apply(lambda x: x['domain']).unique()
    samples_per_domain = n // len(domains)
    
    sampled = []
    for domain in domains:
        domain_df = high_quality[
            high_quality['context'].apply(lambda x: x['domain'] == domain)
        ]
        
        if len(domain_df) > samples_per_domain:
            sample = domain_df.sample(n=samples_per_domain, random_state=42)
        else:
            sample = domain_df
        
        sampled.append(sample)
    
    final_sample = pd.concat(sampled)
    
    # Convert to scenario format
    scenarios = []
    for _, row in final_sample.iterrows():
        scenarios.append({
            'id': f"reddit_{len(scenarios):03d}",
            'user_input': row['user_input'],
            'domain': row['context']['domain'],
            'subreddit': row['context']['subreddit'],
            'quality_upvotes': row['quality_signals']['post_upvotes']
        })
    
    return scenarios

def create_edge_cases() -> List[Dict]:
    """
    Manually create edge case scenarios.
    
    Edge cases:
    - Cultural sensitivity (religious trauma, cultural clashes)
    - Manipulation detection (gaslighting, narcissistic abuse)
    - Crisis situations (but not active harm - just high stress)
    - Identity challenges (LGBTQ+, racial, cultural)
    - Moral dilemmas (conflicting values)
    - Boundary setting (toxic relationships)
    """
    edge_cases = [
        # Cultural/Religious (40 scenarios)
        {
            'id': 'edge_religious_001',
            'user_input': "I left my religion and my family disowned me. I feel lost without the community and purpose it gave me.",
            'domain': 'religious',
            'edge_type': 'faith_deconstruction'
        },
        {
            'id': 'edge_cultural_001',
            'user_input': "My parents expect me to follow traditional gender roles but I want to pursue my career. How do I balance honoring them with my own goals?",
            'domain': 'cultural',
            'edge_type': 'cultural_expectations'
        },
        
        # Manipulation (40 scenarios)
        {
            'id': 'edge_manipulation_001',
            'user_input': "My partner says I'm too sensitive when I bring up concerns. Am I overreacting or is this gaslighting?",
            'domain': 'manipulation',
            'edge_type': 'gaslighting'
        },
        {
            'id': 'edge_boundaries_001',
            'user_input': "My mother guilt-trips me every time I set a boundary. She says I'm selfish for not putting family first.",
            'domain': 'family',
            'edge_type': 'boundary_violation'
        },
        
        # Identity (40 scenarios)
        {
            'id': 'edge_identity_001',
            'user_input': "I'm questioning my gender identity but I'm afraid of losing my family and friends if I transition.",
            'domain': 'identity',
            'edge_type': 'gender_identity'
        },
        {
            'id': 'edge_racial_001',
            'user_input': "I'm the only person of my race at my company and I face microaggressions daily. How do I cope without constantly fighting?",
            'domain': 'cultural',
            'edge_type': 'racial_discrimination'
        },
        
        # High Stress (40 scenarios)
        {
            'id': 'edge_stress_001',
            'user_input': "I'm drowning in work, my relationship is falling apart, and I haven't slept properly in weeks. Everything feels impossible.",
            'domain': 'stress',
            'edge_type': 'overwhelm'
        },
        {
            'id': 'edge_grief_001',
            'user_input': "My parent just died and everyone expects me to be strong. I don't know how to process this while keeping everything together.",
            'domain': 'grief',
            'edge_type': 'acute_grief'
        },
        
        # Moral Dilemmas (40 scenarios)
        {
            'id': 'edge_ethics_001',
            'user_input': "I discovered my company is doing something unethical. If I report it, I'll lose my job and career. What's the Stoic approach?",
            'domain': 'ethics',
            'edge_type': 'whistleblower_dilemma'
        },
        {
            'id': 'edge_values_001',
            'user_input': "My best friend cheated on their spouse. Do I stay silent or tell the truth and destroy their marriage?",
            'domain': 'relationships',
            'edge_type': 'loyalty_vs_honesty'
        },
        
        # Trauma Recovery (20 scenarios)
        {
            'id': 'edge_trauma_001',
            'user_input': "I have PTSD from childhood abuse. How do I practice Stoicism when my body has physical reactions I can't control?",
            'domain': 'trauma',
            'edge_type': 'ptsd_management'
        },
    ]
    
    # In real implementation, expand to 220 total edge cases
    # This is a template showing the structure
    
    return edge_cases[:20]  # Placeholder

def combine_and_validate(
    test_scenarios: List[Dict],
    reddit_scenarios: List[Dict],
    edge_cases: List[Dict]
) -> List[Dict]:
    """
    Combine all scenarios and validate coverage.
    
    Target distribution:
    - Test scenarios: 80 (16%)
    - Reddit samples: 200 (40%)
    - Edge cases: 220 (44%)
    - TOTAL: 500
    """
    all_scenarios = test_scenarios + reddit_scenarios + edge_cases
    
    # Shuffle to mix sources
    random.seed(42)
    random.shuffle(all_scenarios)
    
    # Validate coverage
    domains = {}
    for scenario in all_scenarios:
        domain = scenario.get('domain', 'unknown')
        domains[domain] = domains.get(domain, 0) + 1
    
    print(f"
Scenario Distribution:")
    print(f"Total: {len(all_scenarios)}")
    print(f"
By domain:")
    for domain, count in sorted(domains.items()):
        print(f"  {domain}: {count} ({count/len(all_scenarios)*100:.1f}%)")
    
    return all_scenarios

if __name__ == '__main__':
    # Load sources
    test_scenarios = load_test_scenarios()
    print(f"Loaded {len(test_scenarios)} test scenarios")
    
    reddit_df = pd.read_parquet('evaluation/reddit_data_full.parquet')
    reddit_scenarios = sample_reddit_data(reddit_df, n=200)
    print(f"Sampled {len(reddit_scenarios)} Reddit scenarios")
    
    edge_cases = create_edge_cases()
    print(f"Created {len(edge_cases)} edge case scenarios")
    
    # Combine
    final_scenarios = combine_and_validate(test_scenarios, reddit_scenarios, edge_cases)
    
    # Save
    output = {
        'version': '1.0',
        'total_scenarios': len(final_scenarios),
        'created_at': pd.Timestamp.utcnow().isoformat(),
        'scenarios': final_scenarios
    }
    
    output_path = Path('evaluation/comparison_scenarios.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"
✅ Saved {len(final_scenarios)} scenarios to {output_path}")

```
```

---

### B2.3: Run Multi-LLM Comparison (4 days)

#### File: `scripts/run_multi_llm_comparison.py`

```python

"""
Execute multi-LLM comparison for all 500 scenarios.

RUNTIME:
- 500 scenarios × 6 models = 3,000 API calls
- Average latency: ~3 seconds per scenario (parallel)
- Total time: 500 × 3 = 1,500 seconds = 25 minutes
- With retries and rate limits: ~1 hour

COST:
- GPT-4o: $15
- GPT-4o-mini: $0.50
- Claude: $7.50
- Gemini: $0.50
- Llama: $0 (free)
- TOTAL: ~$24

OUTPUT:
- evaluation/multi_llm_responses.json (3,000 responses)
- evaluation/mental_models.json (mental model tags per response)
- evaluation/comparison_statistics.json (latency, costs, etc.)
"""

import asyncio
import json
import logging
from pathlib import Path
from tqdm.asyncio import tqdm
import pandas as pd

from evaluation.multi_llm_comparator import MultiLLMComparator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_comparison():
    """Execute full multi-LLM comparison."""
    
    # Load API keys
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_keys = {
        'openai': os.getenv('OPENAI_API_KEY'),
        'anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'google': os.getenv('GOOGLE_API_KEY'),
        'groq': os.getenv('GROQ_API_KEY'),
        'marcus_url': os.getenv('MARCUS_API_URL', 'http://localhost:8000')
    }
    
    # Load scenarios
    scenarios_path = Path('evaluation/comparison_scenarios.json')
    with open(scenarios_path) as f:
        data = json.load(f)
        scenarios = data['scenarios']
    
    logger.info(f"Loaded {len(scenarios)} scenarios")
    
    # Initialize comparator
    comparator = MultiLLMComparator(api_keys)
    
    # Generate responses
    all_comparisons = []
    all_mental_models = []
    
    logger.info("Starting multi-LLM comparison...")
    
    for scenario in tqdm(scenarios, desc="Processing scenarios"):
        comparison = await comparator.generate_all(
            user_input=scenario['user_input'],
            scenario_id=scenario['id']
        )
        
        # Identify mental models
        mental_models = comparator.identify_mental_models(comparison['models'])
        
        # Store
        all_comparisons.append(comparison)
        all_mental_models.append({
            'scenario_id': scenario['id'],
            'mental_models': mental_models
        })
        
        # Rate limiting (to be safe)
        await asyncio.sleep(0.5)
    
    # Save results
    responses_path = Path('evaluation/multi_llm_responses.json')
    with open(responses_path, 'w') as f:
        json.dump(all_comparisons, f, indent=2)
    
    models_path = Path('evaluation/mental_models.json')
    with open(models_path, 'w') as f:
        json.dump(all_mental_models, f, indent=2)
    
    # Calculate statistics
    total_cost = sum(c['statistics']['total_cost'] for c in all_comparisons if 'statistics' in c)
    avg_latency = sum(c['statistics']['avg_latency_ms'] for c in all_comparisons if 'statistics' in c) / len(all_comparisons)
    
    stats = {
        'total_scenarios': len(scenarios),
        'total_responses': len(all_comparisons) * 6,
        'total_cost_usd': total_cost,
        'avg_latency_ms': avg_latency,
        'models_compared': ['gpt-4o', 'gpt-4o-mini', 'claude-3.5-sonnet', 'gemini-1.5-pro', 'llama-3-70b', 'marcus-introspection']
    }
    
    stats_path = Path('evaluation/comparison_statistics.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"
{'='*60}")
    logger.info("COMPARISON COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total cost: ${total_cost:.2f}")
    logger.info(f"Avg latency: {avg_latency:.1f}ms")
    logger.info(f"Responses saved: {responses_path}")

if __name__ == '__main__':
    asyncio.run(run_comparison())

```
```

#### What To Do:

1. ✅ Test on 10 scenarios first
2. ✅ Verify all models respond correctly
3. ✅ Check costs match estimates ($24)
4. ✅ Run full 500 scenarios (~1 hour)
5. ✅ Validate output files created

#### What NOT To Do:

❌ **DO NOT** run without testing first  
❌ **DO NOT** forget to monitor API costs in real-time  
❌ **DO NOT** skip rate limiting (can get banned)  
❌ **DO NOT** lose results (save incrementally)

---

## Phase B2 Deliverables

**At end of Phase B2, you will have:**

1. ✅ `evaluation/comparison_scenarios.json` - 500 selected scenarios
2. ✅ `evaluation/multi_llm_responses.json` - 3,000 model responses
3. ✅ `evaluation/mental_models.json` - Mental model tags per response
4. ✅ `evaluation/comparison_statistics.json` - Cost and latency data

**Timeline:** 5 days (1 day setup + 4 days execution)

**Cost:** ~$24 API costs

**Next:** Phase B3 - Data Analysis & Pattern Extraction

---

## Phase B3: Data Analysis & Pattern Extraction

**Duration:** Weeks 3-4 (10 days)  
**Deliverable:** Empirical strategy rules, mental models, quality metrics

### B3.1: Human Rating Interface (2 days)

- Use `rating_interface.html` to collect human preferences
- Recruit 5-10 raters (trusted peers) for 3,000 responses
- Rating dimensions:
  - Empathy
  - Helpfulness
  - Clarity
  - Actionability
  - Overall (1-5 stars)
- Collect qualitative notes per response

### B3.2: Pattern Extraction (4 days)

**Outputs:**

- Mental model effectiveness matrix
- Strategy success rates by scenario type
- Cultural/identity sensitivity analysis
- Crisis response effectiveness
- Emotion trajectory vs. strategy effectiveness

### B3.3: Quality Predictor Training (4 days)

**Goal:** Train ML model to predict response quality

- Inputs: Strategy, mental model, emotional deltas, patterns detected
- Output: Predicted quality score (0-1)
- Success: R² > 0.7 on validation set

---

## Phase B4: AI Reconstruction

**Duration:** Weeks 5-7 (15 days)  
**Deliverable:** Evidence-based Marcus dialogue system

### Components

1. Evidence-based dialogue generator
2. Empirical strategy selection engine
3. Real-time quality predictor
4. Continuous learning loop

---

## Phase B5: Validation & Deployment

**Duration:** Weeks 8-10 (15 days)  
**Deliverable:** Production-ready Marcus AI beating top LLMs

### Validation Steps

- Blind preference tests vs GPT-4, Claude, Gemini
- Statistical significance (p < 0.05)
- A/B testing with real users
- Production monitoring dashboard

---

## What To Do / What NOT To Do

| ✅ Do | ❌ Do NOT |
|-------|----------|
| Test each phase before scaling | Skip testing to move faster |
| Document every dataset and script | Rely on memory |
| Monitor API costs in real time | Assume costs will stay low |
| Follow ethical rules strictly | Scrape sensitive communities |
| Save intermediate results | Run everything in one shot |

---

## Success Metrics

- Data coverage: 30K+ conversations across 8 domains
- Multi-LLM comparison: 500 scenarios × 6 models
- Human ratings: 3,000 responses × 5 dimensions
- Strategy accuracy: 70%+ match to top human-rated responses
- Quality predictor: R² > 0.7
- Marcus vs top LLMs: 70%+ win rate

---

## Timeline & Resources

| Phase | Duration | Key Output |
|-------|----------|------------|
| B1 | Week 1 | Reddit dataset |
| B2 | Week 2 | Multi-LLM responses |
| B3 | Weeks 3-4 | Empirical strategy rules |
| B4 | Weeks 5-7 | Rebuilt Marcus AI |
| B5 | Weeks 8-10 | Validated system |

**People Needed:** 1 engineer + 1 analyst (part-time)  
**Budget:** $24 (API) + $0 (Reddit) + human raters (volunteer)  
**Dependencies:** Reddit API keys, LLM API access, 5-10 raters

---

## Final Notes

- This path creates an undeniable quality advantage before visuals
- Evidence beats theory; data beats intuition
- Once Marcus wins conversations, adding visuals becomes much easier
- All work is reusable for future models and visual layers

**Path B = Build the smartest Marcus first. Visuals come after excellence.**

---