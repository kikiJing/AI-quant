# ============================================================
# Cell 6：技术分析结论 + 综合买卖建议
# ============================================================
from IPython.display import display, Markdown
import pandas as pd

latest   = df.iloc[-1]
prev     = df.iloc[-2]
change   = float(latest["close"]) - float(prev["close"])
pct      = change / float(prev["close"]) * 100
high_52  = df["high"].max()
low_52   = df["low"].min()
avg_vol  = df["vol"].mean()
up_days  = (df["pct_chg"] > 0).sum()
dn_days  = (df["pct_chg"] < 0).sum()
rsi_now  = df["rsi14"].iloc[-1]
macd_now = df["macd_dif"].iloc[-1]
macd_sig = df["macd_dea"].iloc[-1]
pos_pct  = (latest["close"] - low_52) / (high_52 - low_52) * 100
vol_ratio = latest["vol"] / avg_vol

# ---- 均线信号 ----
ma_bull = (
    pd.notna(latest["ma5"]) and pd.notna(latest["ma20"]) and pd.notna(latest["ma60"]) and
    latest["ma5"] > latest["ma20"] > latest["ma60"]
)
ma_bear = (
    pd.notna(latest["ma5"]) and pd.notna(latest["ma20"]) and pd.notna(latest["ma60"]) and
    latest["ma5"] < latest["ma20"] < latest["ma60"]
)
if ma_bull:
    ma_signal = "多头排列（短期 > 中期 > 长期，趋势偏多）"
    ma_lvl    = "偏多"
elif ma_bear:
    ma_signal = "空头排列（短期 < 中期 < 长期，趋势偏空）"
    ma_lvl    = "偏空"
else:
    ma_signal = "均线纠缠，方向不明"
    ma_lvl    = "中性"

# ---- RSI 信号 ----
if pd.notna(rsi_now):
    if rsi_now > 70:
        rsi_sig = f"RSI = {rsi_now:.1f}，进入超买区间，注意回调风险"
        rsi_lvl = "超买"
    elif rsi_now < 30:
        rsi_sig = f"RSI = {rsi_now:.1f}，进入超卖区间，关注反弹机会"
        rsi_lvl = "超卖"
    else:
        rsi_sig = f"RSI = {rsi_now:.1f}，处于正常区间"
        rsi_lvl = "中性"
else:
    rsi_sig = "RSI 数据不足"
    rsi_lvl = "未知"

# ---- MACD 信号 ----
if pd.notna(macd_now) and pd.notna(macd_sig):
    if macd_now > macd_sig and macd_now > 0:
        macd_str = f"DIF({macd_now:.3f}) > DEA({macd_sig:.3f})，金叉且在零轴上方，多头强势"
        macd_lvl = "偏多"
    elif macd_now > macd_sig and macd_now <= 0:
        macd_str = f"DIF({macd_now:.3f}) > DEA({macd_sig:.3f})，金叉但位于零轴下方，反弹力度待观察"
        macd_lvl = "中性偏多"
    elif macd_now < macd_sig and macd_now < 0:
        macd_str = f"DIF({macd_now:.3f}) < DEA({macd_sig:.3f})，死叉且在零轴下方，空头强势"
        macd_lvl = "偏空"
    else:
        macd_str = f"DIF({macd_now:.3f}) < DEA({macd_sig:.3f})，死叉但位于零轴上方，调整力度待观察"
        macd_lvl = "中性偏空"
else:
    macd_str = "MACD 数据不足"
    macd_lvl = "未知"

# ---- 价格位置 ----
if pos_pct > 80:
    pos_str = f"当前价格处于近一年高位（分位 {pos_pct:.1f}%），追高需谨慎"
elif pos_pct < 20:
    pos_str = f"当前价格处于近一年低位（分位 {pos_pct:.1f}%），具备一定安全边际"
else:
    pos_str = f"当前价格处于近一年中部（分位 {pos_pct:.1f}%）"

# ---- 成交量 ----
if vol_ratio > 2:
    vol_str = f"今日成交量放大 {vol_ratio:.1f} 倍，市场关注度高"
elif vol_ratio < 0.5:
    vol_str = f"今日成交量萎缩至均量的 {vol_ratio:.1f} 倍，市场观望"
else:
    vol_str = f"今日成交量约为均量的 {vol_ratio:.1f} 倍，成交正常"

# ---- 综合评分 ----
score = 0
if ma_lvl == "偏多":   score += 2
if ma_lvl == "偏空":   score -= 2
if rsi_lvl == "超买":  score -= 1
if rsi_lvl == "超卖":  score += 1
if macd_lvl == "偏多":       score += 1
if macd_lvl == "中性偏多":   score += 0.5
if macd_lvl == "偏空":       score -= 1
if macd_lvl == "中性偏空":   score -= 0.5
if pos_pct > 80:  score -= 1
if pos_pct < 20:  score += 1
if vol_ratio > 2:  score += 0.5

if score >= 3:
    rec = "买入"
    rec_emoji = "🟢"
elif score >= 1:
    rec = "谨慎买入 / 持有"
    rec_emoji = "🟡"
elif score > -1:
    rec = "观望"
    rec_emoji = "⚪"
elif score > -3:
    rec = "谨慎减仓"
    rec_emoji = "🟠"
else:
    rec = "建议减仓"
    rec_emoji = "🔴"

# ---- 输出报告 ----
ma60_str = f"{latest['ma60']:.2f}" if pd.notna(latest["ma60"]) else "N/A"
arrow   = "📈" if pct >= 0 else "📉"

report = f"""
## 📊 中芯国际（{TS_CODE}）技术分析报告

**数据区间**：{df['trade_date'].min().date()} ~ {df['trade_date'].max().date()}（共 {len(df)} 个交易日）

---

### 📈 行情概览

| 指标 | 数值 |
|------|------|
| 最新价 | **{latest['close']:.2f} 元** |
| 今日涨跌 | {arrow} {change:+.2f} 元（{pct:+.2f}%） |
| 近一年最高 | {high_52:.2f} 元 |
| 近一年最低 | {low_52:.2f} 元 |
| 价格分位 | {pos_pct:.1f}% |
| 今日成交量 | {latest['vol']/1e4:.1f} 万手（均量 {avg_vol/1e4:.1f} 万手）|
| 上涨天数 | {up_days} / {len(df)}（占比 {up_days/len(df)*100:.1f}%）|

---

### 🔍 技术指标分析

**① 均线系统**
> {'🔵' if ma_lvl=='偏多' else '🔴' if ma_lvl=='偏空' else '⚪'} {ma_signal}
> MA5 = {latest['ma5']:.2f}   MA20 = {latest['ma20']:.2f}   MA60 = {ma60_str}

**② RSI(14) 动能**
> {'🔴' if rsi_lvl=='超买' else '🔵' if rsi_lvl=='超卖' else '⚪'} {rsi_sig}

**③ MACD(12,26,9) 趋势**
> {'🔵' if '偏多' in macd_lvl else '🔴' if '偏空' in macd_lvl else '🟡'} {macd_str}

**④ 价格位置**
> {'🔴' if pos_pct>80 else '🔵' if pos_pct<20 else '⚪'} {pos_str}

**⑤ 成交量**
> {'🔵' if vol_ratio>2 else '⚪'} {vol_str}

---

### 🎯 综合操作建议

**{rec_emoji} 综合建议：{rec}**

> ⚠️ **免责声明**：以上分析基于历史价格与技术指标自动生成，
> 仅供参考，不构成任何投资建议。投资有风险，入市需谨慎。
"""

display(Markdown(report))
