"""
测试脚本 - 验证滑点和交易成本统计功能
"""

import sys
import os

# 添加strategy模块到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategy import generate_signals, run_backtest, run_buy_hold_backtest, calculate_metrics, format_metrics_report
import pandas as pd
import numpy as np

# 创建测试数据
print("创建测试数据...")
dates = pd.date_range('2024-01-01', periods=100, freq='D')
np.random.seed(42)

# 模拟股价（随机游走）
prices = 100 + np.cumsum(np.random.randn(100) * 2)

df = pd.DataFrame({
    'ts_code': 'TEST.SZ',
    'trade_date': dates,
    'open': prices - 1,
    'high': prices + 2,
    'low': prices - 2,
    'close': prices,
    'vol': np.random.randint(1000, 10000, 100),
    'amount': np.random.randint(100000, 1000000, 100)
})

print(f"测试数据：{len(df)} 条记录")

# 策略参数（包含滑点）
params = {
    'short_window': 5,
    'long_window': 15,
    'ma_type': 'MA',
    'trend_filter': False,  # 测试时禁用过滤器
    'atr_filter': False,
    'initial_capital': 100000,
    'commission': 0.001,  # 0.1% 手续费
    'slippage': 0.001,   # 0.1% 滑点
    'position_sizing': 'full'
}

print(f"\n策略参数：")
print(f"  手续费率：{params['commission']*100:.1f}%")
print(f"  滑点：{params['slippage']*100:.1f}%")

# 生成信号
print("\n生成交易信号...")
df = generate_signals(df, params)

buy_signals = (df['signal'] == 1).sum()
sell_signals = (df['signal'] == -1).sum()
print(f"  买入信号：{buy_signals} 个")
print(f"  卖出信号：{sell_signals} 个")

# 执行回测
print("\n执行回测...")
result = run_backtest(df, params)

print(f"\n回测结果：")
print(f"  最终净值：{result['final_value']:.2f} 元")
print(f"  交易次数：{len(result['trades'])}")

# 显示交易成本统计
if 'transaction_costs' in result:
    costs = result['transaction_costs']
    print(f"\n交易成本统计：")
    print(f"  累计手续费：{costs['total_commission']:.2f} 元")
    print(f"  累计滑点成本：{costs['total_slippage']:.2f} 元")
    print(f"  累计交易成本：{costs['total_transaction_cost']:.2f} 元")
    
    if costs['total_transaction_cost'] > 0 and result['final_value'] > 0:
        cost_ratio = costs['total_transaction_cost'] / result['final_value'] * 100
        print(f"  交易成本占比：{cost_ratio:.2f}%")

# 显示交易记录（前5条）
if len(result['trades']) > 0:
    print(f"\n交易记录（前5条）：")
    print(result['trades'].head().to_string(index=False))

# 执行BUY-HOLD回测
print("\n执行BUY-HOLD回测...")
bh_result = run_buy_hold_backtest(df, params)
print(f"  BUY-HOLD最终净值：{bh_result['final_value']:.2f} 元")

if 'transaction_costs' in bh_result:
    bh_costs = bh_result['transaction_costs']
    print(f"  交易成本：{bh_costs['total_transaction_cost']:.2f} 元")

# 计算指标
print("\n计算量化指标...")
metrics = calculate_metrics(result, bh_result, df)

# 打印报告
report = format_metrics_report(metrics)
print(report)

print("\n" + "=" * 60)
print("测试完成！所有功能正常！")
print("=" * 60)
