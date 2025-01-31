import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from sklearn.metrics import precision_score, recall_score, f1_score
import joblib
import logging

class MLPredictor:
    def __init__(self):
        self.models = {
            'rf': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            'gb': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
        }
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
        self.selected_model = 'rf'
        
    def prepare_features(self, technical_indicators):
        """Prepare features for ML model"""
        try:
            # Extract basic features
            basic_features = [
                technical_indicators['sma_20'],
                technical_indicators['sma_50'],
                technical_indicators['rsi'],
                technical_indicators['volatility']
            ]
            
            # Calculate advanced features
            sma_ratio = technical_indicators['sma_20'] / technical_indicators['sma_50'] if technical_indicators['sma_50'] else 1.0
            rsi_momentum = 1 if technical_indicators['rsi'] > 50 else -1 if technical_indicators['rsi'] < 50 else 0
            volatility_factor = np.log1p(technical_indicators['volatility']) if technical_indicators['volatility'] else 0
            
            # Add MACD features
            macd_signal = 1 if technical_indicators['macd'] > technical_indicators['macd_signal'] else -1
            macd_trend = np.sign(technical_indicators['macd'])
            
            # Add volume and price features
            volume_trend = np.sign(technical_indicators['obv'])
            price_momentum = technical_indicators['close'] / technical_indicators['sma_20'] - 1
            
            # Combine all features
            features = basic_features + [
                sma_ratio,
                rsi_momentum,
                volatility_factor,
                macd_signal,
                macd_trend,
                volume_trend,
                price_momentum
            ]
            features = np.array(features).reshape(1, -1)
            
            # Handle missing values
            features = np.nan_to_num(features, nan=0.0)
            
            return self.scaler.transform(features)
        except Exception as e:
            self.logger.error(f"Error preparing features: {str(e)}")
            return None
    
    def predict(self, features):
        """Make price movement prediction with confidence score"""
        try:
            if features is None:
                return None, 0.0
                
            model = self.models[self.selected_model]
            prediction = model.predict(features)[0]
            confidence = np.max(model.predict_proba(features)[0])
            
            return prediction, confidence
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            return None, 0.0
    
    def evaluate_model(self, X, y):
        """Evaluate model performance using time series cross-validation"""
        try:
            tscv = TimeSeriesSplit(n_splits=5)
            scores = cross_val_score(self.models[self.selected_model], X, y, cv=tscv)
            
            y_pred = self.models[self.selected_model].predict(X)
            precision = precision_score(y, y_pred, average='weighted')
            recall = recall_score(y, y_pred, average='weighted')
            f1 = f1_score(y, y_pred, average='weighted')
            
            return {
                'cv_scores': scores,
                'cv_mean': scores.mean(),
                'cv_std': scores.std(),
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
        except Exception as e:
            self.logger.error(f"Error evaluating model: {str(e)}")
            return None
    
    def train(self, X, y):
        """Train the ML model with cross-validation"""
        try:
            X_scaled = self.scaler.fit_transform(X)
            
            # Perform cross-validation
            cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)
            self.logger.info(f"Cross-validation scores: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
            
            # Train final model
            self.model.fit(X_scaled, y)
            
            # Calculate performance metrics
            y_pred = self.model.predict(X_scaled)
            precision = precision_score(y, y_pred, average='weighted')
            recall = recall_score(y, y_pred, average='weighted')
            f1 = f1_score(y, y_pred, average='weighted')
            
            self.logger.info(f"Model performance - Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
    
    def save_model(self, path):
        """Save model and scaler to file"""
        try:
            model_path = f"{path}_model.joblib"
            scaler_path = f"{path}_scaler.joblib"
            
            joblib.dump(self.model, model_path)
            joblib.dump(self.scaler, scaler_path)
            self.logger.info(f"Model saved to {model_path}")
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
    
    def load_model(self, path):
        """Load model and scaler from file"""
        try:
            model_path = f"{path}_model.joblib"
            scaler_path = f"{path}_scaler.joblib"
            
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.logger.info(f"Model loaded from {model_path}")
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
    
    def update_features(self, market_data):
        """Update model features with new market data"""
        try:
            if not market_data or 'close' not in market_data:
                return False
                
            # Extract new features
            close_prices = market_data['close']
            returns = np.diff(close_prices) / close_prices[:-1]
            
            # Calculate labels for training
            future_returns = np.roll(returns, -1)
            labels = (future_returns > 0).astype(int)[:-1]
            
            # Prepare features
            features = self.prepare_features(market_data)
            if features is not None and len(labels) > 0:
                # Update model with new data
                self.model.partial_fit(features, labels)
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error updating features: {str(e)}")
            return False