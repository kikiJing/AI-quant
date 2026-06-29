#!/usr/bin/env python3
"""
fetch_smic.py — 获取中芯国际（688981.SH）近一年行情数据，保存为 parquet
用法: python3 fetch_smic.py
"""

import json
import os
import sys
import urllib.request
import urllib.error
import pandas as pd

TOKEN = "023457f3e3911d11db046cb10165c91ade16348d70ee76af3102262c"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "smic_688981_daily.parquet")

FIELDS = ["ts_code", "trade_date", "open", "high", "low", "close",
          "pre_close", "change", "pct_chg", "vol", "amount"]


def fetch_tushare(api_name: str, params: dict, fields: str = "") -> pd.DataFrame:
    """通过 Tushare HTTP API 获取数据（绕过代理）。"""
    url = "http://api.tushare.pro"
    payload = json.dumps({
        "api_name": api_name,
        "token": TOKEN,
        "params": params,
        "fields": fields,
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


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("正在获取中芯国际（688981.SH）近一年日线数据...")

    # Tushare 日期格式：YYYYMMDD，start_date 要早于 end_date
    df = fetch_tushare(
        "daily",
        params={"ts_code": "688981.SH", "start_date": "20240701", "end_date": "20250629"},
    )

    if df.empty:
        print("未获取到数据，请检查 token 或股票代码。")
        sys.exit(1)

    # 类型转换
    numeric_cols = ["open", "high", "low", "close", "pre_close", "change",
                    "pct_chg", "vol", "amount"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # trade_date 转 datetime，并排序（API 返回是按日期降序）
    df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
    df = df.sort_values("trade_date").reset_index(drop=True)

    print(f"获取到 {len(df)} 条记录，日期范围：{df['trade_date'].min().date()} ~ {df['trade_date'].max().date()}")

    # 保存为 CSV（无需额外依赖）
    csv_file = os.path.join(OUTPUT_DIR, "smic_688981_daily.csv")
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    print(f"数据已保存至：{csv_file}")

    print("\n前 5 条：")
    print(df[["trade_date", "open", "high", "low", "close", "vol", "amount"]].head())
    print("\n后 5 条：")
    print(df[["trade_date", "open", "high", "low", "close", "vol", "amount"]].tail())


if __name__ == "__main__":
    main()
