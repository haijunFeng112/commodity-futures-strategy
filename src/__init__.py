"""
src 包初始化文件
"""

from src.data_manager import DataManager
from src.indicators import TechnicalIndicators
from src.strategy import BaseStrategy, TrendFollowingStrategy, MACDStrategy, BollingerBandsStrategy
from src.position_manager import PositionManager, Position
from src.backtest_engine import BacktestEngine
from src.utils import (
    calculate_returns,
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    PerformanceAnalyzer
)
from src.trend_following import (
    SimpleMovingAverageCrossover,
    ExponentialMovingAverageCrossover,
    AdvancedTrendFollowingStrategy,
    TrendFollowingWithATR,
    MomentumTrendFollowing
)

__all__ = [
    'DataManager',
    'TechnicalIndicators',
    'BaseStrategy',
    'TrendFollowingStrategy',
    'MACDStrategy',
    'BollingerBandsStrategy',
    'PositionManager',
    'Position',
    'BacktestEngine',
    'calculate_returns',
    'calculate_sharpe_ratio',
    'calculate_max_drawdown',
    'PerformanceAnalyzer',
    'SimpleMovingAverageCrossover',
    'ExponentialMovingAverageCrossover',
    'AdvancedTrendFollowingStrategy',
    'TrendFollowingWithATR',
    'MomentumTrendFollowing',
]
