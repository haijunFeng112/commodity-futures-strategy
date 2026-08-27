"""
快速开始示例
展示如何快速使用框架的基本功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_manager import DataManager
from src.indicators import TechnicalIndicators
from src.trend_following import SimpleMovingAverageCrossover
from src.backtest_engine import BacktestEngine


def main():
    """快速开始示例"""
    
    print("\n" + "="*60)
    print("快速开始示例")
    print("="*60)
    
    # 第一步：生成示例数据
    print("\n【步骤1】生成示例数据")
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    n = len(dates)
    np.random.seed(42)
    
    # 生成价格数据
    returns = np.random.normal(0.0005, 0.02, n)
    prices = 3000 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high': prices * (1 + abs(np.random.uniform(0, 0.02, n))),
        'low': prices * (1 - abs(np.random.uniform(0, 0.02, n))),
        'close': prices,
        'volume': np.random.randint(50000, 200000, n)
    })
    
    # 确保high >= low
    data['high'] = data[['open', 'close', 'high']].max(axis=1)
    data['low'] = data[['open', 'close', 'low']].min(axis=1)
    
    print(f"数据生成完成: {len(data)} 条记录")
    print(f"价格范围: {data['close'].min():.2f} - {data['close'].max():.2f}")
    
    # 第二步：创建策略
    print("\n【步骤2】创建策略")
    strategy = SimpleMovingAverageCrossover(fast_ma=10, slow_ma=30)
    print(f"策略: {strategy.name}")
    print(f"快线周期: {strategy.fast_ma}")
    print(f"慢线周期: {strategy.slow_ma}")
    
    # 第三步：运行回测
    print("\n【步骤3】运行回测")
    backtest = BacktestEngine(
        strategy=strategy,
        data=data,
        initial_capital=100000,
        commission=2.0
    )
    
    results = backtest.run(verbose=False)
    
    # 第四步：查看结果
    print("\n【步骤4】查看结果")
    backtest.print_results()
    
    # 第五步：计算技术指标
    print("\n【步骤5】计算技术指标")
    indicators = TechnicalIndicators(data)
    indicators.calculate_ma(20)
    indicators.calculate_macd()
    indicators.calculate_rsi(14)
    indicators.calculate_bollinger_bands(20)
    
    indicator_data = indicators.get_data()
    
    # 显示最后几行的指标
    print("\n最后5行的技术指标:")
    cols_to_show = ['date', 'close', 'MA20', 'MACD', 'RSI14', 'BB_Upper', 'BB_Lower']
    print(indicator_data[cols_to_show].tail())
    
    print("\n" + "="*60)
    print("快速开始示例完成！")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
