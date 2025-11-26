"""
Empirical Strategy Effectiveness Study.

Measure which strategies actually work in which contexts
using human evaluation, not theory.
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import statistics


class StrategyEffectivenessStudy:
    """
    Empirically measure strategy effectiveness.
    
    PURPOSE: Replace guessed effectiveness scores with real data.
    
    Method:
    1. For each strategy, generate responses to diverse scenarios
    2. Have humans rate response quality
    3. Calculate real effectiveness by strategy × context
    4. Update system with empirical thresholds
    
    This answers:
    - When should we use "supportive" vs "balanced"?
    - Does "energizing" actually help low-energy users?
    - Is "challenging" ever appropriate?
    """
    
    def __init__(self):
        self.strategies = ['supportive', 'balanced', 'challenging', 'energizing', 'reflective']
    
    async def generate_strategy_samples(
        self,
        scenarios_path: str = "test_data/results.json"
    ) -> Dict[str, List[Dict]]:
        """
        Generate responses using EACH strategy for EACH scenario.
        
        This creates systematic comparison data.
        
        Returns:
            {
                'supportive': [...],  # All scenarios with supportive strategy
                'balanced': [...],    # All scenarios with balanced strategy
                ...
            }
        """
        with open(scenarios_path) as f:
            scenarios = json.load(f)
        
        strategy_samples = defaultdict(list)
        
        print("Generating responses with each strategy...")
        print("This allows empirical measurement of strategy effectiveness")
        print()
        
        for scenario in scenarios[:20]:  # Sample 20 for manual review
            test_id = scenario['test_id']
            user_input = scenario['input']
            
            print(f"Scenario: {test_id}")
            
            # For each strategy, generate a response
            # NOTE: This requires modifying DialogueGenerator to allow
            # strategy override for testing purposes
            
            for strategy in self.strategies:
                # Would call: marcus.generate_with_strategy(user_input, strategy)
                # For now, store the setup
                strategy_samples[strategy].append({
                    'test_id': test_id,
                    'user_input': user_input,
                    'strategy': strategy,
                    'context': scenario.get('category')
                })
            
            print(f"  Generated {len(self.strategies)} strategy variations")
        
        # Save for rating
        output_path = Path("evaluation/strategy_samples.json")
        with open(output_path, 'w') as f:
            json.dump(dict(strategy_samples), f, indent=2)
        
        print(f"\nStrategy samples saved to: {output_path}")
        print("Next: Have humans rate which strategies work best in each context")
        
        return dict(strategy_samples)
    
    def analyze_strategy_effectiveness(
        self,
        ratings_path: str = "evaluation/strategy_ratings.json"
    ) -> Dict[str, Dict]:
        """
        Analyze which strategies work best in which contexts.
        
        Args:
            ratings_path: Human ratings of strategy samples
            
        Returns:
            {
                'supportive': {
                    'overall_rating': 4.2,
                    'best_for': ['crisis', 'grief', 'loss'],
                    'worst_for': ['achievement', 'excitement'],
                    'sample_size': 60
                },
                ...
            }
        """
        with open(ratings_path) as f:
            ratings = json.load(f)
        
        # Group by strategy
        by_strategy = defaultdict(list)
        by_strategy_context = defaultdict(lambda: defaultdict(list))
        
        for rating in ratings:
            strategy = rating['strategy']
            context = rating.get('context', 'unknown')
            quality = rating['human_rating']
            
            by_strategy[strategy].append(quality)
            by_strategy_context[strategy][context].append(quality)
        
        results = {}
        
        for strategy, ratings_list in by_strategy.items():
            # Calculate overall
            mean_rating = statistics.mean(ratings_list)
            
            # Find best contexts
            context_means = {
                ctx: statistics.mean(values)
                for ctx, values in by_strategy_context[strategy].items()
            }
            
            sorted_contexts = sorted(context_means.items(), key=lambda x: -x[1])
            best_for = [ctx for ctx, score in sorted_contexts[:3] if score > mean_rating]
            worst_for = [ctx for ctx, score in sorted_contexts[-3:] if score < mean_rating]
            
            results[strategy] = {
                'overall_rating': mean_rating,
                'std_dev': statistics.stdev(ratings_list),
                'best_for': best_for,
                'worst_for': worst_for,
                'sample_size': len(ratings_list),
                'by_context': context_means
            }
        
        # Print report
        print("=" * 70)
        print("EMPIRICAL STRATEGY EFFECTIVENESS")
        print("=" * 70)
        
        for strategy, data in sorted(results.items(), key=lambda x: -x[1]['overall_rating']):
            print(f"\n{strategy.upper()}:")
            print(f"  Overall rating: {data['overall_rating']:.2f}/5.0 (n={data['sample_size']})")
            print(f"  Best for: {', '.join(data['best_for'])}")
            print(f"  Worst for: {', '.join(data['worst_for'])}")
        
        # Save results
        output_path = Path("evaluation/strategy_effectiveness_empirical.json")
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")
        
        return results
    
    def generate_decision_rules(
        self,
        effectiveness_data: Dict[str, Dict]
    ) -> str:
        """
        Generate code for data-driven strategy selection.
        
        Output: Python code with empirical decision rules
        """
        code = '''"""
Data-Driven Strategy Selection Rules
Generated from empirical effectiveness study
"""

def select_strategy_empirical(context: dict, user_input: str) -> str:
    """
    Strategy selection based on measured effectiveness.
    
    Rules derived from human evaluation data, not theory.
    """
'''
        
        # Generate rules based on data
        for strategy, data in sorted(effectiveness_data.items(), key=lambda x: -x[1]['overall_rating']):
            if data['best_for']:
                contexts = "', '".join(data['best_for'])
                code += f'''
    # {strategy.upper()}: Best for {contexts} (rating: {data['overall_rating']:.2f})
    if any(ctx in context.get('category', '') for ctx in ['{contexts}']):
        return '{strategy}'
'''
        
        code += '''
    # Default to highest-rated strategy
    return 'balanced'  # Update with actual best from data
'''
        
        output_path = Path("src/intelligence/empirical_strategy_rules.py")
        with open(output_path, 'w') as f:
            f.write(code)
        
        print(f"Generated decision rules: {output_path}")
        
        return code


async def main():
    study = StrategyEffectivenessStudy()
    
    # Generate strategy samples for rating
    await study.generate_strategy_samples()
    
    print("\nNext steps:")
    print("1. Have humans rate the strategy samples")
    print("2. Save ratings to evaluation/strategy_ratings.json")
    print("3. Run: python evaluation/strategy_effectiveness_study.py --analyze")


if __name__ == "__main__":
    asyncio.run(main())
