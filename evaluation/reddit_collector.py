"""
Reddit Data Collector for Marcus AI - Ethical & High-Quality
=============================================================

PHILOSOPHY: Quality over quantity, ethics over data volume

APPROACH:
- Collect ONLY top 1% quality (high upvotes)
- 10 strategic subreddits (not 40)
- 1,000 samples total (not 30K)
- Deep ethical filtering
- Complete anonymization

TIMELINE:
- Test mode: 30 minutes (10 posts)
- Validation mode: 1 hour (100 posts)
- Production mode: 4 hours (1,000 posts)

COST: $0 (Reddit API is free for research)
"""

import praw
import pandas as pd
from typing import List, Dict, Optional, Set
from datetime import datetime
import re
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class EthicalRedditCollector:
    """
    Ethical Reddit data collector with strict quality and safety filters.
    
    PRINCIPLES:
    1. Use official API only (not web scraping)
    2. Respect rate limits (60 req/min)
    3. Never collect from vulnerable populations
    4. Anonymize all PII
    5. Filter out crisis content
    6. Training use only - never republish
    """
    
    # Subreddits we will NEVER scrape (ethical boundaries)
    FORBIDDEN_SUBREDDITS: Set[str] = {
        'suicidewatch', 'depression', 'selfharm', 'eatingdisorders',
        'addiction', 'rape', 'domesticviolence', 'teenagers',
        'anxiety',  # Too clinical for training data
    }
    
    # Crisis keywords - auto-reject any post containing these
    CRISIS_KEYWORDS: Set[str] = {
        'kill myself', 'suicide', 'end my life', 'want to die',
        'hurt myself', 'self harm', 'cut myself', 'overdose',
        'jump off', 'hang myself', 'end it all'
    }
    
    # Recommended subreddits by domain (Path B-Minimal: 10 total)
    RECOMMENDED_SUBREDDITS = {
        'philosophy': ['stoicism', 'philosophy'],
        'growth': ['DecidingToBeBetter', 'getdisciplined'],
        'emotional': ['stress'],
        'interpersonal': ['relationships', 'raisedbynarcissists'],
        'existential': ['exchristian'],
        'cultural': ['AsianParentStories'],
        'balance': ['mentalhealth'],  # Handle carefully
    }
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Reddit API client.
        
        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app secret
        """
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent='Marcus AI Research v1.0 (Educational Use)'
        )
        
        self.collected_count = 0
        self.filtered_count = 0
        self.filter_reasons = {}
        
        logger.info("✓ Reddit API client initialized")
    
    def is_ethically_scrapable(
        self,
        subreddit_name: str,
        post_text: str,
        score: int,
        num_comments: int
    ) -> tuple[bool, str]:
        """
        Determine if post meets ethical and quality standards.
        
        Returns:
            (is_ok: bool, reason: str)
        """
        # Check 1: Forbidden subreddit
        if subreddit_name.lower() in self.FORBIDDEN_SUBREDDITS:
            return False, "forbidden_subreddit"
        
        # Check 2: Crisis content
        text_lower = post_text.lower()
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in text_lower:
                return False, "crisis_content"
        
        # Check 3: Minimum quality threshold
        if score < 50:
            return False, "low_quality"
        
        # Check 4: Engagement threshold
        if num_comments < 3:
            return False, "insufficient_engagement"
        
        # Check 5: Minimum length
        if len(post_text) < 50:
            return False, "too_short"
        
        # Check 6: PII detection
        if self._contains_pii(post_text):
            return False, "contains_pii"
        
        return True, "ok"
    
    def _contains_pii(self, text: str) -> bool:
        """
        Detect potential personally identifiable information.
        
        Returns:
            True if PII detected, False otherwise
        """
        # Phone numbers (US format)
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            return True
        
        # Email addresses
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            return True
        
        # Full addresses (simplified check)
        if re.search(r'\d+\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct)', 
                    text, re.IGNORECASE):
            return True
        
        # Social security numbers
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', text):
            return True
        
        return False
    
    def anonymize_text(self, text: str) -> str:
        """
        Deep anonymization of text content.
        
        Replaces:
        - Reddit usernames → [user]
        - Subreddit mentions → [community]
        - Names → [name]
        - Companies → [employer]
        - Schools → [school]
        - Locations → [location]
        """
        # Reddit-specific
        text = re.sub(r'u/\w+', '[user]', text)
        text = re.sub(r'r/\w+', '[community]', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '[link]', text)
        
        # Generic name patterns (conservative - may over-anonymize)
        # Names that aren't sentence starts
        text = re.sub(r'(?<!^)(?<!\. )\b([A-Z][a-z]+)\b', '[name]', text)
        
        # Company/employer mentions
        text = re.sub(
            r'\b(works? at|employed at|job at|company called)\s+[A-Z]\w+',
            r'\1 [employer]',
            text,
            flags=re.IGNORECASE
        )
        
        # School mentions
        text = re.sub(
            r'\b(attend|student at|studying at|university of|college of)\s+[A-Z]\w+',
            r'\1 [school]',
            text,
            flags=re.IGNORECASE
        )
        
        # Location mentions
        text = re.sub(
            r'\b(live in|from|based in|city of)\s+[A-Z]\w+(,\s*[A-Z]{2})?\b',
            r'\1 [location]',
            text,
            flags=re.IGNORECASE
        )
        
        return text
    
    def collect_from_subreddit(
        self,
        subreddit_name: str,
        limit: int = 100,
        min_upvotes: int = 50,
        time_filter: str = 'year'
    ) -> List[Dict]:
        """
        Collect posts from a single subreddit with ethical filtering.
        
        Args:
            subreddit_name: Name of subreddit (without r/)
            limit: Max posts to attempt (before filtering)
            min_upvotes: Minimum quality threshold
            time_filter: 'day', 'week', 'month', 'year', 'all'
        
        Returns:
            List of conversation dictionaries
        """
        # Safety check
        if subreddit_name.lower() in self.FORBIDDEN_SUBREDDITS:
            logger.error(f"❌ Attempted to scrape forbidden subreddit: r/{subreddit_name}")
            return []
        
        logger.info(f"📊 Starting collection from r/{subreddit_name}")
        logger.info(f"   Target: {limit} posts, min upvotes: {min_upvotes}")
        
        subreddit = self.reddit.subreddit(subreddit_name)
        collected = []
        posts_processed = 0
        
        try:
            # Get top posts from time period
            for submission in subreddit.top(time_filter=time_filter, limit=limit):
                posts_processed += 1
                
                # Rate limiting (60 req/min = 1 per second, we do 1.1 to be safe)
                time.sleep(1.1)
                
                # Skip if not text post
                if not submission.selftext or submission.selftext == '[removed]' or submission.selftext == '[deleted]':
                    self.filtered_count += 1
                    self._track_filter_reason('no_text_content')
                    continue
                
                # Ethical filter
                is_ok, reason = self.is_ethically_scrapable(
                    subreddit_name=subreddit_name,
                    post_text=submission.selftext,
                    score=submission.score,
                    num_comments=submission.num_comments
                )
                
                if not is_ok:
                    self.filtered_count += 1
                    self._track_filter_reason(reason)
                    continue
                
                # Get top comments (high-quality responses)
                submission.comments.replace_more(limit=0)  # Don't expand "load more"
                
                for comment in submission.comments.list()[:10]:  # Top 10 comments max
                    # Skip deleted/removed comments
                    if not comment.body or comment.body in ['[removed]', '[deleted]']:
                        continue
                    
                    # Minimum comment quality
                    if comment.score < min_upvotes // 2:  # Half of post threshold
                        continue
                    
                    # Check comment for crisis content too
                    comment_lower = comment.body.lower()
                    if any(kw in comment_lower for kw in self.CRISIS_KEYWORDS):
                        continue
                    
                    # Check if OP responded (engagement signal)
                    op_responded = any(
                        reply.author == submission.author
                        for reply in comment.replies
                        if hasattr(reply, 'author') and reply.author
                    )
                    
                    # Anonymize
                    user_input = self.anonymize_text(submission.selftext)
                    response = self.anonymize_text(comment.body)
                    
                    # Store conversation
                    collected.append({
                        'user_input': user_input,
                        'response': response,
                        'quality_signals': {
                            'post_upvotes': submission.score,
                            'response_upvotes': comment.score,
                            'op_acknowledged': op_responded,
                            'reply_count': len(comment.replies),
                            'post_awards': submission.total_awards_received,
                            'response_awards': getattr(comment, 'total_awards_received', 0)
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
                            'collector_version': 'v1.0-minimal'
                        }
                    })
                    
                    self.collected_count += 1
                    
                    # Progress update every 50 conversations
                    if self.collected_count % 50 == 0:
                        logger.info(f"   ✓ Collected {self.collected_count} conversations...")
        
        except Exception as e:
            logger.error(f"❌ Error collecting from r/{subreddit_name}: {e}")
        
        logger.info(f"✅ Completed r/{subreddit_name}: {len(collected)} conversations")
        logger.info(f"   Posts processed: {posts_processed}")
        logger.info(f"   Pass rate: {len(collected)}/{posts_processed} ({len(collected)/posts_processed*100:.1f}%)")
        
        return collected
    
    def _track_filter_reason(self, reason: str):
        """Track why posts are filtered for analysis."""
        self.filter_reasons[reason] = self.filter_reasons.get(reason, 0) + 1
    
    def _classify_domain(self, subreddit: str) -> str:
        """Classify subreddit into domain categories."""
        subreddit_lower = subreddit.lower()
        
        for domain, subs in self.RECOMMENDED_SUBREDDITS.items():
            if subreddit_lower in [s.lower() for s in subs]:
                return domain
        
        return 'other'
    
    def collect_dataset(
        self,
        subreddits: List[str],
        posts_per_subreddit: int = 100,
        min_upvotes: int = 75
    ) -> pd.DataFrame:
        """
        Collect from multiple subreddits.
        
        Args:
            subreddits: List of subreddit names
            posts_per_subreddit: Posts to attempt per subreddit
            min_upvotes: Minimum quality threshold
        
        Returns:
            DataFrame with all collected conversations
        """
        all_conversations = []
        start_time = datetime.utcnow()
        
        logger.info(f"\n{'='*70}")
        logger.info(f"REDDIT DATA COLLECTION - Path B-Minimal")
        logger.info(f"{'='*70}")
        logger.info(f"Target: {len(subreddits)} subreddits × {posts_per_subreddit} posts")
        logger.info(f"Min upvotes: {min_upvotes}")
        logger.info(f"Started: {start_time.isoformat()}")
        logger.info(f"{'='*70}\n")
        
        for idx, subreddit_name in enumerate(subreddits, 1):
            logger.info(f"\n[{idx}/{len(subreddits)}] Processing r/{subreddit_name}...")
            
            conversations = self.collect_from_subreddit(
                subreddit_name=subreddit_name,
                limit=posts_per_subreddit,
                min_upvotes=min_upvotes,
                time_filter='year'
            )
            
            all_conversations.extend(conversations)
            
            # Save intermediate checkpoint every 3 subreddits
            if idx % 3 == 0 and all_conversations:
                checkpoint_path = Path('evaluation') / f'reddit_checkpoint_{self.collected_count}.parquet'
                checkpoint_df = pd.DataFrame(all_conversations)
                checkpoint_df.to_parquet(checkpoint_path)
                logger.info(f"   💾 Checkpoint saved: {checkpoint_path}")
        
        # Final statistics
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds() / 60  # minutes
        
        logger.info(f"\n{'='*70}")
        logger.info(f"COLLECTION COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Total collected: {self.collected_count} conversations")
        logger.info(f"Total filtered: {self.filtered_count}")
        logger.info(f"Pass rate: {self.collected_count / (self.collected_count + self.filtered_count) * 100:.1f}%")
        logger.info(f"Duration: {duration:.1f} minutes")
        logger.info(f"\nFilter breakdown:")
        for reason, count in sorted(self.filter_reasons.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {reason}: {count} ({count/self.filtered_count*100:.1f}%)")
        logger.info(f"{'='*70}\n")
        
        if not all_conversations:
            logger.warning("⚠️  No conversations collected!")
            return pd.DataFrame()
        
        return pd.DataFrame(all_conversations)


def get_recommended_subreddits() -> List[str]:
    """
    Get the 10 recommended subreddits for Path B-Minimal.
    
    These are strategically selected for:
    - Domain diversity
    - High quality content
    - Ethical appropriateness
    - Marcus alignment
    """
    return [
        # Philosophy (20%)
        'stoicism',
        'philosophy',
        
        # Growth (20%)
        'DecidingToBeBetter',
        'getdisciplined',
        
        # Emotional (10%)
        'stress',
        
        # Interpersonal (20%)
        'relationships',
        'raisedbynarcissists',
        
        # Existential (10%)
        'exchristian',
        
        # Cultural (10%)
        'AsianParentStories',
        
        # Mental Health (10% - handle carefully)
        'mentalhealth',
    ]
