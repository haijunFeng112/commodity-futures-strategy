"""
工具函数模块
提供各种辅助函数
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta


def calculate_returns(prices: pd.Series) -> pd.Series:
    """
    计算收益率
    
    Args:
        prices: 价格序列
        
    Returns:
        收益率序列
    """
    return prices.pct_change()


def calculate_cumulative_returns(prices: pd.Series) -> pd.Series:
    """
    计算累积收益率
    
    Args:
        prices: 价格序列
        
    Returns:
        累积收益率序列
    """
    return (1 + prices.pct_change()).cumprod() - 1


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    计算夏普比率
    
    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率
        
    Returns:
        夏普比率
    """
    excess_returns = returns - risk_free_rate / 252
    if excess_returns.std() == 0:
        return 0
    return excess_returns.mean() / excess_returns.std() * np.sqrt(252)


def calculate_sortino_ratio(returns: pd.Series, target_return: float = 0) -> float:
    """
    计算索提诺比率
    
    Args:
        returns: 收益率序列
        target_return: 目标收益率
        
    Returns:
        索提诺比率
    """
    excess_returns = returns - target_return
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return 0
    
    downside_std = downside_returns.std()
    if downside_std == 0:
        return 0
    
    return excess_returns.mean() / downside_std * np.sqrt(252)


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    计算最大回撤
    
    Args:
        prices: 价格序列
        
    Returns:
        最大回撤比例
    """
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def calculate_calmar_ratio(returns: pd.Series, prices: pd.Series) -> float:
    """
    计算卡玛比率
    
    Args:
        returns: 收益率序列
        prices: 价格序列
        
    Returns:
        卡玛比率
    """
    annual_return = returns.mean() * 252
    max_dd = calculate_max_drawdown(prices)
    
    if max_dd == 0:
        return 0
    
    return annual_return / abs(max_dd)


def calculate_win_rate(pnl_list: List[float]) -> float:
    """
    计算胜率
    
    Args:
        pnl_list: 盈亏列表
        
    Returns:
        胜率
    """
    if len(pnl_list) == 0:
        return 0
    
    wins = len([pnl for pnl in pnl_list if pnl > 0])
    return wins / len(pnl_list)


def calculate_profit_factor(pnl_list: List[float]) -> float:
    """
    计算盈亏比
    
    Args:
        pnl_list: 盈亏列表
        
    Returns:
        盈亏比
    """
    wins = sum([pnl for pnl in pnl_list if pnl > 0])
    losses = abs(sum([pnl for pnl in pnl_list if pnl < 0]))
    
    if losses == 0:
        return 0
    
    return wins / losses


def normalize_data(data: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
    """
    标准化数据
    
    Args:
        data: 数据DataFrame
        columns: 要标准化的列
        
    Returns:
        标准化后的DataFrame
    """
    df = data.copy()
    
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns
    
    for col in columns:
        mean = df[col].mean()
        std = df[col].std()
        if std != 0:
            df[col] = (df[col] - mean) / std
    
    return df


def resample_ohlc(df: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
    """
    重新采样OHLC数据
    
    Args:
        df: OHLC数据
        freq: 频率
        
    Returns:
        重新采样后的数据
    """
    df_copy = df.copy()
    df_copy.set_index('date', inplace=True)
    
    ohlcv = df_copy[['open', 'high', 'low', 'close']].resample(freq).ohlc()
    ohlcv['volume'] = df_copy['volume'].resample(freq).sum()
    
    ohlcv.reset_index(inplace=True)
    ohlcv.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    
    return ohlcv


def identify_trend(ma_fast: pd.Series, ma_slow: pd.Series) -> pd.Series:
    """
    识别趋势
    
    Args:
        ma_fast: 快线
        ma_slow: 慢线
        
    Returns:
        趋势序列 (1: 上升趋势, -1: 下降趋势, 0: 无趋势)
    """
    trend = pd.Series(0, index=ma_fast.index)
    trend[ma_fast > ma_slow] = 1
    trend[ma_fast < ma_slow] = -1
    return trend


def generate_trading_signals(data: pd.DataFrame, 
                            signal_column: str = 'Signal') -> Dict[str, List]:
    """
    提取交易信号
    
    Args:
        data: 包含信号的数据
        signal_column: 信号列名
        
    Returns:
        包含买入和卖出信号的字典
    """
    buy_signals = []
    sell_signals = []
    
    for idx, row in data.iterrows():
        if row[signal_column] == 1:
            buy_signals.append({
                'date': row['date'],
                'price': row['close'],
                'index': idx
            })
        elif row[signal_column] == -1:
            sell_signals.append({
                'date': row['date'],
                'price': row['close'],
                'index': idx
            })
    
    return {
        'buy_signals': buy_signals,
        'sell_signals': sell_signals
    }


def calculate_position_size(capital: float, price: float, 
                           risk_ratio: float = 0.02,
                           stop_loss_pct: float = 0.02) -> int:
    """
    计算持仓数量
    
    Args:
        capital: 账户资金
        price: 入场价格
        risk_ratio: 风险比例
        stop_loss_pct: 止损百分比
        
    Returns:
        持仓数量
    """
    risk_amount = capital * risk_ratio
    price_risk = price * stop_loss_pct
    
    if price_risk == 0:
        return 1
    
    position_size = int(risk_amount / price_risk)
    return max(1, position_size)


def format_number(num: float, decimals: int = 2) -> str:
    """
    格式化数字
    
    Args:
        num: 数字
        decimals: 小数位数
        
    Returns:
        格式化后的字符串
    """
    return f"{num:,.{decimals}f}"


def get_date_range(start_date: str, end_date: str, freq: str = 'D') -> pd.DatetimeIndex:
    """
    获取日期范围
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        freq: 频率
        
    Returns:
        日期索引
    """
    return pd.date_range(start=start_date, end=end_date, freq=freq)


def merge_technical_indicators(data: pd.DataFrame, 
                               indicators_df: pd.DataFrame) -> pd.DataFrame:
    """
    合并技术指标
    
    Args:
        data: 原始数据
        indicators_df: 技术指标数据
        
    Returns:
        合并后的数据
    """
    return pd.concat([data, indicators_df], axis=1)


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self, trades: List[Dict]):
        """
        初始化性能分析器
        
        Args:
            trades: 交易列表
        """
        self.trades = trades
        self.pnl_list = [t.get('pnl', 0) for t in trades]
    
    def get_summary(self) -> Dict:
        """获取总结统计"""
        winning_trades = [pnl for pnl in self.pnl_list if pnl > 0]
        losing_trades = [pnl for pnl in self.pnl_list if pnl < 0]
        
        return {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.trades) if self.trades else 0,
            'total_pnl': sum(self.pnl_list),
            'avg_win': np.mean(winning_trades) if winning_trades else 0,
            'avg_loss': np.mean(losing_trades) if losing_trades else 0,
            'max_win': max(winning_trades) if winning_trades else 0,
            'max_loss': min(losing_trades) if losing_trades else 0,
        }
    
    def get_consecutive_stats(self) -> Dict:
        """获取连续性统计"""
        max_wins = 0
        current_wins = 0
        max_losses = 0
        current_losses = 0
        
        for pnl in self.pnl_list:
            if pnl > 0:
                current_wins += 1
                max_wins = max(max_wins, current_wins)
                current_losses = 0
            else:
                current_losses += 1
                max_losses = max(max_losses, current_losses)
                current_wins = 0
        
        return {
            'max_consecutive_wins': max_wins,
            'max_consecutive_losses': max_losses,
        }
