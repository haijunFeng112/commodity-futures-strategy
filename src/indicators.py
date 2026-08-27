"""
技术指标模块
提供各种技术指标的计算
"""

import pandas as pd
import numpy as np


class TechnicalIndicators:
    """技术指标计算类"""
    
    def __init__(self, data: pd.DataFrame):
        """
        初始化技术指标计算器
        
        Args:
            data: 包含OHLCV数据的DataFrame
        """
        self.data = data.copy()
    
    def calculate_ma(self, period: int = 20, column: str = 'close') -> pd.Series:
        """
        计算简单移动平均线 (SMA)
        
        Args:
            period: 周期
            column: 计算列名
            
        Returns:
            移动平均线Series
        """
        ma = self.data[column].rolling(window=period).mean()
        self.data[f'MA{period}'] = ma
        return ma
    
    def calculate_ema(self, period: int = 20, column: str = 'close') -> pd.Series:
        """
        计算指数移动平均线 (EMA)
        
        Args:
            period: 周期
            column: 计算列名
            
        Returns:
            指数移动平均线Series
        """
        ema = self.data[column].ewm(span=period, adjust=False).mean()
        self.data[f'EMA{period}'] = ema
        return ema
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, 
                      signal: int = 9, column: str = 'close') -> dict:
        """
        计算MACD指标
        
        Args:
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
            column: 计算列名
            
        Returns:
            包含MACD、Signal、Histogram的字典
        """
        exp1 = self.data[column].ewm(span=fast, adjust=False).mean()
        exp2 = self.data[column].ewm(span=slow, adjust=False).mean()
        
        macd = exp1 - exp2
        signal = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal
        
        self.data['MACD'] = macd
        self.data['MACD_Signal'] = signal
        self.data['MACD_Histogram'] = histogram
        
        return {
            'MACD': macd,
            'Signal': signal,
            'Histogram': histogram
        }
    
    def calculate_rsi(self, period: int = 14, column: str = 'close') -> pd.Series:
        """
        计算相对强度指数 (RSI)
        
        Args:
            period: 周期
            column: 计算列名
            
        Returns:
            RSI Series
        """
        delta = self.data[column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        self.data[f'RSI{period}'] = rsi
        return rsi
    
    def calculate_bollinger_bands(self, period: int = 20, std: float = 2.0,
                                 column: str = 'close') -> dict:
        """
        计算布林线 (Bollinger Bands)
        
        Args:
            period: 周期
            std: 标准差倍数
            column: 计算列名
            
        Returns:
            包含upper, middle, lower的字典
        """
        sma = self.data[column].rolling(window=period).mean()
        stdev = self.data[column].rolling(window=period).std()
        
        upper = sma + (stdev * std)
        lower = sma - (stdev * std)
        
        self.data['BB_Upper'] = upper
        self.data['BB_Middle'] = sma
        self.data['BB_Lower'] = lower
        
        return {
            'Upper': upper,
            'Middle': sma,
            'Lower': lower
        }
    
    def calculate_atr(self, period: int = 14) -> pd.Series:
        """
        计算平均真实波幅 (Average True Range)
        
        Args:
            period: 周期
            
        Returns:
            ATR Series
        """
        high = self.data['high']
        low = self.data['low']
        close = self.data['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        self.data[f'ATR{period}'] = atr
        return atr
    
    def calculate_adx(self, period: int = 14) -> dict:
        """
        计算平均方向指数 (ADX)
        
        Args:
            period: 周期
            
        Returns:
            包含DI+, DI-, ADX的字典
        """
        high = self.data['high']
        low = self.data['low']
        close = self.data['close']
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr = self.calculate_atr(period)
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr)
        
        di_diff = abs(plus_di - minus_di)
        di_sum = plus_di + minus_di
        dx = 100 * (di_diff / di_sum)
        adx = dx.rolling(window=period).mean()
        
        self.data['Plus_DI'] = plus_di
        self.data['Minus_DI'] = minus_di
        self.data['ADX'] = adx
        
        return {
            'Plus_DI': plus_di,
            'Minus_DI': minus_di,
            'ADX': adx
        }
    
    def calculate_stochastic(self, period: int = 14, k_period: int = 3,
                            d_period: int = 3) -> dict:
        """
        计算随机指标 (Stochastic)
        
        Args:
            period: 周期
            k_period: K线平滑周期
            d_period: D线平滑周期
            
        Returns:
            包含K, D的字典
        """
        low_min = self.data['low'].rolling(window=period).min()
        high_max = self.data['high'].rolling(window=period).max()
        
        k_percent = 100 * ((self.data['close'] - low_min) / (high_max - low_min))
        k = k_percent.rolling(window=k_period).mean()
        d = k.rolling(window=d_period).mean()
        
        self.data['Stochastic_K'] = k
        self.data['Stochastic_D'] = d
        
        return {
            'K': k,
            'D': d
        }
    
    def get_data(self) -> pd.DataFrame:
        """获取计算后的数据"""
        return self.data
    
    def get_indicator(self, name: str) -> pd.Series:
        """
        获取指定指标
        
        Args:
            name: 指标名称
            
        Returns:
            指标Series
        """
        if name in self.data.columns:
            return self.data[name]
        else:
            print(f"警告: 指标 {name} 不存在")
            return None
