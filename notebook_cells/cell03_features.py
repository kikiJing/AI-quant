# ============================================================
# Cell 3：数据清洗与特征工程
# ============================================================
# 类型转换
df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
for col in ["open", "high", "low", "close", "pre_close",
            "change", "pct_chg", "vol", "amount"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.sort_values("trade_date").reset_index(drop=True)

# ---- 均线 ----
df["ma5"]   = df["close"].rolling(5).mean()
df["ma20"]  = df["close"].rolling(20).mean()
df["ma60"]  = df["close"].rolling(60).mean()

# ---- RSI(14) ----
def calc_rsi(s, period=14):
    delta = s.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss
    return 100 - 100 / (1 + rs)

df["rsi14"] = calc_rsi(df["close"])

# ---- MACD(12,26,9) ----
def calc_macd(s, fast=12, slow=26, signal=9):
    ema_fast = s.ewm(span=fast,  adjust=False).mean()
    ema_slow = s.ewm(span=slow,  adjust=False).mean()
    dif      = ema_fast - ema_slow
    dea      = dif.ewm(span=signal, adjust=False).mean()
    hist     = (dif - dea) * 2
    return dif, dea, hist

df["macd_dif"], df["macd_dea"], df["macd_hist"] = calc_macd(df["close"])

# 保存 CSV
import os
os.makedirs("data", exist_ok=True)
df.to_csv("data/smic_688981_daily.csv", index=False, encoding="utf-8-sig")
print(f"✅ 数据已保存至 data/smic_688981_daily.csv")
print(f"区间：{df['trade_date'].min().date()} ~ {df['trade_date'].max().date()}")
print(f"总记录：{len(df)}\n")
df.tail(3)
