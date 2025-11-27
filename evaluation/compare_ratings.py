#!/usr/bin/env python3
"""
Combined Analysis: AI Ratings vs Human Ratings

Compares automated AI evaluations with human ratings to:
- Validate AI evaluation quality
- Identify where AIs and humans agree/disagree
- Discover which model truly performs best
- Detect biases in AI or human judgment

Usage:
    python compare_ratings.py --ai ai_ratings.json --human human_ratings.json
"""

import json
import argparse
from collections import defaultdict
from typing import Dict, List
import numpy as np
from pathlib import Path


class RatingAnalyzer:
    """Analyzes and compares AI vs Human ratings"""
    
    def __init__(self, ai_ratings_file: str, human_ratings_file: str):
        self.ai_ratings = self._load_json(ai_ratings_file)
        self.human_ratings = self._load_json(human_ratings_file) if human_ratings_file else None
        
        # Model performance tracking
        self.model_scores = defaultdict(lambda: {
            'ai_wins': 0,
            'human_wins': 0,
            'ai_ratings': [],
            'human_ratings': []
        })
        
        self.agreement_scores = []
    
    def _load_json(self, filepath: str) -> dict:
        """Load JSON file"""
        if not Path(filepath).exists():
            print(f"⚠️  File not found: {filepath}")
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def analyze_ai_ratings(self):
        """Analyze AI-generated ratings"""
        print("\n📊 AI RATINGS ANALYSIS")
        print("=" * 70)
        
        if not self.ai_ratings:
            print("❌ No AI ratings found")
            return
        
        # Count wins by model across all AI raters
        model_wins = defaultdict(int)
        total_comparisons = 0
        rater_agreement = defaultdict(list)
        
        for evaluation in self.ai_ratings['evaluations']:
            scenario_id = evaluation['scenario_id']
            
            for pair in evaluation['pairs']:
                model_a = pair['model_a']
                model_b = pair['model_b']
                ratings = pair['ratings']
                
                if not ratings:
                    continue
                
                # Count who each rater picked
                winners = []
                for rater_name, rating in ratings.items():
                    winner = rating.get('winner')
                    if winner == 'A':
                        winners.append(model_a)
                    elif winner == 'B':
                        winners.append(model_b)
                
                if not winners:
                    continue
                
                # Majority vote
                winner_counts = defaultdict(int)
                for w in winners:
                    winner_counts[w] += 1
                
                majority_winner = max(winner_counts.items(), key=lambda x: x[1])[0]
                model_wins[majority_winner] += 1
                total_comparisons += 1
                
                # Track rater agreement
                if len(set(winners)) == 1:
                    rater_agreement['unanimous'].append(scenario_id)
                else:
                    rater_agreement['split'].append(scenario_id)
        
        # Display results
        print(f"\n🏆 MODEL RANKINGS (by AI judges)")
        print("-" * 70)
        
        ranked_models = sorted(model_wins.items(), key=lambda x: x[1], reverse=True)
        for rank, (model, wins) in enumerate(ranked_models, 1):
            win_rate = (wins / total_comparisons * 100) if total_comparisons > 0 else 0
            emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
            print(f"{emoji} {rank}. {model:15s} - {wins:3d} wins ({win_rate:.1f}%)")
        
        print(f"\nTotal comparisons: {total_comparisons}")
        
        # Rater agreement
        unanimous_pct = len(rater_agreement['unanimous']) / (len(rater_agreement['unanimous']) + len(rater_agreement['split'])) * 100 if rater_agreement else 0
        print(f"\n🤝 AI RATER AGREEMENT")
        print("-" * 70)
        print(f"Unanimous decisions: {len(rater_agreement['unanimous'])} ({unanimous_pct:.1f}%)")
        print(f"Split decisions: {len(rater_agreement['split'])} ({100-unanimous_pct:.1f}%)")
        
        # Category breakdown
        self._analyze_by_category()
    
    def _analyze_by_category(self):
        """Break down AI ratings by scenario category"""
        if not self.ai_ratings:
            return
        
        category_wins = defaultdict(lambda: defaultdict(int))
        
        for evaluation in self.ai_ratings['evaluations']:
            domain = evaluation['scenario'].get('domain', 'unknown')
            
            for pair in evaluation['pairs']:
                model_a = pair['model_a']
                model_b = pair['model_b']
                ratings = pair['ratings']
                
                if not ratings:
                    continue
                
                # Majority winner
                winners = []
                for rating in ratings.values():
                    winner = rating.get('winner')
                    if winner == 'A':
                        winners.append(model_a)
                    elif winner == 'B':
                        winners.append(model_b)
                
                if winners:
                    majority_winner = max(set(winners), key=winners.count)
                    category_wins[domain][majority_winner] += 1
        
        print(f"\n📂 PERFORMANCE BY CATEGORY")
        print("-" * 70)
        
        for domain in sorted(category_wins.keys()):
            print(f"\n{domain.upper()}:")
            ranked = sorted(category_wins[domain].items(), key=lambda x: x[1], reverse=True)
            for model, wins in ranked:
                print(f"  {model:15s} - {wins} wins")
    
    def analyze_human_ratings(self):
        """Analyze human ratings if available"""
        print("\n👥 HUMAN RATINGS ANALYSIS")
        print("=" * 70)
        
        if not self.human_ratings:
            print("⚠️  No human ratings available yet")
            print("Collect human ratings via the gamified interface")
            return
        
        # Parse human ratings structure
        # Format depends on what we collect from the interface
        # This is a placeholder for when human data arrives
        
        print("Human rating analysis will appear here once data is collected")
    
    def compare_ai_vs_human(self):
        """Compare AI and human ratings"""
        print("\n🔍 AI vs HUMAN COMPARISON")
        print("=" * 70)
        
        if not self.human_ratings:
            print("⚠️  Need human ratings for comparison")
            print("\nHuman ratings not yet collected")
            return
        
        # Calculate agreement rates
        # Match scenarios and compare winners
        # This will be implemented once we have human data structure
        
        print("Comparison analysis will appear here once human data is available")
    
    def generate_insights(self):
        """Generate actionable insights"""
        print("\n💡 KEY INSIGHTS")
        print("=" * 70)
        
        if not self.ai_ratings:
            return
        
        # Calculate average scores by dimension
        dimension_scores = defaultdict(lambda: defaultdict(list))
        
        for evaluation in self.ai_ratings['evaluations']:
            for pair in evaluation['pairs']:
                model_a = pair['model_a']
                model_b = pair['model_b']
                
                for rating in pair['ratings'].values():
                    if 'response_a' in rating:
                        for dim in ['wisdom', 'empathy', 'actionable']:
                            if dim in rating['response_a']:
                                dimension_scores[model_a][dim].append(rating['response_a'][dim])
                    
                    if 'response_b' in rating:
                        for dim in ['wisdom', 'empathy', 'actionable']:
                            if dim in rating['response_b']:
                                dimension_scores[model_b][dim].append(rating['response_b'][dim])
        
        print("\n📊 AVERAGE SCORES BY DIMENSION (1-5 scale)")
        print("-" * 70)
        
        for model in sorted(dimension_scores.keys()):
            scores = dimension_scores[model]
            print(f"\n{model}:")
            for dim in ['wisdom', 'empathy', 'actionable']:
                if scores[dim]:
                    avg = np.mean(scores[dim])
                    print(f"  {dim.capitalize():12s}: {avg:.2f}/5.0")
    
    def export_summary(self, output_file: str = "analysis_summary.json"):
        """Export summary as JSON"""
        summary = {
            "analysis_date": Path(output_file).stat().st_mtime if Path(output_file).exists() else None,
            "ai_ratings_available": self.ai_ratings is not None,
            "human_ratings_available": self.human_ratings is not None,
            "model_scores": dict(self.model_scores)
        }
        
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Exported summary to: {output_file}")
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        self.analyze_ai_ratings()
        self.analyze_human_ratings()
        self.compare_ai_vs_human()
        self.generate_insights()
        self.export_summary()
        
        print("\n" + "=" * 70)
        print("✅ Analysis complete!")
        print("\nNext steps:")
        print("1. Review AI ratings to validate quality")
        print("2. Deploy human rating interface to Reddit")
        print("3. Re-run this script once human data is collected")
        print("4. Use insights to improve Marcus")


def main():
    parser = argparse.ArgumentParser(description="Compare AI and Human ratings")
    parser.add_argument(
        "--ai",
        default="ai_ratings.json",
        help="AI ratings JSON file"
    )
    parser.add_argument(
        "--human",
        help="Human ratings JSON file (optional, will be collected later)"
    )
    
    args = parser.parse_args()
    
    analyzer = RatingAnalyzer(args.ai, args.human)
    analyzer.run_full_analysis()


if __name__ == "__main__":
    main()


