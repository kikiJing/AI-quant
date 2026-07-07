"""
均线策略核心模块

包含技术指标计算函数：
- 简单移动平均（MA）
- 指数移动平均（EMA）
- 平均真实波幅（ATR）
- 信号生成（含趋势过滤器和ATR过滤器）
"""

import pandas as pd
import numpy as np


def calculate_ma(series: pd.Series, window: int) -> pd.Series:
    """
    计算简单移动平均（MA）
    
    参数：
        series: 价格序列（通常是close）
        window: 均线周期
    
    返回：
        MA序列，前window-1个值为NaN
    """
    return series.rolling(window=window).mean()


def calculate_ema(series: pd.Series, window: int) -> pd.Series:
    """
    计算指数移动平均（EMA）
    
    参数：
        series: 价格序列（通常是close）
        window: 均线周期
    
    返回：
        EMA序列
    """
    return series.ewm(span=window, adjust=False).mean()


def calculate_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    计算平均真实波幅（ATR）
    
    参数：
        df: DataFrame，必须包含 'high', 'low', 'close' 列
        window: ATR计算周期
    
    返回：
        ATR序列
    """
    high = df['high']
    low = df['low']
    close_prev = df['close'].shift(1)
    
    # 计算真实波幅（TR）
    tr1 = high - low
    tr2 = abs(high - close_prev)
    tr3 = abs(low - close_prev)
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 计算ATR（简单移动平均）
    atr = tr.rolling(window=window).mean()
    
    return atr


def calculate_atr_percentile(atr: pd.Series, lookback: int = 100) -> pd.Series:
    """
    计算ATR的历史百分位
    
    参数：
        atr: ATR序列
        lookback: 历史回看天数
    
    返回：
        ATR百分位序列（0-100）
    """
    def percentile_rank(x):
        """计算最后一个值在序列中的百分位排名"""
        if len(x) == 0 or pd.isna(x.iloc[-1]):
            return np.nan
        return (x.rank(pct=True).iloc[-1]) * 100
    
    atr_percentile = atr.rolling(window=lookback).apply(percentile_rank, raw=False)
    
    return atr_percentile


def generate_signals(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """
    生成交易信号（含过滤器）
    
    参数：
        df: DataFrame，必须包含 'ts_code', 'trade_date', 'open', 'high', 'low', 'close' 列
        params: 策略参数字典，包含：
            - short_window: 短均线周期
            - long_window: 长均线周期
            - ma_type: 'MA' 或 'EMA'
            - trend_filter: 是否启用趋势过滤器
            - trend_window: 趋势过滤器周期
            - atr_filter: 是否启用ATR过滤器
            - atr_window: ATR计算周期
            - atr_percentile: ATR百分位阈值
            - atr_lookback: ATR历史回看天数
    
    返回：
        DataFrame，新增列：
            - short_ma: 短均线
            - long_ma: 长均线
            - trend_ma: 趋势均线（如果启用趋势过滤器）
            - atr: ATR值
            - atr_percentile: ATR百分位
            - golden_cross: 金叉标记
            - death_cross: 死叉标记
            - signal: 交易信号（1=买入，-1=卖出，0=无操作）
    """
    df = df.copy()
    
    # 1. 计算均线
    if params['ma_type'].upper() == 'EMA':
        df['short_ma'] = calculate_ema(df['close'], params['short_window'])
        df['long_ma'] = calculate_ema(df['close'], params['long_window'])
        if params.get('trend_filter', False):
            df['trend_ma'] = calculate_ema(df['close'], params['trend_window'])
    else:
        df['short_ma'] = calculate_ma(df['close'], params['short_window'])
        df['long_ma'] = calculate_ma(df['close'], params['long_window'])
        if params.get('trend_filter', False):
            df['trend_ma'] = calculate_ma(df['close'], params['trend_window'])
    
    # 2. 计算ATR
    if params.get('atr_filter', False):
        df['atr'] = calculate_atr(df, params['atr_window'])
        df['atr_percentile'] = calculate_atr_percentile(df['atr'], params['atr_lookback'])
    
    # 3. 识别金叉和死叉
    df['golden_cross'] = (df['short_ma'].shift(1) < df['long_ma'].shift(1)) & \
                         (df['short_ma'] > df['long_ma'])
    df['death_cross'] = (df['short_ma'].shift(1) > df['long_ma'].shift(1)) & \
                        (df['short_ma'] < df['long_ma'])
    
    # 4. 应用过滤器，生成交易信号
    df['signal'] = 0
    
    # 买入信号条件
    buy_condition = df['golden_cross'].copy()
    if params.get('trend_filter', False):
        buy_condition &= (df['close'] > df['trend_ma']) & \
                        (df['short_ma'] > df['trend_ma'])
    if params.get('atr_filter', False):
        buy_condition &= (df['atr_percentile'] > params['atr_percentile'])
    
    df.loc[buy_condition, 'signal'] = 1
    
    # 卖出信号条件
    sell_condition = df['death_cross'].copy()
    if params.get('trend_filter', False):
        sell_condition &= (df['close'] < df['trend_ma']) | \
                         (df['short_ma'] < df['trend_ma'])
    if params.get('atr_filter', False):
        sell_condition &= (df['atr_percentile'] > params['atr_percentile'])
    
    df.loc[sell_condition, 'signal'] = -1
    
    return df


if __name__ == '__main__':
    # 简单测试
    print("均线策略模块加载成功")
    print("可用函数：")
    print("  - calculate_ma(): 计算简单移动平均")
    print("  - calculate_ema(): 计算指数移动平均")
    print("  - calculate_atr(): 计算ATR")
    print("  - calculate_atr_percentile(): 计算ATR百分位")
    print("  - generate_signals(): 生成交易信号")
