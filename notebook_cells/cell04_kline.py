# ============================================================
# Cell 4：K 线图 + 成交量（Plotly 交互式）
# 中国配色：红=涨，绿=跌
# ============================================================
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 涨跌颜色（中国习惯）
df["color"] = df.apply(
    lambda r: "#ef5350" if r["close"] >= r["open"] else "#26a69a",
    axis=1
)

# 子图布局：K 线 + 成交量
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.75, 0.25],
    subplot_titles=(
        f"{TS_CODE}   K线图（近一年）",
        "成交量"
    ),
)

# ---- K 线 ----
fig.add_trace(
    go.Candlestick(
        x=df["trade_date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="K线",
        increasing_line_color="#ef5350",   # 红涨
        decreasing_line_color="#26a69a",   # 绿跌
        increasing_fillcolor="rgba(239,83,80,0.7)",
        decreasing_fillcolor="rgba(38,166,154,0.7)",
    ),
    row=1, col=1
)

# ---- 均线 ----
for col, name, clr in [
    ("ma5",  "MA5",  "#f5a623"),
    ("ma20", "MA20", "#e040fb"),
    ("ma60", "MA60", "#00e5ff"),
]:
    fig.add_trace(
        go.Scatter(x=df["trade_date"], y=df[col],
                   mode="lines", name=name, line=dict(color=clr, width=1.2)),
        row=1, col=1
    )

# ---- 成交量柱状图 ----
fig.add_trace(
    go.Bar(
        x=df["trade_date"],
        y=df["vol"],
        name="成交量",
        marker_color=df["color"],
        opacity=0.7,
    ),
    row=2, col=1
)

# ---- 布局 ----
latest = df.iloc[-1]
fig.update_layout(
    title=dict(
        text=(
            f"中芯国际（{TS_CODE}）近一年行情  "
            f"| 最新价：{latest['close']:.2f}  "
            f"涨跌：{latest['pct_chg']:+.2f}%"
        ),
        x=0.02, font_size=16
    ),
    xaxis_rangeslider_visible=False,
    template="plotly_dark",
    height=700,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
)
fig.update_yaxes(title_text="价格（元）", row=1, col=1)
fig.update_yaxes(title_text="成交量（手）", row=2, col=1)

fig.show()
