import ccxt
import numpy as np
from datetime import datetime
import logging

class TradingEngine:
    def __init__(self):
        # Initialize the exchange connection
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }
        })
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def fetch_market_data(self, symbol, timeframe='1m', limit=100):
        """Fetch market data from exchange
        
        Args:
            symbol (str): Trading pair symbol (e.g. 'BTC/USDT')
            timeframe (str): Candlestick timeframe
            limit (int): Number of candlesticks to fetch
            
        Returns:
            dict: Market data including OHLCV
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return self._process_market_data(ohlcv)
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None
    
    def _process_market_data(self, ohlcv):
        """Process raw market data into structured format
        
        Args:
            ohlcv (list): Raw OHLCV data from exchange
            
        Returns:
            dict: Processed market data
        """
        if not ohlcv:
            return None
            
        data = np.array(ohlcv)
        return {
            'timestamp': data[:, 0],
            'open': data[:, 1],
            'high': data[:, 2],
            'low': data[:, 3],
            'close': data[:, 4],
            'volume': data[:, 5]
        }
    
    def generate_trading_signal(self, market_data):
        """Generate trading signals based on market data
        
        Args:
            market_data (dict): Processed market data
            
        Returns:
            dict: Trading signal with direction and confidence
        """
        if not market_data:
            return None
            
        # Implement basic momentum strategy
        close_prices = market_data['close']
        momentum = (close_prices[-1] - close_prices[0]) / close_prices[0]
        
        # Generate signal based on momentum
        signal = {
            'timestamp': datetime.now().timestamp(),
            'direction': 'long' if momentum > 0 else 'short',
            'confidence': abs(momentum),
            'price': close_prices[-1]
        }
        
        self.logger.info(f"Generated trading signal: {signal}")
        return signal