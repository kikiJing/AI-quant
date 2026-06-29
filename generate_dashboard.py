#!/usr/bin/env python3
"""
generate_dashboard.py — 读取 SMIC CSV 数据，生成独立的 HTML 看板
用法: python3 generate_dashboard.py
"""

import os
import json
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CSV_FILE = os.path.join(DATA_DIR, "smic_688981_daily.csv")
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), "outputs", "smic_dashboard.html")

def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")
    # 确保日期格式正确
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
    # 按日期升序排列
    df = df.sort_values("trade_date").reset_index(drop=True)
    return df

def df_to_candlestick(df: pd.DataFrame) -> list:
    """转换为 lightweight-charts K 线数据格式。"""
    return [
        {
            "time": row["trade_date"],
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
        }
        for _, row in df.iterrows()
    ]

def df_to_volume(df: pd.DataFrame) -> list:
    """转换为成交量柱状图数据格式（绿色/红色区分涨跌）。"""
    result = []
    for _, row in df.iterrows():
        close = float(row["close"])
        open_ = float(row["open"])
        # 中国股票惯例：涨=红，跌=绿
        color = "#ef5350" if close >= open_ else "#26a69a"
        result.append({
            "time": row["trade_date"],
            "value": float(row["vol"]),
            "color": color,
        })
    return result

def generate_html(candle_data: list, volume_data: list, df: pd.DataFrame) -> str:
    candle_json = json.dumps(candle_data, ensure_ascii=False)
    volume_json = json.dumps(volume_data, ensure_ascii=False)

    # 计算统计信息
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    change = float(latest["close"]) - float(prev["close"])
    pct = (change / float(prev["close"])) * 100
    high_52w = df["high"].max()
    low_52w = df["low"].min()
    avg_vol = df["vol"].mean()

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
            background: #1a1a2e;
            color: #e0e0e0;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            padding: 20px 32px;
            border-bottom: 1px solid #333;
        }}
        .header h1 {{
            font-size: 24px;
            font-weight: 600;
            color: #ffffff;
        }}
        .header .subtitle {{
            font-size: 14px;
            color: #888;
            margin-top: 4px;
        }}
        .stats-bar {{
            display: flex;
            gap: 24px;
            padding: 16px 32px;
            background: #16213e;
            border-bottom: 1px solid #333;
            flex-wrap: wrap;
        }}
        .stat-item {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #888;
        }}
        .stat-value {{
            font-size: 18px;
            font-weight: 600;
        }}
        .stat-value.up {{ color: #ef5350; }}
        .stat-value.down {{ color: #26a69a; }}
        .stat-value.neutral {{ color: #ffffff; }}
        .chart-container {{
            padding: 16px 32px;
        }}
        #chart {{
            width: 100%;
            height: 600px;
            background: #1a1a2e;
            border-radius: 8px;
        }}
        .footer {{
            padding: 16px 32px;
            font-size: 12px;
            color: #666;
            text-align: center;
            border-top: 1px solid #333;
        }}
        .legend {{
            display: flex;
            gap: 16px;
            padding: 8px 32px;
            font-size: 13px;
            color: #aaa;
        }}
        .legend span {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }}
        .dot.red {{ background: #ef5350; }}
        .dot.green {{ background: #26a69a; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>中芯国际（688981.SH）</h1>
        <div class="subtitle">科创板 · 近一年日线行情 · 数据来源：Tushare Pro</div>
    </div>

    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-label">最新价（{latest["trade_date"]}）</span>
            <span class="stat-value {'up' if change >= 0 else 'down'}">{float(latest['close']):.2f}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">涨跌额</span>
            <span class="stat-value {'up' if change >= 0 else 'down'}">{change:+.2f}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">涨跌幅</span>
            <span class="stat-value {'up' if change >= 0 else 'down'}">{pct:+.2f}%</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">近一年最高</span>
            <span class="stat-value neutral">{high_52w:.2f}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">近一年最低</span>
            <span class="stat-value neutral">{low_52w:.2f}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">平均成交量（手）</span>
            <span class="stat-value neutral">{avg_vol:,.0f}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">数据条数</span>
            <span class="stat-value neutral">{len(df)} 条</span>
        </div>
    </div>

    <div class="legend">
        <span><span class="dot red"></span> 涨（收盘价 ≥ 开盘价）</span>
        <span><span class="dot green"></span> 跌（收盘价 ＜ 开盘价）</span>
    </div>

    <div class="chart-container">
        <div id="chart"></div>
    </div>

    <div class="footer">
        数据区间：{df.iloc[0]["trade_date"]} ~ {df.iloc[-1]["trade_date"]} ·
        更新时间：{df.iloc[-1]["trade_date"]} ·
        由 WorkBuddy 自动生成
    </div>

    <script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
    <script>
        const candleData = {candle_json};
        const volumeData = {volume_json};

        const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
            layout: {{
                background: {{ type: 'solid', color: '#1a1a2e' }},
                textColor: '#e0e0e0',
                fontSize: 12,
            }},
            grid: {{
                vertLines: {{ color: '#2a2a4a' }},
                horzLines: {{ color: '#2a2a4a' }},
            }},
            crosshair: {{
                mode: LightweightCharts.CrosshairMode.Normal,
            }},
            rightPriceScale: {{
                borderColor: '#444',
            }},
            timeScale: {{
                borderColor: '#444',
                timeVisible: false,
                tickMarkFormatter: (time) => {{
                    const d = new Date(time * 1000);
                    return (d.getMonth() + 1) + '/' + d.getDate();
                }},
            }},
            handleScroll: {{ vertTouchDrag: false }},
        }});

        // K 线图
        const candleSeries = chart.addCandlestickSeries({{
            upColor: '#ef5350',
            downColor: '#26a69a',
            borderUpColor: '#ef5350',
            borderDownColor: '#26a69a',
            wickUpColor: '#ef5350',
            wickDownColor: '#26a69a',
        }});
        candleSeries.setData(candleData);

        // 成交量柱状图（放在 K 线图下方）
        const volumeSeries = chart.addHistogramSeries({{
            priceFormat: {{ type: 'volume' }},
            priceScaleId: 'volume',
        }});
        chart.priceScale('volume').applyOptions({{
            scaleMargins: {{
                top: 0.8,
                bottom: 0,
            }},
        }});
        volumeSeries.setData(volumeData);
        volumeSeries.priceScale().applyOptions({{
            scaleMargins: {{
                top: 0.8,
                bottom: 0,
            }},
        }});

        // 标识最新价位的水平线
        candleSeries.createPriceLine({{
            price: {float(latest['close'])},
            color: '{'#ef5350' if change >= 0 else '#26a69a'}',
            lineWidth: 1,
            lineStyle: LightweightCharts.LineStyle.Dashed,
            axisLabelVisible: true,
            title: '最新 {float(latest['close']):.2f}',
        }});

        chart.timeScale().fitContent();
        window.addEventListener('resize', () => chart.resize(
            document.getElementById('chart').clientWidth, 600
        ));
    </script>
</body>
</html>"""

def main():
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    df = load_data()
    print(f"加载数据：{len(df)} 条记录")

    candle_data = df_to_candlestick(df)
    volume_data = df_to_volume(df)

    html = generate_html(candle_data, volume_data, df)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"HTML 看板已生成：{OUTPUT_HTML}")
    print(f"直接用浏览器打开即可查看（无需服务器）。")

if __name__ == "__main__":
    main()
