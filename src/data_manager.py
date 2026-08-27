"""
数据管理模块
负责加载、清洗和管理期货交易数据
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Optional, Dict, Any


class DataManager:
    """数据管理类"""
    
    def __init__(self, data_path: str = 'data/'):
        """
        初始化数据管理器
        
        Args:
            data_path: 数据存储路径
        """
        self.data_path = data_path
        self.data = None
        
    def load_csv(self, file_path: str, date_column: str = 'date', 
                 parse_dates: bool = True) -> pd.DataFrame:
        """
        从CSV文件加载期货数据
        
        Args:
            file_path: CSV文件路径
            date_column: 日期列名称
            parse_dates: 是否解析日期
            
        Returns:
            期货数据DataFrame
        """
        try:
            if parse_dates:
                df = pd.read_csv(file_path, parse_dates=[date_column])
                df = df.sort_values(by=date_column)
            else:
                df = pd.read_csv(file_path)
            
            self.data = df
            print(f"成功加载数据: {file_path}")
            print(f"数据范围: {df[date_column].min()} 到 {df[date_column].max()}")
            print(f"数据行数: {len(df)}")
            
            return df
        except FileNotFoundError:
            print(f"错误: 文件 {file_path} 不存在")
            return None
        except Exception as e:
            print(f"加载数据时出错: {e}")
            return None
    
    def load_from_dict(self, data_dict: Dict[str, Any]) -> pd.DataFrame:
        """
        从字典加载数据
        
        Args:
            data_dict: 包含期货数据的字典
            
        Returns:
            期货数据DataFrame
        """
        df = pd.DataFrame(data_dict)
        self.data = df
        return df
    
    def save_csv(self, data: pd.DataFrame, file_path: str) -> bool:
        """
        将数据保存为CSV文件
        
        Args:
            data: 待保存的DataFrame
            file_path: 保存路径
            
        Returns:
            是否保存成功
        """
        try:
            data.to_csv(file_path, index=False)
            print(f"数据已保存到: {file_path}")
            return True
        except Exception as e:
            print(f"保存数据时出错: {e}")
            return False
    
    def validate_data(self, df: pd.DataFrame = None) -> bool:
        """
        验证数据完整性
        
        Args:
            df: 待验证的DataFrame，如果为None则验证self.data
            
        Returns:
            数据是否有效
        """
        if df is None:
            df = self.data
        
        if df is None:
            print("错误: 没有加载数据")
            return False
        
        # 检查必要列
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"错误: 缺少必要列: {missing_columns}")
            return False
        
        # 检查是否有NaN值
        if df.isnull().any().any():
            print("警告: 数据中存在NaN值")
            print(df.isnull().sum())
            return False
        
        print("数据验证通过")
        return True
    
    def clean_data(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        清洗数据（移除NaN、异常值等）
        
        Args:
            df: 待清洗的DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        if df is None:
            df = self.data.copy()
        else:
            df = df.copy()
        
        # 移除NaN
        df = df.dropna()
        
        # 移除明显的异常值（例如成交量为0）
        df = df[df['volume'] > 0]
        
        # 确保价格合理（high >= low, close在high和low之间）
        df = df[(df['high'] >= df['low']) & 
                (df['close'] >= df['low']) & 
                (df['close'] <= df['high'])]
        
        self.data = df
        print(f"数据清洗完成，剩余 {len(df)} 条记录")
        
        return df
    
    def resample_data(self, df: pd.DataFrame = None, freq: str = 'D') -> pd.DataFrame:
        """
        重新采样数据（改变时间频率）
        
        Args:
            df: 待重新采样的DataFrame
            freq: 频率 ('D'=日, 'W'=周, 'M'=月)
            
        Returns:
            重新采样后的DataFrame
        """
        if df is None:
            df = self.data.copy()
        else:
            df = df.copy()
        
        # 设置日期索引
        df.set_index('date', inplace=True)
        
        # 重新采样
        ohlcv = df[['open', 'high', 'low', 'close']].resample(freq).ohlc()
        ohlcv['volume'] = df['volume'].resample(freq).sum()
        
        ohlcv.reset_index(inplace=True)
        ohlcv.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        self.data = ohlcv
        print(f"数据已重新采样为 {freq} 频率，共 {len(ohlcv)} 条记录")
        
        return ohlcv
    
    def get_data(self) -> pd.DataFrame:
        """获取当前数据"""
        return self.data
    
    def get_data_slice(self, start_date: str = None, 
                       end_date: str = None) -> pd.DataFrame:
        """
        获取指定日期范围的数据切片
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            切片后的DataFrame
        """
        if self.data is None:
            return None
        
        df = self.data.copy()
        
        if start_date:
            df = df[df['date'] >= start_date]
        
        if end_date:
            df = df[df['date'] <= end_date]
        
        return df
