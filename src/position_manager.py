"""
持仓管理模块
管理交易头寸和风险控制
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class Position:
    """持仓信息类"""
    entry_date: str          # 开仓日期
    entry_price: float       # 开仓价格
    quantity: int            # 持仓数量
    direction: int           # 方向 (1: 多头, -1: 空头)
    stop_loss: Optional[float] = None      # 止损价格
    take_profit: Optional[float] = None    # 止盈价格
    status: str = "open"     # 状态 (open, closed)
    exit_date: Optional[str] = None        # 平仓日期
    exit_price: Optional[float] = None     # 平仓价格
    pnl: Optional[float] = None            # 盈亏
    pnl_ratio: Optional[float] = None      # 盈亏比例


class PositionManager:
    """持仓管理器"""
    
    def __init__(self, initial_capital: float = 100000, 
                 contract_size: int = 10, commission: float = 2.0):
        """
        初始化持仓管理器
        
        Args:
            initial_capital: 初始资金
            contract_size: 合约乘数
            commission: 每手手续费
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.contract_size = contract_size
        self.commission = commission
        
        self.positions: List[Position] = []
        self.open_position: Optional[Position] = None
        self.trade_history: List[Position] = []
        
    def open_position(self, date: str, price: float, quantity: int, 
                     direction: int, stop_loss: float = None,
                     take_profit: float = None) -> bool:
        """
        开仓
        
        Args:
            date: 开仓日期
            price: 开仓价格
            quantity: 开仓数量
            direction: 方向 (1: 多头, -1: 空头)
            stop_loss: 止损价格
            take_profit: 止盈价格
            
        Returns:
            是否开仓成功
        """
        # 检查资金是否充足
        required_margin = price * quantity * self.contract_size + self.commission
        if required_margin > self.capital:
            print(f"警告: 资金不足。所需: {required_margin}, 可用: {self.capital}")
            return False
        
        # 关闭已有头寸（如果存在）
        if self.open_position is not None and self.open_position.status == "open":
            print("警告: 已存在开仓头寸，将其关闭")
            self.close_position(date, price)
        
        # 创建新头寸
        pos = Position(
            entry_date=date,
            entry_price=price,
            quantity=quantity,
            direction=direction,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status="open"
        )
        
        self.open_position = pos
        self.capital -= self.commission
        
        return True
    
    def close_position(self, date: str, price: float, 
                      reason: str = "manual") -> bool:
        """
        平仓
        
        Args:
            date: 平仓日期
            price: 平仓价格
            reason: 平仓原因
            
        Returns:
            是否平仓成功
        """
        if self.open_position is None or self.open_position.status != "open":
            return False
        
        pos = self.open_position
        
        # 计算盈亏
        if pos.direction == 1:  # 多头
            pnl = (price - pos.entry_price) * pos.quantity * self.contract_size
        else:  # 空头
            pnl = (pos.entry_price - price) * pos.quantity * self.contract_size
        
        pnl -= self.commission  # 扣除平仓手续费
        pnl_ratio = pnl / (pos.entry_price * pos.quantity * self.contract_size)
        
        # 更新头寸信息
        pos.exit_date = date
        pos.exit_price = price
        pos.pnl = pnl
        pos.pnl_ratio = pnl_ratio
        pos.status = "closed"
        
        # 更新资金
        self.capital += pnl
        
        # 转移到交易历史
        self.trade_history.append(pos)
        self.open_position = None
        
        return True
    
    def check_stop_conditions(self, date: str, price: float) -> Optional[str]:
        """
        检查止损/止盈条件
        
        Args:
            date: 当前日期
            price: 当前价格
            
        Returns:
            触发的条件名称 ('stop_loss', 'take_profit', None)
        """
        if self.open_position is None or self.open_position.status != "open":
            return None
        
        pos = self.open_position
        
        # 检查止损
        if pos.stop_loss is not None:
            if pos.direction == 1 and price <= pos.stop_loss:
                return "stop_loss"
            elif pos.direction == -1 and price >= pos.stop_loss:
                return "stop_loss"
        
        # 检查止盈
        if pos.take_profit is not None:
            if pos.direction == 1 and price >= pos.take_profit:
                return "take_profit"
            elif pos.direction == -1 and price <= pos.take_profit:
                return "take_profit"
        
        return None
    
    def calculate_position_size(self, price: float, risk_amount: float) -> int:
        """
        根据风险金额计算持仓数量
        
        Args:
            price: 开仓价格
            risk_amount: 风险金额
            
        Returns:
            持仓数量
        """
        # 持仓数量 = 风险金额 / (单位成本 * 合约乘数)
        position_size = int(risk_amount / (price * self.contract_size))
        return max(1, position_size)
    
    def get_open_position(self) -> Optional[Position]:
        """获取当前开仓头寸"""
        return self.open_position
    
    def get_trade_history(self) -> List[Position]:
        """获取交易历史"""
        return self.trade_history
    
    def get_statistics(self) -> Dict:
        """
        获取交易统计信息
        
        Returns:
            统计数据字典
        """
        if len(self.trade_history) == 0:
            return {}
        
        trades = self.trade_history
        
        # 盈利和亏损交易
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]
        
        total_pnl = sum(t.pnl for t in trades)
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        profit_factor = abs(sum(t.pnl for t in winning_trades)) / abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'final_capital': self.capital
        }
    
    def reset(self, capital: float = None) -> None:
        """
        重置管理器
        
        Args:
            capital: 重置的初始资金
        """
        self.capital = capital or self.initial_capital
        self.open_position = None
        self.positions = []
        self.trade_history = []
