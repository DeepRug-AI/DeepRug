import numpy as np
import logging
from datetime import datetime

class RiskManager:
    def __init__(self, max_position_size=0.1, max_drawdown=0.02, stop_loss=0.01):
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.stop_loss = stop_loss
        self.logger = logging.getLogger(__name__)
        self.position_history = []
        self.drawdown_history = []
        self.last_update = datetime.now()
        self.market_state = 'neutral'
        
    def calculate_position_size(self, portfolio_value, volatility, risk_score):
        """Calculate optimal position size based on dynamic risk assessment"""
        try:
            # Base position size
            base_size = portfolio_value * self.max_position_size
            
            # Dynamic volatility adjustment
            vol_factor = 1 / (1 + np.exp(volatility - 0.5))  # Sigmoid function for smooth scaling
            
            # Risk score adjustment with exponential decay
            risk_factor = np.exp(-2 * (1 - risk_score))
            
            # Market condition adjustment
            market_factor = self._assess_market_conditions()
            
            # Time decay factor
            time_factor = self._calculate_time_decay()
            
            # Calculate final position size
            position_size = base_size * vol_factor * risk_factor * market_factor * time_factor
            
            # Apply maximum position constraint
            max_allowed = portfolio_value * self.max_position_size
            position_size = min(position_size, max_allowed)
            
            self.position_history.append(position_size / portfolio_value)
            return position_size
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return 0
    
    def calculate_stop_loss(self, entry_price, position_type='long'):
        """Calculate dynamic stop loss based on market volatility and trend"""
        try:
            # Calculate ATR-based stop loss
            atr_multiplier = 2.0 if self.market_state == 'trending' else 1.5
            volatility_stop = self._calculate_atr() * atr_multiplier
            
            # Calculate percentage-based stop loss
            percent_stop = entry_price * self.stop_loss
            
            # Use the larger of the two stops
            stop_distance = max(volatility_stop, percent_stop)
            
            # Adjust stop distance based on market state
            if self.market_state == 'volatile':
                stop_distance *= 1.2
            
            if position_type == 'long':
                return entry_price - stop_distance
            else:
                return entry_price + stop_distance
        except Exception as e:
            self.logger.error(f"Error calculating stop loss: {str(e)}")
            return None
    
    def _calculate_atr(self, period=14):
        """Calculate Average True Range for dynamic stop loss"""
        try:
            if len(self.position_history) < period:
                return self.stop_loss
                
            # Calculate true range
            true_ranges = []
            for i in range(1, len(self.position_history)):
                true_range = abs(self.position_history[i] - self.position_history[i-1])
                true_ranges.append(true_range)
            
            return np.mean(true_ranges[-period:])
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {str(e)}")
            return self.stop_loss
    
    def _assess_market_conditions(self):
        """Assess current market conditions for position sizing"""
        try:
            if len(self.position_history) < 10:
                return 1.0
                
            recent_positions = self.position_history[-10:]
            trend = np.mean(np.diff(recent_positions))
            volatility = np.std(recent_positions)
            
            # Update market state
            if volatility > np.mean(self.position_history) * 1.5:
                self.market_state = 'volatile'
            elif abs(trend) > np.std(self.position_history) * 2:
                self.market_state = 'trending'
            else:
                self.market_state = 'neutral'
            
            # Calculate market factor
            if self.market_state == 'volatile':
                return 0.7  # Reduce position size in volatile markets
            elif self.market_state == 'trending':
                return 1.2 if trend > 0 else 0.8
            return 1.0
        except Exception as e:
            self.logger.error(f"Error assessing market conditions: {str(e)}")
            return 1.0
    
    def _calculate_time_decay(self):
        """Calculate time decay factor for position sizing"""
        try:
            time_diff = (datetime.now() - self.last_update).total_seconds() / 3600
            decay_factor = np.exp(-0.1 * time_diff)  # Exponential decay
            self.last_update = datetime.now()
            return max(0.5, decay_factor)
        except Exception as e:
            self.logger.error(f"Error calculating time decay: {str(e)}")
            return 1.0
    
    def validate_trade(self, portfolio_value, position_size, stop_loss_price, entry_price):
        """Comprehensive trade validation with multiple risk checks"""
        try:
            # Check position size limits
            if position_size > portfolio_value * self.max_position_size:
                return False, "Position size exceeds maximum allowed"
            
            # Calculate potential loss
            potential_loss = abs(entry_price - stop_loss_price) * position_size / entry_price
            if potential_loss > portfolio_value * self.max_drawdown:
                return False, "Potential loss exceeds maximum drawdown"
            
            # Check market state
            if self.market_state == 'volatile':
                if position_size > portfolio_value * self.max_position_size * 0.7:
                    return False, "Position size too large for volatile market"
            
            # Check recent performance
            if len(self.drawdown_history) > 0:
                recent_drawdown = np.mean(self.drawdown_history[-5:])
                if recent_drawdown > self.max_drawdown * 0.8:
                    return False, "Recent drawdown too high"
            
            return True, "Trade validated"
        except Exception as e:
            self.logger.error(f"Error validating trade: {str(e)}")
            return False, "Validation error"
    
    def update_market_state(self, market_data):
        """Update market state with new data"""
        try:
            if not market_data or 'close' not in market_data:
                return False
            
            # Calculate returns
            close_prices = market_data['close']
            if len(close_prices) < 2:
                return False
            
            returns = np.diff(close_prices) / close_prices[:-1]
            
            # Update drawdown history
            if len(returns) > 0:
                drawdown = min(0, returns[-1])
                self.drawdown_history.append(drawdown)
                
                # Keep history length manageable
                if len(self.drawdown_history) > 100:
                    self.drawdown_history = self.drawdown_history[-100:]
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating market state: {str(e)}")
            return False
    
    def _check_cumulative_risk(self, potential_loss, portfolio_value, lookback=5):
        """Check if recent cumulative risk is too high"""
        try:
            if len(self.drawdown_history) < lookback:
                return False
                
            recent_drawdowns = self.drawdown_history[-lookback:]
            cumulative_risk = sum(recent_drawdowns) + (potential_loss / portfolio_value)
            
            return cumulative_risk > self.max_drawdown * 2
        except Exception as e:
            self.logger.error(f"Error checking cumulative risk: {str(e)}")
            return True  # Conservative approach: reject trade if error