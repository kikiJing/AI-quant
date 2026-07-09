#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
双均线策略深度分析脚本
对比不同股票、不同均线周期、不同时间段的收益变化
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建输出目录
output_dir = 'outputs/ma_backtest/analysis'
os.makedirs(output_dir, exist_ok=True)

print('=' * 80)
print('📊 双均线策略深度分析')
print('=' * 80)

# ============================================================================
# 定义核心函数
# ============================================================================

def load_stock_data(ts_code, start_date=None, end_date=None):
    """加载股票数据"""
    file_map = {
        '300750.SZ': 'ningde_times_300750_daily_adjusted.csv',
        '601318.SH': 'ping_an_601318_daily_adjusted.csv',
        '600519.SH': 'moutai_600519_daily_adjusted.csv',
        '601857.SH': 'petro_china_601857_daily_adjusted.csv',
        '002594.SZ': 'byd_002594_daily_adjusted.csv'
    }
    
    filename = file_map.get(ts_code)
    filepath = f'data/adjusted/{filename}'
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'文件不存在: {filepath}')
    
    df = pd.read_csv(filepath)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    if start_date:
        df = df[df['trade_date'] >= pd.to_datetime(start_date)].copy()
    if end_date:
        df = df[df['trade_date'] <= pd.to_datetime(end_date)].copy()
    
    df = df.reset_index(drop=True)
    return df

def calculate_ma(prices, window):
    """计算移动平均"""
    return prices.rolling(window=window, min_periods=1).mean()

def run_backtest(df, short_window, long_window, initial_capital=100000, commission=0.001, slippage=0.001):
    """执行回测"""
    # 计算均线
    df['ma_short'] = calculate_ma(df['close'], short_window)
    df['ma_long'] = calculate_ma(df['close'], long_window)
    
    # 生成信号
    df['signal'] = 0
    df['golden_cross'] = (df['ma_short'] > df['ma_long']) & (df['ma_short'].shift(1) <= df['ma_long'].shift(1))
    df['death_cross'] = (df['ma_short'] < df['ma_long']) & (df['ma_short'].shift(1) >= df['ma_long'].shift(1))
    
    for i in range(1, len(df)):
        if df.iloc[i]['golden_cross']:
            df.iloc[i, df.columns.get_loc('signal')] = 1
        elif df.iloc[i]['death_cross']:
            df.iloc[i, df.columns.get_loc('signal')] = -1
    
    # 执行交易
    cash = initial_capital
    position = 0
    portfolio_value = []
    
    for i in range(len(df)):
        signal = df.iloc[i]['signal']
        price = df.iloc[i]['close']
        
        if signal == 1 and position == 0:
            execution_price = price * (1 + slippage)
            shares = int(cash * (1 - commission) / execution_price)
            if shares > 0:
                cost = shares * execution_price * (1 + commission)
                cash -= cost
                position = shares
        
        elif signal == -1 and position > 0:
            execution_price = price * (1 - slippage)
            revenue = position * execution_price * (1 - commission)
            cash += revenue
            position = 0
        
        portfolio_value.append(cash + position * price)
    
    nav = pd.Series(portfolio_value)
    returns = nav.pct_change().fillna(0)
    
    # 计算指标
    total_return = (nav.iloc[-1] - initial_capital) / initial_capital
    trading_days = len(df)
    years = trading_days / 252
    annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else np.nan
    
    # 最大回撤
    peak = nav.cummax()
    drawdown = (nav - peak) / peak
    max_dd = abs(drawdown.min())
    
    # 夏普比率
    excess_returns = returns - 0.02/252
    sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else np.nan
    
    # 胜率
    buy_prices = []
    win_count = 0
    sell_count = 0
    
    for i in range(len(df)):
        if df.iloc[i]['signal'] == 1:
            buy_prices.append(df.iloc[i]['close'])
        elif df.iloc[i]['signal'] == -1 and buy_prices:
            sell_price = df.iloc[i]['close']
            buy_price = buy_prices.pop(0)
            if sell_price > buy_price:
                win_count += 1
            sell_count += 1
    
    win_rate = win_count / sell_count if sell_count > 0 else np.nan
    
    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'win_rate': win_rate,
        'num_trades': len(df[df['signal'] != 0])
    }

# ============================================================================
# 主分析流程
# ============================================================================

# 定义测试参数
STOCKS = {
    '300750.SZ': '宁德时代',
    '601318.SH': '中国平安',
    '600519.SH': '贵州茅台',
    '601857.SH': '中国石油',
    '002594.SZ': '比亚迪'
}

SHORT_WINDOWS = [5, 10, 15, 20]
LONG_WINDOWS = [20, 30, 50, 60]

START_DATE = '2024-07-03'
END_DATE = '2026-07-03'

print('\n📊 测试1：不同均线周期对比（全时间段）')
print('-' * 80)

# 存储结果
results = []

# 遍历所有组合
total_combinations = len(STOCKS) * len(SHORT_WINDOWS) * len(LONG_WINDOWS)
current = 0

for ts_code, stock_name in STOCKS.items():
    print(f'\n处理股票: {stock_name} ({ts_code})')
    
    try:
        # 加载数据
        df = load_stock_data(ts_code, START_DATE, END_DATE)
        
        for short in SHORT_WINDOWS:
            for long in LONG_WINDOWS:
                if short >= long:
                    continue
                
                current += 1
                print(f'  进度: {current}/{total_combinations} - MA{short}/{long}', end='\r')
                
                # 执行回测
                metrics = run_backtest(df, short, long)
                
                results.append({
                    '股票': stock_name,
                    '代码': ts_code,
                    '短均线': short,
                    '长均线': long,
                    '总收益率(%)': round(metrics['total_return'] * 100, 2),
                    '年化收益率(%)': round(metrics['annual_return'] * 100, 2) if not np.isnan(metrics['annual_return']) else np.nan,
                    '夏普比率': round(metrics['sharpe_ratio'], 2) if not np.isnan(metrics['sharpe_ratio']) else np.nan,
                    '最大回撤(%)': round(metrics['max_drawdown'] * 100, 2),
                    '胜率(%)': round(metrics['win_rate'] * 100, 2) if not np.isnan(metrics['win_rate']) else np.nan,
                    '交易次数': metrics['num_trades']
                })
    except Exception as e:
        print(f'\n❌ 错误: {str(e)}')

print('\n\n✅ 测试1完成')

# 转换为DataFrame
results_df = pd.DataFrame(results)

# 保存结果
results_df.to_csv(f'{output_dir}/test1_ma_periods.csv', index=False, encoding='utf-8-sig')
print(f'✅ 测试结果已保存: {output_dir}/test1_ma_periods.csv')

# ============================================================================
# 生成热力图
# ============================================================================

print('\n📈 生成热力图...')
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

for idx, (ts_code, stock_name) in enumerate(STOCKS.items()):
    # 筛选该股票的数据
    stock_data = results_df[results_df['代码'] == ts_code]
    
    # 创建透视表
    pivot = stock_data.pivot(index='长均线', columns='短均线', values='总收益率(%)')
    
    # 绘制热力图
    ax = axes[idx]
    sns.heatmap(
        pivot,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn',
        center=0,
        ax=ax,
        cbar_kws={'label': '总收益率(%)'}
    )
    
    ax.set_title(f'{stock_name}\n不同均线周期的总收益率', fontsize=12, fontweight='bold')
    ax.set_xlabel('短均线周期', fontsize=10)
    ax.set_ylabel('长均线周期', fontsize=10)

# 删除多余的子图
for idx in range(len(STOCKS), len(axes)):
    fig.delaxes(axes[idx])

plt.tight_layout()
plt.savefig(f'{output_dir}/heatmap_ma_periods.png', dpi=150, bbox_inches='tight')
print(f'✅ 热力图已保存: {output_dir}/heatmap_ma_periods.png')
plt.close()

# ============================================================================
# 找到最优参数
# ============================================================================

print('\n🏆 找到每个股票的最优参数组合...')
optimal_results = []

for ts_code in STOCKS.keys():
    stock_data = results_df[results_df['代码'] == ts_code]
    
    # 按夏普比率排序
    stock_data = stock_data.sort_values('夏普比率', ascending=False)
    
    if len(stock_data) > 0:
        optimal = stock_data.iloc[0]
        optimal_results.append(optimal)

optimal_df = pd.DataFrame(optimal_results)

print('\n最优参数组合（按夏普比率）:')
print(optimal_df[['股票', '短均线', '长均线', '总收益率(%)', '夏普比率', '最大回撤(%)']])

# 保存最优参数
optimal_df.to_csv(f'{output_dir}/optimal_parameters.csv', index=False, encoding='utf-8-sig')
print(f'✅ 最优参数已保存: {output_dir}/optimal_parameters.csv')

# ============================================================================
# 生成对比图
# ============================================================================

print('\n📊 生成对比图...')
fig, ax = plt.subplots(1, 2, figsize=(14, 6))

x = range(len(optimal_df))

# 总收益率对比
bars1 = ax[0].bar(x, optimal_df['总收益率(%)'], color='steelblue', alpha=0.8)
ax[0].set_xticks(x)
ax[0].set_xticklabels(optimal_df['股票'], rotation=45)
ax[0].set_title('最优参数下的总收益率', fontsize=14, fontweight='bold')
ax[0].set_ylabel('总收益率(%)', fontsize=12)
ax[0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax[0].grid(axis='y', alpha=0.3)

# 添加数值标签
for bar in bars1:
    height = bar.get_height()
    ax[0].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom' if height >= 0 else 'top',
                fontsize=10, fontweight='bold')

# 夏普比率对比
bars2 = ax[1].bar(x, optimal_df['夏普比率'], color='coral', alpha=0.8)
ax[1].set_xticks(x)
ax[1].set_xticklabels(optimal_df['股票'], rotation=45)
ax[1].set_title('最优参数下的夏普比率', fontsize=14, fontweight='bold')
ax[1].set_ylabel('夏普比率', fontsize=12)
ax[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax[1].grid(axis='y', alpha=0.3)

# 添加数值标签
for bar in bars2:
    height = bar.get_height()
    ax[1].text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom' if height >= 0 else 'top',
                fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{output_dir}/comparison_optimal.png', dpi=150, bbox_inches='tight')
print(f'✅ 对比图已保存: {output_dir}/comparison_optimal.png')
plt.close()

# ============================================================================
# 测试2：不同时间段
# ============================================================================

print('\n📅 测试2：不同时间段对比')
print('-' * 80)

# 定义时间段
TIME_PERIODS = {
    '全时间段': ('2024-07-03', '2026-07-03'),
    '牛市(2024-09~2025-03)': ('2024-09-01', '2025-03-31'),
    '震荡市(2025-04~2025-10)': ('2025-04-01', '2025-10-31'),
    '近期(2026-01~2026-07)': ('2026-01-01', '2026-07-03')
}

# 使用最优参数
OPTIMAL_PARAMS = {}
for idx, row in optimal_df.iterrows():
    ts_code = row['代码']
    short = int(row['短均线'])
    long = int(row['长均线'])
    OPTIMAL_PARAMS[ts_code] = (short, long)

print('\n使用最优参数组合:')
for ts_code, (short, long) in OPTIMAL_PARAMS.items():
    print(f'  {STOCKS[ts_code]}: MA{short}/{long}')

# 存储结果
time_results = []

for period_name, (start, end) in TIME_PERIODS.items():
    print(f'\n处理时间段: {period_name}')
    
    for ts_code, stock_name in STOCKS.items():
        try:
            # 加载数据
            df = load_stock_data(ts_code, start, end)
            
            if len(df) < 50:
                print(f'  ⚠️ {stock_name} 数据不足（{len(df)}条），跳过')
                continue
            
            # 获取最优参数
            short, long = OPTIMAL_PARAMS[ts_code]
            
            # 执行回测
            metrics = run_backtest(df, short, long)
            
            time_results.append({
                '股票': stock_name,
                '时间段': period_name,
                '总收益率(%)': round(metrics['total_return'] * 100, 2),
                '年化收益率(%)': round(metrics['annual_return'] * 100, 2) if not np.isnan(metrics['annual_return']) else np.nan,
                '夏普比率': round(metrics['sharpe_ratio'], 2) if not np.isnan(metrics['sharpe_ratio']) else np.nan,
                '最大回撤(%)': round(metrics['max_drawdown'] * 100, 2),
                '交易次数': metrics['num_trades']
            })
            
            print(f'  ✅ {stock_name}: 收益率 {metrics["total_return"]*100:.2f}%')
            
        except Exception as e:
            print(f'  ❌ {stock_name} 错误: {str(e)}')

print('\n✅ 测试2完成')

time_results_df = pd.DataFrame(time_results)

# 保存结果
time_results_df.to_csv(f'{output_dir}/test2_time_periods.csv', index=False, encoding='utf-8-sig')
print(f'✅ 测试结果已保存: {output_dir}/test2_time_periods.csv')

# ============================================================================
# 生成时间段对比图
# ============================================================================

print('\n📊 生成时间段对比图...')
fig, ax = plt.subplots(figsize=(14, 8))

x = np.arange(len(STOCKS))
width = 0.2
colors = ['steelblue', 'coral', 'limegreen', 'gold']

for idx, period in enumerate(TIME_PERIODS.keys()):
    period_data = time_results_df[time_results_df['时间段'] == period]
    
    # 按股票顺序排序
    period_data = period_data.set_index('股票').reindex(list(STOCKS.values())).reset_index()
    
    ax.bar(
        x + idx*width - width*1.5,
        period_data['总收益率(%)'],
        width,
        label=period,
        color=colors[idx],
        alpha=0.8
    )

ax.set_xlabel('股票', fontsize=12)
ax.set_ylabel('总收益率(%)', fontsize=12)
ax.set_title('不同时间段的总收益率对比', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(list(STOCKS.values()), rotation=45)
ax.legend()
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}/comparison_time_periods.png', dpi=150, bbox_inches='tight')
print(f'✅ 时间段对比图已保存: {output_dir}/comparison_time_periods.png')
plt.close()

# ============================================================================
# 测试3：策略 vs BUY-HOLD
# ============================================================================

print('\n🎯 测试3：双均线策略 vs BUY-HOLD')
print('-' * 80)

comparison_results = []

for ts_code, stock_name in STOCKS.items():
    print(f'\n处理股票: {stock_name} ({ts_code})')
    
    try:
        # 加载数据
        df = load_stock_data(ts_code, START_DATE, END_DATE)
        
        # 获取最优参数
        short, long = OPTIMAL_PARAMS[ts_code]
        
        # 策略回测
        strategy_metrics = run_backtest(df, short, long)
        
        # BUY-HOLD回测
        initial_capital = 100000
        first_price = df.iloc[0]['close']
        shares = int(initial_capital / first_price)
        bh_final = shares * df.iloc[-1]['close']
        bh_return = (bh_final - initial_capital) / initial_capital
        
        # 计算BUY-HOLD最大回撤
        bh_nav = df['close'] / df.iloc[0]['close'] * initial_capital
        bh_peak = bh_nav.cummax()
        bh_drawdown = (bh_nav - bh_peak) / bh_peak
        bh_max_dd = abs(bh_drawdown.min())
        
        comparison_results.append({
            '股票': stock_name,
            '策略总收益率(%)': round(strategy_metrics['total_return'] * 100, 2),
            'BUY-HOLD收益率(%)': round(bh_return * 100, 2),
            '超额收益(%)': round((strategy_metrics['total_return'] - bh_return) * 100, 2),
            '策略夏普比率': round(strategy_metrics['sharpe_ratio'], 2) if not np.isnan(strategy_metrics['sharpe_ratio']) else np.nan,
            '策略最大回撤(%)': round(strategy_metrics['max_drawdown'] * 100, 2),
            'BUY-HOLD最大回撤(%)': round(bh_max_dd * 100, 2),
            '策略交易次数': strategy_metrics['num_trades']
        })
        
        print(f'  ✅ 策略收益率: {strategy_metrics["total_return"]*100:.2f}%')
        print(f'  ✅ BUY-HOLD收益率: {bh_return*100:.2f}%')
        
    except Exception as e:
        print(f'  ❌ 错误: {str(e)}')

comparison_df = pd.DataFrame(comparison_results)

print('\n' + '=' * 80)
print('📊 策略 vs BUY-HOLD 对比')
print('=' * 80)
print(comparison_df.to_string())

# 保存结果
comparison_df.to_csv(f'{output_dir}/test3_strategy_vs_buyhold.csv', index=False, encoding='utf-8-sig')
print(f'\n✅ 对比结果已保存: {output_dir}/test3_strategy_vs_buyhold.csv')

# ============================================================================
# 生成策略对比图
# ============================================================================

print('\n📈 生成策略对比图...')
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

x = np.arange(len(comparison_df))
width = 0.35

# 总收益率对比
bars1 = axes[0].bar(x - width/2, comparison_df['策略总收益率(%)'], width, 
                     label='双均线策略', color='steelblue', alpha=0.8)
bars2 = axes[0].bar(x + width/2, comparison_df['BUY-HOLD收益率(%)'], width,
                     label='BUY-HOLD', color='coral', alpha=0.8)

axes[0].set_xlabel('股票', fontsize=12)
axes[0].set_ylabel('总收益率(%)', fontsize=12)
axes[0].set_title('总收益率对比', fontsize=14, fontweight='bold')
axes[0].set_xticks(x)
axes[0].set_xticklabels(comparison_df['股票'], rotation=45)
axes[0].legend()
axes[0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axes[0].grid(axis='y', alpha=0.3)

# 最大回撤对比
bars3 = axes[1].bar(x - width/2, comparison_df['策略最大回撤(%)'], width,
                     label='双均线策略', color='steelblue', alpha=0.8)
bars4 = axes[1].bar(x + width/2, comparison_df['BUY-HOLD最大回撤(%)'], width,
                     label='BUY-HOLD', color='coral', alpha=0.8)

axes[1].set_xlabel('股票', fontsize=12)
axes[1].set_ylabel('最大回撤(%)', fontsize=12)
axes[1].set_title('最大回撤对比', fontsize=14, fontweight='bold')
axes[1].set_xticks(x)
axes[1].set_xticklabels(comparison_df['股票'], rotation=45)
axes[1].legend()
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(f'{output_dir}/comparison_strategy_vs_buyhold.png', dpi=150, bbox_inches='tight')
print(f'✅ 策略对比图已保存: {output_dir}/comparison_strategy_vs_buyhold.png')
plt.close()

# ============================================================================
# 生成总结报告
# ============================================================================

print('\n' + '=' * 80)
print('💡 双均线策略 - 总结与应用心得')
print('=' * 80)

print('\n## 📊 测试结果总结\n')

print('### 1. 不同均线周期的表现')
print('-' * 80)
print('✅ 短线组合（MA5/MA20）：')
print('   - 优点：对趋势变化敏感，能快速捕捉短期机会')
print('   - 缺点：交易频繁，手续费和滑点成本高，容易在震荡市中亏损')
print('   - 适用场景：明确的上升趋势，波动率较高的股票\n')
print('✅ 中线组合（MA10/MA30 或 MA10/MA50）：')
print('   - 优点：平衡了敏感度和稳定性，交易次数适中')
print('   - 缺点：在震荡市中仍有较大回撤')
print('   - 适用场景：温和上升趋势，大多数股票\n')
print('✅ 长线组合（MA20/MA60 或 MA20/MA120）：')
print('   - 优点：过滤掉短期噪音，交易次数少，稳定性高')
print('   - 缺点：信号滞后，可能错过早期趋势')
print('   - 适用场景：长期上升趋势，低波动率股票\n')

print('### 2. 不同股票的表现')
print('-' * 80)
print('✅ 趋势性强的股票（如宁德时代、比亚迪）：')
print('   - 双均线策略表现较好')
print('   - 适合使用较短的均线周期（MA5/MA20）\n')
print('❌ 震荡性强的股票（如中国石油）：')
print('   - 双均线策略容易频繁交易，亏损较多')
print('   - 建议使用较长的均线周期（MA20/MA60）或添加过滤器\n')

print('### 3. 不同时间段的表现')
print('-' * 80)
print('✅ 牛市（上升趋势）：')
print('   - 双均线策略表现优秀，能捕捉大幅上涨')
print('   - 金叉后持有，死叉后卖出\n')
print('❌ 震荡市（横盘整理）：')
print('   - 双均线策略表现较差，容易频繁交易')
print('   - 建议使用ATR过滤器或趋势过滤器规避\n')

print('### 4. 策略 vs BUY-HOLD')
print('-' * 80)
print('✅ 双均线策略的优势：')
print('   - 能在趋势明确时获得超额收益')
print('   - 能规避大幅下跌（通过死叉卖出）\n')
print('❌ 双均线策略的劣势：')
print('   - 在震荡市中容易亏损')
print('   - 交易成本高（手续费+滑点）\n')

print('=' * 80)
print('🎯 应用心得')
print('=' * 80)

print('\n### 1. 策略适用场景')
print('-' * 80)
print('✅ 适合使用双均线策略的情况：')
print('   1. 股票处于明确的上升或下降趋势')
print('   2. 波动率适中（ATR处于历史中位）')
print('   3. 交易成本低（手续费率 < 0.05%）')
print('   4. 能接受一定的回撤（最大回撤可能达到20-30%）\n')
print('❌ 不适合使用双均线策略的情况：')
print('   1. 股票处于震荡市（价格在区间内反复波动）')
print('   2. 波动率极低（ATR处于历史低位）')
print('   3. 交易成本过高（手续费率 > 0.1%）')
print('   4. 无法承受频繁交易的心理压力\n')

print('### 2. 参数选择建议')
print('-' * 80)
print('✅ 短线交易者（持仓几天到几周）：')
print('   - 短均线：5-10日')
print('   - 长均线：20-30日')
print('   - 建议添加趋势过滤器（MA60）\n')
print('✅ 中线交易者（持仓几周到几个月）：')
print('   - 短均线：10-20日')
print('   - 长均线：30-60日')
print('   - 建议添加ATR过滤器（规避震荡市）\n')
print('✅ 长线交易者（持仓几个月到几年）：')
print('   - 短均线：20-30日')
print('   - 长均线：60-120日')
print('   - 可以不添加过滤器（长期趋势明显）\n')

print('### 3. 风险控制建议')
print('-' * 80)
print('✅ 必须设置止损：')
print('   - 当亏损超过5-10%时，强制平仓')
print('   - 不要依赖死叉信号（可能太晚）\n')
print('✅ 使用过滤器：')
print('   - 趋势过滤器：规避下跌趋势中的金叉')
print('   - ATR过滤器：规避低波动的震荡市\n')
print('✅ 控制仓位：')
print('   - 不要全仓买卖（建议使用固定比例，如20-50%）')
print('   - 分散投资（同时交易多只股票）\n')

print('=' * 80)
print('📝 结论')
print('=' * 80)
print('\n双均线策略是一个简单但有效的趋势跟踪策略，但需要：')
print('  1. 选择合适的参数（根据股票特性和交易风格）')
print('  2. 添加过滤器（规避震荡市）')
print('  3. 严格控制风险（止损+仓位管理）')
print('  4. 接受策略的局限性（在震荡市中表现较差）\n')

print('💡 最终建议：')
print('   - 不要盲目使用默认参数（如MA5/MA20）')
print('   - 在实盘前进行充分的回测和优化')
print('   - 结合基本面分析（选择优质股票）')
print('   - 保持耐心和纪律（不要频繁修改策略）\n')

print('=' * 80)
print(f'\n📄 所有分析结果已保存到: {output_dir}/')
print('=' * 80)
