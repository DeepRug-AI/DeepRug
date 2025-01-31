import numpy as np
import pandas as pd
from typing import Dict, Optional
import talib
import logging
from .ml_models import MLPredictor

class SignalGenerator:
    def __init__(self):
        self.ml_predictor = MLPredictor()
        self.logger = logging.getLogger(__name__)
        
    def calculate_technical_indicators(self, ohlcv_data: pd.DataFrame) -> Dict:
        """计算技术指标"""
        try:
            close = ohlcv_data['close'].values
            high = ohlcv_data['high'].values
            low = ohlcv_data['low'].values
            volume = ohlcv_data['volume'].values
            
            # 计算移动平均
            sma_20 = talib.SMA(close, timeperiod=20)[-1]
            sma_50 = talib.SMA(close, timeperiod=50)[-1]
            ema_12 = talib.EMA(close, timeperiod=12)[-1]
            
            # 计算动量指标
            rsi = talib.RSI(close, timeperiod=14)[-1]
            macd, macd_signal, _ = talib.MACD(close)
            macd_value = macd[-1]
            macd_signal = macd_signal[-1]
            
            # 计算波动率
            atr = talib.ATR(high, low, close, timeperiod=14)[-1]
            volatility = talib.STDDEV(close, timeperiod=20)[-1]
            
            # 计算成交量指标
            obv = talib.OBV(close, volume)[-1]
            
            return {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'ema_12': ema_12,
                'rsi': rsi,
                'macd': macd_value,
                'macd_signal': macd_signal,
                'atr': atr,
                'volatility': volatility,
                'obv': obv
            }
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {str(e)}")
            return None
    
    def generate_signal(self, market_data: Dict, portfolio_value: float) -> Optional[Dict]:
        """生成交易信号"""
        try:
            if market_data is None or 'ohlcv' not in market_data:
                return None
                
            # 计算技术指标
            indicators = self.calculate_technical_indicators(market_data['ohlcv'])
            if not indicators:
                return None
            
            # 准备ML模型特征
            features = self.ml_predictor.prepare_features(indicators)
            
            # 获取ML模型预测
            signal, confidence = self.ml_predictor.predict(features)
            
            # 计算技术分析信号
            ta_signal = self._calculate_ta_signal(indicators)
            
            # 综合信号
            final_signal = self._combine_signals(signal, ta_signal, confidence)
            
            return {
                'signal': final_signal,
                'confidence': confidence,
                'indicators': indicators,
                'ml_signal': signal,
                'ta_signal': ta_signal,
                'timestamp': market_data['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error generating signal: {str(e)}")
            return None
    
    def _calculate_ta_signal(self, indicators: Dict) -> int:
        """计算技术分析信号"""
        signals = []
        
        # 移动平均趋势
        if indicators['sma_20'] > indicators['sma_50']:
            signals.append(1)
        elif indicators['sma_20'] < indicators['sma_50']:
            signals.append(-1)
        else:
            signals.append(0)
        
        # RSI信号
        if indicators['rsi'] > 70:
            signals.append(-1)  # 超买
        elif indicators['rsi'] < 30:
            signals.append(1)   # 超卖
        else:
            signals.append(0)
        
        # MACD信号
        if indicators['macd'] > indicators['macd_signal']:
            signals.append(1)
        elif indicators['macd'] < indicators['macd_signal']:
            signals.append(-1)
        else:
            signals.append(0)
        
        # 返回综合信号
        return int(np.sign(sum(signals)))
    
    def _combine_signals(self, ml_signal: int, ta_signal: int, confidence: float) -> int:
        """综合ML和技术分析信号"""
        # 如果ML置信度高，赋予更大权重
        if confidence > 0.8:
            return ml_signal
        elif confidence > 0.6:
            # ML和技术分析信号一致时保持，不一致时偏向ML信号
            return ml_signal if ml_signal == ta_signal else int(np.sign(0.7 * ml_signal + 0.3 * ta_signal))
        else:
            # ML置信度低时偏向技术分析信号
            return ta_signal