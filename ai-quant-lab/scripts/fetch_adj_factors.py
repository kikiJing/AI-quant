#!/usr/bin/env python3
"""
fetch_adj_factors.py — 分步获取复权因子（因API限制1次/小时）
用法: python3 fetch_adj_factors.py
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd

# Tushare token
TOKEN = "023457f3e3911d11db046cb10165c91ade16348d70ee76af3102262c"

# 股票列表
STOCKS = [
    ("300750.SZ", "ningde_times"),
    ("601318.SH", "ping_an"),
    ("600519.SH", "moutai"),
    ("601857.SH", "petro_china"),
    ("002594.SZ", "byd"),
]

# 保存目录
OUTPUT_DIR = Path(__file__).parent / "data" / "adj_factors"


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


def fetch_and_save_adj_factor(ts_code: str, name: str, start_date: str, end_date: str):
    """获取并保存复权因子"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    code_simple = ts_code.split(".")[0]
    output_file = OUTPUT_DIR / f"{name}_{code_simple}_adj_factor.csv"
    
    # 检查是否已存在
    if output_file.exists():
        print(f"  ✓ 复权因子已存在：{output_file}")
        return True
    
    try:
        print(f"  - 正在获取复权因子...")
        adj_df = fetch_tushare_http(
            "adj_factor",
            {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
        )
        
        if adj_df.empty:
            print(f"  ⚠️  未获取到复权因子")
            return False
        
        # 保存
        adj_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"  ✓ 已保存 {len(adj_df)} 条复权因子至：{output_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ 获取失败：{e}")
        return False


def main():
    from datetime import datetime, timedelta
    
    print("="*60)
    print("分步获取复权因子")
    print("="*60)
    print()
    print("注意：因Tushare API限制（1次/小时），")
    print("您需要分多次运行此脚本，每次间隔至少1小时。")
    print()
    
    # 计算日期范围
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365*2)
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    print(f"日期范围：{start_str} ~ {end_str}")
    print()
    
    # 检查哪些股票还需要获取
    stocks_to_fetch = []
    for ts_code, name in STOCKS:
        code_simple = ts_code.split(".")[0]
        output_file = OUTPUT_DIR / f"{name}_{code_simple}_adj_factor.csv"
        
        if output_file.exists():
            print(f"✓ {name} ({ts_code}) — 已获取")
        else:
            print(f"✗ {name} ({ts_code}) — 待获取")
            stocks_to_fetch.append((ts_code, name))
    
    print()
    
    if not stocks_to_fetch:
        print("✅ 所有股票的复权因子已获取完成！")
        print(f"保存位置：{OUTPUT_DIR}")
        return
    
    # 获取第一个待获取的股票
    ts_code, name = stocks_to_fetch[0]
    print(f"正在获取 {name} ({ts_code}) 的复权因子...")
    print()
    
    success = fetch_and_save_adj_factor(ts_code, name, start_str, end_str)
    
    if success:
        print()
        print("✅ 本次获取成功！")
        print()
        
        if len(stocks_to_fetch) > 1:
            print(f"剩余待获取：{len(stocks_to_fetch)-1} 只股票")
            print("请等待1小时后再次运行此脚本以继续获取。")
        else:
            print("✅ 所有复权因子已获取完成！")
    else:
        print()
        print("❌ 获取失败，请检查错误信息并重试。")
    
    print()
    print(f"复权因子保存位置：{OUTPUT_DIR}")


if __name__ == "__main__":
    main()
