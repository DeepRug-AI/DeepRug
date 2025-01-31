import ccxt
import numpy as np
from datetime import datetime
import logging
from .ml_models import MLPredictor
from .risk_manager import RiskManager
from .market_data import MarketDataCollector

class TradingEngine:
    def __init__(self, api_key=None, api_secret=None):
        # Initialize market data collector
        self.market_data = MarketDataCollector(api_key=api_key, api_secret=api_secret)
        
        # Initialize ML predictor and risk manager
        self.ml_predictor = MLPredictor()
        self.risk_manager = RiskManager()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Trading state
        self.active_positions = {}
        self.pending_orders = {}
    
    def fetch_market_data(self, symbol, timeframe='1m', limit=100):
        """Fetch comprehensive market data"""
        try:
            # Fetch OHLCV data
            ohlcv_data = self.market_data.fetch_historical_data(symbol, timeframe, limit)
            if ohlcv_data is None:
                return None
                
            # Fetch orderbook
            orderbook = self.market_data.fetch_orderbook(symbol)
            
            # Fetch recent trades
            trades = self.market_data.fetch_recent_trades(symbol)
            
            # Calculate VWAP
            vwap = self.market_data.calculate_vwap(trades)
            
            return {
                'ohlcv': ohlcv_data,
                'orderbook': orderbook,
                'vwap': vwap,
                'timestamp': datetime.now().timestamp()
            }
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None
    
    def generate_trading_signal(self, market_data, portfolio_value):
        """Generate comprehensive trading signal"""
        try:
            if market_data is None:
                return None
            
            # Calculate technical indicators
            indicators = self.calculate_technical_indicators(market_data['ohlcv'])
            if not indicators:
                return None
            
            # Add market microstructure features
            if market_data['orderbook']:
                trade_size = portfolio_value * 0.01  # 1% of portfolio for impact calculation
                impact = self.market_data.calculate_market_impact(market_data['orderbook'], trade_size)
                indicators.update({
                    'buy_impact': impact['buy_impact'] if impact else None,
                    'sell_impact': impact['sell_impact'] if impact else None,
                    'vwap': market_data['vwap']
                })
            
            # Prepare features for ML model
            features = self.ml_predictor.prepare_features(indicators)
            
            # Get prediction and confidence
            signal, confidence = self.ml_predictor.predict(features)
            
            # Calculate position size based on risk management
            position_size = self.risk_manager.calculate_position_size(
                portfolio_value,
                indicators['volatility'],
                confidence
            )
            
            # Calculate stop loss and take profit levels
            current_price = market_data['ohlcv']['close'].iloc[-1]
            stop_loss = self.risk_manager.calculate_stop_loss(
                current_price,
                'long' if signal > 0 else 'short'
            )
            
            return {
                'signal': signal,  # 1 for long, -1 for short, 0 for neutral
                'confidence': confidence,
                'position_size': position_size,
                'stop_loss': stop_loss,
                'indicators': indicators,
                'timestamp': market_data['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error generating trading signal: {str(e)}")
            return None
    
    def execute_trade(self, symbol, signal):
        """Execute trade based on signal"""
        try:
            if not signal or signal['signal'] == 0:
                return False
                
            # Validate trade with risk manager
            trade_valid, reason = self.risk_manager.validate_trade(
                portfolio_value=self.get_portfolio_value(),
                position_size=signal['position_size'],
                stop_loss_price=signal['stop_loss'],
                entry_price=signal['indicators']['close'][-1]
            )
            
            if not trade_valid:
                self.logger.warning(f"Trade validation failed: {reason}")
                return False
            
            # Place order logic here
            order_type = 'market'
            side = 'buy' if signal['signal'] > 0 else 'sell'
            
            self.logger.info(f"Executing {side} order for {symbol} with size {signal['position_size']}")
            
            # Update position tracking
            self.active_positions[symbol] = {
                'side': side,
                'size': signal['position_size'],
                'entry_price': signal['indicators']['close'][-1],
                'stop_loss': signal['stop_loss'],
                'timestamp': signal['timestamp']
            }
            
            return True
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
            return False
    
    def get_portfolio_value(self):
        """Get current portfolio value"""
        # Implement portfolio value calculation
        return 10000  # Placeholder value

    def calculate_technical_indicators(self, market_data):
        """Calculate technical indicators for trading decisions"""
        if not market_data:
            return None
            
        close_prices = market_data['close']
        high_prices = market_data['high']
        low_prices = market_data['low']
        
        # Calculate SMA
        sma_20 = np.mean(close_prices[-20:]) if len(close_prices) >= 20 else None
        sma_50 = np.mean(close_prices[-50:]) if len(close_prices) >= 50 else None
        
        # Calculate RSI
        delta = np.diff(close_prices)
        gain = (delta > 0) * delta
        loss = (delta < 0) * -delta
        avg_gain = np.mean(gain[-14:]) if len(gain) >= 14 else None
        avg_loss = np.mean(loss[-14:]) if len(loss) >= 14 else None
        
        if avg_gain is not None and avg_loss is not None and avg_loss != 0:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = None
        
        # Calculate volatility
        volatility = np.std(np.diff(np.log(close_prices[-20:]))) if len(close_prices) >= 20 else None
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'rsi': rsi,
            'volatility': volatility
        }
    
    def generate_trading_signal(self, market_data):
        """Generate trading signal based on market data and ML predictions"""
        try:
            # Calculate technical indicators
            indicators = self.calculate_technical_indicators(market_data)
            if not indicators:
                return None
            
            # Prepare features for ML model
            features = self.ml_predictor.prepare_features(indicators)
            
            # Get prediction and confidence
            signal, confidence = self.ml_predictor.predict(features)
            
            # Calculate position size based on risk management
            position_size = self.risk_manager.calculate_position_size(
                portfolio_value=100000,  # Default portfolio value
                volatility=indicators['volatility'],
                risk_score=confidence
            )
            
            # Generate final trading signal
            if signal != 0 and position_size > 0:
                stop_loss = self.risk_manager.calculate_stop_loss(
                    entry_price=market_data['close'][-1],
                    position_type='long' if signal > 0 else 'short'
                )
                
                return {
                    'symbol': market_data.get('symbol'),
                    'signal': signal,  # 1 for long, -1 for short, 0 for neutral
                    'confidence': confidence,
                    'position_size': position_size,
                    'stop_loss': stop_loss,
                    'indicators': indicators,
                    'timestamp': datetime.now().timestamp()
                }
            
            return None
        except Exception as e:
            self.logger.error(f"Error generating trading signal: {str(e)}")
            return None
    
    def validate_signal(self, signal_data):
        """Validate trading signal with risk management rules"""
        if not signal_data:
            return False
            
        try:
            # Validate trade with risk manager
            is_valid, reason = self.risk_manager.validate_trade(
                portfolio_value=100000,  # Default portfolio value
                position_size=signal_data['position_size'],
                stop_loss_price=signal_data['stop_loss'],
                entry_price=signal_data['indicators']['close'][-1]
            )
            
            if not is_valid:
                self.logger.warning(f"Trade validation failed: {reason}")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error validating signal: {str(e)}")
            return False
    
    def update_market_state(self, market_data):
        """Update internal market state with new data"""
        try:
            # Update risk manager with new market data
            self.risk_manager.update_market_state(market_data)
            
            # Update ML model features
            self.ml_predictor.update_features(market_data)
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating market state: {str(e)}")
            return False
            
            return {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'rsi': rsi
            }
        return None
        
    def generate_trading_signal(self, market_data):
        """Generate trading signals based on market data and technical analysis
        
        Args:
            market_data (dict): Processed market data
            
        Returns:
            dict: Trading signal with direction and confidence
        """
        if not market_data:
            return None
            
        # Calculate technical indicators
        indicators = self.calculate_technical_indicators(market_data)
        if not indicators:
            return None
            
        # Get ML prediction
        features = self.ml_predictor.prepare_features(indicators)
        prediction = self.ml_predictor.predict(features)
        
        # Calculate volatility
        close_prices = market_data['close']
        returns = np.diff(close_prices) / close_prices[:-1]
        volatility = np.std(returns)
        
        # Generate signal
        signal = {
            'timestamp': datetime.now().timestamp(),
            'symbol': market_data.get('symbol'),
            'direction': 'buy' if prediction == 1 else 'sell' if prediction == -1 else None,
            'confidence': abs(prediction),
            'volatility': volatility,
            'indicators': indicators
        }
        
        # Validate signal with risk management
        if signal['direction']:
            portfolio_value = self.get_portfolio_value()
            position_size = self.risk_manager.calculate_position_size(
                portfolio_value,
                volatility,
                signal['confidence']
            )
            
            current_price = close_prices[-1]
            stop_loss = self.risk_manager.calculate_stop_loss(
                current_price,
                'long' if signal['direction'] == 'buy' else 'short'
            )
            
            is_valid, reason = self.risk_manager.validate_trade(
                portfolio_value,
                position_size,
                stop_loss,
                current_price
            )
            
            if not is_valid:
                self.logger.warning(f"Trade validation failed: {reason}")
                return None
                
            signal['position_size'] = position_size
            signal['stop_loss'] = stop_loss
        
        return signal if signal['direction'] else None

    def get_portfolio_value(self):
        """Get current portfolio value
        
        Returns:
            float: Total portfolio value in USDT
        """
        try:
            balance = self.exchange.fetch_balance()
            return float(balance['total']['USDT'])
        except Exception as e:
            self.logger.error(f"Error fetching portfolio value: {str(e)}")
            return 0.0
        # Trading logic based on multiple indicators
        close_prices = market_data['close']
        current_price = close_prices[-1]
        
        # Trend following strategy
        trend_signal = 'long' if indicators['sma_20'] > indicators['sma_50'] else 'short'
        
        # RSI strategy
        rsi_signal = None
        if indicators['rsi'] is not None:
            if indicators['rsi'] < 30:
                rsi_signal = 'long'  # Oversold
            elif indicators['rsi'] > 70:
                rsi_signal = 'short'  # Overbought
        
        # Combine signals
        final_direction = trend_signal
        if rsi_signal and rsi_signal != trend_signal:
            # If RSI contradicts trend, reduce confidence
            confidence = 0.5
        else:
            confidence = 0.8
        
        signal = {
            'timestamp': datetime.now().timestamp(),
            'direction': final_direction,
            'confidence': confidence,
            'price': current_price,
            'indicators': indicators
        }
        
        self.logger.info(f"Generated trading signal: {signal}")
        return signal