# 商品期货趋势跟踪策略框架

一个基于Python的量化交易框架，专门用于中国商品期货的趋势跟踪策略开发和回测。

## 功能特性

- 🎯 **趋势跟踪策略**：支持多种技术指标（MA、MACD、Bollinger Bands等）
- 📊 **数据管理**：本地数据管理和数据加载功能
- 🧪 **完整回测框架**：支持历史数据回测、性能评估和风险分析
- 📈 **可视化**：策略信号、K线图表、收益曲线等可视化展示
- 🛡️ **风险管理**：支持止损、止盈、持仓管理等风险控制

## 项目结构

```
commodity-futures-strategy/
├── src/
│   ├── __init__.py              # 包初始化
│   ├── config.py                # 配置文件
│   ├── data_manager.py          # 数据管理模块
│   ├── indicators.py            # 技术指标模块
│   ├── strategy.py              # 策略基类
│   ├── trend_following.py       # 趋势跟踪策略实现
│   ├── backtest_engine.py       # 回测引擎
│   ├── position_manager.py      # 持仓管理
│   └── utils.py                 # 工具函数
├── examples/
│   ├── run_backtest.py          # 回测运行示例
│   └── quick_start.py           # 快速开始示例
├── data/                        # 数据文件目录
├── backtest_results/            # 回测结果输出
├── requirements.txt             # Python依赖
└── README.md                    # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 快速运行

```bash
# 快速开始示例
python examples/quick_start.py

# 完整回测示例
python examples/run_backtest.py
```

### 3. 基础使用

```python
from src.data_manager import DataManager
from src.backtest_engine import BacktestEngine
from src.trend_following import SimpleMovingAverageCrossover

# 加载数据
dm = DataManager()
data = dm.load_csv('data/RB.csv')

# 创建策略
strategy = SimpleMovingAverageCrossover(fast_ma=10, slow_ma=30)

# 运行回测
backtest = BacktestEngine(
    strategy=strategy,
    data=data,
    initial_capital=100000
)
results = backtest.run()

# 查看结果
backtest.print_results()
```

## 支持的期货品种

国内主要商品期货：
- **黑色系**：螺纹钢(RB)、焦炭(J)、焦煤(JM)、铁矿石(I)
- **农产品**：大豆(A)、豆粕(M)、豆油(OI)、玉米(C)、小麦(WH)
- **贵金属**：黄金(AU)、白银(AG)
- **能源**：原油(SC)、燃油(FU)、天然气(NG)
- **化工**：聚乙烯(L)、聚丙烯(PP)、橡胶(RU)

## API 文档

### 数据管理器 (DataManager)

```python
from src.data_manager import DataManager

# 初始化
dm = DataManager(data_path='data/')

# 加载CSV数据
data = dm.load_csv('data/RB.csv')

# 验证数据
if dm.validate_data(data):
    print("数据有效")

# 清洗数据
data = dm.clean_data(data)

# 保存数据
dm.save_csv(data, 'data/processed.csv')
```

### 技术指标 (TechnicalIndicators)

```python
from src.indicators import TechnicalIndicators

indicators = TechnicalIndicators(data)

# 计算各种指标
indicators.calculate_ma(period=20)           # 移动平均线
indicators.calculate_ema(period=20)          # 指数移动平均线
indicators.calculate_macd()                  # MACD
indicators.calculate_rsi(period=14)          # RSI
indicators.calculate_bollinger_bands(20)     # 布林线
indicators.calculate_atr(period=14)          # ATR
indicators.calculate_adx(period=14)          # ADX
indicators.calculate_stochastic()            # 随机指标

# 获取计算后的数据
data_with_indicators = indicators.get_data()
```

### 策略框架 (Strategy)

```python
from src.strategy import BaseStrategy
from src.trend_following import SimpleMovingAverageCrossover

# 使用内置策略
strategy = SimpleMovingAverageCrossover(fast_ma=10, slow_ma=30)

# 或创建自定义策略
class MyStrategy(BaseStrategy):
    def generate_signals(self):
        # 实现信号生成逻辑
        pass
```

### 回测引擎 (BacktestEngine)

```python
from src.backtest_engine import BacktestEngine

# 创建回测引擎
backtest = BacktestEngine(
    strategy=strategy,
    data=data,
    initial_capital=100000,  # 初始资金
    commission=2.0,          # 手续费
    slippage=0.5             # 滑点
)

# 运行回测
results = backtest.run(verbose=True)

# 查看结果
backtest.print_results()

# 绘制图表
backtest.plot_results('result.png')

# 保存结果
backtest.save_results('backtest_results/')
```

## 性能指标

回测结果包含以下性能指标：

- **总收益率** (Total Return): 总体投资收益百分比
- **年化收益率** (Annual Return): 按年度计算的平均收益
- **夏普比率** (Sharpe Ratio): 风险调整后的收益指标
- **最大回撤** (Max Drawdown): 最大亏损幅度
- **胜率** (Win Rate): 盈利交易的比例
- **盈亏比** (Profit Factor): 盈利总额与亏损总额的比值
- **交易次数** (Total Trades): 总交易笔数

## 内置策略

### 1. SimpleMovingAverageCrossover (简单MA交叉)
最经典的趋势跟踪策略，基于两条移动平均线的交叉。

### 2. ExponentialMovingAverageCrossover (EMA交叉)
使用指数移动平均线，对近期价格变化更敏感。

### 3. AdvancedTrendFollowingStrategy (高级趋势策略)
综合使用MA、MACD和RSI等多个指标的高级趋势策略。

### 4. TrendFollowingWithATR (基于ATR的趋势策略)
结合ATR波动率指标的趋势跟踪策略。

### 5. MomentumTrendFollowing (动量趋势策略)
结合价格动量的趋势跟踪策略。

## 配置说明

编辑 `src/config.py` 配置策略参数：

```python
# 策略参数
FAST_MA_PERIOD = 10      # 快线周期
SLOW_MA_PERIOD = 30      # 慢线周期

# 回测参数
INITIAL_CAPITAL = 100000  # 初始资金
COMMISSION = 2            # 手续费
SLIPPAGE = 0.5           # 滑点

# 交易参数
CONTRACT_SIZE = 10        # 合约乘数
MIN_TICK = 1             # 最小变动单位
```

## 数据格式

期货交易数据应包含以下列：

```csv
date,open,high,low,close,volume
2024-01-01,3000,3050,2980,3020,100000
2024-01-02,3020,3080,3010,3060,120000
```

## 常见问题

### Q: 如何添加自定义技术指标？
A: 在 `src/indicators.py` 中的 `TechnicalIndicators` 类中添加新方法。

### Q: 如何优化策略参数？
A: 可以遍历不同参数组合运行回测，找到最优参数。参考 `examples/run_backtest.py` 中的多策略对比示例。

### Q: 如何使用实时数据？
A: 可以继承 `DataManager` 类，实现从实时数据源（如期货API）获取数据的功能。

### Q: 支持多品种回测吗？
A: 框架设计支持多品种，可以为每个品种创建独立的 `BacktestEngine` 实例进行回测。

## 风险警示

⚠️ **免责声明**：本框架仅供学习和研究使用。任何基于本框架的交易决策都存在风险，使用者需自行承担所有后果。

在实际交易前，请：
1. 充分理解策略逻辑
2. 在模拟盘上充分测试
3. 从小资金开始交易
4. 设置合理的风险控制措施

## 性能优化建议

1. **减少交易频率**：调整MA周期，减少交易次数
2. **添加过滤条件**：结合其他指标（RSI、MACD等）过滤假信号
3. **优化止损设置**：使用ATR动态设置止损
4. **考虑交易成本**：调整持仓大小以降低相对手续费
5. **分散品种**：在多个品种上运行策略以降低风险

## 贡献指南

欢迎提交问题报告和功能建议！

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交 Issue 或讨论。
