"""
A/B Testing Framework for Marcus AI.

Enables scientific validation of system improvements through
controlled experiments with real users.
"""

import uuid
import random
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from scipy import stats as scipy_stats

logger = logging.getLogger(__name__)


class VariantType(str, Enum):
    """Experiment variant types."""
    CONTROL = "control"
    TREATMENT = "treatment"


@dataclass
class ExperimentConfig:
    """Configuration for an A/B test experiment."""
    experiment_id: str
    name: str
    description: str
    control_variant: Callable  # Function that generates response
    treatment_variant: Callable  # Alternative function
    metric: str  # What to measure: 'quality', 'engagement', 'effectiveness'
    traffic_split: float = 0.5  # % of users in treatment (0.5 = 50/50)
    min_sample_size: int = 100  # Minimum samples before analysis
    significance_threshold: float = 0.05  # P-value threshold


@dataclass
class ExperimentResult:
    """Results from an A/B test."""
    experiment_id: str
    control_mean: float
    treatment_mean: float
    control_std: float
    treatment_std: float
    control_n: int
    treatment_n: int
    effect_size: float  # Cohen's d
    p_value: float
    significant: bool
    winner: Optional[str]  # 'control', 'treatment', or None
    recommendation: str


class ABTestFramework:
    """
    A/B testing framework for validating improvements.
    
    PURPOSE: Ensure all changes improve user experience, not just developer intuition.
    
    USAGE:
        # Define experiment
        experiment = ExperimentConfig(
            experiment_id="improved_sentiment_v1",
            name="Transformer Sentiment vs Keyword",
            control_variant=generate_with_keyword_sentiment,
            treatment_variant=generate_with_transformer_sentiment,
            metric="quality_score"
        )
        
        # Run experiment
        framework = ABTestFramework(db_session)
        result = await framework.run_experiment(experiment, n_samples=200)
        
        if result.significant and result.winner == 'treatment':
            print("✓ Improvement validated - deploy treatment")
        else:
            print("✗ No improvement - keep control")
    
    CRITICAL: NEVER deploy without A/B validation.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.session = db_session
        self.active_experiments: Dict[str, ExperimentConfig] = {}
    
    def register_experiment(self, config: ExperimentConfig):
        """Register a new experiment for tracking."""
        self.active_experiments[config.experiment_id] = config
        logger.info(f"Registered experiment: {config.name}")
    
    async def assign_variant(
        self,
        experiment_id: str,
        user_id: uuid.UUID
    ) -> VariantType:
        """
        Assign user to control or treatment variant.
        
        Uses consistent hashing so same user always gets same variant.
        """
        if experiment_id not in self.active_experiments:
            return VariantType.CONTROL
        
        config = self.active_experiments[experiment_id]
        
        # Consistent hashing (same user → same variant)
        hash_value = hash(f"{experiment_id}:{user_id}")
        normalized = (hash_value % 10000) / 10000.0
        
        return VariantType.TREATMENT if normalized < config.traffic_split else VariantType.CONTROL
    
    async def record_outcome(
        self,
        experiment_id: str,
        user_id: uuid.UUID,
        variant: VariantType,
        metric_value: float,
        metadata: Optional[Dict] = None
    ):
        """
        Record experiment outcome.
        
        Saves to database for later analysis.
        """
        await self.session.execute(
            """
            INSERT INTO events (session_id, event_type, event_data)
            VALUES (:user_id, 'ab_test_outcome', :data)
            """,
            {
                'user_id': user_id,
                'data': {
                    'experiment_id': experiment_id,
                    'variant': variant.value,
                    'metric_value': metric_value,
                    'metadata': metadata or {},
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        )
        
        await self.session.commit()
    
    async def analyze_experiment(
        self,
        experiment_id: str
    ) -> ExperimentResult:
        """
        Analyze experiment results with statistical testing.
        
        Returns:
            ExperimentResult with winner, significance, and recommendation
        """
        # Query results from database
        results = await self.session.execute(
            """
            SELECT 
                (event_data->>'variant')::text as variant,
                (event_data->>'metric_value')::float as value
            FROM events
            WHERE event_type = 'ab_test_outcome'
              AND (event_data->>'experiment_id')::text = :experiment_id
            """,
            {'experiment_id': experiment_id}
        )
        
        # Separate by variant
        control_values = []
        treatment_values = []
        
        for row in results:
            if row.variant == 'control':
                control_values.append(row.value)
            else:
                treatment_values.append(row.value)
        
        if len(control_values) < 30 or len(treatment_values) < 30:
            return ExperimentResult(
                experiment_id=experiment_id,
                control_mean=0.0,
                treatment_mean=0.0,
                control_std=0.0,
                treatment_std=0.0,
                control_n=len(control_values),
                treatment_n=len(treatment_values),
                effect_size=0.0,
                p_value=1.0,
                significant=False,
                winner=None,
                recommendation="Need more data (minimum 30 samples per variant)"
            )
        
        # Calculate statistics
        import numpy as np
        
        control_mean = np.mean(control_values)
        treatment_mean = np.mean(treatment_values)
        control_std = np.std(control_values)
        treatment_std = np.std(treatment_values)
        
        # T-test for significance
        t_stat, p_value = scipy_stats.ttest_ind(treatment_values, control_values)
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt((control_std**2 + treatment_std**2) / 2)
        cohens_d = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0.0
        
        # Determine winner
        config = self.active_experiments.get(experiment_id)
        threshold = config.significance_threshold if config else 0.05
        
        significant = p_value < threshold
        winner = None
        recommendation = ""
        
        if significant:
            if treatment_mean > control_mean:
                winner = "treatment"
                recommendation = f"Deploy treatment variant (improvement: {(treatment_mean - control_mean):.3f}, p={p_value:.4f})"
            else:
                winner = "control"
                recommendation = f"Keep control variant (treatment worse: {(control_mean - treatment_mean):.3f}, p={p_value:.4f})"
        else:
            recommendation = f"No significant difference (p={p_value:.4f}) - keep control, don't deploy treatment"
        
        return ExperimentResult(
            experiment_id=experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_values),
            treatment_n=len(treatment_values),
            effect_size=cohens_d,
            p_value=p_value,
            significant=significant,
            winner=winner,
            recommendation=recommendation
        )
    
    async def run_simulated_experiment(
        self,
        config: ExperimentConfig,
        test_inputs: List[str],
        n_samples: int = 100
    ) -> ExperimentResult:
        """
        Run simulated A/B test using test scenarios.
        
        Use this BEFORE production to validate improvements.
        """
        logger.info(f"Running simulated experiment: {config.name}")
        
        control_outcomes = []
        treatment_outcomes = []
        
        for i, test_input in enumerate(test_inputs[:n_samples]):
            # Assign to variant
            variant = VariantType.TREATMENT if random.random() < config.traffic_split else VariantType.CONTROL
            
            try:
                if variant == VariantType.CONTROL:
                    outcome = await config.control_variant(test_input)
                    control_outcomes.append(outcome[config.metric])
                else:
                    outcome = await config.treatment_variant(test_input)
                    treatment_outcomes.append(outcome[config.metric])
                
                logger.info(f"[{i+1}/{n_samples}] {variant.value}: {outcome[config.metric]:.3f}")
                
            except Exception as e:
                logger.error(f"Error in experiment: {e}")
                continue
        
        # Analyze results
        import numpy as np
        
        if not control_outcomes or not treatment_outcomes:
            logger.error("Insufficient data collected")
            return None
        
        control_mean = np.mean(control_outcomes)
        treatment_mean = np.mean(treatment_outcomes)
        control_std = np.std(control_outcomes)
        treatment_std = np.std(treatment_outcomes)
        
        t_stat, p_value = scipy_stats.ttest_ind(treatment_outcomes, control_outcomes)
        
        pooled_std = np.sqrt((control_std**2 + treatment_std**2) / 2)
        cohens_d = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0.0
        
        significant = p_value < config.significance_threshold
        winner = None
        
        if significant:
            winner = "treatment" if treatment_mean > control_mean else "control"
        
        recommendation = ""
        if significant and winner == "treatment":
            improvement = ((treatment_mean - control_mean) / control_mean * 100)
            recommendation = f"✓ Deploy treatment: {improvement:.1f}% improvement (p={p_value:.4f}, d={cohens_d:.2f})"
        elif significant and winner == "control":
            regression = ((control_mean - treatment_mean) / control_mean * 100)
            recommendation = f"✗ Keep control: treatment {regression:.1f}% worse (p={p_value:.4f})"
        else:
            recommendation = f"~ No significant difference (p={p_value:.4f}) - additional data needed or change too small"
        
        return ExperimentResult(
            experiment_id=config.experiment_id,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            control_std=control_std,
            treatment_std=treatment_std,
            control_n=len(control_outcomes),
            treatment_n=len(treatment_outcomes),
            effect_size=cohens_d,
            p_value=p_value,
            significant=significant,
            winner=winner,
            recommendation=recommendation
        )
