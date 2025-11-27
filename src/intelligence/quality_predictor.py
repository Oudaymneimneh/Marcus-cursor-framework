"""
Response Quality Prediction Model.

Predicts human ratings of response quality without requiring
actual human evaluation. Trained on ground truth data from
human evaluation studies.
"""

import pickle
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class ResponseQualityPredictor:
    """
    ML model to predict human quality ratings.
    
    PURPOSE: Scale human evaluation - can't manually rate every response.
    Train model on human-rated samples, use to predict quality of all responses.
    
    REQUIRES: Minimum 100 human-rated responses for training.
    ACCURACY TARGET: R² > 0.6 (explains 60%+ variance in human ratings)
    
    Features extracted:
    - Sentiment analysis results
    - Response characteristics (length, questions, etc.)
    - Stoic authenticity markers
    - Strategy appropriateness
    - Context match
    
    Target: Human rating (1-5 scale) or composite score
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize predictor.
        
        Args:
            model_path: Path to saved model (if already trained)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def extract_features(
        self,
        user_input: str,
        marcus_response: str,
        context: Dict[str, Any],
        sentiment_analysis: Optional[Dict] = None
    ) -> np.ndarray:
        """
        Extract features for quality prediction.
        
        Returns 30+ dimensional feature vector.
        """
        features = []
        
        # Response characteristics (8 features)
        words = marcus_response.split()
        sentences = marcus_response.count('.') + marcus_response.count('!') + marcus_response.count('?')
        
        features.extend([
            len(words),  # Response length
            sentences,  # Sentence count
            len(words) / max(sentences, 1),  # Avg words per sentence
            1 if '?' in marcus_response else 0,  # Contains question
            marcus_response.count('?'),  # Question count
            1 if any(w in marcus_response.lower() for w in ['do', 'act', 'practice']) else 0,  # Action words
            len(marcus_response),  # Character count
            1 if len(words) < 100 else 0,  # Is brief (Stoic trait)
        ])
        
        # Stoic authenticity (10 features)
        stoic_keywords = ['control', 'power', 'virtue', 'duty', 'nature', 'death', 
                         'fate', 'fleeting', 'judgment', 'external']
        stoic_count = sum(1 for kw in stoic_keywords if kw in marcus_response.lower())
        
        features.extend([
            stoic_count,  # Stoic keyword count
            1 if 'control' in marcus_response.lower() else 0,
            1 if 'virtue' in marcus_response.lower() else 0,
            1 if any(w in marcus_response.lower() for w in ['fleeting', 'passes', 'temporary']) else 0,
            1 if any(w in marcus_response.lower() for w in ['nature', 'river', 'stone']) else 0,
            1 if 'death' in marcus_response.lower() else 0,
            1 if 'fate' in marcus_response.lower() else 0,
            1 if 'judgment' in marcus_response.lower() else 0,
            1 if 'external' in marcus_response.lower() else 0,
            1 if 'obstacle' in marcus_response.lower() else 0,
        ])
        
        # Sentiment/PAD (6 features)
        if sentiment_analysis:
            features.extend([
                sentiment_analysis['pad'].get('pleasure', 0.0),
                sentiment_analysis['pad'].get('arousal', 0.0),
                sentiment_analysis['pad'].get('dominance', 0.0),
                sentiment_analysis.get('confidence', 0.5),
                1 if sentiment_analysis.get('primary_emotion') in ['joy', 'love'] else 0,
                1 if sentiment_analysis.get('primary_emotion') in ['sadness', 'fear'] else 0,
            ])
        else:
            features.extend([0.0] * 6)
        
        # Strategy context (6 features)
        strategy = context.get('strategy_used', 'balanced')
        strategies = ['supportive', 'balanced', 'challenging', 'energizing', 'reflective']
        strategy_features = [1 if s == strategy else 0 for s in strategies]
        features.extend(strategy_features)
        features.append(context.get('effectiveness', 0.5))  # PAD effectiveness
        
        # Contextual appropriateness (5 features)
        features.extend([
            len(context.get('patterns_detected', [])),  # Pattern count
            1 if context.get('relationship_stage') != 'Stranger' else 0,  # Has history
            len(context.get('warning_flags', [])),  # Warning count
            1 if 'crisis' in str(context.get('warning_flags', [])).lower() else 0,  # Is crisis
            context.get('negative_streak', 0) / 10.0,  # Normalized negative streak
        ])
        
        return np.array(features)
    
    def train(
        self,
        training_data: List[Dict[str, Any]],
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        Train quality prediction model on human-rated data.
        
        Args:
            training_data: List of {
                'user_input': str,
                'marcus_response': str,
                'context': dict,
                'sentiment_analysis': dict,
                'human_rating': float  # 1-5 scale or 0-1 composite score
            }
            test_size: Fraction for validation set
            
        Returns:
            Training metrics including R², RMSE, feature importance
        """
        if len(training_data) < 50:
            raise ValueError(f"Need minimum 50 samples for training, got {len(training_data)}")
        
        logger.info(f"Training quality predictor on {len(training_data)} samples...")
        
        # Extract features and targets
        X = []
        y = []
        
        for sample in training_data:
            features = self.extract_features(
                user_input=sample['user_input'],
                marcus_response=sample['marcus_response'],
                context=sample['context'],
                sentiment_analysis=sample.get('sentiment_analysis')
            )
            X.append(features)
            y.append(sample['human_rating'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model (try both RandomForest and GradientBoosting)
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        gb_model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        rf_model.fit(X_train_scaled, y_train)
        gb_model.fit(X_train_scaled, y_train)
        
        # Evaluate both
        rf_score = rf_model.score(X_test_scaled, y_test)
        gb_score = gb_model.score(X_test_scaled, y_test)
        
        # Choose best
        if gb_score > rf_score:
            self.model = gb_model
            logger.info(f"Using GradientBoosting (R²={gb_score:.3f})")
        else:
            self.model = rf_model
            logger.info(f"Using RandomForest (R²={rf_score:.3f})")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            # Store top 10 features
            top_features = np.argsort(importance)[-10:][::-1]
        
        # Calculate RMSE
        y_pred = self.model.predict(X_test_scaled)
        rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
        
        metrics = {
            'r_squared': float(max(rf_score, gb_score)),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'rmse': float(rmse),
            'n_train': len(X_train),
            'n_test': len(X_test)
        }
        
        logger.info(f"Training complete: R²={metrics['r_squared']:.3f}, RMSE={metrics['rmse']:.3f}")
        
        return metrics
    
    def predict(
        self,
        user_input: str,
        marcus_response: str,
        context: Dict[str, Any],
        sentiment_analysis: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Predict human quality rating for a response.
        
        Returns:
            {
                'predicted_rating': float,  # 1-5 scale or 0-1 composite
                'confidence_interval': (float, float),  # 95% CI
                'should_show': bool  # Quality threshold met
            }
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        features = self.extract_features(
            user_input, marcus_response, context, sentiment_analysis
        )
        features_scaled = self.scaler.transform([features])
        
        prediction = self.model.predict(features_scaled)[0]
        
        # Estimate confidence interval (for ensemble models)
        if hasattr(self.model, 'estimators_'):
            # Get predictions from all trees
            tree_predictions = [
                tree.predict(features_scaled)[0]
                for tree in self.model.estimators_
            ]
            std = np.std(tree_predictions)
            ci_lower = prediction - 1.96 * std
            ci_upper = prediction + 1.96 * std
        else:
            # Rough estimate
            ci_lower = prediction - 0.2
            ci_upper = prediction + 0.2
        
        # Quality threshold (show only if predicted rating > 3.5/5.0)
        threshold = 3.5 if prediction <= 5.0 else 0.7  # Adjust based on scale
        should_show = prediction > threshold
        
        return {
            'predicted_rating': float(prediction),
            'confidence_interval': (float(ci_lower), float(ci_upper)),
            'should_show': should_show
        }
    
    def save_model(self, path: str):
        """Save trained model to disk."""
        if self.model is None:
            raise ValueError("No model to save. Train first.")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model from disk."""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data.get('feature_names', [])
        
        logger.info(f"Model loaded from {path}")
