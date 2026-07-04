# AI Quant Lab - 股票技术分析工具

一个灵活的股票技术分析工具，支持多种技术指标计算、参数调节和可视化。

## 📊 功能特性

### 1. 数据获取
- 从Tushare Pro获取A股日线数据
- 支持近2年历史数据下载
- 自动保存为CSV格式

### 2. 技术指标计算
支持以下技术指标（所有指标均可调节参数）：

| 指标 | 说明 | 默认参数 |
|------|------|----------|
| MA | 移动平均线 | 5, 10, 20, 60 |
| RSI | 相对强弱指标 | 14 |
| MACD | 移动平均收敛发散 | 12, 26, 9 |
| 布林带 | Bollinger Bands | 20, 2倍标准差 |
| ATR | 平均真实波幅 | 14 |
| DMI/ADX | 动向指标 | 14 |
| KDJ | 随机指标 | 9, 3, 3 |
| VWAP | 成交量加权平均价 | - |

### 3. 数据分析
- 描述性统计（均值、标准差、分位数等）
- 数据质量检查（缺失值、异常值）
- 复权处理（前复权）

### 4. 可视化
- K线图与指标叠加
- 独立指标面板（RSI、MACD、KDJ、DMI等）
- 交互式参数调节（计划）
- HTML报告生成（计划）

## 📁 项目结构

```
ai-quant-lab/
├── data/               # 数据文件（CSV格式）
├── scripts/            # Python脚本
│   ├── fetch_stocks.py           # 数据获取脚本
│   ├── diagnose_and_adjust_stocks.py  # 数据诊断与复权
│   ├── fetch_adj_factors.py      # 获取复权因子
│   └── apply_adjustment.py       # 应用复权处理
├── notebooks/          # Jupyter Notebooks
│   └── technical_indicators_demo.ipynb  # 技术指标代码复现
├── docs/               # 文档
│   ├── DESIGN_DOCUMENT.md        # 产品设计文档
│   ├── interface_prototype.html  # 界面原型
│   └── README_adjustment.md      # 复权处理说明
├── outputs/            # 输出文件
└── README.md           # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pandas numpy tushare requests
```

### 2. 配置Tushare Token

在 `config.py` 中设置您的Tushare token：

```python
TUSHARE_TOKEN = "您的token"
```

或设置环境变量：

```bash
export TUSHARE_TOKEN="您的token"
```

### 3. 获取数据

```bash
python scripts/fetch_stocks.py
```

这将从Tushare获取5只代表性A股近2年的数据，并保存为CSV文件。

### 4. 运行Jupyter Notebook

```bash
jupyter notebook notebooks/technical_indicators_demo.ipynb
```

在Notebook中，您可以：
- 学习每个技术指标的计算方法
- 调节参数观察指标变化
- 可视化指标图形

## 📖 使用说明

### 数据获取

`fetch_stocks.py` 获取以下5只代表性股票的数据：
1. 宁德时代 (300750.SZ) - 科技/新能源
2. 中国平安 (601318.SH) - 金融
3. 贵州茅台 (600519.SH) - 消费
4. 中国石油 (601857.SH) - 能源
5. 比亚迪 (002594.SZ) - 制造

### 技术指标计算

所有技术指标的计算函数都在 `technical_indicators_demo.ipynb` 中提供，包括：
- 完整的Python实现代码
- 详细的参数说明
- 可视化示例
- 参数调节效果对比

### 复权处理

由于Tushare API的频率限制，复权处理需要分步进行：

1. 获取复权因子（每次间隔1小时）：
   ```bash
   python scripts/fetch_adj_factors.py
   ```

2. 应用复权处理：
   ```bash
   python scripts/apply_adjustment.py
   ```

详细步骤请参考 `docs/README_adjustment.md`。

## 🔧 技术指标参数说明

### RSI（相对强弱指标）
- **参数**：period (默认14)
- **解读**：>70 超买，<30 超卖
- **用途**：识别反转信号

### MACD（移动平均收敛发散）
- **参数**：fast_period (12), slow_period (26), signal_period (9)
- **解读**：DIF上穿DEA买入，下穿卖出
- **用途**：趋势反转识别

### 布林带（Bollinger Bands）
- **参数**：period (20), std_dev (2)
- **解读**：价格触及上轨可能回落，触及下轨可能反弹
- **用途**：波动范围评估

### ATR（平均真实波幅）
- **参数**：period (14)
- **解读**：值越大波动越强
- **用途**：止损位设置

### DMI/ADX（动向指标）
- **参数**：period (14)
- **解读**：ADX>25趋势强，<20无趋势
- **用途**：趋势强度评估

### KDJ（随机指标）
- **参数**：n (9), m1 (3), m2 (3)
- **解读**：>80 超买，<20 超卖；K线上穿D线买入
- **用途**：短期反转识别

### VWAP（成交量加权平均价）
- **参数**：reset_daily (True/False)
- **解读**：价格>VWAP看涨，<VWAP看跌
- **用途**：机构成本参考

## 📊 设计文档

详细的产品设计文档请参考：
- `docs/DESIGN_DOCUMENT.md` - 完整的功能设计和技术架构
- `docs/interface_prototype.html` - 界面设计原型（可在浏览器中打开查看）

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📝 许可证

MIT License

## 📧 联系方式

如有问题，请提交Issue或联系作者。

---

**⚠️ 免责声明**：本工具仅供参考学习，不构成投资建议。投资有风险，入市需谨慎。