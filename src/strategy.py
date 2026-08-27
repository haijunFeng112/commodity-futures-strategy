"""
策略基类模块
定义所有策略应该继承的基类
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Any


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str = "BaseStrategy"):
        """
        初始化策略
        
        Args:
            name: 策略名称
        """
        self.name = name
        self.data = None
        self.signals = None
        self.positions = None
    
    def set_data(self, data: pd.DataFrame) -> None:
        """
        设置策略数据
        
        Args:
            data: OHLCV数据
        """
        self.data = data.copy()
    
    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """
        生成交易信号
        
        Returns:
            包含信号列的DataFrame
            1: 买入信号
            0: 不操作
            -1: 卖出信号
        """
        pass
    
    def get_signals(self) -> pd.DataFrame:
        """获取交易信号"""
        if self.signals is None:
            self.signals = self.generate_signals()
        return self.signals
    
    def validate(self) -> bool:
        """
        验证策略有效性
        
        Returns:
            策略是否有效
        """
        if self.data is None or len(self.data) == 0:
            print("错误: 未设置数据")
            return False
        
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing = [col for col in required_columns if col not in self.data.columns]
        if missing:
            print(f"错误: 缺少必要列 {missing}")
            return False
        
        return True
    
    def __str__(self) -> str:
        """策略字符串表示"""
        return f"Strategy: {self.name}"


class TrendFollowingStrategy(BaseStrategy):
    """趋势跟踪策略基类"""
    
    def __init__(self, name: str = "TrendFollowing", 
                 fast_ma: int = 10, slow_ma: int = 30):
        """
        初始化趋势跟踪策略
        
        Args:
            name: 策略名称
            fast_ma: 快线周期
            slow_ma: 慢线周期
        """
        super().__init__(name)
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
    
    def generate_signals(self) -> pd.DataFrame:
        """
        生成趋势跟踪信号
        基于快线和慢线的交叉
        
        Returns:
            包含信号的DataFrame
        """
        if not self.validate():
            return None
        
        df = self.data.copy()
        
        # 计算移动平均线
        df['MA_Fast'] = df['close'].rolling(window=self.fast_ma).mean()
        df['MA_Slow'] = df['close'].rolling(window=self.slow_ma).mean()
        
        # 生成信号
        df['Signal'] = 0
        
        # 快线上穿慢线：买入信号
        df.loc[df['MA_Fast'] > df['MA_Slow'], 'Signal'] = 1
        
        # 快线下穿慢线：卖出信号
        df.loc[df['MA_Fast'] < df['MA_Slow'], 'Signal'] = -1
        
        # 提取交叉点
        df['Position'] = df['Signal'].shift(1)  # 前一个周期的信号作为当前持仓
        df['Signal_Change'] = df['Signal'].diff()
        
        self.signals = df
        return df


class MACDStrategy(BaseStrategy):
    """MACD策略基类"""
    
    def __init__(self, name: str = "MACD",
                 fast: int = 12, slow: int = 26, signal: int = 9):
        """
        初始化MACD策略
        
        Args:
            name: 策略名称
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
        """
        super().__init__(name)
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signals(self) -> pd.DataFrame:
        """
        生成MACD信号
        
        Returns:
            包含信号的DataFrame
        """
        if not self.validate():
            return None
        
        df = self.data.copy()
        
        # 计算MACD
        exp1 = df['close'].ewm(span=self.fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=self.slow, adjust=False).mean()
        
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=self.signal, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # 生成信号
        df['Signal'] = 0
        
        # MACD上穿信号线：买入
        df.loc[df['MACD'] > df['MACD_Signal'], 'Signal'] = 1
        
        # MACD下穿信号线：卖出
        df.loc[df['MACD'] < df['MACD_Signal'], 'Signal'] = -1
        
        # 额外条件：只在MACD_Histogram为正时买入
        df.loc[df['MACD_Histogram'] < 0, 'Signal'] = 0
        
        df['Position'] = df['Signal'].shift(1)
        df['Signal_Change'] = df['Signal'].diff()
        
        self.signals = df
        return df


class BollingerBandsStrategy(BaseStrategy):
    """布林线策略基类"""
    
    def __init__(self, name: str = "BollingerBands",
                 period: int = 20, std: float = 2.0):
        """
        初始化布林线策略
        
        Args:
            name: 策略名称
            period: 周期
            std: 标准差倍数
        """
        super().__init__(name)
        self.period = period
        self.std = std
    
    def generate_signals(self) -> pd.DataFrame:
        """
        生成布林线信号
        价格触及下轨买入，触及上轨卖出
        
        Returns:
            包含信号的DataFrame
        """
        if not self.validate():
            return None
        
        df = self.data.copy()
        
        # 计算布林线
        sma = df['close'].rolling(window=self.period).mean()
        stdev = df['close'].rolling(window=self.period).std()
        
        df['BB_Upper'] = sma + (stdev * self.std)
        df['BB_Middle'] = sma
        df['BB_Lower'] = sma - (stdev * self.std)
        
        # 生成信号
        df['Signal'] = 0
        
        # 价格触及下轨：买入
        df.loc[df['close'] <= df['BB_Lower'], 'Signal'] = 1
        
        # 价格触及上轨：卖出
        df.loc[df['close'] >= df['BB_Upper'], 'Signal'] = -1
        
        df['Position'] = df['Signal'].shift(1)
        df['Signal_Change'] = df['Signal'].diff()
        
        self.signals = df
        return df
