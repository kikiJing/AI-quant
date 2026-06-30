#!/usr/bin/env python3
"""
generate_dashboard.py — 读取 SMIC CSV 数据，生成独立的 HTML 看板
用法: python3 generate_dashboard.py

功能：
  - K线图 + 成交量（双Y轴）
  - 均线 MA5/MA20/MA60
  - RSI 指标图
  - MACD 指标图
  - 统计面板（涨跌幅分布、价格区间等）
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


def compute_ma(series: pd.Series, window: int) -> list:
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
    """将 datetime 转为 Unix 时间戳（秒）。"""
    return int(dt.timestamp())


def df_to_candlestick(df: pd.DataFrame) -> list:
    return [
        {
            "time": date_to_ts(row["trade_date"]),
            "open": round(float(row["open"]), 2),
            "high": round(float(row["high"]), 2),
            "low": round(float(row["low"]), 2),
            "close": round(float(row["close"]), 2),
        }
        for _, row in df.iterrows()
    ]


def df_to_volume(df: pd.DataFrame) -> list:
    result = []
    for _, row in df.iterrows():
        close = float(row["close"])
        open_ = float(row["open"])
        color = "#ef5350" if close >= open_ else "#26a69a"
        result.append({
            "time": date_to_ts(row["trade_date"]),
            "value": round(float(row["vol"]), 2),
            "color": color,
        })
    return result


def series_to_line(df: pd.DataFrame, col: str, col_name: str) -> list:
    return [
        {"time": date_to_ts(row["trade_date"]), "value": round(v, 2)}
        for _, row in df.iterrows()
        if not math.isnan(v := float(row[col]))
    ]


def generate_html(df: pd.DataFrame) -> str:
    # ---- 计算指标 ----
    df["ma5"] = compute_ma(df["close"], 5)
    df["ma20"] = compute_ma(df["close"], 20)
    df["ma60"] = compute_ma(df["close"], 60)
    df["rsi14"] = compute_rsi(df["close"], 14)
    df["macd"], df["macd_signal"], df["macd_hist"] = compute_macd(df["close"])

    # ---- 序列数据 ----
    candle_data = df_to_candlestick(df)
    volume_data = df_to_volume(df)
    ma5_data = series_to_line(df, "ma5", "MA5")
    ma20_data = series_to_line(df, "ma20", "MA20")
    ma60_data = series_to_line(df, "ma60", "MA60")
    rsi_data = series_to_line(df, "rsi14", "RSI")
    macd_line_data = series_to_line(df, "macd", "MACD")
    macd_signal_data = series_to_line(df, "macd_signal", "Signal")
    macd_hist_data = [
        {"time": date_to_ts(row["trade_date"]),
         "value": round(float(row["macd_hist"]), 4),
         "color": "#ef5350" if float(row["macd_hist"]) >= 0 else "#26a69a"}
        for _, row in df.iterrows()
        if not math.isnan(row["macd_hist"])
    ]

    # JSON 序列化
    candle_json = json.dumps(candle_data, ensure_ascii=False)
    volume_json = json.dumps(volume_data, ensure_ascii=False)
    ma5_json = json.dumps(ma5_data, ensure_ascii=False)
    ma20_json = json.dumps(ma20_data, ensure_ascii=False)
    ma60_json = json.dumps(ma60_data, ensure_ascii=False)
    rsi_json = json.dumps(rsi_data, ensure_ascii=False)
    macd_line_json = json.dumps(macd_line_data, ensure_ascii=False)
    macd_signal_json = json.dumps(macd_signal_data, ensure_ascii=False)
    macd_hist_json = json.dumps(macd_hist_data, ensure_ascii=False)

    # ---- 统计指标 ----
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    change = float(latest["close"]) - float(prev["close"])
    pct = change / float(prev["close"]) * 100
    high_52w = df["high"].max()
    low_52w = df["low"].min()
    avg_vol = df["vol"].mean()
    avg_amount = df["amount"].mean()

    # 涨跌幅分布
    up_days = (df["pct_chg"] > 0).sum()
    down_days = (df["pct_chg"] < 0).sum()
    flat_days = len(df) - up_days - down_days
    max_up = df["pct_chg"].max()
    max_down = df["pct_chg"].min()

    # 近 5/20/60 日涨跌
    ret_5d = (df["close"].iloc[-1] / df["close"].iloc[-6] - 1) * 100 if len(df) > 5 else 0
    ret_20d = (df["close"].iloc[-1] / df["close"].iloc[-21] - 1) * 100 if len(df) > 20 else 0
    ret_60d = (df["close"].iloc[-1] / df["close"].iloc[-61] - 1) * 100 if len(df) > 60 else 0

    date_start = df["trade_date"].iloc[0].strftime("%Y-%m-%d")
    date_end = df["trade_date"].iloc[-1].strftime("%Y-%m-%d")

    up_color = "#ef5350"
    down_color = "#26a69a"
    change_color = up_color if change >= 0 else down_color

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
    background: #0d1117;
    color: #e0e0e0;
    min-height: 100vh;
  }}
  a {{ color: #58a6ff; text-decoration: none; }}

  /* ---- 头部 ---- */
  .header {{
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    padding: 20px 32px 12px;
    border-bottom: 1px solid #30363d;
  }}
  .header h1 {{ font-size: 22px; font-weight: 700; color: #f0f6fc; }}
  .header .sub {{ font-size: 13px; color: #8b949e; margin-top: 4px; }}

  /* ---- 统计栏 ---- */
  .stats-bar {{
    display: flex; gap: 20px; padding: 14px 32px;
    background: #161b22; border-bottom: 1px solid #30363d;
    flex-wrap: wrap; align-items: center;
  }}
  .stat {{ display: flex; flex-direction: column; gap: 2px; }}
  .stat-label {{ font-size: 11px; color: #8b949e; }}
  .stat-val {{ font-size: 16px; font-weight: 600; color: #f0f6fc; }}
  .stat-val.up {{ color: {up_color}; }}
  .stat-val.down {{ color: {down_color}; }}
  .sep {{ width: 1px; height: 36px; background: #30363d; }}

  /* ---- 图例 ---- */
  .legend-bar {{
    display: flex; gap: 18px; padding: 8px 32px;
    background: #161b22; font-size: 12px; color: #8b949e;
    border-bottom: 1px solid #30363d; flex-wrap: wrap; align-items: center;
  }}
  .legend-item {{ display: flex; align-items: center; gap: 5px; }}
  .legend-line {{
    display: inline-block; width: 18px; height: 2px; vertical-align: middle;
  }}
  .legend-dot {{
    display: inline-block; width: 10px; height: 10px; border-radius: 2px;
  }}

  /* ---- 图表容器 ---- */
  .chart-section {{
    padding: 12px 32px 4px;
  }}
  .chart-title {{
    font-size: 13px; color: #8b949e; margin-bottom: 4px; font-weight: 500;
  }}
  .chart-box {{
    border: 1px solid #30363d; border-radius: 6px; overflow: hidden;
    margin-bottom: 12px; background: #0d1117;
  }}
  .chart-box > div {{ display: block; }}

  /* ---- 统计面板 ---- */
  .stats-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 12px; padding: 16px 32px;
  }}
  .card {{
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 16px;
  }}
  .card h3 {{ font-size: 14px; color: #f0f6fc; margin-bottom: 12px; }}
  .card-row {{
    display: flex; justify-content: space-between; padding: 6px 0;
    font-size: 13px; border-bottom: 1px solid #21262d;
  }}
  .card-row:last-child {{ border-bottom: none; }}
  .card-label {{ color: #8b949e; }}
  .card-value {{ color: #f0f6fc; font-weight: 500; }}
  .card-value.up {{ color: {up_color}; }}
  .card-value.down {{ color: {down_color}; }}

  /* ---- 页脚 ---- */
  .footer {{
    padding: 16px 32px; font-size: 12px; color: #6e7681;
    text-align: center; border-top: 1px solid #30363d; margin-top: 8px;
  }}

  /* ---- 涨跌幅分布条 ---- */
  .bar-container {{ margin-top: 8px; }}
  .bar-label {{ font-size: 12px; color: #8b949e; margin-bottom: 4px; }}
  .bar {{
    height: 22px; border-radius: 4px; display: flex; overflow: hidden;
    font-size: 11px; line-height: 22px; text-align: center; color: #fff;
  }}
  .bar-up {{ background: {up_color}; }}
  .bar-down {{ background: {down_color}; }}
  .bar-flat {{ background: #6e7681; }}
</style>
</head>
<body>

<!-- ========== 头部 ========== -->
<div class="header">
  <h1>中芯国际（688981.SH）</h1>
  <div class="sub">科创板 · 近一年日线行情 · 数据来源：Tushare Pro</div>
</div>

<!-- ========== 统计栏 ========== -->
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

<!-- ========== 图例 ========== -->
<div class="legend-bar">
  <span class="legend-item"><span class="legend-dot" style="background:#ef5350"></span> 阳线（涨）</span>
  <span class="legend-item"><span class="legend-dot" style="background:#26a69a"></span> 阴线（跌）</span>
  <span class="legend-item"><span class="legend-line" style="background:#f5a623"></span> MA5</span>
  <span class="legend-item"><span class="legend-line" style="background:#388bfd"></span> MA20</span>
  <span class="legend-item"><span class="legend-line" style="background:#a371f7"></span> MA60</span>
  <span class="legend-item"><span class="legend-dot" style="background:#8b949e"></span> 成交量</span>
</div>

<!-- ========== K线 + 成交量 ========== -->
<div class="chart-section">
  <div class="chart-title">K线图 / 成交量</div>
  <div class="chart-box"><div id="chart_main" style="width:100%;height:520px"></div></div>
</div>

<!-- ========== RSI ========== -->
<div class="chart-section">
  <div class="chart-title">RSI（14日）</div>
  <div class="chart-box"><div id="chart_rsi" style="width:100%;height:180px"></div></div>
</div>

<!-- ========== MACD ========== -->
<div class="chart-section">
  <div class="chart-title">MACD（12,26,9）</div>
  <div class="chart-box"><div id="chart_macd" style="width:100%;height:220px"></div></div>
</div>

<!-- ========== 统计面板 ========== -->
<div class="stats-grid">

  <!-- 涨跌幅统计 -->
  <div class="card">
    <h3>📊 涨跌统计（近一年）</h3>
    <div class="card-row">
      <span class="card-label">交易天数</span>
      <span class="card-value">{len(df)} 天</span>
    </div>
    <div class="card-row">
      <span class="card-label">上涨天数</span>
      <span class="card-value up">{up_days} 天（{up_days/len(df)*100:.1f}%）</span>
    </div>
    <div class="card-row">
      <span class="card-label">下跌天数</span>
      <span class="card-value down">{down_days} 天（{down_days/len(df)*100:.1f}%）</span>
    </div>
    <div class="card-row">
      <span class="card-label">平盘天数</span>
      <span class="card-value">{flat_days} 天</span>
    </div>
    <div class="card-row">
      <span class="card-label">最大单日涨幅</span>
      <span class="card-value up">+{max_up:.2f}%</span>
    </div>
    <div class="card-row">
      <span class="card-label">最大单日跌幅</span>
      <span class="card-value down">{max_down:.2f}%</span>
    </div>
    <div class="bar-container">
      <div class="bar-label">涨跌分布</div>
      <div class="bar">
        <div class="bar-up" style="width:{up_days/len(df)*100:.1f}%">{up_days}</div>
        <div class="bar-flat" style="width:{flat_days/len(df)*100:.1f}%"></div>
        <div class="bar-down" style="width:{down_days/len(df)*100:.1f}%">{down_days}</div>
      </div>
    </div>
  </div>

  <!-- 各周期回报 -->
  <div class="card">
    <h3>📈 各周期回报</h3>
    <div class="card-row">
      <span class="card-label">近 5 日</span>
      <span class="card-value {'up' if ret_5d>=0 else 'down'}">{ret_5d:+.2f}%</span>
    </div>
    <div class="card-row">
      <span class="card-label">近 20 日</span>
      <span class="card-value {'up' if ret_20d>=0 else 'down'}">{ret_20d:+.2f}%</span>
    </div>
    <div class="card-row">
      <span class="card-label">近 60 日</span>
      <span class="card-value {'up' if ret_60d>=0 else 'down'}">{ret_60d:+.2f}%</span>
    </div>
    <div class="card-row">
      <span class="card-label">今年以来</span>
      <span class="card-value">—</span>
    </div>
    <div class="card-row">
      <span class="card-label">数据区间</span>
      <span class="card-value">{date_start} ~ {date_end}</span>
    </div>
    <div class="card-row">
      <span class="card-label">平均成交量</span>
      <span class="card-value">{avg_vol:,.0f} 手</span>
    </div>
    <div class="card-row">
      <span class="card-label">平均成交额</span>
      <span class="card-value">{avg_amount/1e4:,.0f} 万元</span>
    </div>
  </div>

  <!-- 价格区间统计 -->
  <div class="card">
    <h3>💹 价格区间分析</h3>
    <div class="card-row">
      <span class="card-label">当前价</span>
      <span class="card-value {'up' if change>=0 else 'down'}">{float(latest['close']):.2f}</span>
    </div>
    <div class="card-row">
      <span class="card-label">近一年最高</span>
      <span class="card-value">{high_52w:.2f}</span>
    </div>
    <div class="card-row">
      <span class="card-label">近一年最低</span>
      <span class="card-value">{low_52w:.2f}</span>
    </div>
    <div class="card-row">
      <span class="card-label">距最高回撤</span>
      <span class="card-value down">{((float(latest['close'])-high_52w)/high_52w*100):.2f}%</span>
    </div>
    <div class="card-row">
      <span class="card-label">距最低涨幅</span>
      <span class="card-value up">{((float(latest['close'])-low_52w)/low_52w*100):.2f}%</span>
    </div>
    <div class="card-row">
      <span class="card-label">近一年振幅</span>
      <span class="card-value">{((high_52w-low_52w)/low_52w*100):.2f}%</span>
    </div>
    <div class="card-row">
      <span class="card-label">平均价格</span>
      <span class="card-value">{df['close'].mean():.2f}</span>
    </div>
  </div>

</div>

<!-- ========== 页脚 ========== -->
<div class="footer">
  数据区间：{date_start} ~ {date_end} ·
  生成时间：{date_end} · 由 WorkBuddy 自动生成 ·
  <a href="https://github.com/kikiJing/AI-quant" target="_blank">GitHub 仓库</a>
</div>

<!-- ========== JS ========== -->
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<script>
(function() {{
  const commonOptions = {{
    layout: {{
      background: {{ type: 'solid', color: '#0d1117' }},
      textColor: '#8b949e',
      fontSize: 12,
    }},
    grid: {{
      vertLines: {{ color: '#21262d' }},
      horzLines: {{ color: '#21262d' }},
    }},
    crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }},
  }};

  /* ====== 1. 主图：K线 + 均线 + 成交量 ====== */
  const chartMain = LightweightCharts.createChart(
    document.getElementById('chart_main'),
    {{
      ...commonOptions,
      width: document.getElementById('chart_main').clientWidth,
      height: 520,
      rightPriceScale: {{ borderColor: '#30363d' }},
      timeScale: {{
        borderColor: '#30363d',
        timeVisible: false,
        tickMarkFormatter: (time) => {{
          const d = new Date(time * 1000);
          return (d.getMonth()+1) + '/' + d.getDate();
        }},
      }},
    }}
  );

  // K线
  const candleSeries = chartMain.addCandlestickSeries({{
    upColor: '#ef5350', downColor: '#26a69a',
    borderUpColor: '#ef5350', borderDownColor: '#26a69a',
    wickUpColor: '#ef5350', wickDownColor: '#26a69a',
  }});
  candleSeries.setData({candle_json});

  // 均线
  const ma5 = chartMain.addLineSeries({{
    color: '#f5a623', lineWidth: 1, priceLineVisible: false, lastValueVisible: false,
  }});
  ma5.setData({ma5_json});

  const ma20 = chartMain.addLineSeries({{
    color: '#388bfd', lineWidth: 1, priceLineVisible: false, lastValueVisible: false,
  }});
  ma20.setData({ma20_json});

  const ma60 = chartMain.addLineSeries({{
    color: '#a371f7', lineWidth: 1, priceLineVisible: false, lastValueVisible: false,
  }});
  ma60.setData({ma60_json});

  // 成交量（独立价格轴）
  const volumeSeries = chartMain.addHistogramSeries({{
    priceFormat: {{ type: 'volume' }},
    priceScaleId: 'volume',
  }});
  chartMain.priceScale('volume').applyOptions({{
    scaleMargins: {{ top: 0.75, bottom: 0 }},
  }});
  volumeSeries.setData({volume_json});

  // 最新价线
  candleSeries.createPriceLine({{
    price: {float(latest['close'])},
    color: '{change_color}',
    lineWidth: 1,
    lineStyle: LightweightCharts.LineStyle.Dashed,
    axisLabelVisible: true,
    title: '最新',
  }});

  chartMain.timeScale().fitContent();

  /* ====== 2. RSI ====== */
  const chartRSI = LightweightCharts.createChart(
    document.getElementById('chart_rsi'),
    {{
      ...commonOptions,
      width: document.getElementById('chart_rsi').clientWidth,
      height: 180,
      rightPriceScale: {{ borderColor: '#30363d', scaleMargins: {{ top: 0.1, bottom: 0.1 }} }},
      timeScale: {{
        borderColor: '#30363d', timeVisible: false,
        tickMarkFormatter: () => '',
      }},
    }}
  );
  const rsiSeries = chartRSI.addLineSeries({{
    color: '#f5a623', lineWidth: 1,
    priceLineVisible: false, lastValueVisible: true,
  }});
  rsiSeries.setData({rsi_json});

  // RSI 超买/超卖参考线
  const rsiOverbought = chartRSI.addLineSeries({{
    color: '#30363d', lineWidth: 1, lineStyle: 2,
    priceLineVisible: false, lastValueVisible: false,
  }});
  rsiOverbought.setData(
    {rsi_json}.filter((_,i) => i===0 || (_ && i===0)).map(d => ({{...d, value: 70}}))
  );
  // 简化：直接画两条参考线
  const rsi70 = []; const rsi30 = [];
  const rsiTimes = {rsi_json}.map(d => d.time);
  if (rsiTimes.length) {{
    rsi70.push({{time: rsiTimes[0], value: 70}}, {{time: rsiTimes[rsiTimes.length-1], value: 70}});
    rsi30.push({{time: rsiTimes[0], value: 30}}, {{time: rsiTimes[rsiTimes.length-1], value: 30}});
  }}
  const line70 = chartRSI.addLineSeries({{color:'#30363d',lineWidth:1,lineStyle:2,priceLineVisible:false,lastValueVisible:false}});
  const line30 = chartRSI.addLineSeries({{color:'#30363d',lineWidth:1,lineStyle:2,priceLineVisible:false,lastValueVisible:false}});
  line70.setData(rsi70);
  line30.setData(rsi30);

  chartRSI.timeScale().fitContent();

  /* ====== 3. MACD ====== */
  const chartMACD = LightweightCharts.createChart(
    document.getElementById('chart_macd'),
    {{
      ...commonOptions,
      width: document.getElementById('chart_macd').clientWidth,
      height: 220,
      rightPriceScale: {{ borderColor: '#30363d' }},
      timeScale: {{
        borderColor: '#30363d', timeVisible: false,
        tickMarkFormatter: (time) => {{
          const d = new Date(time * 1000);
          const m = d.getMonth()+1, day = d.getDate();
          return m + '/' + day;
        }},
      }},
    }}
  );
  const macdLine = chartMACD.addLineSeries({{
    color: '#f5a623', lineWidth: 1,
    priceLineVisible: false, lastValueVisible: true, title: 'MACD',
  }});
  macdLine.setData({macd_line_json});

  const signalLine = chartMACD.addLineSeries({{
    color: '#388bfd', lineWidth: 1,
    priceLineVisible: false, lastValueVisible: true, title: 'Signal',
  }});
  signalLine.setData({macd_signal_json});

  const macdHist = chartMACD.addHistogramSeries({{
    priceFormat: {{ type: 'price' }},
    priceScaleId: 'macd',
  }});
  chartMACD.priceScale('macd').applyOptions({{ scaleMargins: {{ top: 0.1, bottom: 0.1 }} }});
  macdHist.setData({macd_hist_json});

  chartMACD.timeScale().fitContent();

  /* ====== 同步时间轴 ====== */
  [chartMain, chartRSI, chartMACD].forEach(c => {{
    c.timeScale().subscribeVisibleLogicalRangeChange(range => {{
      const r = c.timeScale().getVisibleLogicalRange();
      if (r) {{
        [chartMain, chartRSI, chartMACD].forEach(other => {{
          if (other !== c) other.timeScale().setVisibleLogicalRange(r);
        }});
      }}
    }});
  }});

  /* ====== 自适应宽度 ====== */
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
    print(f"  共 {len(df)} 条记录，{df['trade_date'].iloc[0].date()} ~ {df['trade_date'].iloc[-1].date()}")

    print("计算技术指标（MA / RSI / MACD）...")
    html = generate_html(df)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML 看板已生成：{OUTPUT_HTML}")
    print("   直接在浏览器中打开即可查看。")


if __name__ == "__main__":
    main()
