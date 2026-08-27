"""
回测单元测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_manager import DataManager
from src.trend_following import SimpleMovingAverageCrossover
from src.backtest_engine import BacktestEngine
from src.position_manager import PositionManager


class TestDataManager(unittest.TestCase):
    """数据管理器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.dm = DataManager()
        
        # 创建示例数据
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.sample_data = pd.DataFrame({
            'date': dates,
            'open': np.random.rand(len(dates)) * 1000 + 2000,
            'high': np.random.rand(len(dates)) * 1000 + 2050,
            'low': np.random.rand(len(dates)) * 1000 + 1950,
            'close': np.random.rand(len(dates)) * 1000 + 2000,
            'volume': np.random.randint(50000, 200000, len(dates))
        })
    
    def test_validate_data(self):
        """测试数据验证"""
        # 有效数据
        self.assertTrue(self.dm.validate_data(self.sample_data))
        
        # 缺少必要列
        invalid_data = self.sample_data.drop('volume', axis=1)
        self.assertFalse(self.dm.validate_data(invalid_data))
    
    def test_clean_data(self):
        """测试数据清洗"""
        # 添加NaN值
        dirty_data = self.sample_data.copy()
        dirty_data.loc[0, 'close'] = np.nan
        
        cleaned = self.dm.clean_data(dirty_data)
        self.assertEqual(len(cleaned), len(self.sample_data) - 1)
        self.assertFalse(cleaned.isnull().any().any())


class TestPositionManager(unittest.TestCase):
    """持仓管理器测试"""
    
    def setUp(self):
        """测试初始化"""
        self.pm = PositionManager(initial_capital=100000)
    
    def test_open_position(self):
        """测试开仓"""
        result = self.pm.open_position('2023-01-01', 3000, 10, 1)
        self.assertTrue(result)
        self.assertIsNotNone(self.pm.open_position)
    
    def test_close_position(self):
        """测试平仓"""
        self.pm.open_position('2023-01-01', 3000, 10, 1)
        result = self.pm.close_position('2023-01-02', 3100)
        self.assertTrue(result)
        self.assertEqual(len(self.pm.trade_history), 1)
    
    def test_calculate_position_size(self):
        """测试持仓数量计算"""
        size = self.pm.calculate_position_size(price=3000, risk_amount=2000)
        self.assertGreater(size, 0)


class TestBacktestEngine(unittest.TestCase):
    """回测引擎测试"""
    
    def setUp(self):
        """测试初始化"""
        # 创建简单的测试数据
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        prices = 3000 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, len(dates))))
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': prices * 0.99,
            'high': prices * 1.01,
            'low': prices * 0.98,
            'close': prices,
            'volume': np.random.randint(50000, 200000, len(dates))
        })
    
    def test_run_backtest(self):
        """测试回测运行"""
        strategy = SimpleMovingAverageCrossover(fast_ma=10, slow_ma=30)
        backtest = BacktestEngine(
            strategy=strategy,
            data=self.test_data,
            initial_capital=100000
        )
        
        results = backtest.run(verbose=False)
        self.assertIsNotNone(results)
        self.assertIn('performance_metrics', results)
        self.assertIn('trade_statistics', results)


if __name__ == '__main__':
    unittest.main()
