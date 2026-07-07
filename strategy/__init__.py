"""
均线策略回测系统

包含以下模块：
- ma_strategy: 技术指标计算
- backtester: 回测引擎
- metrics: 量化指标计算
"""

from .ma_strategy import calculate_ma, calculate_ema, calculate_atr, generate_signals
from .backtester import run_backtest, run_buy_hold_backtest
from .metrics import calculate_metrics, format_metrics_report

__all__ = [
    'calculate_ma',
    'calculate_ema',
    'calculate_atr',
    'generate_signals',
    'run_backtest',
    'run_buy_hold_backtest',
    'calculate_metrics',
    'format_metrics_report'
]
