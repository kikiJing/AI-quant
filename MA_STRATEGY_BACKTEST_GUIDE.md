# 📊 均线策略回测系统 - 使用文档

> **一个灵活的均线策略回测工具，支持双均线策略、趋势过滤器、ATR过滤器**

---

## 📋 目录

- [功能特点](#功能特点)
- [快速开始](#快速开始)
- [参数说明](#参数说明)
- [使用示例](#使用示例)
- [输出说明](#输出说明)
- [常见问题](#常见问题)
- [进阶用法](#进阶用法)

---

## 🌟 功能特点

### ✅ 核心功能

1. **数据加载** - 支持加载本地复权股价数据（CSV格式）
2. **技术指标计算** - 支持 MA（简单移动平均）和 EMA（指数移动平均）
3. **信号生成** - 双均线策略 + 趋势过滤器 + ATR过滤器
4. **模拟回测** - 支持手续费、滑点、多种仓位管理方式
5. **量化指标** - 收益类、风险类、综合类、交易质量类指标
6. **可视化** - 交互式K线图、买卖信号标记、净值曲线
7. **BUY-HOLD对比** - 与买入持有策略进行多维度对比

### 🔍 信号过滤器

#### 1. 趋势过滤器
- **原理**：使用第三条更长周期的均线（如120日）作为趋势判断
- **规则**：
  - ✅ 只有当**价格 > 趋势均线** 且 **短期均线 > 趋势均线** 时，才参与金叉做多
  - ❌ 否则，即使出现金叉信号也不买入（规避下跌趋势中的反弹）

#### 2. ATR过滤器
- **原理**：ATR（平均真实波幅）衡量市场波动率
- **规则**：
  - ✅ 当 ATR 处于历史高位时（如 > P80），认为是趋势市，参与交易
  - ❌ 当 ATR 处于历史低位时（如 < P20），认为是震荡市，规避交易

---

## 🚀 快速开始

### 方法 1：使用 Jupyter Notebook（推荐）

1. **打开 Notebook**
   ```bash
   cd /Users/kikijing/Desktop/AI\ quant
   jupyter notebook ma_strategy_backtest_interface.ipynb
   ```

2. **按顺序运行 Cells**
   - Cell 1: 安装依赖库
   - Cell 2: 配置策略参数
   - Cell 3: 加载股票数据
   - Cell 4: 计算技术指标和生成信号
   - Cell 5: 执行回测
   - Cell 6: 查看可视化图表
   - Cell 7: 查看量化指标
   - Cell 8: 查看交易记录
   - Cell 9: 批量回测（可选）
   - Cell 10: 参数优化（可选）

### 方法 2：使用 Python 脚本

```bash
cd /Users/kikijing/Desktop/AI\ quant
python ma_strategy_backtest.py
```

---

## ⚙️ 参数说明

### 📐 均线参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `short_window` | 5 | 短均线周期（如5日、10日） |
| `long_window` | 15 | 长均线周期（如15日、20日） |
| `ma_type` | `'MA'` | 均线类型：`'MA'`（简单移动平均）或 `'EMA'`（指数移动平均） |

**建议配置**：
- 短线交易：short=5, long=15
- 中线交易：short=10, long=30
- 长线交易：short=20, long=60

### 🔍 过滤器参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `trend_filter` | `True` | 是否启用趋势过滤器 |
| `trend_window` | 120 | 趋势过滤器周期（建议60/120/200） |
| `atr_filter` | `True` | 是否启用ATR过滤器 |
| `atr_window` | 14 | ATR计算周期（建议14） |
| `atr_percentile` | 20 | ATR历史百分位阈值（建议20-40） |
| `atr_lookback` | 100 | ATR历史回看天数（建议100） |

**ATR百分位说明**：
- `20` - 严格模式（只有ATR > P20时才交易）
- `30` - 中等模式
- `40` - 宽松模式

### 💰 回测参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `initial_capital` | 100000 | 初始资金（元） |
| `commission` | 0.001 | 手续费率（0.1% = 0.001） |
| `slippage` | 0.001 | 滑点（0.1% = 0.001） |

**A股手续费参考**：
- 万3（0.03%）= 0.0003
- 万5（0.05%）= 0.0005
- 千1（0.1%）= 0.001

### 📊 仓位管理

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `position_sizing` | `'full'` | 仓位管理方式 |
| `fixed_shares` | 100 | 固定数量（当 `position_sizing='fixed_shares'` 时） |
| `fixed_ratio` | 0.2 | 固定比例（当 `position_sizing='fixed_ratio'` 时） |

**仓位管理选项**：
- `'full'` - 全仓买卖（所有资金一次性买入/卖出）
- `'fixed_shares'` - 固定数量（每次买入/卖出固定数量的股票）
- `'fixed_ratio'` - 固定比例（每次买入/卖出固定比例的持仓）

---

## 📖 使用示例

### 示例 1：回测贵州茅台（单只股票）

```python
# 在 Jupyter Notebook 中运行

# Cell 2: 选择股票
SELECTED_STOCK = '600519.SH'  # 贵州茅台

# Cell 2: 配置参数
STRATEGY_PARAMS = {
    'short_window': 10,          # 短均线10日
    'long_window': 30,           # 长均线30日
    'ma_type': 'MA',            # 使用简单移动平均
    'trend_filter': True,       # 启用趋势过滤器
    'trend_window': 120,        # 趋势均线120日
    'atr_filter': True,         # 启用ATR过滤器
    'atr_percentile': 20,       # ATR百分位P20
    'initial_capital': 100000,  # 初始资金10万元
    'commission': 0.0005,       # 手续费万5
    'slippage': 0.001,          # 滑点0.1%
}

# 运行 Cell 3-8 查看结果
```

### 示例 2：批量回测5只股票

```python
# 在 Jupyter Notebook 中运行 Cell 9

# 自动回测所有5只股票并生成对比报告
# 输出：outputs/ma_backtest/reports/summary_report.csv
```

### 示例 3：参数优化

```python
# 在 Jupyter Notebook 中运行 Cell 10

# 网格搜索最优参数组合
# 输出：按夏普比率排序的参数组合表
```

---

## 📊 输出说明

### 1. 可视化图表

#### K线图 & 买卖信号
- 📈 收盘价走势（白色线）
- 🔵 短均线（蓝色线）
- 🟠 长均线（橙色线）
- 🟢 趋势均线（绿色虚线，可选）
- 🔴 买入信号（红色▲）
- 🟢 卖出信号（绿色▼）

#### 净值曲线
- 🔵 策略净值（蓝色实线）
- 🟠 BUY-HOLD净值（橙色虚线）

### 2. 量化指标报告

#### 收益类指标
- 策略总收益率
- BUY-HOLD总收益率
- 超额收益
- 策略年化收益率
- BUY-HOLD年化收益率

#### 风险类指标
- 策略最大回撤
- BUY-HOLD最大回撤

#### 综合类指标
- 策略夏普比率
- BUY-HOLD夏普比率

#### 交易质量类指标
- 交易次数
- 胜率
- 盈亏比

#### 交易成本统计
- 累计手续费
- 累计滑点成本
- 累计交易成本
- 平均单次交易成本

### 3. 交易记录 CSV

**文件路径**：`outputs/ma_backtest/reports/{股票名}_{代码}_trades.csv`

**字段说明**：
- `date` - 交易日期
- `type` - 交易类型（BUY/SELL）
- `signal_price` - 信号触发价格
- `execution_price` - 实际执行价格（含滑点）
- `shares` - 交易数量（股）
- `commission` - 手续费成本
- `slippage` - 滑点成本
- `total_cost` - 总交易成本
- `cash_after` - 交易后现金余额
- `position_after` - 交易后持仓数量

### 4. 汇总对比报告

**文件路径**：`outputs/ma_backtest/reports/summary_report.csv`

**字段说明**：
- 股票、行业
- 策略收益率、BUY-HOLD收益率、超额收益
- 策略夏普比率、BUY-HOLD夏普比率
- 策略最大回撤
- 交易次数

---

## ❓ 常见问题

### Q1: 如何修改回测时间段？

**A**: 修改 `STRATEGY_PARAMS` 中的 `start_date` 和 `end_date`：

```python
STRATEGY_PARAMS = {
    'start_date': '2024-01-01',  # 修改为想要的起始日期
    'end_date': '2024-12-31',    # 修改为想要的结束日期
}
```

### Q2: 如何禁用某个过滤器？

**A**: 将对应参数设置为 `False`：

```python
STRATEGY_PARAMS = {
    'trend_filter': False,  # 禁用趋势过滤器
    'atr_filter': False,    # 禁用ATR过滤器
}
```

### Q3: 为什么没有交易信号？

**A**: 可能原因：
1. 趋势过滤器过于严格 - 尝试减小 `trend_window` 或禁用 `trend_filter`
2. ATR过滤器过于严格 - 尝试增大 `atr_percentile` 或禁用 `atr_filter`
3. 数据时间范围太短 - 确保有足够的数据计算长期均线

### Q4: 如何保存图表？

**A**: Plotly 图表支持：
1. 点击图表右上角的相机图标保存为PNG
2. 在代码中使用 `fig.write_html('chart.html')` 保存为HTML

### Q5: 手续费和滑点如何设置？

**A**: 
- **手续费**：`commission=0.001` 表示 0.1%
- **滑点**：`slippage=0.001` 表示 0.1%

**计算公式**：
- 买入执行价格 = 信号价格 × (1 + 滑点)
- 卖出执行价格 = 信号价格 × (1 - 滑点)
- 手续费 = 交易金额 × 手续费率

---

## 🔧 进阶用法

### 1. 自定义股票列表

**修改 `STOCKS` 字典**：

```python
STOCKS = {
    '000001.SZ': {'name': '平安银行', 'industry': '金融'},\n    '000002.SZ': {'name': '万科A', 'industry': '房地产'},\n    # 添加更多股票...\n}
```

**注意**：需要在 `data/adjusted/` 目录下有对应的CSV数据文件。

### 2. 增加止损止盈

**在 `run_backtest()` 函数中添加**：

```python
# 止损（当亏损超过5%时强制平仓）
if (current_value - initial_capital) / initial_capital < -0.05:\n    # 执行卖出\n    pass\n\n# 止盈（当盈利超过20%时分批止盈）\nif (current_value - initial_capital) / initial_capital > 0.20:\n    # 执行分批卖出\n    pass
```

### 3. 导出PDF报告

**使用 `pdfkit` 或 `weasyprint` 库**：

```python
import weasyprint

# 将 Notebook 转换为 HTML
# 然后使用 weasyprint 转换为 PDF
```

---

## 📂 文件结构

```
/Users/kikijing/Desktop/AI quant/
├── ma_strategy_backtest_interface.ipynb  # Jupyter Notebook（本文件）
├── ma_strategy_backtest.py               # Python 脚本版本
├── strategy/                             # 策略模块包
│   ├── __init__.py                      # 包初始化
│   ├── ma_strategy.py                   # 技术指标计算
│   ├── backtester.py                    # 回测引擎
│   └── metrics.py                       # 量化指标计算
├── data/adjusted/                        # 数据目录
│   ├── ningde_times_300750_daily_adjusted.csv
│   ├── ping_an_601318_daily_adjusted.csv
│   ├── moutai_600519_daily_adjusted.csv
│   ├── petro_china_601857_daily_adjusted.csv
│   └── byd_002594_daily_adjusted.csv
└── outputs/ma_backtest/                  # 输出目录
    ├── charts/                          # HTML图表
    └── reports/                         # CSV报告
```

---

## 📞 联系与反馈

如有问题或建议，请：
1. 在 GitHub 上提交 Issue
2. 或直接修改代码并提交 Pull Request

---

## 📄 许可证

MIT License

---

**最后更新**：2026-07-07
