#!/usr/bin/env python3
"""
generate_dashboard.py — 读取 SMIC CSV 数据，生成独立的 HTML 看板
用法: python3 generate_dashboard.py

功能：
  - K线图 + 成交量（双Y轴），悬浮显示详细数据
  - 均线 MA5/MA20/MA60
  - RSI 指标图 + 超买超卖参考线
  - MACD 指标图
  - 统计面板 + AI 风格分析结论（买卖建议）
"""

import os
import json
import math
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "smic_688981_daily.csv")
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), "outputs", "smic_dashboard.html")


def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    df = df.sort_values("trade_date").reset_index(drop=True)
    return df


def compute_ma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def date_to_ts(dt) -> int:
    return int(dt.timestamp())


def fmt_date(ts) -> str:
    d = pd.Timestamp(ts, unit="s")
    return d.strftime("%Y-%m-%d")


def generate_analysis(df: pd.DataFrame, latest, change, pct) -> dict:
    """
    基于技术指标生成分析结论和买卖建议。
    返回 dict，包含各维度的结论文字和建议等级。
    """
    # ---- 均线趋势 ----
    ma5 = df["ma5"].iloc[-1]
    ma20 = df["ma20"].iloc[-1]
    ma60 = df["ma60"].iloc[-1]
    close = float(latest["close"])

    ma_trend = ""
    ma_signal = "neutral"
    if pd.notna(ma5) and pd.notna(ma20) and pd.notna(ma60):
        if close > ma5 > ma20 > ma60:
            ma_trend = "强势多头排列（价格 > MA5 > MA20 > MA60），上升趋势明确"
            ma_signal = "bullish"
        elif ma5 > ma20 > ma60:
            ma_trend = "均线多头排列，中期趋势偏多"
            ma_signal = "bullish"
        elif close < ma5 < ma20 < ma60:
            ma_trend = "均线空头排列（价格 < MA5 < MA20 < MA60），下降趋势明确"
            ma_signal = "bearish"
        elif ma5 < ma20 < ma60:
            ma_trend = "均线空头排列，中期趋势偏空"
            ma_signal = "bearish"
        else:
            ma_trend = "均线交织，趋势不明，建议观望"
            ma_signal = "neutral"
    else:
        ma_trend = "均线数据不足（上市未满60日）"
        ma_signal = "neutral"

    # ---- RSI 信号 ----
    rsi = df["rsi14"].iloc[-1]
    rsi_signal = "neutral"
    rsi_conclusion = ""
    if pd.notna(rsi):
        if rsi > 70:
            rsi_conclusion = f"RSI = {rsi:.1f}，进入超买区间，短期回调风险较高"
            rsi_signal = "overbought"
        elif rsi > 50:
            rsi_conclusion = f"RSI = {rsi:.1f}，处于强势区间（50-70），多头力量占优"
            rsi_signal = "bullish"
        elif rsi > 30:
            rsi_conclusion = f"RSI = {rsi:.1f}，处于弱势区间（30-50），空头力量占优"
            rsi_signal = "bearish"
        else:
            rsi_conclusion = f"RSI = {rsi:.1f}，进入超卖区间，短期反弹概率增加"
            rsi_signal = "oversold"

    # ---- MACD 信号 ----
    macd = df["macd"].iloc[-1]
    macd_signal_val = df["macd_signal"].iloc[-1]
    macd_hist = df["macd_hist"].iloc[-1]
    macd_prev_hist = df["macd_hist"].iloc[-2] if len(df) > 1 else 0

    macd_conclusion = ""
    macd_signal = "neutral"
    if pd.notna(macd) and pd.notna(macd_signal_val):
        if macd > macd_signal_val and macd_hist > 0:
            macd_conclusion = "MACD 柱状图为正且在扩张，DIF 在 DEA 上方，多头信号"
            macd_signal = "bullish"
        elif macd > macd_signal_val and macd_hist < 0:
            macd_conclusion = "DIF 在 DEA 上方但柱状图为负，多头动能减弱"
            macd_signal = "neutral"
        elif macd < macd_signal_val and macd_hist < 0:
            macd_conclusion = "MACD 柱状图为负且在扩张，DIF 在 DEA 下方，空头信号"
            macd_signal = "bearish"
        else:
            macd_conclusion = "DIF 在 DEA 下方但柱状图为负值收窄，空头动能减弱"
            macd_signal = "neutral"

    # ---- 价格位置 ----
    high_52w = df["high"].max()
    low_52w = df["low"].min()
    pos_pct = (close - low_52w) / (high_52w - low_52w) * 100 if high_52w > low_52w else 50

    if pos_pct > 80:
        pos_conclusion = f"当前价格处于近一年高位区间（{pos_pct:.0f}%），注意回调风险"
    elif pos_pct < 20:
        pos_conclusion = f"当前价格处于近一年低位区间（{pos_pct:.0f}%），关注反弹机会"
    else:
        pos_conclusion = f"当前价格处于近一年中部区间（{pos_pct:.0f}%），方向待确认"

    # ---- 成交量信号 ----
    avg_vol_20 = df["vol"].iloc[-20:].mean() if len(df) >= 20 else df["vol"].mean()
    vol_ratio = float(latest["vol"]) / avg_vol_20 if avg_vol_20 > 0 else 1

    if vol_ratio > 2:
        vol_conclusion = f"今日成交量约为20日均量的 {vol_ratio:.1f} 倍，放量明显，关注突破或出货"
    elif vol_ratio > 1.5:
        vol_conclusion = f"今日成交量较20日均值放大 {vol_ratio:.1f} 倍，有一定资金关注"
    elif vol_ratio < 0.5:
        vol_conclusion = f"今日成交量仅为20日均值 {vol_ratio:.1f} 倍，极度缩量，市场观望"
    else:
        vol_conclusion = f"今日成交量约为20日均值，无明显异常"

    # ---- 综合建议 ----
    signals = [ma_signal, rsi_signal, macd_signal]
    bullish_count = signals.count("bullish") + signals.count("oversold")
    bearish_count = signals.count("bearish") + signals.count("overbought")

    if bullish_count >= 2 and bearish_count == 0:
        recommendation = "综合多个指标偏多，短期可关注做多机会，建议轻仓试探，设好止损"
        rec_level = "buy"
    elif bearish_count >= 2 and bullish_count == 0:
        recommendation = "综合多个指标偏空，短期建议观望或减仓，持有者注意风险控制"
        rec_level = "sell"
    elif bullish_count > bearish_count:
        recommendation = "部分指标偏多，可选择性关注，建议轻仓操作，密切跟踪"
        rec_level = "cautious_buy"
    elif bearish_count > bullish_count:
        recommendation = "部分指标偏空，建议谨慎操作，控制仓位，等待更明确信号"
        rec_level = "cautious_sell"
    else:
        recommendation = "多空信号交织，趋势不明，建议观望等待方向确认后再介入"
        rec_level = "neutral"

    return {
        "ma_trend": ma_trend,
        "ma_signal": ma_signal,
        "rsi_conclusion": rsi_conclusion,
        "rsi_value": round(rsi, 1) if pd.notna(rsi) else None,
        "macd_conclusion": macd_conclusion,
        "macd_signal": macd_signal,
        "macd_value": round(macd, 3) if pd.notna(macd) else None,
        "pos_conclusion": pos_conclusion,
        "pos_pct": round(pos_pct, 1),
        "vol_conclusion": vol_conclusion,
        "vol_ratio": round(vol_ratio, 2),
        "recommendation": recommendation,
        "rec_level": rec_level,
    }


def generate_html(df: pd.DataFrame) -> str:
    # ---- 计算指标 ----
    df["ma5"] = compute_ma(df["close"], 5)
    df["ma20"] = compute_ma(df["close"], 20)
    df["ma60"] = compute_ma(df["close"], 60)
    df["rsi14"] = compute_rsi(df["close"], 14)
    df["macd"], df["macd_signal"], df["macd_hist"] = compute_macd(df["close"])

    # ---- 序列数据 ----
    def make_candle(row):
        return {
            "time": date_to_ts(row["trade_date"]),
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
        }

    def make_volume(row):
        c = float(row["close"])
        o = float(row["open"])
        return {
            "time": date_to_ts(row["trade_date"]),
            "value": round(float(row["vol"]), 2),
            "color": "#ef5350" if c >= o else "#26a69a",
        }

    candle_data = [make_candle(row) for _, row in df.iterrows()]
    volume_data = [make_volume(row) for _, row in df.iterrows()]

    def series_to_line(col):
        return [
            {"time": date_to_ts(row["trade_date"]), "value": round(float(row[col]), 2)}
            for _, row in df.iterrows() if pd.notna(row[col])
        ]

    ma5_data = series_to_line("ma5")
    ma20_data = series_to_line("ma20")
    ma60_data = series_to_line("ma60")
    rsi_data = series_to_line("rsi14")
    macd_line_data = series_to_line("macd")
    macd_signal_data = series_to_line("macd_signal")
    macd_hist_data = [
        {"time": date_to_ts(row["trade_date"]),
         "value": round(float(row["macd_hist"]), 4),
         "color": "#ef5350" if float(row["macd_hist"]) >= 0 else "#26a69a"}
        for _, row in df.iterrows() if pd.notna(row["macd_hist"])
    ]

    # ---- 统计 + 分析（需要在辅助变量之前计算） ----
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    change = float(latest["close"]) - float(prev["close"])
    pct = change / float(prev["close"]) * 100
    high_52w = df["high"].max()
    low_52w = df["low"].min()
    avg_vol = df["vol"].mean()
    avg_amount = df["amount"].mean()
    up_days = (df["pct_chg"] > 0).sum()
    down_days = (df["pct_chg"] < 0).sum()
    flat_days = len(df) - up_days - down_days
    max_up = df["pct_chg"].max()
    max_down = df["pct_chg"].min()
    ret_5d = (df["close"].iloc[-1] / df["close"].iloc[-6] - 1) * 100 if len(df) > 5 else 0
    ret_20d = (df["close"].iloc[-1] / df["close"].iloc[-21] - 1) * 100 if len(df) > 20 else 0
    ret_60d = (df["close"].iloc[-1] / df["close"].iloc[-61] - 1) * 100 if len(df) > 60 else 0
    date_start = df["trade_date"].iloc[0].strftime("%Y-%m-%d")
    date_end = df["trade_date"].iloc[-1].strftime("%Y-%m-%d")

    # ---- 分析结论 ----
    analysis = generate_analysis(df, latest, change, pct)

    # ---- 辅助变量（依赖 analysis） ----
    ma60_val = f"{df['ma60'].iloc[-1]:.2f}" if pd.notna(df['ma60'].iloc[-1]) else "N/A"
    macd_val_str = f"{analysis['macd_value']:.3f}" if analysis['macd_value'] else "—"
    macd_signal_str = f"{df['macd_signal'].iloc[-1]:.3f}" if pd.notna(df['macd_signal'].iloc[-1]) else "—"

    UP = "#ef5350"
    DOWN = "#26a69a"

    # 建议等级对应颜色
    rec_colors = {
        "buy": "#ef5350",
        "cautious_buy": "#ff8a65",
        "neutral": "#8b949e",
        "cautious_sell": "#4db6ac",
        "sell": "#26a69a",
    }
    rec_color = rec_colors.get(analysis["rec_level"], "#8b949e")
    rec_emoji = {"buy": "🔴", "cautious_buy": "🟠", "neutral": "⚪", "cautious_sell": "🟢", "sell": "🟢"}.get(analysis["rec_level"], "⚪")

    # 信号等级标签
    sig_labels = {
        "bullish": ("偏多", UP),
        "bearish": ("偏空", DOWN),
        "overbought": ("超买", "#ff9800"),
        "oversold": ("超卖", "#4caf50"),
        "neutral": ("中性", "#8b949e"),
    }

    def sig_badge(sig):
        label, color = sig_labels.get(sig, ("—", "#8b949e"))
        return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:4px;font-size:12px;">{label}</span>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>中芯国际（688981.SH）行情看板</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #0d1117; color: #e0e0e0; min-height: 100vh;
  }}
  a {{ color: #58a6ff; text-decoration: none; }}

  .header {{
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    padding: 20px 32px 12px; border-bottom: 1px solid #30363d;
  }}
  .header h1 {{ font-size: 22px; font-weight: 700; color: #f0f6fc; }}
  .header .sub {{ font-size: 13px; color: #8b949e; margin-top: 4px; }}

  .stats-bar {{
    display: flex; gap: 20px; padding: 14px 32px;
    background: #161b22; border-bottom: 1px solid #30363d;
    flex-wrap: wrap; align-items: center;
  }}
  .stat {{ display: flex; flex-direction: column; gap: 2px; }}
  .stat-label {{ font-size: 11px; color: #8b949e; }}
  .stat-val {{ font-size: 16px; font-weight: 600; color: #f0f6fc; }}
  .stat-val.up {{ color: {UP}; }}
  .stat-val.down {{ color: {DOWN}; }}
  .sep {{ width: 1px; height: 36px; background: #30363d; }}

  .legend-bar {{
    display: flex; gap: 18px; padding: 8px 32px;
    background: #161b22; font-size: 12px; color: #8b949e;
    border-bottom: 1px solid #30363d; flex-wrap: wrap; align-items: center;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 5px; }}
  .legend-line {{ display: inline-block; width: 18px; height: 2px; }}
  .legend-dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; }}

  /* ---- 自定义十字线 tooltip ---- */
  #tooltip {{
    position: absolute; display: none;
    background: rgba(22,27,34,0.95); border: 1px solid #30363d;
    border-radius: 6px; padding: 10px 14px; font-size: 12px;
    color: #e0e0e0; pointer-events: none; z-index: 100;
    min-width: 180px; line-height: 1.7;
  }}
  #tooltip .tt-date {{ font-weight: 600; color: #f0f6fc; font-size: 13px; margin-bottom: 4px; }}
  #tooltip .tt-row {{ display: flex; justify-content: space-between; gap: 16px; }}
  #tooltip .tt-label {{ color: #8b949e; }}
  #tooltip .tt-val {{ font-weight: 500; }}

  .chart-section {{ padding: 12px 32px 4px; position: relative; }}
  .chart-title {{ font-size: 13px; color: #8b949e; margin-bottom: 4px; font-weight: 500; }}
  .chart-box {{
    border: 1px solid #30363d; border-radius: 6px; overflow: hidden;
    margin-bottom: 12px; background: #0d1117; position: relative;
  }}

  /* ---- 统计面板 ---- */
  .stats-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 12px; padding: 16px 32px;
  }}
  .card {{
    background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px;
  }}
  .card h3 {{ font-size: 14px; color: #f0f6fc; margin-bottom: 12px; }}
  .card-row {{
    display: flex; justify-content: space-between; padding: 6px 0;
    font-size: 13px; border-bottom: 1px solid #21262d;
  }}
  .card-row:last-child {{ border-bottom: none; }}
  .card-label {{ color: #8b949e; }}
  .card-value {{ color: #f0f6fc; font-weight: 500; }}
  .card-value.up {{ color: {UP}; }}
  .card-value.down {{ color: {DOWN}; }}

  .bar-container {{ margin-top: 8px; }}
  .bar-label {{ font-size: 12px; color: #8b949e; margin-bottom: 4px; }}
  .bar {{ height: 22px; border-radius: 4px; display: flex; overflow: hidden;
          font-size: 11px; line-height: 22px; text-align: center; color: #fff; }}
  .bar-up {{ background: {UP}; }}
  .bar-down {{ background: {DOWN}; }}
  .bar-flat {{ background: #6e7681; }}

  /* ---- 分析结论卡片 ---- */
  .analysis-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 12px; padding: 0 32px 16px;
  }}
  .analysis-card {{
    background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px 20px;
  }}
  .analysis-card h3 {{ font-size: 14px; color: #f0f6fc; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }}
  .analysis-item {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 7px 0; font-size: 13px; border-bottom: 1px solid #21262d;
  }}
  .analysis-item:last-child {{ border-bottom: none; }}
  .analysis-text {{ color: #c9d1d9; font-size: 13px; line-height: 1.6; }}
  .analysis-badge {{ flex-shrink: 0; }}

  /* ---- 综合建议 ---- */
  .rec-card {{
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 20px 24px; margin: 0 32px 16px;
  }}
  .rec-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
  .rec-title {{ font-size: 16px; font-weight: 600; color: #f0f6fc; }}
  .rec-badge {{
    background: {rec_color}; color: #fff; padding: 3px 12px;
    border-radius: 4px; font-size: 13px; font-weight: 600;
  }}
  .rec-text {{ font-size: 14px; color: #c9d1d9; line-height: 1.7; }}

  .footer {{
    padding: 16px 32px; font-size: 12px; color: #6e7681;
    text-align: center; border-top: 1px solid #30363d; margin-top: 8px;
  }}
</style>
</head>
<body>

<div class="header">
  <h1>中芯国际（688981.SH）</h1>
  <div class="sub">科创板 · 近一年日线行情 · 数据来源：Tushare Pro</div>
</div>

<div class="stats-bar">
  <div class="stat">
    <span class="stat-label">最新价（{date_end}）</span>
    <span class="stat-val {'up' if change>=0 else 'down'}">{float(latest['close']):.2f}</span>
  </div>
  <div class="sep"></div>
  <div class="stat">
    <span class="stat-label">涨跌额</span>
    <span class="stat-val {'up' if change>=0 else 'down'}">{change:+.2f}</span>
  </div>
  <div class="sep"></div>
  <div class="stat">
    <span class="stat-label">涨跌幅</span>
    <span class="stat-val {'up' if change>=0 else 'down'}">{pct:+.2f}%</span>
  </div>
  <div class="sep"></div>
  <div class="stat">
    <span class="stat-label">近一年最高</span>
    <span class="stat-val" style="color:#f0f6fc">{high_52w:.2f}</span>
  </div>
  <div class="sep"></div>
  <div class="stat">
    <span class="stat-label">近一年最低</span>
    <span class="stat-val" style="color:#f0f6fc">{low_52w:.2f}</span>
  </div>
  <div class="sep"></div>
  <div class="stat">
    <span class="stat-label">平均成交额（万元）</span>
    <span class="stat-val" style="color:#f0f6fc">{avg_amount/1e4:,.0f}</span>
  </div>
</div>

<div class="legend-bar">
  <span class="legend-item"><span class="legend-dot" style="background:#ef5350"></span> 阳线（涨）</span>
  <span class="legend-item"><span class="legend-dot" style="background:#26a69a"></span> 阴线（跌）</span>
  <span class="legend-item"><span class="legend-line" style="background:#f5a623"></span> MA5</span>
  <span class="legend-item"><span class="legend-line" style="background:#388bfd"></span> MA20</span>
  <span class="legend-item"><span class="legend-line" style="background:#a371f7"></span> MA60</span>
  <span class="legend-item"><span class="legend-dot" style="background:#8b949e;opacity:0.6"></span> 成交量</span>
  <span style="margin-left:auto;color:#6e7681;font-size:11px;">💡 鼠标移至K线可查看详细数据</span>
</div>

<!-- ========== K线图 ========== -->
<div class="chart-section">
  <div class="chart-title">K线图 / 成交量（悬浮查看详细数据）</div>
  <div class="chart-box">
    <div id="chart_main" style="width:100%;height:540px"></div>
    <div id="tooltip"></div>
  </div>
</div>

<!-- ========== RSI ========== -->
<div class="chart-section">
  <div class="chart-title">RSI（14日）&nbsp; 当前值：<span style="color:#f5a623;font-weight:600;">{analysis['rsi_value'] if analysis['rsi_value'] else '—'}</span></div>
  <div class="chart-box"><div id="chart_rsi" style="width:100%;height:180px"></div></div>
</div>

<!-- ========== MACD ========== -->
<div class="chart-section">
  <div class="chart-title">MACD（12,26,9）&nbsp; DIF：<span style="color:#f5a623;">{macd_val_str}</span></div>
  <div class="chart-box"><div id="chart_macd" style="width:100%;height:220px"></div></div>
</div>

<!-- ========== 分析结论 ========== -->
<div class="analysis-grid">
  <div class="analysis-card">
    <h3>📊 均线趋势分析</h3>
    <div class="analysis-item">
      <span class="analysis-text">{analysis['ma_trend']}</span>
      <span class="analysis-badge">{sig_badge(analysis['ma_signal'])}</span>
    </div>
    <div class="analysis-item" style="border:none;padding-top:10px;">
      <span class="analysis-text" style="color:#8b949e;font-size:12px;">
        MA5 = {df['ma5'].iloc[-1]:.2f} &nbsp; MA20 = {df['ma20'].iloc[-1]:.2f} &nbsp; MA60 = {ma60_val}
      </span>
    </div>
  </div>

  <div class="analysis-card">
    <h3>📈 RSI 动能分析</h3>
    <div class="analysis-item">
      <span class="analysis-text">{analysis['rsi_conclusion']}</span>
      <span class="analysis-badge">{sig_badge('overbought' if analysis['rsi_value'] and analysis['rsi_value']>70 else ('oversold' if analysis['rsi_value'] and analysis['rsi_value']<30 else ('bullish' if analysis['rsi_value'] and analysis['rsi_value']>50 else 'bearish')))}</span>
    </div>
    <div class="analysis-item" style="border:none;padding-top:10px;">
      <span class="analysis-text" style="color:#8b949e;font-size:12px;">
        参考：RSI > 70 超买（警惕回调）&nbsp;|&nbsp; RSI < 30 超卖（关注反弹）
      </span>
    </div>
  </div>

  <div class="analysis-card">
    <h3>🔄 MACD 趋势分析</h3>
    <div class="analysis-item">
      <span class="analysis-text">{analysis['macd_conclusion']}</span>
      <span class="analysis-badge">{sig_badge(analysis['macd_signal'])}</span>
    </div>
    <div class="analysis-item" style="border:none;padding-top:10px;">
      <span class="analysis-text" style="color:#8b949e;font-size:12px;">
        DIF = {macd_val_str} &nbsp;|&nbsp; DEA = {macd_signal_str}
      </span>
    </div>
  </div>

  <div class="analysis-card">
    <h3>📍 价格位置分析</h3>
    <div class="analysis-item">
      <span class="analysis-text">{analysis['pos_conclusion']}</span>
    </div>
    <div class="analysis-item" style="border:none;padding-top:10px;">
      <span class="analysis-text" style="color:#8b949e;font-size:12px;">
        距最高回撤 {((float(latest['close'])-high_52w)/high_52w*100):.1f}% &nbsp;|&nbsp; 距最低涨幅 {((float(latest['close'])-low_52w)/low_52w*100):.1f}%
      </span>
    </div>
  </div>

  <div class="analysis-card">
    <h3>📦 成交量分析</h3>
    <div class="analysis-item">
      <span class="analysis-text">{analysis['vol_conclusion']}</span>
    </div>
    <div class="analysis-item" style="border:none;padding-top:10px;">
      <span class="analysis-text" style="color:#8b949e;font-size:12px;">
        今日成交量 {float(latest['vol']):,.0f} 手 &nbsp;|&nbsp; 20日均量 {df['vol'].iloc[-20:].mean():,.0f} 手
      </span>
    </div>
  </div>
</div>

<!-- ========== 综合建议 ========== -->
<div class="rec-card">
  <div class="rec-header">
    <span class="rec-title">{rec_emoji} 综合分析与操作建议</span>
    <span class="rec-badge">{'买入' if analysis['rec_level']=='buy' else ('谨慎买入' if analysis['rec_level']=='cautious_buy' else ('观望' if analysis['rec_level']=='neutral' else ('谨慎减仓' if analysis['rec_level']=='cautious_sell' else '建议减仓')))}</span>
  </div>
  <div class="rec-text">{analysis['recommendation']}</div>
  <div style="margin-top:12px;font-size:12px;color:#6e7681;">
    ⚠️ 以上分析基于技术指标自动生成，仅供参考，不构成投资建议。股市有风险，投资需谨慎。
  </div>
</div>

<!-- ========== 统计面板 ========== -->
<div class="stats-grid">
  <div class="card">
    <h3>📊 涨跌统计（近一年）</h3>
    <div class="card-row"><span class="card-label">交易天数</span><span class="card-value">{len(df)} 天</span></div>
    <div class="card-row"><span class="card-label">上涨天数</span><span class="card-value up">{up_days} 天（{up_days/len(df)*100:.1f}%）</span></div>
    <div class="card-row"><span class="card-label">下跌天数</span><span class="card-value down">{down_days} 天（{down_days/len(df)*100:.1f}%）</span></div>
    <div class="card-row"><span class="card-label">最大单日涨幅</span><span class="card-value up">+{max_up:.2f}%</span></div>
    <div class="card-row"><span class="card-label">最大单日跌幅</span><span class="card-value down">{max_down:.2f}%</span></div>
    <div class="bar-container">
      <div class="bar-label">涨跌分布</div>
      <div class="bar">
        <div class="bar-up" style="width:{up_days/len(df)*100:.1f}%">{up_days}</div>
        <div class="bar-flat" style="width:{flat_days/len(df)*100:.1f}%"></div>
        <div class="bar-down" style="width:{down_days/len(df)*100:.1f}%">{down_days}</div>
      </div>
    </div>
  </div>

  <div class="card">
    <h3>📈 各周期回报</h3>
    <div class="card-row"><span class="card-label">近 5 日</span><span class="card-value {'up' if ret_5d>=0 else 'down'}">{ret_5d:+.2f}%</span></div>
    <div class="card-row"><span class="card-label">近 20 日</span><span class="card-value {'up' if ret_20d>=0 else 'down'}">{ret_20d:+.2f}%</span></div>
    <div class="card-row"><span class="card-label">近 60 日</span><span class="card-value {'up' if ret_60d>=0 else 'down'}">{ret_60d:+.2f}%</span></div>
    <div class="card-row"><span class="card-label">数据区间</span><span class="card-value">{date_start} ~ {date_end}</span></div>
    <div class="card-row"><span class="card-label">平均成交量</span><span class="card-value">{avg_vol:,.0f} 手</span></div>
    <div class="card-row"><span class="card-label">平均成交额</span><span class="card-value">{avg_amount/1e4:,.0f} 万元</span></div>
  </div>

  <div class="card">
    <h3>💹 价格区间分析</h3>
    <div class="card-row"><span class="card-label">当前价</span><span class="card-value {'up' if change>=0 else 'down'}">{float(latest['close']):.2f}</span></div>
    <div class="card-row"><span class="card-label">近一年最高</span><span class="card-value">{high_52w:.2f}</span></div>
    <div class="card-row"><span class="card-label">近一年最低</span><span class="card-value">{low_52w:.2f}</span></div>
    <div class="card-row"><span class="card-label">距最高回撤</span><span class="card-value down">{((float(latest['close'])-high_52w)/high_52w*100):.2f}%</span></div>
    <div class="card-row"><span class="card-label">距最低涨幅</span><span class="card-value up">{((float(latest['close'])-low_52w)/low_52w*100):.2f}%</span></div>
    <div class="card-row"><span class="card-label">近一年振幅</span><span class="card-value">{((high_52w-low_52w)/low_52w*100):.2f}%</span></div>
  </div>
</div>

<div class="footer">
  数据区间：{date_start} ~ {date_end} · 生成时间：{date_end} ·
  由 WorkBuddy 自动生成 ·
  <a href="https://github.com/kikiJing/AI-quant" target="_blank">GitHub</a>
</div>

<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<script>
(function() {{
  const UP = '{UP}';
  const DOWN = '{DOWN}';

  // ========== 原始数据（用于 tooltip） ==========
  const rawData = {json.dumps(candle_data, ensure_ascii=False)};
  const volData = {json.dumps(volume_data, ensure_ascii=False)};
  const timeToIdx = {{}};
  rawData.forEach((d, i) => timeToIdx[d.time] = i);

  // ========== Tooltip ==========
  const tooltip = document.getElementById('tooltip');

  function showTooltip(chart, series, data) {{
    const coord = chart.timeScale().logicalToCoordinate(
      chart.timeScale().coordinateToLogical ? 
      chart.timeScale().coordinateToLogical(event.clientY) : null
    );
    // 使用 crosshairMove 事件参数
  }}

  // ========== 通用图表配置 ==========
  const commonOpts = {{
    layout: {{
      background: {{ type: 'solid', color: '#0d1117' }},
      textColor: '#8b949e', fontSize: 12,
    }},
    grid: {{ vertLines: {{ color: '#21262d' }}, horzLines: {{ color: '#21262d' }} }},
    crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }},
  }};

  // ========== 1. 主图 ==========
  const chartMain = LightweightCharts.createChart(
    document.getElementById('chart_main'),
    {{
      ...commonOpts,
      width: document.getElementById('chart_main').clientWidth,
      height: 540,
      rightPriceScale: {{ borderColor: '#30363d' }},
      timeScale: {{
        borderColor: '#30363d', timeVisible: false,
        tickMarkFormatter: (time) => {{
          const d = new Date(time * 1000);
          return (d.getMonth()+1) + '/' + d.getDate();
        }},
      }},
      handleScroll: {{ vertTouchDrag: false }},
    }}
  );

  // K线
  const candleSeries = chartMain.addCandlestickSeries({{
    upColor: UP, downColor: DOWN,
    borderUpColor: UP, borderDownColor: DOWN,
    wickUpColor: UP, wickDownColor: DOWN,
  }});
  candleSeries.setData({json.dumps(candle_data, ensure_ascii=False)});

  // 自定义 tooltip（crosshairMove）
  chartMain.subscribeCrosshairMove(param => {{
    if (!param.time || !param.seriesData) {{
      tooltip.style.display = 'none';
      return;
    }}
    const data = param.seriesData.get(candleSeries);
    if (!data) {{ tooltip.style.display = 'none'; return; }}

    const idx = timeToIdx[data.time];
    const vol = idx !== undefined ? volData[idx] : null;
    const d = new Date(data.time * 1000);
    const dateStr = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
    const isUp = data.close >= data.open;
    const chg = data.close - data.open;
    const chgPct = (chg / data.open * 100).toFixed(2);

    tooltip.innerHTML = `
      <div class="tt-date">${{dateStr}}</div>
      <div class="tt-row"><span class="tt-label">开盘</span><span class="tt-val" style="color:${{isUp?UP:DOWN}}">${{data.open.toFixed(2)}}</span></div>
      <div class="tt-row"><span class="tt-label">最高</span><span class="tt-val" style="color:${{isUp?UP:DOWN}}">${{data.high.toFixed(2)}}</span></div>
      <div class="tt-row"><span class="tt-label">最低</span><span class="tt-val" style="color:${{isUp?UP:DOWN}}">${{data.low.toFixed(2)}}</span></div>
      <div class="tt-row"><span class="tt-label">收盘</span><span class="tt-val" style="color:${{isUp?UP:DOWN}}">${{data.close.toFixed(2)}}</span></div>
      <div class="tt-row"><span class="tt-label">涨跌</span><span class="tt-val" style="color:${{isUp?UP:DOWN}}">${{chg>=0?'+':''}}${{chg.toFixed(2)}}（${{chgPct}}%）</span></div>
      <div class="tt-row"><span class="tt-label">成交量</span><span class="tt-val" style="color:#8b949e">${{vol ? (vol.value/10000).toFixed(0) + ' 万手' : '—'}}</span></div>
    `;
    tooltip.style.display = 'block';

    const chartRect = document.getElementById('chart_main').getBoundingClientRect();
    let left = param.logical !== undefined
      ? chartMain.timeScale().logicalToCoordinate
        ? chartMain.timeScale().logicalToCoordinate(param.logical) + chartRect.left
        : param.logical + chartRect.left
      : chartRect.left + 100;

    // 更简单的方式：用 param 中的坐标
    const x = param.logical !== null ? param.logical : chartRect.width / 2;
    let tx = x + chartRect.left - 100;
    let ty = param.point && param.point.y !== undefined ? param.point.y + chartRect.top - 80 : chartRect.top + 40;

    // 边界修正
    tx = Math.max(10, Math.min(tx, chartRect.right - 220));
    ty = Math.max(10, Math.min(ty, chartRect.bottom - 180));

    tooltip.style.left = tx + 'px';
    tooltip.style.top = ty + 'px';
  }});

  // 离开图表隐藏 tooltip
  document.getElementById('chart_main').addEventListener('mouseleave', () => {{
    tooltip.style.display = 'none';
  }});

  // 均线
  [['MA5', '#f5a623', {json.dumps(ma5_data, ensure_ascii=False)}],
   ['MA20', '#388bfd', {json.dumps(ma20_data, ensure_ascii=False)}],
   ['MA60', '#a371f7', {json.dumps(ma60_data, ensure_ascii=False)}],
  ].forEach(([name, color, data]) => {{
    const s = chartMain.addLineSeries({{
      color, lineWidth: 1,
      priceLineVisible: false, lastValueVisible: true, title: name,
    }});
    s.setData(data);
  }});

  // 成交量
  const volumeSeries = chartMain.addHistogramSeries({{
    priceFormat: {{ type: 'volume' }}, priceScaleId: 'volume',
  }});
  chartMain.priceScale('volume').applyOptions({{ scaleMargins: {{ top: 0.78, bottom: 0 }} }});
  volumeSeries.setData({json.dumps(volume_data, ensure_ascii=False)});

  // 最新价线
  candleSeries.createPriceLine({{
    price: {float(latest['close'])},
    color: '{UP if change>=0 else DOWN}',
    lineWidth: 1, lineStyle: LightweightCharts.LineStyle.Dashed,
    axisLabelVisible: true, title: '最新',
  }});

  chartMain.timeScale().fitContent();

  // ========== 2. RSI ==========
  const chartRSI = LightweightCharts.createChart(
    document.getElementById('chart_rsi'), {{
      ...commonOpts,
      width: document.getElementById('chart_rsi').clientWidth, height: 180,
      rightPriceScale: {{ borderColor: '#30363d', scaleMargins: {{ top:0.1, bottom:0.1 }} }},
      timeScale: {{ borderColor: '#30363d', timeVisible: false, tickMarkFormatter: () => '' }},
    }}
  );
  const rsiSeries = chartRSI.addLineSeries({{
    color: '#f5a623', lineWidth: 1,
    priceLineVisible: true, lastValueVisible: true, title: 'RSI',
  }});
  rsiSeries.setData({json.dumps(rsi_data, ensure_ascii=False)});

  // 超买超卖线
  const rsiTimes = {json.dumps(rsi_data, ensure_ascii=False)};
  if (rsiTimes.length) {{
    const t0 = rsiTimes[0].time, t1 = rsiTimes[rsiTimes.length-1].time;
    [70, 30].forEach(v => {{
      const s = chartRSI.addLineSeries({{
        color: '#30363d', lineWidth: 1, lineStyle: 2,
        priceLineVisible: false, lastValueVisible: false,
      }});
      s.setData([{{time:t0,value:v}},{{time:t1,value:v}}]);
    }});
  }}
  chartRSI.timeScale().fitContent();

  // ========== 3. MACD ==========
  const chartMACD = LightweightCharts.createChart(
    document.getElementById('chart_macd'), {{
      ...commonOpts,
      width: document.getElementById('chart_macd').clientWidth, height: 220,
      rightPriceScale: {{ borderColor: '#30363d' }},
      timeScale: {{
        borderColor: '#30363d', timeVisible: false,
        tickMarkFormatter: (time) => {{
          const d = new Date(time * 1000);
          return (d.getMonth()+1) + '/' + d.getDate();
        }},
      }},
    }}
  );
  const macdLine = chartMACD.addLineSeries({{
    color: '#f5a623', lineWidth: 1,
    priceLineVisible: false, lastValueVisible: true, title: 'DIF',
  }});
  macdLine.setData({json.dumps(macd_line_data, ensure_ascii=False)});
  const sigLine = chartMACD.addLineSeries({{
    color: '#388bfd', lineWidth: 1,
    priceLineVisible: false, lastValueVisible: true, title: 'DEA',
  }});
  sigLine.setData({json.dumps(macd_signal_data, ensure_ascii=False)});
  const macdHist = chartMACD.addHistogramSeries({{
    priceFormat: {{ type: 'price' }}, priceScaleId: 'macd',
  }});
  chartMACD.priceScale('macd').applyOptions({{ scaleMargins: {{ top:0.1, bottom:0.1 }} }});
  macdHist.setData({json.dumps(macd_hist_data, ensure_ascii=False)});
  chartMACD.timeScale().fitContent();

  // ========== 时间轴联动 ==========
  function syncTime(source, targets) {{
    source.timeScale().subscribeVisibleLogicalRangeChange(range => {{
      const r = source.timeScale().getVisibleLogicalRange();
      if (r) targets.forEach(t => t.timeScale().setVisibleLogicalRange(r));
    }});
  }}
  syncTime(chartMain, [chartRSI, chartMACD]);
  syncTime(chartRSI, [chartMain, chartMACD]);
  syncTime(chartMACD, [chartMain, chartRSI]);

  // ========== 自适应宽度 ==========
  window.addEventListener('resize', () => {{
    chartMain.applyOptions({{width: document.getElementById('chart_main').clientWidth}});
    chartRSI.applyOptions({{width: document.getElementById('chart_rsi').clientWidth}});
    chartMACD.applyOptions({{width: document.getElementById('chart_macd').clientWidth}});
  }});
}})();
</script>
</body>
</html>"""


def main():
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    print("加载数据...")
    df = load_data()
    print(f"  {len(df)} 条记录，{df['trade_date'].iloc[0].date()} ~ {df['trade_date'].iloc[-1].date()}")

    print("计算技术指标...")
    html = generate_html(df)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ 看板已生成：{OUTPUT_HTML}")


if __name__ == "__main__":
    main()
