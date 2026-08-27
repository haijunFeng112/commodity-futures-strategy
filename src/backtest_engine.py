"""
回测引擎模块
执行策略回测并计算性能指标
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from src.strategy import BaseStrategy
from src.position_manager import PositionManager


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, strategy: BaseStrategy, data: pd.DataFrame,
                 initial_capital: float = 100000, commission: float = 2.0,
                 slippage: float = 0.5, contract_size: int = 10):
        """
        初始化回测引擎
        
        Args:
            strategy: 交易策略
            data: 历史数据
            initial_capital: 初始资金
            commission: 手续费
            slippage: 滑点
            contract_size: 合约乘数
        """
        self.strategy = strategy
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.contract_size = contract_size
        
        self.position_manager = PositionManager(
            initial_capital=initial_capital,
            contract_size=contract_size,
            commission=commission
        )
        
        self.trades = []
        self.equity_curve = []
        self.results = None
    
    def run(self, verbose: bool = True) -> Dict:
        """
        运行回测
        
        Args:
            verbose: 是否打印详细信息
            
        Returns:
            回测结果字典
        """
        # 设置策略数据
        self.strategy.set_data(self.data)
        
        # 验证策略
        if not self.strategy.validate():
            print("错误: 策略验证失败")
            return None
        
        # 生成信号
        signals_data = self.strategy.generate_signals()
        if signals_data is None:
            print("错误: 生成信号失败")
            return None
        
        # 逐行执行回测
        for idx, row in signals_data.iterrows():
            current_date = row['date']
            current_price = row['close']
            signal = row['Signal']
            
            # 记录当前资金
            self.equity_curve.append({
                'date': current_date,
                'equity': self.position_manager.capital
            })
            
            # 检查止损/止盈
            stop_condition = self.position_manager.check_stop_conditions(
                current_date, current_price
            )
            if stop_condition:
                self.position_manager.close_position(current_date, current_price)
                if verbose:
                    print(f"{current_date}: 触发{stop_condition}，平仓价格: {current_price}")
            
            # 执行交易信号
            if signal == 1:  # 买入信号
                if self.position_manager.open_position is None:
                    quantity = self.position_manager.calculate_position_size(
                        current_price, 
                        self.initial_capital * 0.02  # 风险比例2%
                    )
                    entry_price = current_price + self.slippage  # 加入滑点
                    
                    self.position_manager.open_position(
                        current_date, entry_price, quantity, 1,
                        stop_loss=entry_price * 0.98,
                        take_profit=entry_price * 1.05
                    )
                    if verbose:
                        print(f"{current_date}: 买入信号，开仓价格: {entry_price}, 数量: {quantity}")
            
            elif signal == -1:  # 卖出信号
                if self.position_manager.open_position is not None:
                    exit_price = current_price - self.slippage  # 加入滑点
                    self.position_manager.close_position(current_date, exit_price)
                    if verbose:
                        print(f"{current_date}: 卖出信号，平仓价格: {exit_price}")
        
        # 平仓所有未平仓头寸
        if self.position_manager.open_position is not None:
            last_price = self.data.iloc[-1]['close']
            last_date = self.data.iloc[-1]['date']
            self.position_manager.close_position(last_date, last_price)
        
        # 计算性能指标
        self.results = self._calculate_metrics(signals_data)
        
        return self.results
    
    def _calculate_metrics(self, signals_data: pd.DataFrame) -> Dict:
        """
        计算性能指标
        
        Args:
            signals_data: 带有信号的数据
            
        Returns:
            性能指标字典
        """
        trade_history = self.position_manager.get_trade_history()
        
        if len(trade_history) == 0:
            print("警告: 没有交易记录")
            return {}
        
        # 基础统计
        stats = self.position_manager.get_statistics()
        
        # 计算收益率
        total_return = (self.position_manager.capital - self.initial_capital) / self.initial_capital
        
        # 计算年化收益率（假设一年250个交易日）
        total_days = (self.data.iloc[-1]['date'] - self.data.iloc[0]['date']).days
        annual_return = total_return * (365 / max(total_days, 1))
        
        # 计算最大回撤
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()
        
        # 计算夏普比率
        returns = equity_df['equity'].pct_change().dropna()
        if len(returns) > 0:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        else:
            sharpe_ratio = 0
        
        # 合并结果
        results = {
            'performance_metrics': {
                'total_return': total_return,
                'annual_return': annual_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'final_capital': self.position_manager.capital,
                'initial_capital': self.initial_capital,
                'total_profit': self.position_manager.capital - self.initial_capital,
            },
            'trade_statistics': stats,
            'equity_curve': equity_df,
            'trade_history': trade_history
        }
        
        return results
    
    def print_results(self) -> None:
        """打印回测结果"""
        if self.results is None:
            print("错误: 还未运行回测")
            return
        
        print("\n" + "="*60)
        print("回测结果")
        print("="*60)
        
        # 性能指标
        metrics = self.results['performance_metrics']
        print("\n【性能指标】")
        print(f"初始资金: ¥{metrics['initial_capital']:,.2f}")
        print(f"最终资金: ¥{metrics['final_capital']:,.2f}")
        print(f"总收益: ¥{metrics['total_profit']:,.2f}")
        print(f"收益率: {metrics['total_return']*100:.2f}%")
        print(f"年化收益率: {metrics['annual_return']*100:.2f}%")
        print(f"最大回撤: {metrics['max_drawdown']*100:.2f}%")
        print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
        
        # 交易统计
        trade_stats = self.results['trade_statistics']
        print("\n【交易统计】")
        print(f"总交易数: {trade_stats.get('total_trades', 0)}")
        print(f"盈利交易: {trade_stats.get('winning_trades', 0)}")
        print(f"亏损交易: {trade_stats.get('losing_trades', 0)}")
        print(f"胜率: {trade_stats.get('win_rate', 0)*100:.2f}%")
        print(f"平均盈利: ¥{trade_stats.get('avg_win', 0):.2f}")
        print(f"平均亏损: ¥{trade_stats.get('avg_loss', 0):.2f}")
        print(f"盈亏比: {trade_stats.get('profit_factor', 0):.2f}")
        print("="*60 + "\n")
    
    def plot_results(self, save_path: str = None) -> None:
        """
        绘制回测结果
        
        Args:
            save_path: 保存路径
        """
        if self.results is None:
            print("错误: 还未运行回测")
            return
        
        equity_df = self.results['equity_curve']
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'{self.strategy.name} 回测结果', fontsize=16, fontweight='bold')
        
        # 1. 资金曲线
        ax1 = axes[0, 0]
        ax1.plot(equity_df['date'], equity_df['equity'], linewidth=2, color='blue')
        ax1.set_title('资金曲线')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('资金 (¥)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. 回撤曲线
        ax2 = axes[0, 1]
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
        ax2.fill_between(equity_df['date'], equity_df['drawdown'], 0, alpha=0.5, color='red')
        ax2.set_title('回撤曲线')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('回撤 (%)')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. 收益分布
        ax3 = axes[1, 0]
        trade_history = self.results['trade_history']
        pnls = [t.pnl for t in trade_history if t.pnl is not None]
        if pnls:
            ax3.hist(pnls, bins=30, color='steelblue', alpha=0.7, edgecolor='black')
            ax3.set_title('交易收益分布')
            ax3.set_xlabel('收益 (¥)')
            ax3.set_ylabel('频数')
            ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 性能指标展示
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        metrics = self.results['performance_metrics']
        trade_stats = self.results['trade_statistics']
        
        text_info = f"""
性能指标:
  总收益率: {metrics['total_return']*100:.2f}%
  年化收益率: {metrics['annual_return']*100:.2f}%
  最大回撤: {metrics['max_drawdown']*100:.2f}%
  夏普比率: {metrics['sharpe_ratio']:.2f}

交易统计:
  总交易数: {trade_stats.get('total_trades', 0)}
  胜率: {trade_stats.get('win_rate', 0)*100:.2f}%
  盈亏比: {trade_stats.get('profit_factor', 0):.2f}
  最终资金: ¥{metrics['final_capital']:,.2f}
        """
        
        ax4.text(0.1, 0.5, text_info, fontsize=11, verticalalignment='center',
                fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def save_results(self, output_path: str) -> None:
        """
        保存回测结果
        
        Args:
            output_path: 输出路径
        """
        if self.results is None:
            print("错误: 还未运行回测")
            return
        
        # 保存交易记录
        trade_history = self.results['trade_history']
        trade_records = []
        
        for trade in trade_history:
            record = {
                'entry_date': trade.entry_date,
                'entry_price': trade.entry_price,
                'exit_date': trade.exit_date,
                'exit_price': trade.exit_price,
                'quantity': trade.quantity,
                'direction': '多' if trade.direction == 1 else '空',
                'pnl': trade.pnl,
                'pnl_ratio': trade.pnl_ratio
            }
            trade_records.append(record)
        
        trade_df = pd.DataFrame(trade_records)
        trade_df.to_csv(f"{output_path}/trades.csv", index=False, encoding='utf-8')
        
        # 保存资金曲线
        equity_df = self.results['equity_curve']
        equity_df.to_csv(f"{output_path}/equity.csv", index=False, encoding='utf-8')
        
        print(f"结果已保存到: {output_path}")
