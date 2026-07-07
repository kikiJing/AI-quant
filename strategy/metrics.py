"""
量化指标计算模块

计算策略回测的各项量化指标：
- 收益类：累计回报、总收益率、年化收益率、超额收益
- 交易质量类：胜率、盈亏比
- 风险类：最大回撤
- 综合类：夏普比率
"""

import pandas as pd
import numpy as np


def calculate_max_drawdown(nav: pd.Series) -> float:
    """
    计算最大回撤
    
    参数：
        nav: 净值序列
    
    返回：
        最大回撤（百分比，如0.15表示15%）
    """
    # 计算累计最大值
    cumulative_max = nav.cummax()
    
    # 计算回撤
    drawdown = (nav - cumulative_max) / cumulative_max
    
    # 最大回撤（负值，取绝对值）
    max_drawdown = abs(drawdown.min())
    
    return max_drawdown


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.025) -> float:
    """
    计算夏普比率
    
    参数：
        returns: 日收益率序列
        risk_free_rate: 无风险利率（年化，默认2.5%）
    
    返回：
        夏普比率
    """
    # 年化收益率
    annual_return = returns.mean() * 252
    
    # 年化波动率
    annual_volatility = returns.std() * np.sqrt(252)
    
    if annual_volatility == 0:
        return np.nan
    
    # 夏普比率
    sharpe = (annual_return - risk_free_rate) / annual_volatility
    
    return sharpe


def calculate_win_rate(trades: pd.DataFrame) -> float:
    """
    计算胜率
    
    参数：
        trades: 交易记录DataFrame，必须包含 'type', 'execution_price' 列
    
    返回：
        胜率（0-1之间）
    """
    if len(trades) == 0:
        return np.nan
    
    # 只统计卖出交易
    sell_trades = trades[trades['type'] == 'SELL'].copy()
    
    if len(sell_trades) == 0:
        return np.nan
    
    # 计算每笔交易的盈亏
    # 需要匹配买入和卖出
    buy_prices = []
    win_count = 0
    total_sell_count = 0
    
    for idx, trade in trades.iterrows():
        if trade['type'] == 'BUY':
            buy_prices.append(trade['execution_price'])
        elif trade['type'] == 'SELL' and buy_prices:
            # 使用FIFO方法匹配
            buy_price = buy_prices.pop(0)
            if trade['execution_price'] > buy_price:
                win_count += 1
            total_sell_count += 1
    
    if total_sell_count == 0:
        return np.nan
    
    win_rate = win_count / total_sell_count
    
    return win_rate


def calculate_profit_loss_ratio(trades: pd.DataFrame) -> float:
    """
    计算盈亏比
    
    参数：
        trades: 交易记录DataFrame
    
    返回：
        盈亏比（平均盈利 / 平均亏损）
    """
    if len(trades) == 0:
        return np.nan
    
    # 计算每笔交易的盈亏
    profits = []
    losses = []
    buy_prices = []
    
    for idx, trade in trades.iterrows():
        if trade['type'] == 'BUY':
            buy_prices.append(trade['execution_price'])
        elif trade['type'] == 'SELL' and buy_prices:
            buy_price = buy_prices.pop(0)
            profit = trade['execution_price'] - buy_price
            if profit > 0:
                profits.append(profit)
            elif profit < 0:
                losses.append(abs(profit))
    
    if not profits or not losses:
        return np.nan
    
    avg_profit = np.mean(profits)
    avg_loss = np.mean(losses)
    
    if avg_loss == 0:
        return np.inf
    
    return avg_profit / avg_loss


def calculate_metrics(backtest_result: dict, buy_hold_result: dict, df: pd.DataFrame) -> dict:
    """
    计算所有量化指标
    
    参数：
        backtest_result: 策略回测结果（run_backtest的返回值）
        buy_hold_result: BUY-HOLD回测结果（run_buy_hold_backtest的返回值）
        df: 原始数据DataFrame（用于计算交易日数）
    
    返回：
        字典，包含所有量化指标
    """
    # 策略指标
    strategy_nav = backtest_result['nav']
    strategy_returns = backtest_result['returns']
    strategy_final = backtest_result['final_value']
    strategy_trades = backtest_result['trades']
    
    # BUY-HOLD指标
    bh_nav = buy_hold_result['nav']
    bh_final = buy_hold_result['final_value']
    
    # 初始资金
    initial = strategy_nav.iloc[0]
    
    # 交易日数
    trading_days = len(df)
    
    # 收益类指标
    strategy_total_return = (strategy_final - initial) / initial
    bh_total_return = (bh_final - initial) / initial
    excess_return = strategy_total_return - bh_total_return
    
    # 年化收益率
    years = trading_days / 252
    if years > 0:
        strategy_annual_return = (1 + strategy_total_return) ** (1 / years) - 1
        bh_annual_return = (1 + bh_total_return) ** (1 / years) - 1
    else:
        strategy_annual_return = np.nan
        bh_annual_return = np.nan
    
    # 风险类指标
    strategy_max_dd = calculate_max_drawdown(strategy_nav)
    bh_max_dd = calculate_max_drawdown(bh_nav)
    
    # 综合类指标
    strategy_sharpe = calculate_sharpe_ratio(strategy_returns)
    bh_sharpe = calculate_sharpe_ratio(bh_nav.pct_change().fillna(0))
    
    # 交易质量类指标
    win_rate = calculate_win_rate(strategy_trades)
    pl_ratio = calculate_profit_loss_ratio(strategy_trades)
    
    # 交易成本统计
    strategy_transaction_costs = backtest_result.get('transaction_costs', {})
    bh_transaction_costs = buy_hold_result.get('transaction_costs', {})
    
    # 汇总
    metrics = {
        'strategy_total_return': strategy_total_return,
        'strategy_annual_return': strategy_annual_return,
        'strategy_max_drawdown': strategy_max_dd,
        'strategy_sharpe': strategy_sharpe,
        'strategy_win_rate': win_rate,
        'strategy_pl_ratio': pl_ratio,
        'bh_total_return': bh_total_return,
        'bh_annual_return': bh_annual_return,
        'bh_max_drawdown': bh_max_dd,
        'bh_sharpe': bh_sharpe,
        'excess_return': excess_return,
        'trading_days': trading_days,
        'num_trades': len(strategy_trades),
        # 交易成本
        'strategy_total_commission': strategy_transaction_costs.get('total_commission', 0),
        'strategy_total_slippage': strategy_transaction_costs.get('total_slippage', 0),
        'strategy_total_transaction_cost': strategy_transaction_costs.get('total_transaction_cost', 0),
        'bh_total_commission': bh_transaction_costs.get('total_commission', 0),
        'bh_total_slippage': bh_transaction_costs.get('total_slippage', 0),
        'bh_total_transaction_cost': bh_transaction_costs.get('total_transaction_cost', 0)
    }
    
    return metrics


def format_metrics_report(metrics: dict) -> str:
    """
    格式化指标报告（文本形式）
    
    参数：
        metrics: calculate_metrics的返回值
    
    返回：
        格式化的文本报告
    """
    report = []
    report.append("=" * 60)
    report.append("量化策略回测报告")
    report.append("=" * 60)
    report.append("")
    
    report.append("-" * 60)
    report.append("收益类指标")
    report.append("-" * 60)
    report.append(f"策略总收益率: {metrics['strategy_total_return']*100:.2f}%")
    report.append(f"BUY-HOLD总收益率: {metrics['bh_total_return']*100:.2f}%")
    report.append(f"超额收益: {metrics['excess_return']*100:.2f}%")
    report.append(f"策略年化收益率: {metrics['strategy_annual_return']*100:.2f}%")
    report.append(f"BUY-HOLD年化收益率: {metrics['bh_annual_return']*100:.2f}%")
    report.append("")
    
    report.append("-" * 60)
    report.append("风险类指标")
    report.append("-" * 60)
    report.append(f"策略最大回撤: {metrics['strategy_max_drawdown']*100:.2f}%")
    report.append(f"BUY-HOLD最大回撤: {metrics['bh_max_drawdown']*100:.2f}%")
    report.append("")
    
    report.append("-" * 60)
    report.append("综合类指标")
    report.append("-" * 60)
    report.append(f"策略夏普比率: {metrics['strategy_sharpe']:.2f}")
    report.append(f"BUY-HOLD夏普比率: {metrics['bh_sharpe']:.2f}")
    report.append("")
    
    report.append("-" * 60)
    report.append("交易质量类指标")
    report.append("-" * 60)
    report.append(f"交易次数: {metrics['num_trades']}")
    if not np.isnan(metrics['strategy_win_rate']):
        report.append(f"胜率: {metrics['strategy_win_rate']*100:.2f}%")
    if not np.isnan(metrics['strategy_pl_ratio']):
        report.append(f"盈亏比: {metrics['strategy_pl_ratio']:.2f}")
    report.append("")
    
    report.append("-" * 60)
    report.append("交易成本统计")
    report.append("-" * 60)
    report.append(f"策略累计手续费: {metrics['strategy_total_commission']:.2f} 元")
    report.append(f"策略累计滑点成本: {metrics['strategy_total_slippage']:.2f} 元")
    report.append(f"策略累计交易成本: {metrics['strategy_total_transaction_cost']:.2f} 元")
    if metrics['strategy_total_transaction_cost'] > 0 and metrics['num_trades'] > 0:
        avg_cost = metrics['strategy_total_transaction_cost'] / metrics['num_trades']
        report.append(f"平均单次交易成本: {avg_cost:.2f} 元")
    report.append("")
    
    report.append("=" * 60)
    
    return "\n".join(report)


if __name__ == '__main__':
    print("量化指标计算模块加载成功")
    print("可用函数：")
    print("  - calculate_max_drawdown(): 计算最大回撤")
    print("  - calculate_sharpe_ratio(): 计算夏普比率")
    print("  - calculate_win_rate(): 计算胜率")
    print("  - calculate_profit_loss_ratio(): 计算盈亏比")
    print("  - calculate_metrics(): 计算所有指标")
    print("  - format_metrics_report(): 格式化报告")
