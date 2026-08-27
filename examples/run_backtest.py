"""
回测运行示例
演示如何使用框架进行策略回测
"""

import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_manager import DataManager
from src.backtest_engine import BacktestEngine
from src.trend_following import (
    SimpleMovingAverageCrossover,
    ExponentialMovingAverageCrossover,
    AdvancedTrendFollowingStrategy,
    TrendFollowingWithATR,
    MomentumTrendFollowing
)
from src.config import INITIAL_CAPITAL, COMMISSION


def create_sample_data():
    """
    创建示例数据
    模拟期货交易数据
    """
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    n = len(dates)
    
    # 生成随机但真实的价格数据
    np.random.seed(42)
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
    
    # 确保high >= low >= open/close
    data['high'] = data[['open', 'close', 'high']].max(axis=1)
    data['low'] = data[['open', 'close', 'low']].min(axis=1)
    
    return data


def run_single_strategy_backtest(strategy, data, strategy_name):
    """
    运行单个策略的回测
    
    Args:
        strategy: 策略对象
        data: 历史数据
        strategy_name: 策略名称
    """
    print(f"\n{'='*60}")
    print(f"运行策略: {strategy_name}")
    print(f"{'='*60}")
    
    # 创建回测引擎
    backtest = BacktestEngine(
        strategy=strategy,
        data=data,
        initial_capital=INITIAL_CAPITAL,
        commission=COMMISSION
    )
    
    # 运行回测
    results = backtest.run(verbose=False)
    
    if results is None:
        print(f"策略 {strategy_name} 回测失败")
        return None
    
    # 打印结果
    backtest.print_results()
    
    # 绘制结果（可选）
    # backtest.plot_results(f"results/{strategy_name}.png")
    
    return results


def compare_strategies(data):
    """
    比较多个策略的性能
    
    Args:
        data: 历史数据
    """
    print("\n" + "="*80)
    print("策略性能对比")
    print("="*80)
    
    strategies = [
        (SimpleMovingAverageCrossover(fast_ma=10, slow_ma=30), "SMA Crossover (10/30)"),
        (ExponentialMovingAverageCrossover(fast_ema=12, slow_ema=26), "EMA Crossover (12/26)"),
        (AdvancedTrendFollowingStrategy(fast_ma=10, slow_ma=30, use_macd=True), "Advanced Trend (with MACD)"),
        (TrendFollowingWithATR(fast_ma=10, slow_ma=30, atr_period=14), "Trend with ATR"),
        (MomentumTrendFollowing(fast_ma=10, slow_ma=30, momentum_period=12), "Momentum Trend"),
    ]
    
    results_summary = []
    
    for strategy, name in strategies:
        results = run_single_strategy_backtest(strategy, data, name)
        
        if results is not None:
            metrics = results['performance_metrics']
            stats = results['trade_statistics']
            
            results_summary.append({
                '策略': name,
                '总收益率': f"{metrics['total_return']*100:.2f}%",
                '年化收益': f"{metrics['annual_return']*100:.2f}%",
                '最大回撤': f"{metrics['max_drawdown']*100:.2f}%",
                '夏普比率': f"{metrics['sharpe_ratio']:.2f}",
                '总交易数': stats.get('total_trades', 0),
                '胜率': f"{stats.get('win_rate', 0)*100:.2f}%",
                '盈亏比': f"{stats.get('profit_factor', 0):.2f}",
            })
    
    # 打印对比表
    if results_summary:
        summary_df = pd.DataFrame(results_summary)
        print("\n" + "="*80)
        print("性能对比总结")
        print("="*80)
        print(summary_df.to_string(index=False))


def run_example_with_csv():
    """
    使用CSV文件运行示例
    """
    print("\n【使用CSV文件的示例】")
    print("-" * 60)
    
    # 创建数据管理器
    dm = DataManager(data_path='data/')
    
    # 尝试加载数据（如果��件存在）
    csv_path = 'data/sample_data.csv'
    if os.path.exists(csv_path):
        data = dm.load_csv(csv_path)
        print(f"已加载数据: {csv_path}")
    else:
        print(f"文件不存在: {csv_path}")
        print("将使用生成的示例数据")
        data = create_sample_data()
        # 保存为CSV供后续使用
        dm.save_csv(data, csv_path)
    
    # 验证和清洗数据
    if not dm.validate_data(data):
        print("数据验证失败，尝试清洗...")
        data = dm.clean_data(data)
    
    return data


def main():
    """
    主函数
    """
    print("\n" + "="*80)
    print("商品期货趋势跟踪策略框架 - 回测示例")
    print("="*80)
    
    # 生成或加载数据
    print("\n【第一步】加载数据")
    print("-" * 60)
    
    try:
        data = run_example_with_csv()
    except Exception as e:
        print(f"加载数据失败: {e}")
        print("使用生成的示例数据...")
        data = create_sample_data()
    
    if data is not None and len(data) > 0:
        print(f"\n数据信息:")
        print(f"  时间范围: {data['date'].min()} 到 {data['date'].max()}")
        print(f"  数据行数: {len(data)}")
        print(f"  价格范围: {data['close'].min():.2f} - {data['close'].max():.2f}")
    else:
        print("数据加载失败")
        return
    
    # 运行策略对比
    print("\n【第二步】运行策略回测")
    print("-" * 60)
    compare_strategies(data)
    
    print("\n" + "="*80)
    print("回测完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    import numpy as np
    main()
