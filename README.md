# AI Quant Lab 🧪

一个灵活的股票技术分析工具，支持多种技术指标计算和可视化。

## ✨ 功能特性

### 📊 技术指标（8种）
- **MA**（移动平均线）：MA5/10/20/60，参数可调
- **RSI**（相对强弱指标）：超买超卖判断，参数可调
- **MACD**：DIF/DEA/MACD柱状图，快慢线参数可调
- **布林带**（Bollinger Bands）：上轨/中轨/下轨，周期和标准差可调
- **DMI/ADX**：+DI/-DI/ADX，趋势强度判断
- **KDJ**：K/D/J线，随机指标
- **VWAP**：成交量加权平均价，机构常用指标
- **ATR**：平均真实波幅，波动率衡量

### 🎯 交易信号分析
自动计算并展示6种技术指标的买卖信号：
- 信号强度评估（强/中/弱）
- 信号原因分析
- 实时更新最新信号

### 📈 交互式图表
- 使用 TradingView Lightweight Charts 渲染
- K线图 + 成交量图
- 所有指标图表支持缩放、拖拽
- 图表下方有详细图例说明

### 📁 数据支持
- 直接加载 CSV 文件
- 支持 Tushare 数据格式（trade_date/vol 列名）
- 内置5只示例股票数据：
  - 宁德时代 (300750.SZ)
  - 中国平安 (601318.SH)
  - 贵州茅台 (600519.SH)
  - 中国石油 (601857.SH)
  - 比亚迪 (002594.SZ)

## 🚀 快速开始

### 方法1: 一键启动（推荐）
```bash
cd ai-quant-lab
python3 run.py
```
然后访问 `http://localhost:8000/index.html`

### 方法2: 手动启动
```bash
cd ai-quant-lab
python3 -m http.server 8000
```
然后访问 `http://localhost:8000/index.html`

### 方法3: 直接打开（功能受限）
双击 `index.html` 文件，但 CSV 加载可能失败（浏览器 CORS 限制）。

## 📂 项目结构
```
AI quant/
├── ai-quant-lab/          # 主应用目录
│   ├── index.html         # 主界面（单文件完整应用）
│   ├── run.py             # 启动脚本
│   ├── start.sh           # 启动脚本（Mac/Linux）
│   ├── data/              # 股票数据CSV文件
│   └── test_csv_parse.html # CSV解析测试工具
├── data/                  # 原始数据目录
├── fetch_stocks.py        # 股票数据获取脚本
├── tushare_client.py      # Tushare API 封装
└── DESIGN_DOCUMENT.md    # 详细设计文档
```

## 🛠️ 使用说明

### 1. 加载数据
- 打开网页后，在左侧面板选择股票
- 点击"🔄 加载数据"按钮
- 数据加载成功后，图表自动显示

### 2. 调节指标参数
- 在左侧"参数设置"面板调节各指标参数
- 修改后点击"🔄 更新图表"应用新参数

### 3. 查看交易信号
- 滚动到页面下方"🎯 交易信号分析"面板
- 查看各指标的最新买卖信号

### 4. 图表交互
- 鼠标滚轮：缩放
- 鼠标拖拽：平移
- 双击：重置视图

## 📊 技术指标说明

| 指标 | 用途 | 买入信号 | 卖出信号 |
|------|------|----------|----------|
| RSI | 超买超卖 | < 30 | > 70 |
| MACD | 趋势反转 | DIF上穿DEA | DIF下穿DEA |
| 布林带 | 价格波动 | 触及下轨 | 触及上轨 |
| KDJ | 随机指标 | K线上穿D线 | K线下穿D线 |
| DMI | 趋势强度 | +DI上穿-DI | -DI上穿+DI |
| MA | 均线支撑 | 价格在MA上方 | 价格在MA下方 |

## 📦 数据来源

示例数据来自 [Tushare Pro](https://tushare.pro/)（免费版）。

要获取最新数据，运行：
```bash
python fetch_stocks.py
```

需要配置 Tushare token（在 `config.py` 中设置）。

## 🔧 技术栈

- **前端**：HTML + CSS + JavaScript（单文件）
- **图表库**：[Lightweight Charts](https://www.tradingview.com/lightweight-charts/)
- **数据源**：Tushare Pro API
- **运行环境**：Python http.server（本地HTTP服务器）

## 📝 开发笔记

- 所有计算在浏览器端完成，无需后端
- 单HTML文件架构，方便分发
- 支持 Chrome/Edge/Firefox/Safari 现代浏览器

## 📄 许可证

MIT License

## 🙏 致谢

- [Tushare Pro](https://tushare.pro/) - 提供A股数据
- [Lightweight Charts](https://www.tradingview.com/lightweight-charts/) - 提供专业图表库

---

**⚠️ 免责声明**：本工具仅供学习和研究使用，不构成任何投资建议。投资有风险，入市需谨慎。
