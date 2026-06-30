# ============================================================
# Cell 5：RSI + MACD 技术指标图
# ============================================================
fig2 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.08,
    row_heights=[0.5, 0.5],
    subplot_titles=("RSI(14) 相对强弱指标", "MACD(12,26,9)"),
)

# ---- RSI ----
fig2.add_trace(
    go.Scatter(x=df["trade_date"], y=df["rsi14"],
               mode="lines", name="RSI(14)",
               line=dict(color="#ffa726", width=1.8)),
    row=1, col=1
)
# 超买/超卖参考线
for lvl, clr, label in [(70, "#ef5350", "超买 70"), (30, "#26a69a", "超卖 30")]:
    fig2.add_hline(y=lvl, line_dash="dash", line_color=clr,
                   annotation_text=label, row=1, col=1)

# ---- MACD DIF / DEA ----
fig2.add_trace(
    go.Scatter(x=df["trade_date"], y=df["macd_dif"],
               mode="lines", name="DIF", line=dict(color="#f5a623", width=1.5)),
    row=2, col=1
)
fig2.add_trace(
    go.Scatter(x=df["trade_date"], y=df["macd_dea"],
               mode="lines", name="DEA", line=dict(color="#00e5ff", width=1.5)),
    row=2, col=1
)
# MACD 柱状图
fig2.add_trace(
    go.Bar(
        x=df["trade_date"], y=df["macd_hist"],
        name="MACD Hist",
        marker_color=["#ef5350" if v >= 0 else "#26a69a" for v in df["macd_hist"]],
        opacity=0.6,
    ),
    row=2, col=1
)

fig2.update_layout(
    template="plotly_dark",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
)
fig2.update_yaxes(title_text="RSI", row=1, col=1)
fig2.update_yaxes(title_text="MACD", row=2, col=1)

fig2.show()
