#!/usr/bin/env python3
"""
diagnose_and_adjust_stocks.py — 诊断分析股票数据，检查缺失值、描述性统计量，并处理复权
用法: python3 diagnose_and_adjust_stocks.py
"""

import json
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import numpy as np

# ============ 配置区 ============

# Tushare token
TOKEN = "023457f3e3911d11db046cb10165c91ade16348d70ee76af3102262c"

# 股票列表：(ts_code, 名称英文缩写)
STOCKS = [
    ("300750.SZ", "ningde_times"),
    ("601318.SH", "ping_an"),
    ("600519.SH", "moutai"),
    ("601857.SH", "petro_china"),
    ("002594.SZ", "byd"),
]

# 数据目录
DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = DATA_DIR / "adjusted"  # 复权后数据保存目录


# ============ 工具函数 ============

def fetch_tushare_http(api_name: str, params: dict) -> pd.DataFrame:
    """通过直接HTTP API获取数据（绕过代理）"""
    import urllib.request
    import urllib.error
    
    url = "http://api.tushare.pro"
    payload = json.dumps({
        "api_name": api_name,
        "token": TOKEN,
        "params": params,
        "fields": "",
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    # 绕过本地代理
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络请求失败: {e}")
    
    code = result.get("code", -1)
    if code != 0:
        raise RuntimeError(f"Tushare 返回错误 code={code}: {result.get('msg')}")
    
    data = result["data"]
    cols = data["fields"]
    rows = data["items"]
    return pd.DataFrame(rows, columns=cols)


def load_stock_data(ts_code: str, name: str) -> pd.DataFrame:
    """加载已保存的CSV文件"""
    code_simple = ts_code.split(".")[0]
    filename = f"{name}_{code_simple}_daily.csv"
    filepath = DATA_DIR / filename
    
    if not filepath.exists():
        print(f"  ⚠️  文件不存在：{filepath}")
        return pd.DataFrame()
    
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    print(f"  ✓ 已加载 {len(df)} 条记录")
    return df


def diagnose_data(df: pd.DataFrame, ts_code: str) -> dict:
    """诊断数据分析：检查缺失值、描述性统计量"""
    print(f"\n{'='*60}")
    print(f"数据诊断报告：{ts_code}")
    print(f"{'='*60}\n")
    
    diagnosis = {}
    
    # 1. 基本信息
    print("1. 基本信息：")
    print(f"   - 记录数：{len(df)}")
    print(f"   - 字段数：{len(df.columns)}")
    print(f"   - 字段列表：{', '.join(df.columns.tolist())}")
    
    if 'trade_date' in df.columns:
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        print(f"   - 日期范围：{df['trade_date'].min()} ~ {df['trade_date'].max()}")
        diagnosis['date_range'] = (df['trade_date'].min(), df['trade_date'].max())
    
    diagnosis['record_count'] = len(df)
    diagnosis['columns'] = df.columns.tolist()
    
    # 2. 缺失值检查
    print("\n2. 缺失值检查：")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        '缺失数': missing,
        '缺失比例(%)': missing_pct
    })
    missing_df = missing_df[missing_df['缺失数'] > 0]
    
    if len(missing_df) == 0:
        print("   ✓ 无缺失值")
        diagnosis['missing'] = '无'
    else:
        print(missing_df)
        diagnosis['missing'] = missing_df.to_dict()
    
    # 3. 描述性统计量
    print("\n3. 描述性统计量：")
    numeric_cols = ['open', 'high', 'low', 'close', 'vol', 'amount']
    numeric_cols = [col for col in numeric_cols if col in df.columns]
    
    if numeric_cols:
        stats = df[numeric_cols].describe().round(2)
        print(stats)
        diagnosis['stats'] = stats.to_dict()
    
    # 4. 检查是否有复权因子字段
    print("\n4. 复权检查：")
    if 'adj_factor' in df.columns:
        print("   ✓ 数据已包含复权因子")
        diagnosis['is_adjusted'] = True
    else:
        print("   ⚠️  数据未包含复权因子，可能需要复权处理")
        diagnosis['is_adjusted'] = False
    
    # 5. 检查价格合理性（简单检查）
    print("\n5. 价格合理性检查：")
    price_cols = ['open', 'high', 'low', 'close']
    price_cols = [col for col in price_cols if col in df.columns]
    
    if price_cols:
        for col in price_cols:
            if col in df.columns:
                min_price = df[col].min()
                max_price = df[col].max()
                print(f"   - {col}: [{min_price:.2f}, {max_price:.2f}]")
        
        # 检查高低价关系
        invalid_hl = (df['high'] < df['low']).sum()
        invalid_oh = (df['open'] > df['high']).sum()
        invalid_ol = (df['open'] < df['low']).sum()
        invalid_ch = (df['close'] > df['high']).sum()
        invalid_cl = (df['close'] < df['low']).sum()
        
        if invalid_hl + invalid_oh + invalid_ol + invalid_ch + invalid_cl > 0:
            print(f"   ⚠️  发现价格异常：")
            print(f"      - high < low: {invalid_hl} 条")
            print(f"      - open > high: {invalid_oh} 条")
            print(f"      - open < low: {invalid_ol} 条")
            print(f"      - close > high: {invalid_ch} 条")
            print(f"      - close < low: {invalid_cl} 条")
        else:
            print("   ✓ 价格关系合理（high >= low, open/close 在 [low, high] 范围内）")
    
    print(f"\n{'='*60}\n")
    
    return diagnosis


def adjust_data_with_factor(ts_code: str, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    使用复权因子对数据进行前复权处理
    
    前复权公式：复权价格 = 实际价格 × (复权因子 / 最新复权因子)
    """
    print(f"正在对 {ts_code} 进行复权处理...")
    
    try:
        # 获取复权因子
        print("  - 正在获取复权因子...")
        adj_df = fetch_tushare_http(
            "adj_factor",
            {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
        )
        
        if adj_df.empty:
            print("  ⚠️  未获取到复权因子，跳过复权处理")
            return df
        
        # 转换日期格式并排序
        adj_df['trade_date'] = pd.to_datetime(adj_df['trade_date'], format='%Y%m%d')
        adj_df = adj_df.sort_values('trade_date').reset_index(drop=True)
        
        print(f"  ✓ 获取到 {len(adj_df)} 条复权因子记录")
        
        # 合并数据
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        merged = pd.merge(df, adj_df[['trade_date', 'adj_factor']], on='trade_date', how='left')
        
        # 检查复权因子缺失情况
        missing_adj = merged['adj_factor'].isnull().sum()
        if missing_adj > 0:
            print(f"  ⚠️  {missing_adj} 条记录缺少复权因子，将向前填充")
            merged['adj_factor'] = merged['adj_factor'].ffill()
        
        # 前复权处理：使用最新的复权因子作为基准
        latest_adj_factor = merged['adj_factor'].iloc[-1]  # 最新日期的复权因子
        
        print(f"  - 最新复权因子：{latest_adj_factor:.4f}")
        print("  - 正在进行前复权处理...")
        
        # 计算前复权价格
        price_cols = ['open', 'high', 'low', 'close', 'pre_close']
        price_cols = [col for col in price_cols if col in merged.columns]
        
        for col in price_cols:
            merged[f'{col}_adj'] = merged[col] * (merged['adj_factor'] / latest_adj_factor)
        
        # 替换原始价格为复权后价格
        for col in price_cols:
            merged[col] = merged[f'{col}_adj']
            merged = merged.drop(columns=[f'{col}_adj'])
        
        # 重新计算涨跌幅（基于复权后价格）
        merged['change'] = merged['close'] - merged['pre_close']
        merged['pct_chg'] = (merged['change'] / merged['pre_close'] * 100).round(2)
        
        # 删除复权因子列
        if 'adj_factor' in merged.columns:
            merged = merged.drop(columns=['adj_factor'])
        
        print("  ✓ 复权处理完成")
        
        return merged
        
    except Exception as e:
        print(f"  ❌ 复权处理失败：{e}")
        traceback.print_exc()
        return df


def save_adjusted_data(df: pd.DataFrame, ts_code: str, name: str) -> str:
    """保存复权后的数据"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    code_simple = ts_code.split(".")[0]
    filename = f"{name}_{code_simple}_daily_adjusted.csv"
    filepath = OUTPUT_DIR / filename
    
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"  ✓ 复权数据已保存至：{filepath}")
    
    return str(filepath)


def main():
    """主函数：诊断分析所有股票数据，并进行复权处理"""
    
    print("="*60)
    print("股票数据诊断与复权处理")
    print("="*60)
    print()
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"复权数据保存目录：{OUTPUT_DIR}")
    print()
    
    # 计算日期范围
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365*2)
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    print(f"数据日期范围：{start_str} ~ {end_str}")
    print()
    
    # 诊断报告汇总
    all_diagnoses = {}
    
    # 处理每只股票
    for ts_code, name in STOCKS:
        print(f"\n{'#'*60}")
        print(f"处理股票：{name} ({ts_code})")
        print(f"{'#'*60}\n")
        
        # 1. 加载数据
        print("步骤1：加载数据...")
        df = load_stock_data(ts_code, name)
        
        if df.empty:
            print("  ❌ 数据加载失败，跳过此股票")
            continue
        
        # 2. 诊断分析
        print("\n步骤2：诊断分析...")
        diagnosis = diagnose_data(df, ts_code)
        all_diagnoses[ts_code] = diagnosis
        
        # 3. 复权处理
        print("步骤3：复权处理...")
        df_adjusted = adjust_data_with_factor(ts_code, df, start_str, end_str)
        
        # 4. 保存复权后数据
        print("\n步骤4：保存复权后数据...")
        save_adjusted_data(df_adjusted, ts_code, name)
        
        print(f"\n✅ {name} ({ts_code}) 处理完成\n")
        
        # 延迟60秒以避免API频率限制（adj_factor接口限制1次/分钟）
        if ts_code != STOCKS[-1][0]:  # 不是最后一只股票
            print(f"⏳ 等待60秒以避免API频率限制...")
            time.sleep(60)
    
    # 打印汇总报告
    print("\n" + "="*60)
    print("汇总报告")
    print("="*60)
    print(f"\n成功处理：{len(all_diagnoses)}/{len(STOCKS)} 只股票")
    print()
    
    for ts_code, diag in all_diagnoses.items():
        print(f"- {ts_code}:")
        print(f"  记录数：{diag['record_count']}")
        print(f"  日期范围：{diag['date_range'][0].date()} ~ {diag['date_range'][1].date()}")
        print(f"  缺失值：{diag['missing']}")
        print(f"  是否已复权：{'是' if diag['is_adjusted'] else '否（已处理）'}")
        print()
    
    print("="*60)
    print("所有任务完成！")
    print("="*60)
    print(f"\n复权后数据已保存至：{OUTPUT_DIR}")
    print()


if __name__ == "__main__":
    main()
