"""
趋势跟踪策略实现
基于移动平均线的经典趋势跟踪策略
"""

import pandas as pd
import numpy as np
from src.strategy import BaseStrategy
from src.indicators import TechnicalIndicators


class AdvancedTrendFollowingStrategy(BaseStrategy):
    """高级趋势跟踪策略"""
    
    def __init__(self, name: str = "Advanced Trend Following",
                 fast_ma: int = 10, slow_ma: int = 30,
                 use_macd: bool = True, use_rsi: bool = True):
        """
        初始化高级趋势跟踪策略
        
        Args:
            name: 策略名称
            fast_ma: 快线周期
            slow_ma: 慢线周期
            use_macd: 是否使用MACD
            use_rsi: 是否使用RSI
        """
        super().__init__(name)
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.use_macd = use_macd
        self.use_rsi = use_rsi
    
    def generate_signals(self) -> pd.DataFrame:
        """
        生成高级趋势跟踪信号
        
        综合考虑：
        1. 双均线交叉
        2. MACD指标（可选）
        3. RSI指标（可选）
        
        Returns:
            包含信号的DataFrame
        """
        if not self.validate():
            return None
        
        df = self.data.copy()
        indicators = TechnicalIndicators(df)
        
        # 计算移动平均线
        indicators.calculate_ma(self.fast_ma)
        indicators.calculate_ma(self.slow_ma)
        
        df = indicators.get_data()
        
        # 基础信号：双均线交叉
        df['MA_Trend'] = 0
        df.loc[df[f'MA{self.fast_ma}'] > df[f'MA{self.slow_ma}'], 'MA_Trend'] = 1
        df.loc[df[f'MA{self.fast_ma}'] < df[f'MA{self.slow_ma}'], 'MA_Trend'] = -1
        
        # 初始化综合信号
        df['Signal'] = df['MA_Trend']
        
        # 可选：使用MACD进行过滤
        if self.use_macd:
            macd_dict = indicators.calculate_macd()
            df = indicators.get_data()
            
            # MACD确认信号
            df['MACD_Signal'] = 0
            df.loc[df['MACD'] > df['MACD_Signal'], 'MACD_Signal'] = 1
            df.loc[df['MACD'] < df['MACD_Signal'], 'MACD_Signal'] = -1
            
            # 信号确认：只有在MACD和MA都同向时才生成信号
            df['Signal'] = df['Signal'] * (df['MACD_Signal'] == df['MA_Trend']).astype(int)
        
        # 可选：使用RSI进行过滤
        if self.use_rsi:
            rsi = indicators.calculate_rsi(period=14)
            df = indicators.get_data()
            
            # RSI 过度买入/卖出过滤
            # 如果RSI > 70（过度买入），不生成买入信号
            # 如果RSI < 30（过度卖出），不生成卖出信号
            df.loc[df['RSI14'] > 70, 'Signal'] = 0
            df.loc[df['RSI14'] < 30, 'Signal'] = 0
        
        # 填充NaN值
        df['Signal'] = df['Signal'].fillna(0)
        df['Signal'] = df['Signal'].astype(int)
        
        # 提取信号变化
        df['Signal_Change'] = df['Signal'].diff()
        df['Position'] = df['Signal'].shift(1)
        
        self.signals = df
        return df


class SimpleMovingAverageCrossover(BaseStrategy):
    """简单移动平均线交叉策略"""
    
    def __init__(self, name: str = "SMA Crossover",
                 fast_ma: int = 10, slow_ma: int = 30):
        """
        初始化简单MA交叉策略
        
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
        生成简单MA交叉信号
        
        逻辑：
        - 快线 > 慢线：买入信号
        - 快线 < 慢线：卖出信号
        
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
        df.loc[df['MA_Fast'] > df['MA_Slow'], 'Signal'] = 1
        df.loc[df['MA_Fast'] < df['MA_Slow'], 'Signal'] = -1
        
        # 检测交叉点
        df['MA_Cross'] = df['Signal'].diff()  # 交叉点处diff不为0
        
        # 处理NaN
        df['Signal'] = df['Signal'].fillna(0).astype(int)
        
        df['Position'] = df['Signal'].shift(1)
        df['Signal_Change'] = df['Signal'].diff()
        
        self.signals = df
        return df


class ExponentialMovingAverageCrossover(BaseStrategy):
    """指数移动平均线交叉策略"""
    
    def __init__(self, name: str = "EMA Crossover",
                 fast_ema: int = 12, slow_ema: int = 26):
        """
        初始化EMA交叉策略
        
        Args:
            name: 策略名称
            fast_ema: 快线周期
            slow_ema: 慢线周期
        """
        super().__init__(name)
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
    
    def generate_signals(self) -> pd.DataFrame:
        """
        生成EMA交叉信号
        
        EMA对近期价格更敏感，相比SMA反应更快
        
        Returns:
            包含信号的DataFrame
        """
        if not self.validate():
            return None
        
        df = self.data.copy()
        indicators = TechnicalIndicators(df)
        
        # 计算指数移动平均线
        indicators.calculate_ema(self.fast_ema)
        indicators.calculate_ema(self.slow_ema)
        
        df = indicators.get_data()
        
        # 生成信号
        df['Signal'] = 0
        df.loc[df[f'EMA{self.fast_ema}'] > df[f'EMA{self.slow_ema}'], 'Signal'] = 1
        df.loc[df[f'EMA{self.fast_ema}'] < df[f'EMA{self.slow_ema}'], 'Signal'] = -1
        
        df['Signal'] = df['Signal'].fillna(0).astype(int)
        df['Position'] = df['Signal'].shift(1)
        df['Signal_Change'] = df['Signal'].diff()
        
        self.signals = df
        return df


class TrendFollowingWithATR(BaseStrategy):
    """基于ATR的趋势跟踪策略"""
    
    def __init__(self, name: str = "Trend Following with ATR",
                 fast_ma: int = 10, slow_ma: int = 30,
                 atr_period: int = 14, atr_multiplier: float = 2.0):
        """
        初始化基于ATR的趋势策略
        
        Args:
            name: 策略名称
            fast_ma: 快线周期
            slow_ma: 慢线周期
            atr_period: ATR周期
            atr_multiplier: ATR倍数（用于止损/止盈）
        """
        super().__init__(name)
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
    
    def generate_signals(self) -> pd.DataFrame:
        """
        生成基于ATR的趋势信号
        
        综合MA趋势和ATR波动率
        
        Returns:
            包含信号的DataFrame
        """
        if not self.validate():
            return None
        
        df = self.data.copy()
        indicators = TechnicalIndicators(df)
        
        # 计算指标
        indicators.calculate_ma(self.fast_ma)
        indicators.calculate_ma(self.slow_ma)
        atr = indicators.calculate_atr(self.atr_period)
        
        df = indicators.get_data()
        
        # 基础趋势信号
        df['Trend'] = 0
        df.loc[df[f'MA{self.fast_ma}'] > df[f'MA{self.slow_ma}'], 'Trend'] = 1
        df.loc[df[f'MA{self.fast_ma}'] < df[f'MA{self.slow_ma}'], 'Trend'] = -1
        
        # 考虑波动率
        df['Signal'] = 0
        
        # 上升趋势且波动率不过高
        high_volatility = df[f'ATR{self.atr_period}'] > df['close'] * 0.05
        df.loc[(df['Trend'] == 1) & ~high_volatility, 'Signal'] = 1
        
        # 下降趋势且波动率不过高
        df.loc[(df['Trend'] == -1) & ~high_volatility, 'Signal'] = -1
        
        df['Signal'] = df['Signal'].fillna(0).astype(int)
        df['Position'] = df['Signal'].shift(1)
        df['Signal_Change'] = df['Signal'].diff()
        
        self.signals = df
        return df


class MomentumTrendFollowing(BaseStrategy):
    """动量趋势跟踪策略"""
    
    def __init__(self, name: str = "Momentum Trend Following",
                 fast_ma: int = 10, slow_ma: int = 30,
                 momentum_period: int = 12):
        """
        初始化动量趋势策略
        
        Args:
            name: 策略名称
            fast_ma: 快线周期
            slow_ma: 慢线周期
            momentum_period: 动量周期
        """
        super().__init__(name)
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.momentum_period = momentum_period
    
    def generate_signals(self) -> pd.DataFrame:
        """
        生成动量趋势信号
        
        结合趋势方向和价格动量
        
        Returns:
            包含信号的DataFrame
        """
        if not self.validate():
            return None
        
        df = self.data.copy()
        
        # 计算MA趋势
        df['MA_Fast'] = df['close'].rolling(window=self.fast_ma).mean()
        df['MA_Slow'] = df['close'].rolling(window=self.slow_ma).mean()
        
        # 计算动量（价格变化）
        df['Momentum'] = df['close'] - df['close'].shift(self.momentum_period)
        
        # 生成信号
        df['Signal'] = 0
        
        # 上升趋势 + 正动量 = 买入
        df.loc[(df['MA_Fast'] > df['MA_Slow']) & (df['Momentum'] > 0), 'Signal'] = 1
        
        # 下降趋势 + 负动量 = 卖出
        df.loc[(df['MA_Fast'] < df['MA_Slow']) & (df['Momentum'] < 0), 'Signal'] = -1
        
        df['Signal'] = df['Signal'].fillna(0).astype(int)
        df['Position'] = df['Signal'].shift(1)
        df['Signal_Change'] = df['Signal'].diff()
        
        self.signals = df
        return df
