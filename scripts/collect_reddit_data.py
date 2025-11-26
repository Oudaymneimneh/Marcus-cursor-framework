#!/usr/bin/env python3
"""
Reddit Data Collection Script - Path B-Minimal
==============================================

THREE MODES:

1. TEST MODE (30 minutes)
   - 1 subreddit (stoicism)
   - 10 posts
   - Verify everything works

2. VALIDATION MODE (1 hour)
   - 4 subreddits
   - 25 posts each = 100 total
   - Verify quality before full collection

3. PRODUCTION MODE (4 hours)
   - 10 subreddits
   - 100 posts each = 1,000 target
   - Full dataset collection

USAGE:
    python scripts/collect_reddit_data.py --test
    python scripts/collect_reddit_data.py --validate
    python scripts/collect_reddit_data.py --production
"""

import argparse
import logging
import os
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation.reddit_collector import EthicalRedditCollector, get_recommended_subreddits

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'evaluation' / 'reddit_collection.log'),
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
        logger.error("❌ Missing Reddit API credentials!")
        logger.error("\nTo fix:")
        logger.error("1. Go to https://www.reddit.com/prefs/apps")
        logger.error("2. Click 'Create App' or 'Create Another App'")
        logger.error("3. Fill out:")
        logger.error("   - Name: Marcus AI Research")
        logger.error("   - Type: script")
        logger.error("   - Redirect URI: http://localhost:8080")
        logger.error("4. Copy Client ID and Secret")
        logger.error("5. Add to .env file:")
        logger.error("   REDDIT_CLIENT_ID=your_client_id")
        logger.error("   REDDIT_CLIENT_SECRET=your_secret")
        sys.exit(1)
    
    return client_id, client_secret


def test_mode():
    """
    TEST MODE: Quick sanity check (30 minutes)
    
    Collects:
    - 1 subreddit (r/stoicism)
    - 10 posts
    - Verifies API works and quality is good
    
    Decision Gate:
    - If quality looks good → Proceed to validation
    - If issues found → Fix before continuing
    """
    logger.info("🧪 Running in TEST MODE")
    logger.info("=" * 70)
    logger.info("Purpose: Verify API connection and data quality")
    logger.info("Time: ~30 minutes")
    logger.info("Output: ~10-20 conversations")
    logger.info("=" * 70)
    
    client_id, client_secret = load_credentials()
    collector = EthicalRedditCollector(client_id, client_secret)
    
    # Test on just stoicism
    conversations = collector.collect_from_subreddit(
        subreddit_name='stoicism',
        limit=10,
        min_upvotes=50
    )
    
    if not conversations:
        logger.error("❌ TEST FAILED: No conversations collected")
        logger.error("Check:")
        logger.error("  - Are Reddit credentials correct?")
        logger.error("  - Is Reddit API responding?")
        logger.error("  - Are quality thresholds too high?")
        return
    
    # Save
    df = pd.DataFrame(conversations)
    output_file = project_root / 'evaluation' / 'reddit_test_sample.parquet'
    df.to_parquet(output_file)
    
    # Display results
    logger.info(f"\n{'='*70}")
    logger.info("TEST RESULTS")
    logger.info(f"{'='*70}")
    logger.info(f"✓ Conversations collected: {len(df)}")
    logger.info(f"✓ Average upvotes: {df['quality_signals'].apply(lambda x: x['response_upvotes']).mean():.1f}")
    logger.info(f"✓ OP engagement rate: {df['quality_signals'].apply(lambda x: x['op_acknowledged']).mean()*100:.1f}%")
    logger.info(f"✓ Saved to: {output_file}")
    
    # Show sample
    logger.info(f"\n{'='*70}")
    logger.info("SAMPLE CONVERSATION:")
    logger.info(f"{'='*70}")
    sample = conversations[0]
    logger.info(f"\nUser Input ({len(sample['user_input'])} chars):")
    logger.info(sample['user_input'][:200] + "..." if len(sample['user_input']) > 200 else sample['user_input'])
    logger.info(f"\nResponse ({len(sample['response'])} chars, {sample['quality_signals']['response_upvotes']} upvotes):")
    logger.info(sample['response'][:200] + "..." if len(sample['response']) > 200 else sample['response'])
    
    logger.info(f"\n{'='*70}")
    logger.info("✅ TEST COMPLETE")
    logger.info(f"{'='*70}")
    logger.info("\nNext step: Review quality, then run --validate mode")


def validation_mode():
    """
    VALIDATION MODE: Quality check before full collection (1 hour)
    
    Collects:
    - 4 diverse subreddits
    - 25 posts each = 100 total
    - Statistical validation
    
    Decision Gate:
    - All checks pass → Proceed to production
    - Any check fails → Adjust filters and retry
    """
    logger.info("✓ Running in VALIDATION MODE")
    logger.info("=" * 70)
    logger.info("Purpose: Validate quality across domains")
    logger.info("Time: ~1 hour")
    logger.info("Output: ~100-150 conversations")
    logger.info("=" * 70)
    
    validation_subs = ['stoicism', 'DecidingToBeBetter', 'relationships', 'stress']
    
    response = input(f"\nCollect from {len(validation_subs)} subreddits (~1 hour)? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Cancelled by user")
        return
    
    client_id, client_secret = load_credentials()
    collector = EthicalRedditCollector(client_id, client_secret)
    
    df = collector.collect_dataset(
        subreddits=validation_subs,
        posts_per_subreddit=25,
        min_upvotes=75
    )
    
    if df.empty:
        logger.error("❌ VALIDATION FAILED: No data collected")
        return
    
    # Save
    output_file = project_root / 'evaluation' / 'reddit_validation_sample.parquet'
    df.to_parquet(output_file)
    
    # Run validation checks
    logger.info(f"\n{'='*70}")
    logger.info("VALIDATION CHECKS")
    logger.info(f"{'='*70}")
    
    checks_passed = 0
    checks_total = 5
    
    # Check 1: Total conversations
    total = len(df)
    check1 = total >= 80
    logger.info(f"{'✓' if check1 else '✗'} Total conversations: {total} (target: >= 80)")
    if check1: checks_passed += 1
    
    # Check 2: Average upvotes
    avg_upvotes = df['quality_signals'].apply(lambda x: x['response_upvotes']).mean()
    check2 = avg_upvotes >= 40
    logger.info(f"{'✓' if check2 else '✗'} Average upvotes: {avg_upvotes:.1f} (target: >= 40)")
    if check2: checks_passed += 1
    
    # Check 3: OP engagement
    op_engagement = df['quality_signals'].apply(lambda x: x['op_acknowledged']).mean()
    check3 = op_engagement >= 0.25
    logger.info(f"{'✓' if check3 else '✗'} OP engagement: {op_engagement*100:.1f}% (target: >= 25%)")
    if check3: checks_passed += 1
    
    # Check 4: Domain diversity
    domains = df['context'].apply(lambda x: x['domain']).nunique()
    check4 = domains >= 4
    logger.info(f"{'✓' if check4 else '✗'} Domain diversity: {domains} domains (target: >= 4)")
    if check4: checks_passed += 1
    
    # Check 5: Response length
    avg_length = df['context'].apply(lambda x: x['response_length']).mean()
    check5 = 100 <= avg_length <= 500
    logger.info(f"{'✓' if check5 else '✗'} Response length: {avg_length:.0f} chars (target: 100-500)")
    if check5: checks_passed += 1
    
    logger.info(f"\n{'='*70}")
    if checks_passed == checks_total:
        logger.info(f"✅ ALL CHECKS PASSED ({checks_passed}/{checks_total})")
        logger.info(f"{'='*70}")
        logger.info(f"✓ Data quality verified")
        logger.info(f"✓ Saved to: {output_file}")
        logger.info("\n🚀 Ready for production mode!")
        logger.info("Run: python scripts/collect_reddit_data.py --production")
    else:
        logger.warning(f"⚠️  SOME CHECKS FAILED ({checks_passed}/{checks_total})")
        logger.info(f"{'='*70}")
        logger.info("Review issues and adjust:")
        if not check1: logger.info("  - Reduce min_upvotes threshold")
        if not check2: logger.info("  - Quality too low - increase min_upvotes")
        if not check3: logger.info("  - Expected - OP engagement varies")
        if not check4: logger.info("  - Add more diverse subreddits")
        if not check5: logger.info("  - Response length distribution issue")


def production_mode():
    """
    PRODUCTION MODE: Full data collection (4 hours)
    
    Collects:
    - 10 strategic subreddits
    - 100 posts each = 1,000 target
    - Expected yield: ~600-800 after filtering
    
    Output:
    - evaluation/reddit_data_1000.parquet
    - evaluation/reddit_statistics.json
    """
    logger.info("🚀 Running in PRODUCTION MODE")
    logger.info("=" * 70)
    logger.info("Purpose: Full dataset collection")
    logger.info("Time: ~4 hours")
    logger.info("Output: ~600-800 high-quality conversations")
    logger.info("=" * 70)
    
    subreddits = get_recommended_subreddits()
    
    logger.info(f"\nSubreddits ({len(subreddits)}):")
    for sub in subreddits:
        logger.info(f"  - r/{sub}")
    
    response = input(f"\nThis will take ~4 hours. Continue? (yes/no): ")
    if response.lower() != 'yes':
        logger.info("Cancelled by user")
        return
    
    client_id, client_secret = load_credentials()
    collector = EthicalRedditCollector(client_id, client_secret)
    
    start_time = datetime.utcnow()
    
    df = collector.collect_dataset(
        subreddits=subreddits,
        posts_per_subreddit=100,
        min_upvotes=100  # Top quality only
    )
    
    if df.empty:
        logger.error("❌ PRODUCTION FAILED: No data collected")
        return
    
    end_time = datetime.utcnow()
    duration_minutes = (end_time - start_time).total_seconds() / 60
    
    # Save main dataset
    output_file = project_root / 'evaluation' / 'reddit_data_1000.parquet'
    df.to_parquet(output_file)
    
    # Calculate statistics
    stats = {
        'collection_date': end_time.isoformat(),
        'duration_minutes': duration_minutes,
        'total_conversations': len(df),
        'subreddits': subreddits,
        'by_domain': df['context'].apply(lambda x: x['domain']).value_counts().to_dict(),
        'by_subreddit': df['context'].apply(lambda x: x['subreddit']).value_counts().to_dict(),
        'quality_metrics': {
            'avg_post_upvotes': float(df['quality_signals'].apply(lambda x: x['post_upvotes']).mean()),
            'avg_response_upvotes': float(df['quality_signals'].apply(lambda x: x['response_upvotes']).mean()),
            'avg_response_length': float(df['context'].apply(lambda x: x['response_length']).mean()),
            'op_engagement_rate': float(df['quality_signals'].apply(lambda x: x['op_acknowledged']).mean()),
        },
        'collection_stats': {
            'collected': collector.collected_count,
            'filtered': collector.filtered_count,
            'pass_rate': collector.collected_count / (collector.collected_count + collector.filtered_count)
        }
    }
    
    stats_file = project_root / 'evaluation' / 'reddit_statistics.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Final report
    logger.info(f"\n{'='*70}")
    logger.info("✅ PRODUCTION COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Duration: {duration_minutes:.1f} minutes ({duration_minutes/60:.1f} hours)")
    logger.info(f"Total conversations: {len(df)}")
    logger.info(f"\nQuality metrics:")
    logger.info(f"  Avg post upvotes: {stats['quality_metrics']['avg_post_upvotes']:.1f}")
    logger.info(f"  Avg response upvotes: {stats['quality_metrics']['avg_response_upvotes']:.1f}")
    logger.info(f"  Response length: {stats['quality_metrics']['avg_response_length']:.0f} chars")
    logger.info(f"  OP engagement: {stats['quality_metrics']['op_engagement_rate']*100:.1f}%")
    logger.info(f"\nDomain distribution:")
    for domain, count in sorted(stats['by_domain'].items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {domain}: {count} ({count/len(df)*100:.1f}%)")
    logger.info(f"\nFiles created:")
    logger.info(f"  Data: {output_file}")
    logger.info(f"  Stats: {stats_file}")
    logger.info(f"{'='*70}")
    logger.info("\n🎯 Next step: Run multi-LLM comparison")
    logger.info("   python scripts/run_multi_llm_comparison.py")


def main():
    parser = argparse.ArgumentParser(
        description='Reddit data collection for Marcus AI - Path B-Minimal',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/collect_reddit_data.py --test       # Quick test (30 min)
  python scripts/collect_reddit_data.py --validate   # Quality check (1 hour)
  python scripts/collect_reddit_data.py --production # Full collection (4 hours)

Modes:
  TEST        → 10 posts from r/stoicism
  VALIDATE    → 100 posts from 4 subreddits
  PRODUCTION  → 1,000 posts from 10 subreddits
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--test', action='store_true', help='Test mode (10 posts, 30 min)')
    group.add_argument('--validate', action='store_true', help='Validation mode (100 posts, 1 hour)')
    group.add_argument('--production', action='store_true', help='Production mode (1,000 posts, 4 hours)')
    
    args = parser.parse_args()
    
    # Ensure evaluation directory exists
    eval_dir = project_root / 'evaluation'
    eval_dir.mkdir(exist_ok=True)
    
    # Run selected mode
    if args.test:
        test_mode()
    elif args.validate:
        validation_mode()
    elif args.production:
        production_mode()


if __name__ == '__main__':
    main()
