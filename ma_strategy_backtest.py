"""
均线策略回测系统 - 主执行脚本

功能：
1. 加载5只不同行业的复权股价数据
2. 计算技术指标（MA/EMA、ATR）
3. 生成交易信号（含趋势过滤器和ATR过滤器）
4. 执行回测（策略 vs BUY-HOLD）
5. 计算量化指标
6. 生成可视化图表（HTML格式）
7. 输出交易记录和汇总报告

使用方法：
    python ma_strategy_backtest.py
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 添加strategy模块到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from strategy import (
    generate_signals,
    run_backtest,
    run_buy_hold_backtest,
    calculate_metrics,
    format_metrics_report
)

# ============================================================================
# 全局配置
# ============================================================================

# 数据目录
DATA_DIR = 'data/adjusted'

# 输出目录
OUTPUT_DIR = 'outputs/ma_backtest'
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')

# 股票列表（5只不同行业的股票）
STOCKS = [
    {'ts_code': '300750.SZ', 'name': '宁德时代', 'industry': '科技/新能源'},
    {'ts_code': '601318.SH', 'name': '中国平安', 'industry': '金融'},
    {'ts_code': '600519.SH', 'name': '贵州茅台', 'industry': '消费'},
    {'ts_code': '601857.SH', 'name': '中国石油', 'industry': '能源'},
    {'ts_code': '002594.SZ', 'name': '比亚迪', 'industry': '制造'}
]

# ============================================================================
# 策略参数配置（用户可自定义）
# ============================================================================

STRATEGY_PARAMS = {
    'short_window': 5,           # 短均线周期
    'long_window': 15,           # 长均线周期
    'ma_type': 'MA',             # 'MA' 或 'EMA'
    'trend_filter': True,        # 是否启用趋势过滤器
    'trend_window': 120,        # 趋势过滤器周期
    'atr_filter': True,          # 是否启用ATR过滤器
    'atr_window': 14,           # ATR计算周期
    'atr_percentile': 20,       # ATR历史百分位阈值（P20）
    'atr_lookback': 100,       # ATR历史lookback天数
    'initial_capital': 100000,   # 初始资金（元）
    'commission': 0.0003,       # 手续费率（万三 = 0.03% = 0.0003）
    'slippage': 0.0001,        # 滑点（万一 = 0.01% = 0.0001）
    'position_sizing': 'full',   # 仓位管理方式：'full' | 'fixed_shares' | 'fixed_ratio'
    'fixed_shares': 100,        # 固定数量（position_sizing='fixed_shares'时生效）
    'fixed_ratio': 0.5,          # 固定比例（position_sizing='fixed_ratio'时生效，50%仓位）
    'buy_ratio': 1.0,           # 买入时仓位比例（1.0 = 全仓买入）
    'sell_ratio': 1.0,          # 卖出时仓位比例（1.0 = 全仓卖出）
    'start_date': '2024-07-03',
    'end_date': '2026-07-03',
}

# ============================================================================
# 工具函数
# ============================================================================

def ensure_dir(directory: str):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")


def load_stock_data(ts_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    加载股票数据
    
    参数：
        ts_code: 股票代码
        start_date: 起始日期（可选）
        end_date: 结束日期（可选）
    
    返回：
        处理后的DataFrame
    """
    # 根据ts_code找到对应的文件名
    file_map = {
        '300750.SZ': 'ningde_times_300750_daily_adjusted.csv',
        '601318.SH': 'ping_an_601318_daily_adjusted.csv',
        '600519.SH': 'moutai_600519_daily_adjusted.csv',
        '601857.SH': 'petro_china_601857_daily_adjusted.csv',
        '002594.SZ': 'byd_002594_daily_adjusted.csv'
    }
    
    filename = file_map.get(ts_code)
    if not filename:
        raise ValueError(f"未找到股票代码 {ts_code} 对应的文件")
    
    filepath = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    # 加载数据
    df = pd.read_csv(filepath)
    
    # 数据预处理
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    # 筛选日期范围
    if start_date:
        start_date = pd.to_datetime(start_date)
        df = df[df['trade_date'] >= start_date].copy()
    if end_date:
        end_date = pd.to_datetime(end_date)
        df = df[df['trade_date'] <= end_date].copy()
    
    # 重置索引
    df = df.reset_index(drop=True)
    
    print(f"加载数据: {filename}")
    print(f"  日期范围: {df['trade_date'].min().date()} 至 {df['trade_date'].max().date()}")
    print(f"  数据条数: {len(df)}")
    
    return df


# ============================================================================
# 可视化函数
# ============================================================================

def plot_strategy_results(df: pd.DataFrame, stock_info: dict, backtest_result: dict, 
                         buy_hold_result: dict, metrics: dict, output_path: str):
    """
    绘制策略回测结果图表
    
    参数：
        df: 包含信号和指标的DataFrame
        stock_info: 股票信息字典
        backtest_result: 策略回测结果
        buy_hold_result: BUY-HOLD回测结果
        metrics: 量化指标
        output_path: 输出文件路径（HTML）
    """
    # 创建子图：2行1列（主图 + 净值图）
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=(
            f"{stock_info['name']} ({stock_info['ts_code']}) - 均线策略回测",
            '策略净值 vs BUY-HOLD'
        )
    )
    
    # ---- 主图：K线 + 均线 + 交易信号 ----
    
    # K线图
    fig.add_trace(
        go.Candlestick(
            x=df['trade_date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='股价',
            increasing_line_color='red',   # 中国股市：涨为红
            decreasing_line_color='green',  # 中国股市：跌为绿
        ),
        row=1, col=1
    )
    
    # 短均线
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=df['short_ma'],
            mode='lines',
            name=f"短均线({STRATEGY_PARAMS['short_window']})",
            line=dict(color='orange', width=1.5)
        ),
        row=1, col=1
    )
    
    # 长均线
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=df['long_ma'],
            mode='lines',
            name=f"长均线({STRATEGY_PARAMS['long_window']})",
            line=dict(color='blue', width=1.5)
        ),
        row=1, col=1
    )
    
    # 趋势均线（如果启用）
    if STRATEGY_PARAMS['trend_filter']:
        fig.add_trace(
            go.Scatter(
                x=df['trade_date'],
                y=df['trend_ma'],
                mode='lines',
                name=f"趋势均线({STRATEGY_PARAMS['trend_window']})",
                line=dict(color='purple', width=1.5, dash='dash')
            ),
            row=1, col=1
        )
    
    # 买入信号
    buy_signals = df[df['signal'] == 1]
    if len(buy_signals) > 0:
        fig.add_trace(
            go.Scatter(
                x=buy_signals['trade_date'],
                y=buy_signals['close'],
                mode='markers',
                name='买入信号',
                marker=dict(
                    symbol='triangle-up',
                    size=12,
                    color='green',
                    line=dict(width=2, color='darkgreen')
                )
            ),
            row=1, col=1
        )
    
    # 卖出信号
    sell_signals = df[df['signal'] == -1]
    if len(sell_signals) > 0:
        fig.add_trace(
            go.Scatter(
                x=sell_signals['trade_date'],
                y=sell_signals['close'],
                mode='markers',
                name='卖出信号',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color='red',
                    line=dict(width=2, color='darkred')
                )
            ),
            row=1, col=1
        )
    
    # ---- 副图：净值曲线对比 ----
    
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=backtest_result['nav'],
            mode='lines',
            name='策略净值',
            line=dict(color='blue', width=2)
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['trade_date'],
            y=buy_hold_result['nav'],
            mode='lines',
            name='BUY-HOLD',
            line=dict(color='gray', width=2, dash='dash')
        ),
        row=2, col=1
    )
    
    # 添加初始资金参考线
    fig.add_hline(
        y=STRATEGY_PARAMS['initial_capital'],
        line_dash='dot',
        line_color='green',
        annotation_text='初始资金',
        row=2, col=1
    )
    
    # ---- 布局设置 ----
    
    fig.update_layout(
        title=dict(
            text=f"{stock_info['name']} ({stock_info['industry']}) - 均线策略回测",
            x=0.5,
            font=dict(size=20)
        ),
        xaxis_title='日期',
        yaxis_title='价格（元）',
        yaxis2_title='净值（元）',
        template='plotly_white',
        height=800,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified'
    )
    
    fig.update_xaxes(rangeslider_visible=False)
    
    # 保存HTML
    fig.write_html(output_path)
    print(f"  图表已保存: {output_path}")
    
    # 显示图表（如果在Jupyter环境中）
    try:
        fig.show()
    except:
        pass


# ============================================================================
# 主执行函数
# ============================================================================

def run_single_stock_backtest(stock_info: dict) -> dict:
    """
    对单只股票执行完整的回测流程
    
    参数：
        stock_info: 股票信息字典
    
    返回：
        包含回测结果和指标的字典
    """
    print("\n" + "=" * 80)
    print(f"处理股票: {stock_info['name']} ({stock_info['ts_code']})")
    print("=" * 80)
    
    # 1. 加载数据
    print("\n[1/6] 加载数据...")
    df = load_stock_data(
        stock_info['ts_code'],
        start_date=STRATEGY_PARAMS['start_date'],
        end_date=STRATEGY_PARAMS['end_date']
    )
    
    # 2. 计算技术指标和生成信号
    print("\n[2/6] 计算技术指标和生成信号...")
    df = generate_signals(df, STRATEGY_PARAMS)
    
    # 统计信号数量
    num_buy = (df['signal'] == 1).sum()
    num_sell = (df['signal'] == -1).sum()
    print(f"  生成买入信号: {num_buy} 个")
    print(f"  生成卖出信号: {num_sell} 个")
    
    # 3. 执行策略回测
    print("\n[3/6] 执行策略回测...")
    backtest_result = run_backtest(df, STRATEGY_PARAMS)
    print(f"  策略最终净值: {backtest_result['final_value']:.2f} 元")
    print(f"  策略交易次数: {len(backtest_result['trades'])}")
    
    # 显示交易成本统计
    if 'transaction_costs' in backtest_result:
        costs = backtest_result['transaction_costs']
        print(f"  交易成本统计:")
        print(f"    累计手续费: {costs['total_commission']:.2f} 元")
        print(f"    累计滑点成本: {costs['total_slippage']:.2f} 元")
        print(f"    累计交易成本: {costs['total_transaction_cost']:.2f} 元")
        if costs['total_transaction_cost'] > 0:
            cost_ratio = costs['total_transaction_cost'] / backtest_result['final_value'] * 100
            print(f"    交易成本占比: {cost_ratio:.2f}%")
    
    # 4. 执行BUY-HOLD回测
    print("\n[4/6] 执行BUY-HOLD回测...")
    buy_hold_result = run_buy_hold_backtest(df, STRATEGY_PARAMS)
    print(f"  BUY-HOLD最终净值: {buy_hold_result['final_value']:.2f} 元")
    
    # 显示BUY-HOLD交易成本
    if 'transaction_costs' in buy_hold_result:
        costs = buy_hold_result['transaction_costs']
        print(f"  交易成本: {costs['total_transaction_cost']:.2f} 元")
    
    # 5. 计算量化指标
    print("\n[5/6] 计算量化指标...")
    metrics = calculate_metrics(backtest_result, buy_hold_result, df)
    
    # 打印指标报告
    report = format_metrics_report(metrics)
    print(report)
    
    # 6. 生成可视化图表
    print("\n[6/6] 生成可视化图表...")
    ensure_dir(CHARTS_DIR)
    
    output_filename = f"{stock_info['name']}_{stock_info['ts_code']}_backtest.html"
    output_path = os.path.join(CHARTS_DIR, output_filename)
    
    plot_strategy_results(df, stock_info, backtest_result, buy_hold_result, metrics, output_path)
    
    # 7. 保存交易记录
    ensure_dir(REPORTS_DIR)
    
    trades_filename = f"{stock_info['name']}_{stock_info['ts_code']}_trades.csv"
    trades_path = os.path.join(REPORTS_DIR, trades_filename)
    
    backtest_result['trades'].to_csv(trades_path, index=False, encoding='utf-8-sig')
    print(f"  交易记录已保存: {trades_path}")
    
    return {
        'stock_info': stock_info,
        'df': df,
        'backtest_result': backtest_result,
        'buy_hold_result': buy_hold_result,
        'metrics': metrics
    }


def main():
    """主函数"""
    print("=" * 80)
    print("均线策略回测系统")
    print("=" * 80)
    print(f"\n策略参数:")
    print(f"  短均线周期: {STRATEGY_PARAMS['short_window']}")
    print(f"  长均线周期: {STRATEGY_PARAMS['long_window']}")
    print(f"  均线类型: {STRATEGY_PARAMS['ma_type']}")
    print(f"  趋势过滤器: {'启用' if STRATEGY_PARAMS['trend_filter'] else '禁用'}")
    print(f"  ATR过滤器: {'启用' if STRATEGY_PARAMS['atr_filter'] else '禁用'}")
    print(f"  初始资金: {STRATEGY_PARAMS['initial_capital']} 元")
    print(f"  手续费率: {STRATEGY_PARAMS['commission']*100:.1f}%")
    
    # 确保输出目录存在
    ensure_dir(OUTPUT_DIR)
    ensure_dir(CHARTS_DIR)
    ensure_dir(REPORTS_DIR)
    
    # 存储所有股票的回测结果
    all_results = []
    
    # 对每只股票执行回测
    for stock in STOCKS:
        result = run_single_stock_backtest(stock)
        all_results.append(result)
    
    # 生成汇总对比表
    print("\n" + "=" * 80)
    print("汇总对比表")
    print("=" * 80)
    
    summary_data = []
    for result in all_results:
        metrics = result['metrics']
        summary_data.append({
            '股票': result['stock_info']['name'],
            '行业': result['stock_info']['industry'],
            '策略收益率(%)': f"{metrics['strategy_total_return']*100:.2f}",
            'BUY-HOLD收益率(%)': f"{metrics['bh_total_return']*100:.2f}",
            '超额收益(%)': f"{metrics['excess_return']*100:.2f}",
            '策略夏普比率': f"{metrics['strategy_sharpe']:.2f}",
            'BUY-HOLD夏普比率': f"{metrics['bh_sharpe']:.2f}",
            '策略最大回撤(%)': f"{metrics['strategy_max_drawdown']*100:.2f}",
            '交易次数': metrics['num_trades']
        })
    
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    
    # 保存汇总表
    summary_path = os.path.join(REPORTS_DIR, 'summary_report.csv')
    summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
    print(f"\n汇总报告已保存: {summary_path}")
    
    print("\n" + "=" * 80)
    print("回测完成！")
    print("=" * 80)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print(f"  图表目录: {CHARTS_DIR}")
    print(f"  报告目录: {REPORTS_DIR}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='均线策略回测系统')
    
    # 股票选择
    parser.add_argument('--ts_code', type=str, default=None,
                        help='股票代码（如 600519.SH）。不指定则回测所有5只股票')
    
    # 策略参数
    parser.add_argument('--short_window', type=int, default=None,
                        help='短均线周期（默认5）')
    parser.add_argument('--long_window', type=int, default=None,
                        help='长均线周期（默认15）')
    parser.add_argument('--ma_type', type=str, default=None,
                        choices=['MA', 'EMA'],
                        help='均线类型（MA 或 EMA，默认MA）')
    parser.add_argument('--trend_filter', action='store_true', default=None,
                        help='启用趋势过滤器')
    parser.add_argument('--no_trend_filter', action='store_false', dest='trend_filter',
                        help='禁用趋势过滤器')
    parser.add_argument('--trend_window', type=int, default=None,
                        help='趋势过滤器周期（默认120）')
    parser.add_argument('--atr_filter', action='store_true', default=None,
                        help='启用ATR过滤器')
    parser.add_argument('--no_atr_filter', action='store_false', dest='atr_filter',
                        help='禁用ATR过滤器')
    parser.add_argument('--atr_window', type=int, default=None,
                        help='ATR计算周期（默认14）')
    parser.add_argument('--atr_percentile', type=float, default=None,
                        help='ATR历史百分位阈值（默认20）')
    
    # 回测参数
    parser.add_argument('--initial_capital', type=float, default=None,
                        help='初始资金（元，默认100000）')
    parser.add_argument('--commission', type=float, default=None,
                        help='手续费率（如0.0003表示万三，默认0.0003）')
    parser.add_argument('--slippage', type=float, default=None,
                        help='滑点（如0.0001表示万一，默认0.0001）')
    parser.add_argument('--position_sizing', type=str, default=None,
                        choices=['full', 'fixed_shares', 'fixed_ratio'],
                        help='仓位管理方式（默认full）')
    parser.add_argument('--fixed_shares', type=int, default=None,
                        help='固定数量（position_sizing=fixed_shares时生效）')
    parser.add_argument('--fixed_ratio', type=float, default=None,
                        help='固定比例（position_sizing=fixed_ratio时生效，如0.5表示50%%）')
    parser.add_argument('--buy_ratio', type=float, default=None,
                        help='买入时仓位比例（0.0-1.0，默认1.0表示全仓）')
    parser.add_argument('--sell_ratio', type=float, default=None,
                        help='卖出时仓位比例（0.0-1.0，默认1.0表示全仓）')
    
    # 日期范围
    parser.add_argument('--start_date', type=str, default=None,
                        help='起始日期（格式：YYYY-MM-DD，默认2024-07-03）')
    parser.add_argument('--end_date', type=str, default=None,
                        help='结束日期（格式：YYYY-MM-DD，默认2026-07-03）')
    
    # 输出选项
    parser.add_argument('--output_dir', type=str, default=None,
                        help='输出目录（默认outputs/ma_backtest）')
    parser.add_argument('--no_plot', action='store_true',
                        help='不生成图表（仅计算指标）')
    
    args = parser.parse_args()
    
    # 更新策略参数（如果命令行指定了）
    if args.ts_code:
        # 单只股票回测
        stock_map = {s['ts_code']: s for s in STOCKS}
        if args.ts_code not in stock_map:
            print(f"错误：未找到股票代码 {args.ts_code}")
            print(f"可用股票：{', '.join([s['ts_code'] for s in STOCKS])}")
            sys.exit(1)
        target_stocks = [stock_map[args.ts_code]]
    else:
        # 所有股票回测
        target_stocks = STOCKS
    
    # 更新全局参数
    for key, value in vars(args).items():
        if value is not None and key in STRATEGY_PARAMS:
            STRATEGY_PARAMS[key] = value
    
    # 更新输出目录
    if args.output_dir:
        OUTPUT_DIR = args.output_dir
        CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')
        REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
    
    # 执行回测
    print("=" * 80)
    print("均线策略回测系统")
    print("=" * 80)
    print(f"\n策略参数:")
    for key, value in STRATEGY_PARAMS.items():
        if key in ['short_window', 'long_window', 'ma_type', 'trend_filter', 
                   'atr_filter', 'initial_capital', 'commission', 'start_date', 'end_date']:
            print(f"  {key}: {value}")
    
    # 确保输出目录存在
    ensure_dir(OUTPUT_DIR)
    ensure_dir(CHARTS_DIR)
    ensure_dir(REPORTS_DIR)
    
    # 存储所有股票的回测结果
    all_results = []
    
    # 对每只股票执行回测
    for stock in target_stocks:
        result = run_single_stock_backtest(stock)
        all_results.append(result)
    
    # 如果回测了多只股票，生成汇总对比表
    if len(all_results) > 1:
        print("\n" + "=" * 80)
        print("汇总对比表")
        print("=" * 80)
        
        summary_data = []
        for result in all_results:
            metrics = result['metrics']
            summary_data.append({
                '股票': result['stock_info']['name'],
                '行业': result['stock_info']['industry'],
                '策略收益率(%)': f"{metrics['strategy_total_return']*100:.2f}",
                'BUY-HOLD收益率(%)': f"{metrics['bh_total_return']*100:.2f}",
                '超额收益(%)': f"{metrics['excess_return']*100:.2f}",
                '策略夏普比率': f"{metrics['strategy_sharpe']:.2f}",
                '策略最大回撤(%)': f"{metrics['strategy_max_drawdown']*100:.2f}",
                '交易次数': metrics['num_trades']
            })
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
        
        # 保存汇总表
        summary_path = os.path.join(REPORTS_DIR, 'summary_report.csv')
        summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
        print(f"\n汇总报告已保存: {summary_path}")
    
    print("\n" + "=" * 80)
    print("回测完成！")
    print("=" * 80)
    print(f"\n输出目录: {OUTPUT_DIR}")
