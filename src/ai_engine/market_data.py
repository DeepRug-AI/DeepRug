import ccxt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

class MarketDataCollector:
    def __init__(self, exchange_id='binance', api_key=None, api_secret=None):
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        self.logger = logging.getLogger(__name__)
        
    def fetch_historical_data(self, symbol, timeframe='1h', limit=1000):
        """获取历史K线数据"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return self._convert_to_dataframe(ohlcv)
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {str(e)}")
            return None
    
    def fetch_orderbook(self, symbol, limit=20):
        """获取市场深度数据"""
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            return {
                'bids': np.array(orderbook['bids']),
                'asks': np.array(orderbook['asks']),
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error fetching orderbook: {str(e)}")
            return None
    
    def fetch_recent_trades(self, symbol, limit=100):
        """获取最近成交数据"""
        try:
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            return pd.DataFrame(trades)
        except Exception as e:
            self.logger.error(f"Error fetching recent trades: {str(e)}")
            return None
    
    def _convert_to_dataframe(self, ohlcv):
        """将OHLCV数据转换为DataFrame格式"""
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    
    def calculate_vwap(self, trades_df):
        """计算成交量加权平均价格"""
        if trades_df is None or trades_df.empty:
            return None
        
        trades_df['vwap'] = (trades_df['price'] * trades_df['amount']).cumsum() / trades_df['amount'].cumsum()
        return trades_df['vwap'].iloc[-1]
    
    def calculate_market_impact(self, orderbook, trade_size):
        """计算市场冲击成本"""
        if orderbook is None:
            return None
            
        bids, asks = orderbook['bids'], orderbook['asks']
        
        def calculate_impact(orders, size, side='buy'):
            remaining_size = size
            total_cost = 0
            for price, volume in orders:
                if remaining_size <= 0:
                    break
                executed = min(remaining_size, volume)
                total_cost += executed * price
                remaining_size -= executed
            return total_cost / size if remaining_size <= 0 else None
        
        buy_impact = calculate_impact(asks, trade_size, 'buy')
        sell_impact = calculate_impact(bids, trade_size, 'sell')
        
        return {
            'buy_impact': buy_impact,
            'sell_impact': sell_impact
        }