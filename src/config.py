# 配置文件
import os

# ========== 策略参数 ==========
# 移动平均线参数
FAST_MA_PERIOD = 10      # 快线周期
SLOW_MA_PERIOD = 30      # 慢线周期

# MACD参数
MACD_FAST_PERIOD = 12
MACD_SLOW_PERIOD = 26
MACD_SIGNAL_PERIOD = 9

# Bollinger Bands参数
BB_PERIOD = 20
BB_STD = 2.0

# 风险管理参数
RISK_RATIO = 0.02        # 每笔交易的风险比例（相对于账户资金）
STOP_LOSS_PERCENT = 2.0  # 止损百分比
TAKE_PROFIT_PERCENT = 5.0  # 止盈百分比

# ========== 回测参数 ==========
INITIAL_CAPITAL = 100000  # 初始资金（元）
COMMISSION = 2            # 每手手续费（元）
SLIPPAGE = 0.5           # 滑点（元）

# ========== 数据参数 ==========
DATA_PATH = 'data/'           # 数据目录
OUTPUT_PATH = 'backtest_results/'  # 输出目录
LOG_PATH = 'logs/'

# ========== 交易参数 ==========
CONTRACT_SIZE = 10        # 每手合约乘数（以螺纹钢为例）
MIN_TICK = 1             # 最小变动单位

# 创建必要的目录
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(LOG_PATH, exist_ok=True)
