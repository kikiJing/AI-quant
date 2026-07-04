#!/usr/bin/env python3
"""
fetch_stocks.py — 获取多只代表性A股近2年日线数据，保存为CSV
用法: python3 fetch_stocks.py
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen, ProxyHandler, build_opener, install_opener

import pandas as pd

# ============ 配置区 ============

# Tushare Token
TOKEN = "023457f3e3911d11db046cb10165c91ade16348d70ee76af3102262c"

# 股票列表：(ts_code, 名称英文缩写)
STOCKS = [
    ("300750.SZ", "ningde_times"),
    ("601318.SH", "ping_an"),
    ("600519.SH", "moutai"),
    ("601857.SH", "petro_china"),
    ("002594.SZ", "byd"),
]

# 数据字段（所有可用字段）
FIELDS = None  # None 表示保存所有字段

# 数据目录
DATA_DIR = Path(__file__).parent / "data"


# ============ 核心函数 ============

def fetch_tushare(api_name: str, params: dict) -> pd.DataFrame:
    """通过 Tushare HTTP API 获取数据（绕过代理）。"""
    url = "http://api.tushare.pro"
    payload = json.dumps({
        "api_name": api_name,
        "token": TOKEN,
        "params": params,
        "fields": "",
    }).encode("utf-8")

    req = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    # 绕过本地代理
    proxy_handler = ProxyHandler({})
    opener = build_opener(proxy_handler)
    install_opener(opener)

    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"网络请求失败: {e}")

    code = result.get("code", -1)
    if code != 0:
        raise RuntimeError(f"Tushare 返回错误 code={code}: {result.get('msg')}")

    data = result["data"]
    cols = data["fields"]
    rows = data["items"]
    return pd.DataFrame(rows, columns=cols)


def fetch_stock_data(ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    获取单只股票的日线数据。

    参数:
        ts_code: 股票代码（如 "300750.SZ"）
        start_date: 开始日期（YYYYMMDD格式）
        end_date: 结束日期（YYYYMMDD格式）

    返回:
        DataFrame，包含FIELDS定义的字段
    """
    try:
        # 调用 Tushare HTTP API 获取数据
        df = fetch_tushare("daily", {"ts_code": ts_code, "start_date": start_date, "end_date": end_date})

        if df.empty:
            print(f"  ⚠️  未获取到数据（{ts_code}）")
            return pd.DataFrame()

        # 如果指定了字段，则只选择指定字段（FIELDS=None 时保存所有字段）
        if FIELDS is not None:
            available_fields = [f for f in FIELDS if f in df.columns]
            df = df[available_fields]

        # 类型转换：数值列转为numeric
        numeric_cols = ["open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # trade_date 转 datetime，并排序（API返回是按日期降序）
        df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
        df = df.sort_values("trade_date").reset_index(drop=True)

        return df

    except Exception as e:
        print(f"  ❌ 获取失败（{ts_code}）：{e}")
        return pd.DataFrame()


def save_to_csv(df: pd.DataFrame, ts_code: str, name: str) -> str:
    """
    将数据保存为CSV文件。

    参数:
        df: 数据DataFrame
        ts_code: 股票代码
        name: 股票名称英文缩写

    返回:
        保存的文件路径
    """
    # 生成文件名：{name}_{code}_daily.csv
    code_simple = ts_code.split(".")[0]  # 去掉交易所后缀
    filename = f"{name}_{code_simple}_daily.csv"
    filepath = DATA_DIR / filename

    # 保存为CSV（utf-8-sig编码兼容中文Excel）
    df.to_csv(filepath, index=False, encoding="utf-8-sig")

    return str(filepath)


def main():
    """主函数：连接Tushare，获取所有股票数据并保存。"""

    # 1. 检查 Tushare 连接
    print("=" * 60)
    print("正在检查 Tushare Pro 连接...")
    try:
        # 简单测试：获取一只股票的基本信息
        df = fetch_tushare("stock_basic", {"list_status": "L", "fields": "ts_code"})
        if df is not None and not df.empty:
            print(f"✅ 连接成功 ✓  — 可查询 {len(df)} 条股票基本信息")
        else:
            print("❌ 连接成功但查询返回为空")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        sys.exit(1)
    print()

    # 2. 创建数据目录
    DATA_DIR.mkdir(exist_ok=True)
    print(f"数据保存目录：{DATA_DIR}")
    print()

    # 3. 计算日期范围（近2年）
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * 2)

    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")

    print(f"获取时间范围：{start_str} ~ {end_str}（近2年）")
    print("=" * 60)
    print()

    # 4. 循环获取每只股票的数据
    success_count = 0
    failed_stocks = []

    for ts_code, name in STOCKS:
        print(f"正在获取 {name}（{ts_code}）...")

        # 获取数据
        df = fetch_stock_data(ts_code, start_str, end_str)

        if df.empty:
            failed_stocks.append((ts_code, name))
            print()
            continue

        # 保存为CSV
        filepath = save_to_csv(df, ts_code, name)

        # 打印统计信息
        print(f"  ✅ 获取到 {len(df)} 条记录")
        print(f"     日期范围：{df['trade_date'].min().date()} ~ {df['trade_date'].max().date()}")
        print(f"     保存至：{filepath}")
        print()

        success_count += 1

    # 5. 打印汇总信息
    print("=" * 60)
    print(f"完成！成功获取 {success_count}/{len(STOCKS)} 只股票")

    if failed_stocks:
        print("\n失败股票：")
        for ts_code, name in failed_stocks:
            print(f"  ❌ {name}（{ts_code}）")

    print("\n前5条数据示例（最后一只成功股票）：")
    if success_count > 0:
        print(df[["trade_date", "open", "high", "low", "close", "vol", "amount"]].head())


if __name__ == "__main__":
    main()
