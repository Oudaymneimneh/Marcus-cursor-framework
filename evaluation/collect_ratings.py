"""
Collect and aggregate human ratings of Marcus responses.

Usage:
    python evaluation/collect_ratings.py --analyze
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import statistics


class RatingCollector:
    """
    Collect and aggregate human ratings from multiple raters.
    
    Purpose: Establish ground truth for response quality.
    """
    
    def __init__(self, ratings_dir: str = "evaluation/ratings"):
        self.ratings_dir = Path(ratings_dir)
        self.ratings_dir.mkdir(parents=True, exist_ok=True)
    
    def load_all_ratings(self) -> List[Dict[str, Any]]:
        """Load ratings from all raters."""
        all_ratings = []
        
        for rating_file in self.ratings_dir.glob("*.json"):
            with open(rating_file) as f:
                ratings = json.load(f)
                if isinstance(ratings, list):
                    all_ratings.extend(ratings)
                else:
                    all_ratings.append(ratings)
        
        return all_ratings
    
    def aggregate_by_scenario(self, ratings: List[Dict]) -> Dict[str, Dict]:
        """
        Aggregate ratings by test scenario.
        
        Returns:
            {
                "test_id": {
                    "appropriateness": [5, 4, 5],  # From 3 raters
                    "helpfulness": [4, 4, 5],
                    ...
                    "overall": ["yes", "yes", "maybe"]
                }
            }
        """
        aggregated = defaultdict(lambda: defaultdict(list))
        
        for rating in ratings:
            test_id = rating['test_id']
            
            # Aggregate dimension scores
            for dimension, score in rating['ratings'].items():
                aggregated[test_id][dimension].append(score)
            
            # Aggregate overall
            aggregated[test_id]['overall'].append(rating['overall'])
            
            # Aggregate comments
            if rating.get('comments'):
                aggregated[test_id].setdefault('comments', []).append(rating['comments'])
        
        return dict(aggregated)
    
    def calculate_agreement(self, ratings: List[Dict]) -> Dict[str, float]:
        """
        Calculate inter-rater reliability.
        
        Uses:
        - Fleiss' Kappa for categorical data (overall rating)
        - Intraclass Correlation Coefficient for ordinal data (1-5 scales)
        
        Returns:
            {
                "fleiss_kappa": float,  # Overall agreement
                "icc_appropriateness": float,
                "icc_helpfulness": float,
                ...
            }
        """
        aggregated = self.aggregate_by_scenario(ratings)
        
        # Calculate ICC for each dimension
        icc_scores = {}
        dimensions = ['appropriateness', 'helpfulness', 'stoic_authenticity', 
                     'emotional_intelligence', 'actionability']
        
        for dimension in dimensions:
            scores_by_scenario = [
                aggregated[test_id][dimension] 
                for test_id in aggregated.keys()
            ]
            icc = self._calculate_icc(scores_by_scenario)
            icc_scores[f'icc_{dimension}'] = icc
        
        # Calculate Fleiss' Kappa for overall
        overall_by_scenario = [
            aggregated[test_id]['overall']
            for test_id in aggregated.keys()
        ]
        fleiss_kappa = self._calculate_fleiss_kappa(overall_by_scenario)
        
        return {
            'fleiss_kappa': fleiss_kappa,
            **icc_scores,
            'average_icc': statistics.mean(icc_scores.values())
        }
    
    def _calculate_icc(self, scores_matrix: List[List[int]]) -> float:
        """
        Calculate Intraclass Correlation Coefficient (ICC).
        
        Simplified ICC(2,1) implementation.
        Measures absolute agreement between raters.
        
        ICC interpretation:
        < 0.5: Poor agreement
        0.5-0.75: Moderate agreement
        0.75-0.9: Good agreement
        > 0.9: Excellent agreement
        """
        import numpy as np
        
        # Convert to numpy array
        data = np.array(scores_matrix, dtype=float)
        
        n_scenarios = data.shape[0]
        n_raters = data.shape[1]
        
        # Calculate variance components
        scenario_means = np.mean(data, axis=1)
        grand_mean = np.mean(data)
        
        # Between-scenario variance
        ss_between = n_raters * np.sum((scenario_means - grand_mean) ** 2)
        ms_between = ss_between / (n_scenarios - 1)
        
        # Within-scenario variance
        ss_within = np.sum((data - scenario_means[:, np.newaxis]) ** 2)
        ms_within = ss_within / (n_scenarios * (n_raters - 1))
        
        # ICC calculation
        icc = (ms_between - ms_within) / (ms_between + (n_raters - 1) * ms_within)
        
        return float(icc)
    
    def _calculate_fleiss_kappa(self, ratings_matrix: List[List[str]]) -> float:
        """
        Calculate Fleiss' Kappa for categorical data.
        
        Measures agreement beyond chance.
        
        Kappa interpretation:
        < 0: No agreement
        0-0.2: Slight agreement
        0.2-0.4: Fair agreement
        0.4-0.6: Moderate agreement
        0.6-0.8: Substantial agreement
        0.8-1.0: Almost perfect agreement
        """
        import numpy as np
        
        # Convert to counts per category
        categories = ['yes', 'maybe', 'no']
        n_scenarios = len(ratings_matrix)
        n_raters = len(ratings_matrix[0]) if ratings_matrix else 0
        
        if n_raters == 0:
            return 0.0
        
        # Build contingency matrix
        counts = np.zeros((n_scenarios, len(categories)))
        for i, scenario_ratings in enumerate(ratings_matrix):
            for rating in scenario_ratings:
                cat_idx = categories.index(rating)
                counts[i, cat_idx] += 1
        
        # Calculate P (observed agreement)
        P_i = np.sum(counts * (counts - 1), axis=1) / (n_raters * (n_raters - 1))
        P_bar = np.mean(P_i)
        
        # Calculate P_e (expected agreement by chance)
        p_j = np.sum(counts, axis=0) / (n_scenarios * n_raters)
        P_e = np.sum(p_j ** 2)
        
        # Fleiss' Kappa
        kappa = (P_bar - P_e) / (1 - P_e)
        
        return float(kappa)
    
    def generate_consensus_ratings(self, ratings: List[Dict]) -> Dict[str, Dict]:
        """
        Generate consensus ratings by averaging across raters.
        
        Returns:
            {
                "test_id": {
                    "appropriateness_mean": 4.3,
                    "appropriateness_std": 0.5,
                    "helpfulness_mean": 4.0,
                    ...
                    "overall_consensus": "yes",  # Majority vote
                    "n_raters": 3
                }
            }
        """
        aggregated = self.aggregate_by_scenario(ratings)
        consensus = {}
        
        for test_id, data in aggregated.items():
            scenario_consensus = {'n_raters': len(data['appropriateness'])}
            
            # Calculate mean and std for each dimension
            for dimension in ['appropriateness', 'helpfulness', 'stoic_authenticity',
                            'emotional_intelligence', 'actionability']:
                scores = data[dimension]
                scenario_consensus[f'{dimension}_mean'] = statistics.mean(scores)
                scenario_consensus[f'{dimension}_std'] = statistics.stdev(scores) if len(scores) > 1 else 0.0
                scenario_consensus[f'{dimension}_median'] = statistics.median(scores)
            
            # Majority vote for overall
            overall_counts = {
                'yes': data['overall'].count('yes'),
                'maybe': data['overall'].count('maybe'),
                'no': data['overall'].count('no')
            }
            scenario_consensus['overall_consensus'] = max(overall_counts, key=overall_counts.get)
            scenario_consensus['overall_distribution'] = overall_counts
            
            # Overall quality score (average of all dimensions)
            all_dimension_means = [
                scenario_consensus['appropriateness_mean'],
                scenario_consensus['helpfulness_mean'],
                scenario_consensus['stoic_authenticity_mean'],
                scenario_consensus['emotional_intelligence_mean'],
                scenario_consensus['actionability_mean']
            ]
            scenario_consensus['overall_quality_score'] = statistics.mean(all_dimension_means)
            
            consensus[test_id] = scenario_consensus
        
        return consensus
    
    def analyze_and_report(self):
        """Generate comprehensive analysis report."""
        ratings = self.load_all_ratings()
        
        if not ratings:
            print("No ratings found. Please add rating files to evaluation/ratings/")
            return
        
        print("=" * 70)
        print("MARCUS AI - HUMAN EVALUATION REPORT")
        print("=" * 70)
        
        # Basic stats
        n_raters = len(set(r['rater_id'] for r in ratings))
        n_scenarios = len(set(r['test_id'] for r in ratings))
        
        print(f"\nRatings Collected:")
        print(f"  Total ratings: {len(ratings)}")
        print(f"  Unique raters: {n_raters}")
        print(f"  Scenarios rated: {n_scenarios}")
        print(f"  Coverage: {n_scenarios}/80 scenarios ({n_scenarios/80*100:.0f}%)")
        
        # Inter-rater reliability
        print(f"\nInter-Rater Reliability:")
        agreement = self.calculate_agreement(ratings)
        print(f"  Fleiss' Kappa (overall): {agreement['fleiss_kappa']:.3f}", end="")
        self._print_kappa_interpretation(agreement['fleiss_kappa'])
        print(f"  Average ICC (dimensions): {agreement['average_icc']:.3f}", end="")
        self._print_icc_interpretation(agreement['average_icc'])
        
        for dimension in ['appropriateness', 'helpfulness', 'stoic_authenticity',
                         'emotional_intelligence', 'actionability']:
            icc = agreement[f'icc_{dimension}']
            print(f"  {dimension}: {icc:.3f}")
        
        # Consensus ratings
        print(f"\nConsensus Quality Scores:")
        consensus = self.generate_consensus_ratings(ratings)
        
        # Overall statistics
        overall_scores = [c['overall_quality_score'] for c in consensus.values()]
        print(f"  Average quality: {statistics.mean(overall_scores):.2f}/5.0")
        print(f"  Std deviation: {statistics.stdev(overall_scores):.2f}")
        print(f"  Median: {statistics.median(overall_scores):.2f}")
        print(f"  Range: {min(overall_scores):.2f} - {max(overall_scores):.2f}")
        
        # Overall distribution
        yes_count = sum(1 for c in consensus.values() if c['overall_consensus'] == 'yes')
        maybe_count = sum(1 for c in consensus.values() if c['overall_consensus'] == 'maybe')
        no_count = sum(1 for c in consensus.values() if c['overall_consensus'] == 'no')
        
        print(f"\nOverall Acceptance:")
        print(f"  YES (would use): {yes_count} ({yes_count/len(consensus)*100:.0f}%)")
        print(f"  MAYBE: {maybe_count} ({maybe_count/len(consensus)*100:.0f}%)")
        print(f"  NO: {no_count} ({no_count/len(consensus)*100:.0f}%)")
        
        # Save consensus to file
        output_file = Path("evaluation/consensus_ratings.json")
        with open(output_file, 'w') as f:
            json.dump(consensus, f, indent=2)
        
        print(f"\nConsensus ratings saved to: {output_file}")
        
        # Generate detailed report
        self._generate_detailed_report(ratings, consensus, agreement)
    
    def _print_kappa_interpretation(self, kappa: float):
        """Print interpretation of Kappa score."""
        if kappa < 0:
            print(" (No agreement)")
        elif kappa < 0.2:
            print(" (Slight agreement)")
        elif kappa < 0.4:
            print(" (Fair agreement)")
        elif kappa < 0.6:
            print(" (Moderate agreement)")
        elif kappa < 0.8:
            print(" (Substantial agreement)")
        else:
            print(" (Almost perfect agreement)")
    
    def _print_icc_interpretation(self, icc: float):
        """Print interpretation of ICC score."""
        if icc < 0.5:
            print(" (Poor agreement)")
        elif icc < 0.75:
            print(" (Moderate agreement)")
        elif icc < 0.9:
            print(" (Good agreement)")
        else:
            print(" (Excellent agreement)")
    
    def _generate_detailed_report(
        self,
        ratings: List[Dict],
        consensus: Dict[str, Dict],
        agreement: Dict[str, float]
    ):
        """Generate markdown report with full analysis."""
        report_path = Path("evaluation/HUMAN_EVALUATION_REPORT.md")
        
        with open(report_path, 'w') as f:
            f.write("# Marcus AI - Human Evaluation Report\n\n")
            f.write(f"**Date:** {ratings[0]['timestamp'][:10]}\n")
            f.write(f"**Raters:** {len(set(r['rater_id'] for r in ratings))}\n")
            f.write(f"**Scenarios:** {len(consensus)}\n\n")
            
            f.write("---\n\n")
            f.write("## Summary\n\n")
            
            overall_scores = [c['overall_quality_score'] for c in consensus.values()]
            f.write(f"**Overall Quality Score:** {statistics.mean(overall_scores):.2f}/5.0\n\n")
            
            yes_count = sum(1 for c in consensus.values() if c['overall_consensus'] == 'yes')
            f.write(f"**Acceptance Rate:** {yes_count/len(consensus)*100:.0f}% would use responses\n\n")
            
            f.write(f"**Inter-Rater Reliability:** {agreement['average_icc']:.3f} (")
            if agreement['average_icc'] > 0.75:
                f.write("Good agreement)\n\n")
            elif agreement['average_icc'] > 0.5:
                f.write("Moderate agreement)\n\n")
            else:
                f.write("Poor agreement - may need rater training)\n\n")
            
            f.write("---\n\n")
            f.write("## Dimension Scores\n\n")
            f.write("| Dimension | Mean | Std Dev | ICC |\n")
            f.write("|-----------|------|---------|-----|\n")
            
            for dim in ['appropriateness', 'helpfulness', 'stoic_authenticity',
                       'emotional_intelligence', 'actionability']:
                scores = [c[f'{dim}_mean'] for c in consensus.values()]
                mean = statistics.mean(scores)
                std = statistics.stdev(scores)
                icc = agreement[f'icc_{dim}']
                f.write(f"| {dim.replace('_', ' ').title()} | {mean:.2f} | {std:.2f} | {icc:.3f} |\n")
            
            f.write("\n---\n\n")
            f.write("## Top 10 Highest Rated Responses\n\n")
            
            sorted_scenarios = sorted(
                consensus.items(),
                key=lambda x: x[1]['overall_quality_score'],
                reverse=True
            )[:10]
            
            for i, (test_id, data) in enumerate(sorted_scenarios, 1):
                f.write(f"### {i}. {test_id} (Score: {data['overall_quality_score']:.2f})\n\n")
                f.write(f"**Overall:** {data['overall_consensus'].upper()}\n\n")
                
                # Find original scenario
                with open('test_data/results.json') as rf:
                    results = json.load(rf)
                    scenario = next((r for r in results if r['test_id'] == test_id), None)
                    if scenario:
                        f.write(f"**Input:** {scenario['input']}\n\n")
                        f.write(f"**Response:** {scenario['marcus_response']}\n\n")
                
                f.write("---\n\n")
            
            f.write("## Bottom 10 Lowest Rated Responses\n\n")
            
            bottom_scenarios = sorted_scenarios[-10:]
            for i, (test_id, data) in enumerate(bottom_scenarios, 1):
                f.write(f"### {i}. {test_id} (Score: {data['overall_quality_score']:.2f})\n\n")
                f.write(f"**Overall:** {data['overall_consensus'].upper()}\n\n")
                
                with open('test_data/results.json') as rf:
                    results = json.load(rf)
                    scenario = next((r for r in results if r['test_id'] == test_id), None)
                    if scenario:
                        f.write(f"**Input:** {scenario['input']}\n\n")
                        f.write(f"**Response:** {scenario['marcus_response']}\n\n")
                
                f.write("---\n\n")
        
        print(f"\nDetailed report saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(description='Collect and analyze human ratings')
    parser.add_argument('--analyze', action='store_true', help='Analyze existing ratings')
    parser.add_argument('--ratings-dir', default='evaluation/ratings', help='Directory with rating files')
    
    args = parser.parse_args()
    
    collector = RatingCollector(args.ratings_dir)
    
    if args.analyze:
        collector.analyze_and_report()
    else:
        print("Usage:")
        print("  python evaluation/collect_ratings.py --analyze")
        print("\nOr open evaluation/rating_interface.html in a browser to rate responses")


if __name__ == "__main__":
    main()
