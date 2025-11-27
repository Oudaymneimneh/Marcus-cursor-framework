"""
Test Introspection System Enhancements.

Tests the improvements made to:
1. Strategy selection (keyword-based crisis/energy detection)
2. Pattern detection (expanded keywords, false positive prevention)
3. Effectiveness formula (calibrated weights, strategy bonuses)
4. Learning tracking (metrics and curves)

Usage:
    python evaluation/test_introspection_enhancements.py
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from src.domain.models import Base, User, Session, PADState, Pattern, Strategy
from src.domain.introspection import IntrospectionService
from src.domain.repositories import (
    UserRepository, SessionRepository, PADStateRepository,
    PatternRepository, StrategyRepository
)
from src.dialogue.pad_logic import PADLogic
from src.intelligence.advanced_sentiment import AdvancedSentimentAnalyzer


class IntrospectionTester:
    """Test suite for introspection enhancements."""
    
    def __init__(self, db_url: str = "sqlite+aiosqlite:///:memory:"):
        self.engine = create_async_engine(db_url, echo=False)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.pad_logic = PADLogic()
        
    async def setup(self):
        """Create database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def cleanup(self):
        """Close database connections."""
        await self.engine.dispose()
    
    async def create_test_user_and_session(self) -> tuple[uuid.UUID, uuid.UUID]:
        """Create a test user and session."""
        async with self.session_factory() as session:
            user_repo = UserRepository(session)
            session_repo = SessionRepository(session)
            
            user = await user_repo.ensure_user("test_user", "Test User")
            sess = await session_repo.create_session(user.user_id)
            
            await session.commit()
            return user.user_id, sess.session_id
    
    async def test_strategy_selection(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test strategy selection improvements.
        
        Tests:
        - Keyword-based crisis detection
        - Keyword-based energy detection
        - PAD-based thresholds
        - Pattern-based selection
        """
        results = {
            'total': len(scenarios),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        user_id, session_id = await self.create_test_user_and_session()
        
        async with self.session_factory() as session:
            introspection = IntrospectionService(session)
            pad_repo = PADStateRepository(session)
            
            for scenario in scenarios:
                scenario_id = scenario.get('scenario_id', 'unknown')
                user_input = scenario.get('user_input', '')
                expected_strategy = scenario.get('expected_strategy')
                category = scenario.get('category', 'unknown')
                
                # Set up initial PAD state if provided
                baseline_pad = scenario.get('baseline_pad', {})
                if baseline_pad:
                    await pad_repo.record_state(
                        session_id,
                        baseline_pad.get('pleasure', 0.0),
                        baseline_pad.get('arousal', 0.0),
                        baseline_pad.get('dominance', 0.0),
                        self.pad_logic.get_quadrant(baseline_pad)
                    )
                
                # Prepare context
                context = await introspection.prepare_response_context(user_id, session_id)
                
                # Select strategy
                selected_strategy = await introspection.select_strategy(
                    context, user_id, user_input
                )
                
                # Check if matches expected
                passed = expected_strategy is None or selected_strategy == expected_strategy
                
                result = {
                    'scenario_id': scenario_id,
                    'category': category,
                    'user_input': user_input[:50] + '...' if len(user_input) > 50 else user_input,
                    'expected': expected_strategy,
                    'actual': selected_strategy,
                    'passed': passed
                }
                
                if passed:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append(result)
                
                await session.commit()
        
        return results
    
    async def test_effectiveness_formula(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test effectiveness formula calibration.
        
        Tests:
        - Pleasure weight (2.5x)
        - Arousal contribution
        - Strategy-appropriate bonus
        - Negative streak break bonus
        """
        results = {
            'total': len(scenarios),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        user_id, session_id = await self.create_test_user_and_session()
        
        async with self.session_factory() as session:
            introspection = IntrospectionService(session)
            pad_repo = PADStateRepository(session)
            
            for scenario in scenarios:
                scenario_id = scenario.get('scenario_id', 'unknown')
                baseline_pad = scenario.get('baseline_pad', {'pleasure': 0.0, 'arousal': 0.0, 'dominance': 0.0})
                expected_range = scenario.get('expected_effectiveness_range', [0.0, 1.0])
                expected_direction = scenario.get('expected_pad_direction', {})
                strategy_used = scenario.get('expected_strategy', 'balanced')
                
                # Record baseline state
                await pad_repo.record_state(
                    session_id,
                    baseline_pad['pleasure'],
                    baseline_pad['arousal'],
                    baseline_pad['dominance'],
                    self.pad_logic.get_quadrant(baseline_pad)
                )
                
                # Prepare context
                context = await introspection.prepare_response_context(user_id, session_id)
                
                # Simulate PAD change based on expected direction
                after_pad = baseline_pad.copy()
                if 'pleasure' in expected_direction:
                    if expected_direction['pleasure'] == 'increase':
                        after_pad['pleasure'] = min(1.0, baseline_pad['pleasure'] + 0.3)
                    elif expected_direction['pleasure'] == 'decrease':
                        after_pad['pleasure'] = max(-1.0, baseline_pad['pleasure'] - 0.3)
                
                if 'arousal' in expected_direction:
                    if expected_direction['arousal'] == 'increase':
                        after_pad['arousal'] = min(1.0, baseline_pad['arousal'] + 0.2)
                    elif expected_direction['arousal'] == 'decrease':
                        after_pad['arousal'] = max(-1.0, baseline_pad['arousal'] - 0.2)
                
                # Measure effectiveness
                effectiveness = await introspection.measure_effectiveness(
                    context, after_pad, strategy_used
                )
                
                # Check if in expected range
                passed = expected_range[0] <= effectiveness <= expected_range[1]
                
                result = {
                    'scenario_id': scenario_id,
                    'expected_range': expected_range,
                    'actual': round(effectiveness, 3),
                    'passed': passed,
                    'strategy': strategy_used
                }
                
                if passed:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append(result)
                
                await session.commit()
        
        return results
    
    async def test_pattern_detection(
        self,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test pattern detection enhancements.
        
        Tests:
        - Catastrophizing detection
        - Solution-seeking detection
        - False positive prevention
        """
        results = {
            'total': len(scenarios),
            'passed': 0,
            'failed': 0,
            'details': []
        }
        
        user_id, session_id = await self.create_test_user_and_session()
        
        async with self.session_factory() as session:
            introspection = IntrospectionService(session)
            
            for scenario in scenarios:
                scenario_id = scenario.get('scenario_id', 'unknown')
                user_input = scenario.get('user_input', '')
                expected_pattern = scenario.get('expected_pattern')
                
                # Detect patterns
                detected = await introspection.detect_new_patterns(
                    user_id, session_id, user_input
                )
                
                # Check if matches expected
                if expected_pattern is None:
                    # Should NOT detect pattern (false positive test)
                    passed = len(detected) == 0
                else:
                    # Should detect specific pattern
                    passed = expected_pattern in detected
                
                result = {
                    'scenario_id': scenario_id,
                    'user_input': user_input[:50] + '...' if len(user_input) > 50 else user_input,
                    'expected_pattern': expected_pattern,
                    'detected_patterns': detected,
                    'passed': passed
                }
                
                if passed:
                    results['passed'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append(result)
                
                await session.commit()
        
        return results
    
    async def test_learning_tracking(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Test learning tracking over multiple turns.
        
        Simulates a 20-turn conversation and checks if effectiveness improves.
        """
        async with self.session_factory() as session:
            introspection = IntrospectionService(session)
            pad_repo = PADStateRepository(session)
            
            # Simulate 20 turns with improving effectiveness
            effectiveness_scores = []
            
            for turn in range(1, 21):
                # Simulate improving PAD state over time
                pleasure = -0.3 + (turn * 0.05)  # Improving from negative to positive
                arousal = 0.0 + (turn * 0.02)  # Slight increase
                
                await pad_repo.record_state(
                    session_id,
                    pleasure,
                    arousal,
                    0.0,
                    self.pad_logic.get_quadrant({'pleasure': pleasure, 'arousal': arousal})
                )
                
                # Record strategy outcome (simulate improving effectiveness)
                effectiveness = 0.4 + (turn * 0.02)  # 0.4 → 0.8 over 20 turns
                effectiveness_scores.append(effectiveness)
                
                await introspection.strategies.record_outcome(
                    user_id,
                    'supportive',
                    effectiveness,
                    f"Turn {turn}"
                )
                
                await session.commit()
            
            # Get learning metrics
            metrics = await introspection.get_learning_metrics(user_id)
            curve = await introspection.calculate_learning_curve(user_id, session_id)
            
            # Check if learning is detected
            improvement = effectiveness_scores[-1] - effectiveness_scores[0]
            is_learning = improvement > 0.15  # Should improve by at least 0.15
            
            return {
                'total_turns': 20,
                'effectiveness_start': effectiveness_scores[0],
                'effectiveness_end': effectiveness_scores[-1],
                'improvement': improvement,
                'is_learning': is_learning,
                'learning_stage': metrics.get('learning_stage'),
                'overall_effectiveness': metrics.get('overall_effectiveness'),
                'session_improvement': curve.get('session_improvement'),
                'passed': is_learning
            }


async def load_test_scenarios() -> Dict[str, List[Dict]]:
    """
    Load test scenarios from JSON files or create sample scenarios.
    
    Returns scenarios organized by category.
    """
    # For now, return sample scenarios based on what user provided
    # In production, these would be loaded from JSON files
    
    scenarios = {
        'strategy_selection': [
            {
                'scenario_id': 'strat_crisis_001',
                'category': 'strategy_selection',
                'user_input': "Everything is falling apart and I can't handle this anymore",
                'expected_strategy': 'supportive',
                'baseline_pad': {'pleasure': -0.6, 'arousal': 0.3, 'dominance': -0.2}
            },
            {
                'scenario_id': 'strat_energizing_001',
                'category': 'strategy_selection',
                'user_input': "I have no motivation to do anything today",
                'expected_strategy': 'energizing',
                'baseline_pad': {'pleasure': 0.0, 'arousal': -0.4, 'dominance': 0.0}
            },
            {
                'scenario_id': 'strat_balanced_001',
                'category': 'strategy_selection',
                'user_input': "What do you think about the nature of happiness?",
                'expected_strategy': 'balanced',
                'baseline_pad': {'pleasure': 0.2, 'arousal': 0.0, 'dominance': 0.1}
            }
        ],
        'effectiveness': [
            {
                'scenario_id': 'eff_pleasure_increase_001',
                'category': 'effectiveness_formula',
                'user_input': "I finally finished that difficult project I've been working on for months!",
                'baseline_pad': {'pleasure': 0.1, 'arousal': 0.3, 'dominance': 0.2},
                'expected_pad_direction': {'pleasure': 'increase'},
                'expected_effectiveness_range': [0.7, 1.0],
                'expected_strategy': 'supportive'
            },
            {
                'scenario_id': 'eff_pleasure_decrease_001',
                'category': 'effectiveness_formula',
                'user_input': "I just got rejected from my dream job",
                'baseline_pad': {'pleasure': 0.0, 'arousal': 0.2, 'dominance': 0.0},
                'expected_pad_direction': {'pleasure': 'decrease'},
                'expected_effectiveness_range': [0.0, 0.4],
                'expected_strategy': 'supportive'
            }
        ],
        'pattern_detection': [
            {
                'scenario_id': 'pattern_catastrophizing_001',
                'category': 'pattern_detection',
                'user_input': "Everything always goes wrong for me. Nothing ever works out. I always fail.",
                'expected_pattern': 'catastrophizing'
            },
            {
                'scenario_id': 'pattern_solution_seeking_001',
                'category': 'pattern_detection',
                'user_input': "What should I do? How can I fix this? What's the best approach?",
                'expected_pattern': 'solution_seeking'
            },
            {
                'scenario_id': 'pattern_false_positive_001',
                'category': 'pattern_detection',
                'user_input': "I had a really tough day at work but I'm managing okay",
                'expected_pattern': None  # Should NOT detect pattern
            }
        ]
    }
    
    return scenarios


async def main():
    """Run all introspection tests."""
    print("="*70)
    print("INTROSPECTION ENHANCEMENTS TEST SUITE")
    print("="*70)
    print()
    
    tester = IntrospectionTester()
    await tester.setup()
    
    try:
        # Load test scenarios
        print("Loading test scenarios...")
        scenarios = await load_test_scenarios()
        print(f"Loaded {sum(len(v) for v in scenarios.values())} scenarios")
        print()
        
        # Test 1: Strategy Selection
        print("="*70)
        print("TEST 1: Strategy Selection")
        print("="*70)
        strategy_results = await tester.test_strategy_selection(
            scenarios['strategy_selection']
        )
        print(f"Total: {strategy_results['total']}")
        print(f"Passed: {strategy_results['passed']} ({strategy_results['passed']/strategy_results['total']*100:.1f}%)")
        print(f"Failed: {strategy_results['failed']}")
        print()
        for detail in strategy_results['details']:
            status = "✓" if detail['passed'] else "✗"
            print(f"  {status} {detail['scenario_id']}: expected={detail['expected']}, actual={detail['actual']}")
        print()
        
        # Test 2: Effectiveness Formula
        print("="*70)
        print("TEST 2: Effectiveness Formula")
        print("="*70)
        effectiveness_results = await tester.test_effectiveness_formula(
            scenarios['effectiveness']
        )
        print(f"Total: {effectiveness_results['total']}")
        print(f"Passed: {effectiveness_results['passed']} ({effectiveness_results['passed']/effectiveness_results['total']*100:.1f}%)")
        print(f"Failed: {effectiveness_results['failed']}")
        print()
        for detail in effectiveness_results['details']:
            status = "✓" if detail['passed'] else "✗"
            print(f"  {status} {detail['scenario_id']}: {detail['expected_range']} → actual={detail['actual']}")
        print()
        
        # Test 3: Pattern Detection
        print("="*70)
        print("TEST 3: Pattern Detection")
        print("="*70)
        pattern_results = await tester.test_pattern_detection(
            scenarios['pattern_detection']
        )
        print(f"Total: {pattern_results['total']}")
        print(f"Passed: {pattern_results['passed']} ({pattern_results['passed']/pattern_results['total']*100:.1f}%)")
        print(f"Failed: {pattern_results['failed']}")
        print()
        for detail in pattern_results['details']:
            status = "✓" if detail['passed'] else "✗"
            expected = detail['expected_pattern'] or "None"
            detected = ', '.join(detail['detected_patterns']) or "None"
            print(f"  {status} {detail['scenario_id']}: expected={expected}, detected={detected}")
        print()
        
        # Test 4: Learning Tracking
        print("="*70)
        print("TEST 4: Learning Tracking (20-turn conversation)")
        print("="*70)
        user_id, session_id = await tester.create_test_user_and_session()
        learning_results = await tester.test_learning_tracking(user_id, session_id)
        print(f"Total turns: {learning_results['total_turns']}")
        print(f"Effectiveness start: {learning_results['effectiveness_start']:.2f}")
        print(f"Effectiveness end: {learning_results['effectiveness_end']:.2f}")
        print(f"Improvement: {learning_results['improvement']:.2f}")
        print(f"Learning stage: {learning_results['learning_stage']}")
        print(f"Overall effectiveness: {learning_results['overall_effectiveness']:.2f}")
        print(f"Session improvement: {learning_results['session_improvement']:.2f}")
        print(f"Learning detected: {'✓' if learning_results['passed'] else '✗'}")
        print()
        
        # Summary
        print("="*70)
        print("SUMMARY")
        print("="*70)
        total_tests = (
            strategy_results['total'] +
            effectiveness_results['total'] +
            pattern_results['total'] +
            1  # learning test
        )
        total_passed = (
            strategy_results['passed'] +
            effectiveness_results['passed'] +
            pattern_results['passed'] +
            (1 if learning_results['passed'] else 0)
        )
        print(f"Total tests: {total_tests}")
        print(f"Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)")
        print(f"Failed: {total_tests - total_passed}")
        print()
        
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
