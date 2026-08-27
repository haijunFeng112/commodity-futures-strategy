"""
数据管理模块
提供数据的加载、验证和处理功能
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import os


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_path: str = 'data/'):
        """
        初始化数据管理器
        
        Args:
            data_path: 数据文件路径
        """
        self.data_path = data_path
        
        # 创建数据目录
        os.makedirs(data_path, exist_ok=True)
    
    def load_csv(self, filepath: str) -> pd.DataFrame:
        """
        加载CSV文件
        
        Args:
            filepath: CSV文件路径
            
        Returns:
            加载的DataFrame
        """
        try:
            df = pd.read_csv(filepath)
            
            # 转换日期列
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            print(f"成功加载数据: {filepath}")
            print(f"数据形状: {df.shape}")
            
            return df
        except FileNotFoundError:
            print(f"错误: 文件不存在 {filepath}")
            return None
        except Exception as e:
            print(f"错误: 加载文件失败 {e}")
            return None
    
    def save_csv(self, data: pd.DataFrame, filepath: str) -> bool:
        """
        保存数据为CSV
        
        Args:
            data: 要保存的DataFrame
            filepath: 保存路径
            
        Returns:
            是否保存成功
        """
        try:
            data.to_csv(filepath, index=False)
            print(f"成功保存数据: {filepath}")
            return True
        except Exception as e:
            print(f"错误: 保存文件失败 {e}")
            return False
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        验证数据
        
        Args:
            data: 要验证的DataFrame
            
        Returns:
            数据是否有效
        """
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        # 检查必要列
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            print(f"错误: 缺少必要列 {missing_cols}")
            return False
        
        # 检查数据数量
        if len(data) == 0:
            print("错误: 数据为空")
            return False
        
        # 检查数据类型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if not pd.api.types.is_numeric_dtype(data[col]):
                print(f"错误: 列 {col} 应为数值类型")
                return False
        
        # 检查high >= low
        if (data['high'] < data['low']).any():
            print("警告: 存在high < low的数据")
        
        print("数据验证成功")
        return True
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        清洗数据
        
        Args:
            data: 要清洗的DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        df = data.copy()
        
        # 移除NaN
        initial_len = len(df)
        df = df.dropna()
        removed = initial_len - len(df)
        if removed > 0:
            print(f"清除了{removed}行含有NaN的数据")
        
        # 移除重覆数据
        df = df.drop_duplicates(subset=['date'], keep='first')
        
        # 按日期排序
        df = df.sort_values('date').reset_index(drop=True)
        
        # 修复high/low不一致
        df['high'] = df[['open', 'close', 'high']].max(axis=1)
        df['low'] = df[['open', 'close', 'low']].min(axis=1)
        
        print(f"数据清洗成功: {len(df)}条记录")
        return df
    
    def get_data_summary(self, data: pd.DataFrame) -> Dict:
        """
        获取数据简介
        
        Args:
            data: DataFrame
            
        Returns:
            数据简介字典
        """
        return {
            'rows': len(data),
            'columns': len(data.columns),
            'date_range': f"{data['date'].min()} to {data['date'].max()}",
            'price_range': f"{data['close'].min():.2f} - {data['close'].max():.2f}",
            'avg_volume': data['volume'].mean(),
            'missing_values': data.isnull().sum().sum()
        }
    
    def resample_data(self, data: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
        """
        重新采样数据
        
        Args:
            data: 原始数据
            freq: 采样频率 ('D': 日, 'W': 周, 'M': 月)
            
        Returns:
            重新采样后的数据
        """
        df = data.copy()
        df.set_index('date', inplace=True)
        
        try:
            # 重新采样OHLCV
            ohlc_dict = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }
            
            resampled = df.resample(freq).agg(ohlc_dict)
            resampled = resampled.dropna()
            resampled.reset_index(inplace=True)
            
            print(f"重新采样成功: {len(resampled)}条记录")
            return resampled
        except Exception as e:
            print(f"错误: 重新采样失败 {e}")
            return None
    
    def split_train_test(self, data: pd.DataFrame, 
                        test_ratio: float = 0.2) -> tuple:
        """
        分割训练集和测试集
        
        Args:
            data: 整个数据集
            test_ratio: 测试集比例
            
        Returns:
            (训练集, 测试集)
        """
        split_idx = int(len(data) * (1 - test_ratio))
        
        train_data = data[:split_idx].reset_index(drop=True)
        test_data = data[split_idx:].reset_index(drop=True)
        
        print(f"数据分割: 训练集{len(train_data)}, 测试集{len(test_data)}")
        return train_data, test_data
