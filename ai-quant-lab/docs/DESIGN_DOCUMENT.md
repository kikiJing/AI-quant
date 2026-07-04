# 股票数据分析工具 - 产品设计文档

## 1. 产品概述

### 1.1 产品名称
**StockAnalyzer Pro** - 交互式股票技术分析工具

### 1.2 产品定位
一个基于浏览器的独立HTML工具，为用户提供灵活的股票数据可视化与技术指标分析功能，无需服务器端处理，所有计算和渲染均在客户端完成。

### 1.3 目标用户
- 股票投资者和技术分析爱好者
- 量化交易初学者
- 需要快速验证技术指标的分析师

### 1.4 核心价值
- **灵活性**：支持多股票选择、指标参数自定义
- **交互性**：实时调节参数，即时看到图表变化
- **专业性**：提供完整的技术指标和统计分析方法
- **独立性**：生成单个HTML文件，可离线使用，无需服务器

---

## 2. 功能需求

### 2.1 数据管理模块

#### 2.1.1 数据源支持
- **CSV文件上传**：用户可以上传本地CSV文件（格式兼容已生成的股票数据）
- **示例数据**：内置5只示例股票数据（宁德时代、中国平安、贵州茅台、中国石油、比亚迪）
- **数据格式要求**：
  - 必需字段：`trade_date`, `open`, `high`, `low`, `close`, `vol`, `amount`
  - 可选字段：`ts_code`, `pre_close`, `change`, `pct_chg`
  - 日期格式：YYYY-MM-DD 或 YYYYMMDD

#### 2.1.2 数据预览
- 显示加载数据的股票代码、日期范围、记录数
- 数据质量检查：缺失值、异常值检测

### 2.2 技术指标计算模块

#### 2.2.1 均线系统（MA）
- **参数**：周期（默认：5, 20, 60）
- **可视化**：叠加在K线主图上，最多支持5条均线同时显示
- **参数调节**：用户输入框，可添加/删除均线

#### 2.2.2 RSI（相对强弱指标）
- **参数**：周期（默认：14）
- **可视化**：独立面板，显示RSI曲线
- **参考线**：超买线（70）、超卖线（30）
- **参数调节**：滑块或输入框，实时更新

#### 2.2.3 MACD（指数平滑异同移动平均线）
- **参数**：
  - 快线周期（默认：12）
  - 慢线周期（默认：26）
  - 信号线周期（默认：9）
- **可视化**：独立面板，显示DIF线、DEA线、柱状图
- **参数调节**：三个参数的独立输入框

#### 2.2.4 布林带（Bollinger Bands）
- **参数**：
  - 周期（默认：20）
  - 标准差倍数（默认：2.0）
- **可视化**：叠加在K线主图上，显示上轨、中轨、下轨
- **填充区域**：可选是否填充上下轨之间的区域
- **参数调节**：周期和标准差倍数的输入框

#### 2.2.5 ATR（平均真实波幅）
- **参数**：周期（默认：14）
- **可视化**：独立面板，显示ATR曲线
- **应用提示**：提供基于ATR的止损位计算
- **参数调节**：周期输入框

#### 2.2.6 DMI/ADX（动向指标/平均趋向指标）

**功能**：衡量市场趋势的强度，不关心趋势方向。ADX > 25 表示有明确趋势。

**参数**：
- 周期（默认：14）

**可视化**：
- 独立面板，显示三条线：
  - ADX线（主指标，较粗线条）
  - +DI线（正向动向指标）
  - -DI线（负向动向指标）
- 参考线：ADX = 20（趋势强弱分界线）、ADX = 40（强趋势线）

**信号解读**：
- ADX > 25 且 +DI > -DI：上升趋势，多头力量占优
- ADX > 25 且 -DI > +DI：下降趋势，空头力量占优
- ADX < 20：无趋势市场，不适合趋势跟踪策略
- +DI 从下向上穿越 -DI：买入信号
- -DI 从上向下穿越 +DI：卖出信号

**配色方案**：
- ADX线：`#e040fb`（紫色），线宽2.0
- +DI线：`#ef5350`（红色），线宽1.5
- -DI线：`#26a69a`（绿色），线宽1.5

#### 2.2.7 KDJ（随机指标）

**功能**：超买超卖指标，基于统计学原理研判价格偏离程度。由K线（快线）、D线（慢线）、J线（方向敏感线）组成。

**参数**：
- N（RSV周期，默认：9）
- M1（K值平滑参数，默认：3）
- M2（D值平滑参数，默认：3）

**可视化**：
- 独立面板，显示三条线：K线、D线、J线
- 参考线：超买线（80）、超卖线（20）、中轴线（50）

**信号解读**：
- K、D < 20 且 K线从下向上穿越D线（金叉）：买入信号
- K、D > 80 且 K线从上向下穿越D线（死叉）：卖出信号
- J > 100：市场超买，价格可能回调
- J < 0：市场超卖，价格可能反弹
- 顶背离：价格创新高，但KDJ未创新高 → 卖出信号
- 底背离：价格创新低，但KDJ未创新低 → 买入信号

**配色方案**：
- K线：`#f5a623`（橙色），线宽1.5
- D线：`#388bfd`（蓝色），线宽1.5
- J线：`#e040fb`（紫色），线宽1.0，虚线

#### 2.2.8 VWAP（成交量加权平均价）

**功能**：衡量股票在一段时间内成交平均价格，作为动态支撑/阻力位。机构交易常用参考指标。

**参数**：
- 周期（可选，用于滚动VWAP）
- 会话重置（是/否）：选择"是"则每日重置VWAP计算

**可视化**：
- 叠加在K线主图上，显示VWAP曲线
- 可选：显示VWAP偏离带（±1%、±2%）

**信号解读**：
- 价格 > VWAP：市场看涨情绪较强，VWAP作为动态支撑位
- 价格 < VWAP：市场看跌情绪较强，VWAP作为动态阻力位
- 价格从下向上突破VWAP：买入信号
- 价格从上向下跌破VWAP：卖出信号
- VWAP偏离度 > +2%：价格偏高，可能回调
- VWAP偏离度 < -2%：价格偏低，可能反弹

**配色方案**：
- 会话VWAP：`#ff9800`（橙色），线宽2.0
- 滚动VWAP：`#00bcd4`（青色），线宽1.5，虚线

#### 2.2.9 可扩展设计
- 预留接口，方便后续添加更多指标（如OBV、SAR等）

### 2.3 描述性统计模块

#### 2.3.1 基本统计量
- 均值、中位数、标准差
- 最大值、最小值、四分位数
- 偏度、峰度

#### 2.3.2 涨跌统计
- 上涨天数、下跌天数、平盘天数
- 最大单日涨幅、最大单日跌幅
- 涨跌分布可视化（条形图）

#### 2.3.3 周期性回报
- 近5日、20日、60日收益率
- 年化收益率、波动率

#### 2.3.4 价格区间分析
- 当前价格在近一年的最高/最低位置
- 距最高价回撤百分比
- 距最低价涨幅百分比

### 2.4 图表交互模块

#### 2.4.1 K线主图
- **图表类型**：蜡烛图（Candlestick）
- **配色方案**：
  - 上涨：红色（中国股市惯例）
  - 下跌：绿色
- **交互功能**：
  - 鼠标悬停显示详细数据（开盘、最高、最低、收盘、涨跌、成交量）
  - 缩放、拖拽时间轴
  - 跨图表时间轴联动

#### 2.4.2 成交量图
- **位置**：K线图下方，共享X轴
- **可视化**：柱状图，颜色与K线一致
- **均线**：可选显示成交量均线

#### 2.4.3 指标图
- **布局**：每个指标独立面板，垂直堆叠
- **可配置**：用户可以选择显示/隐藏某个指标
- **时间轴联动**：所有图表共享时间轴，缩放/拖拽同步

#### 2.4.4 图表控制
- **时间范围选择**：快速按钮（1个月、3个月、6个月、1年、全部）
- **图表类型切换**：蜡烛图、折线图、面积图
- **主题切换**：深色主题（默认）、浅色主题

### 2.5 参数调节界面

#### 2.5.1 调节方式
- **输入框**：精确数值输入
- **滑块**：快速调节（适用于有一定范围的参数）
- **实时更新**：参数改变后，图表立即重绘

#### 2.5.2 参数面板设计
- **位置**：图表左侧或右侧，可折叠
- **分组**：按指标类型分组（均线、RSI、MACD、布林带、ATR）
- **重置按钮**：恢复默认参数

### 2.6 指标分析模块

#### 2.6.1 多指标共振分析

**原理**：当多个技术指标同时发出相同的信号时，信号的可信度大大提高。

**实现方案**：
1. **信号分类**：
   - 买入信号（Bullish）
   - 卖出信号（Bearish）
   - 中性信号（Neutral）

2. **指标信号定义**：

| 指标 | 买入信号 | 卖出信号 | 中性信号 |
|------|----------|----------|----------|
| MA | 多头排列（MA5>MA20>MA60）且价格在MA上方 | 空头排列（MA5<MA20<MA60）且价格在MA下方 | 均线交织 |
| RSI | RSI < 30（超卖）或 RSI从下方突破50 | RSI > 70（超买）或 RSI从上方跌破50 | 30 < RSI < 70 |
| MACD | DIF > DEA 且柱状图为正且扩张 | DIF < DEA 且柱状图为负且扩张 | 其他情况 |
| DMI/ADX | +DI > -DI 且 ADX > 25 | -DI > +DI 且 ADX > 25 | ADX < 20 |
| KDJ | K、D < 20 且 K线上穿D线（金叉） | K、D > 80 且 K线下穿D线（死叉） | 20 < K、D < 80 |
| VWAP | 价格从下方突破VWAP | 价格从上方跌破VWAP | 价格围绕VWAP震荡 |

3. **共振评分算法**：
```
共振得分 = Σ(指标权重 × 信号强度)

其中：
- 指标权重：可调整，默认相等
- 信号强度：
  - 强烈买入：+2
  - 温和买入：+1
  - 中性：0
  - 温和卖出：-1
  - 强烈卖出：-2
```

4. **共振结论**：
   - 得分 ≥ 4：强烈买入信号
   - 得分 = 2~3：温和买入信号
   - 得分 = -1~1：观望
   - 得分 = -3~-2：温和卖出信号
   - 得分 ≤ -4：强烈卖出信号

#### 2.6.2 背离分析

**原理**：当价格与技术指标走势不一致时，往往预示着趋势的反转。

**实现方案**：

1. **背离类型**：

**价格与RSI背离**：
- 顶背离：价格创新高，RSI未创新高 → 看跌
- 底背离：价格创新低，RSI未创新低 → 看涨

**价格与MACD背离**：
- 顶背离：价格创新高，MACD DIF未创新高 → 看跌
- 底背离：价格创新低，MACD DIF未创新低 → 看涨

**价格与KDJ背离**：
- 顶背离：价格创新高，KDJ未创新高 → 看跌
- 底背离：价格创新低，KDJ未创新低 → 看涨

2. **背离检测算法**：
   - 找出价格和指标的局部高点和低点
   - 检查价格创新高/低时，指标是否也创新高/低
   - 如不一致，则检测到背离

3. **背离可视化**：
   - 在价格和指标图上用连线标记背离
   - 用箭头或特殊符号标记背离点
   - 在分析面板列出检测到的背离

4. **背离确认规则**：
   - 单一背离：仅供参考
   - 多个指标同时背离：高可信度信号
   - 背离后价格突破确认：最强信号

#### 2.6.3 趋势强度评估

**原理**：综合多个指标评估当前趋势的强度，帮助投资者判断趋势的可持续性。

**实现方案**：

1. **趋势强度因子**：

| 因子 | 计算方法 | 权重 |
|------|----------|------|
| ADX值 | ADX > 25: 强趋势; ADX > 40: 很强 | 30% |
| 均线排列 | 多头/空头排列的完整度 | 20% |
| MACD柱状图 | 柱状图的大小和持续性 | 20% |
| 价格与VWAP偏离 | 偏离度和方向一致性 | 15% |
| 成交量确认 | 价格上涨伴随放量 | 15% |

2. **趋势强度评分**：
   - 很强（80-100分）：趋势非常明确，可持续
   - 强（60-79分）：趋势明确，可跟随
   - 中等（40-59分）：趋势存在但不强
   - 弱（20-39分）：趋势不明显
   - 很弱（0-19分）：无趋势，震荡市

3. **趋势方向判断**：
   - 结合ADX、+DI/-DI、均线排列、MACD方向综合判断
   - 输出：上升趋势、下降趋势、震荡

#### 2.6.4 综合分析报告

**功能**：生成综合性的技术分析报告

**报告内容**：
1. **市场状态**：趋势/震荡，强度
2. **多指标共振结论**：买入/卖出/观望
3. **检测到的背离**：列出所有背离
4. **关键支撑/阻力位**：基于VWAP、MA、布林带
5. **操作建议**：具体的买入/卖出/止损建议
6. **风险提示**：可能的反转信号、不确定性

---

## 3. 技术架构设计

### 3.1 整体架构

```
StockAnalyzer Pro (单HTML文件)
│
├─ 数据层 (Data Layer)
│  ├─ CSV文件解析器
│  ├─ 数据验证与清洗
│  └─ 数据存储器 (JavaScript Array/Object)
│
├─ 计算层 (Calculation Layer)
│  ├─ 技术指标计算引擎
│  │  ├─ MA计算
│  │  ├─ RSI计算
│  │  ├─ MACD计算
│  │  ├─ 布林带计算
│  │  ├─ ATR计算
│  │  ├─ DMI/ADX计算
│  │  ├─ KDJ计算
│  │  └─ VWAP计算
│  └─ 描述性统计计算
│  └─ 指标分析引擎
│
├─ 可视化层 (Visualization Layer)
│  ├─ Lightweight Charts (K线图、指标图)
│  ├─ 自定义Canvas/SVG (统计图表)
│  └─ DOM操作 (统计面板、参数控件)
│
└─ 控制层 (Control Layer)
   ├─ 参数调节事件监听
   ├─ 图表重绘调度
   └─ 数据加载处理
```

### 3.2 技术栈选择

#### 3.2.1 核心图表库
**推荐：Lightweight Charts (by TradingView)**
- **优势**：
  - 专为金融图表设计，性能优秀
  - 支持蜡烛图、折线图、柱状图
  - 内置时间轴联动、十字线、缩放拖拽
  - 文件体积小（约150KB gzipped）
  - 可离线使用（下载到本地）

- **备选**：Chart.js + 自定义插件
  - 更轻量，但需要更多自定义开发

#### 3.2.2 数据处理
- **纯JavaScript实现**：所有计算在浏览器端完成
- **性能优化**：
  - 使用TypedArray处理大量数据
  - 计算结果为缓存，参数变更时只重算受影响的部分

#### 3.2.3 UI组件
- **纯HTML/CSS/JavaScript**：不依赖大型UI框架
- **样式设计**：CSS Grid/Flexbox布局，深色主题
- **控件**：原生HTML input + 自定义样式

#### 3.2.4 文件结构
单个HTML文件，内部包含：
- `<style>`：所有CSS样式
- `<body>`：HTML结构
- `<script>`：所有JavaScript代码
  - 数据解析模块
  - 指标计算模块
  - 图表渲染模块
  - 事件处理模块

### 3.3 数据流设计

```
用户上传CSV / 选择示例数据
         ↓
   数据解析与验证
         ↓
   数据存储（原始数据）
         ↓
   指标计算（使用当前参数）
         ↓
   图表数据准备（格式化为Lightweight Charts所需格式）
         ↓
   图表渲染
         ↓
   用户调节参数
         ↓
   重新计算受影响的指标
         ↓
   局部图表更新（只重绘变化的图表）
```

### 3.4 性能指标

- **数据量**：支持最多5000条日线数据（约20年）
- **计算速度**：指标计算应在100ms内完成
- **渲染速度**：图表重绘应在50ms内完成
- **文件大小**：最终HTML文件应控制在500KB以内（包含示例代码）

---

## 4. 用户界面设计

### 4.1 整体布局

```
┌─────────────────────────────────────────────────────────┐
│  头部：工具名称 + 当前股票信息 + 数据区间              │
├─────────────────────────────────────────────────────────┤
│  数据选择栏：上传CSV | 选择示例数据 | 数据预览        │
├──────────────┬──────────────────────────────────────────┤
│              │  图表区域：                                │
│  参数调节   │  ┌──────────────────────────────────┐     │
│  面板       │  │ K线图 + 成交量                   │     │
│  (可折叠)  │  └──────────────────────────────────┘     │
│              │  ┌──────────────────────────────────┐     │
│  □ 均线     │  │ RSI图表                         │     │
│  □ RSI      │  └──────────────────────────────────┘     │
│  □ MACD     │  ┌──────────────────────────────────┐     │
│  □ 布林带   │  │ MACD图表                        │     │
│  □ ATR      │  └──────────────────────────────────┘     │
│              │  ┌──────────────────────────────────┐     │
│  参数输入   │  │ 布林带图表（如启用）            │     │
│  框/滑块   │  └──────────────────────────────────┘     │
│              │  ┌──────────────────────────────────┐     │
│              │  │ ATR图表（如启用）               │     │
│              │  └──────────────────────────────────┘     │
├──────────────┴──────────────────────────────────────────┤
│  统计信息面板：描述性统计 + 涨跌统计 + 周期性回报    │
├─────────────────────────────────────────────────────────┤
│  分析结论：技术指标分析 + 综合操作建议                │
└─────────────────────────────────────────────────────────┘
```

### 4.2 参数调节面板详细设计

#### 4.2.1 均线参数
```
┌─────────────────────┐
│ 均线 (MA)          │
│ □ 显示均线         │
│ ┌───────────────┐ │
│ │ MA1: [5    ]  │ │
│ │ MA2: [20   ]  │ │
│ │ MA3: [60   ]  │ │
│ │ [+添加] [-删除] │ │
│ └───────────────┘ │
└─────────────────────┘
```

#### 4.2.2 RSI参数
```
┌─────────────────────┐
│ RSI                │
│ □ 显示RSI          │
│ 周期: [14   ]     │
│ 超买线: [70   ]   │
│ 超卖线: [30   ]   │
└─────────────────────┘
```

#### 4.2.3 MACD参数
```
┌─────────────────────┐
│ MACD               │
│ □ 显示MACD         │
│ 快线周期: [12  ]  │
│ 慢线周期: [26  ]  │
│ 信号线周期: [9  ] │
└─────────────────────┘
```

#### 4.2.4 布林带参数
```
┌─────────────────────┐
│ 布林带             │
│ □ 显示布林带       │
│ 周期: [20      ]  │
│ 标准差倍数: [2.0] │
│ □ 填充区域         │
└─────────────────────┘
```

#### 4.2.5 ATR参数
```
┌─────────────────────┐
│ ATR                │
│ □ 显示ATR          │
│ 周期: [14      ]  │
│ □ 显示止损建议     │
└─────────────────────┘
```

#### 4.2.6 DMI/ADX参数
```
┌─────────────────────┐
│ DMI/ADX           │
│ □ 显示DMI/ADX     │
│ 周期: [14      ]  │
│ □ 显示+DI/-DI    │
└─────────────────────┘
```

#### 4.2.7 KDJ参数
```
┌─────────────────────┐
│ KDJ               │
│ □ 显示KDJ         │
│ RSV周期: [9    ]  │
│ K值平滑: [3     ]  │
│ D值平滑: [3     ]  │
└─────────────────────┘
```

#### 4.2.8 VWAP参数
```
┌─────────────────────┐
│ VWAP              │
│ □ 显示VWAP        │
│ □ 会话重置        │
│ 周期: [20      ]  │
└─────────────────────┘
```

### 4.3 配色方案

#### 4.3.1 深色主题（默认）
- **背景色**：
  - 主背景：`#0d1117`
  - 卡片背景：`#161b22`
  - 边框：`#30363d`
- **文字色**：
  - 主文字：`#e0e0e0`
  - 次要文字：`#8b949e`
  - 标题：`#f0f6fc`
- **图表色**：
  - 上涨（阳线）：`#ef5350`（红色）
  - 下跌（阴线）：`#26a69a`（绿色）
  - 均线1（MA5）：`#f5a623`（橙色）
  - 均线2（MA20）：`#388bfd`（蓝色）
  - 均线3（MA60）：`#a371f7`（紫色）
  - RSI线：`#f5a623`
  - MACD DIF线：`#f5a623`
  - MACD DEA线：`#388bfd`
  - 布林带上轨：`#ff9800`
  - 布林带下轨：`#4caf50`
  - ATR线：`#e040fb`

#### 4.3.2 浅色主题（可选）
- 背景色：`#ffffff`, `#f5f5f5`
- 文字色：`#333333`, `#666666`
- 图表色：调整对比度，适应浅色背景

---

## 5. 数据结构设计

### 5.1 原始数据存储
```javascript
let stockData = {
    ts_code: "300750.SZ",
    name: "宁德时代",
    data: [
        {
            trade_date: "2024-07-03",
            open: 177.0,
            high: 182.5,
            low: 176.31,
            close: 179.5,
            vol: 162053.21,
            amount: 2906473.774,
            // ... 其他字段
        },
        // ... 更多记录
    ]
};
```

### 5.2 计算后的指标数据
```javascript
let indicatorData = {
    ma: {
        ma5: [...],   // 数组，与原始数据等长，null表示无效值
        ma20: [...],
        ma60: [...]
    },
    rsi: {
        rsi14: [...]  // 数组
    },
    macd: {
        dif: [...],
        dea: [...],
        histogram: [...]
    },
    bollinger: {
        upper: [...],
        middle: [...],
        lower: [...]
    },
    atr: {
        atr14: [...]
    },
    dmi: {
        adx: [...],
        pos_di: [...],
        neg_di: [...]
    },
    kdj: {
        k: [...],
        d: [...],
        j: [...]
    },
    vwap: {
        vwap: [...]
    }
};
```

### 5.3 参数配置
```javascript
let config = {
    ma: {
        enabled: true,
        periods: [5, 20, 60]
    },
    rsi: {
        enabled: true,
        period: 14,
        overbought: 70,
        oversold: 30
    },
    macd: {
        enabled: true,
        fast: 12,
        slow: 26,
        signal: 9
    },
    bollinger: {
        enabled: true,
        period: 20,
        stdDev: 2.0,
        fillArea: false
    },
    atr: {
        enabled: true,
        period: 14
    },
    dmi: {
        enabled: true,
        period: 14,
        show_di: true
    },
    kdj: {
        enabled: true,
        n: 9,
        m1: 3,
        m2: 3
    },
    vwap: {
        enabled: true,
        session_reset: true,
        period: 20
    }
};
```

---

## 6. 实施路线图

### 阶段1：基础框架搭建（1-2天）
- [ ] 创建HTML文件基本结构
- [ ] 实现CSV文件上传和解析
- [ ] 集成Lightweight Charts库
- [ ] 实现基本的K线图+成交量图展示
- [ ] 实现示例数据加载

### 阶段2：技术指标计算（2-3天）
- [ ] 实现MA计算
- [ ] 实现RSI计算
- [ ] 实现MACD计算
- [ ] 实现布林带计算
- [ ] 实现ATR计算

### 阶段3：参数调节界面（1-2天）
- [ ] 设计参数调节面板UI
- [ ] 实现参数输入控件（输入框、滑块）
- [ ] 实现参数变化事件监听
- [ ] 实现图表实时重绘

### 阶段4：描述性统计（1天）
- [ ] 实现基本统计量计算
- [ ] 实现涨跌统计
- [ ] 实现周期性回报计算
- [ ] 设计统计信息面板UI

### 阶段5：分析结论（1天）
- [ ] 实现技术指标信号识别
- [ ] 实现综合评分算法
- [ ] 实现操作建议生成
- [ ] 设计分析结论卡片UI

### 阶段6：优化与测试（1-2天）
- [ ] 性能优化（大数据量测试）
- [ ] 浏览器兼容性测试
- [ ] 移动端适配（可选）
- [ ] 文档编写（使用说明）

---

## 7. 关键技术与实现细节

### 7.1 CSV文件解析
```javascript
function parseCSV(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const text = e.target.result;
            const lines = text.split('\n');
            const headers = lines[0].split(',');
            const data = [];
            
            for (let i = 1; i < lines.length; i++) {
                if (lines[i].trim() === '') continue;
                const values = lines[i].split(',');
                const row = {};
                headers.forEach((header, index) => {
                    row[header.trim()] = values[index].trim();
                });
                data.push(row);
            }
            
            resolve(data);
        };
        reader.readAsText(file);
    });
}
```

### 7.2 技术指标计算核心代码

#### 7.2.1 MA计算
```javascript
function calculateMA(data, period) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            result.push(null);
        } else {
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += parseFloat(data[i - j].close);
            }
            result.push(sum / period);
        }
    }
    return result;
}
```

#### 7.2.2 RSI计算
```javascript
function calculateRSI(data, period) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
        if (i < period) {
            result.push(null);
        } else {
            let gains = 0, losses = 0;
            for (let j = 0; j < period; j++) {
                const change = parseFloat(data[i - j].close) - parseFloat(data[i - j - 1].close);
                if (change > 0) gains += change;
                else losses += Math.abs(change);
            }
            const avgGain = gains / period;
            const avgLoss = losses / period;
            const rs = avgGain / avgLoss;
            const rsi = 100 - (100 / (1 + rs));
            result.push(rsi);
        }
    }
    return result;
}
```

#### 7.2.3 布林带计算
```javascript
function calculateBollingerBands(data, period, stdDev) {
    const middle = calculateMA(data, period);
    const upper = [];
    const lower = [];
    
    for (let i = 0; i < data.length; i++) {
        if (i < period - 1) {
            upper.push(null);
            lower.push(null);
        } else {
            // 计算标准差
            let sum = 0;
            for (let j = 0; j < period; j++) {
                sum += Math.pow(parseFloat(data[i - j].close) - middle[i], 2);
            }
            const stdDevValue = Math.sqrt(sum / period);
            
            upper.push(middle[i] + stdDevValue * stdDev);
            lower.push(middle[i] - stdDevValue * stdDev);
        }
    }
    
    return { upper, middle, lower };
}
```

#### 7.2.4 DMI/ADX计算
```javascript
function calculateDMIADX(data, period) {
    const tr = [];
    const posDM = [];
    const negDM = [];
    const posDI = [];
    const negDI = [];
    const dx = [];
    const adx = [];
    
    // 1. 计算TR
    for (let i = 0; i < data.length; i++) {
        if (i === 0) {
            tr.push(parseFloat(data[i].high) - parseFloat(data[i].low));
        } else {
            const hl = parseFloat(data[i].high) - parseFloat(data[i].low);
            const hc = Math.abs(parseFloat(data[i].high) - parseFloat(data[i-1].close));
            const lc = Math.abs(parseFloat(data[i].low) - parseFloat(data[i-1].close));
            tr.push(Math.max(hl, hc, lc));
        }
    }
    
    // 2. 计算+DM和-DM
    for (let i = 0; i < data.length; i++) {
        if (i === 0) {
            posDM.push(0);
            negDM.push(0);
        } else {
            const upMove = parseFloat(data[i].high) - parseFloat(data[i-1].high);
            const downMove = parseFloat(data[i-1].low) - parseFloat(data[i].low);
            
            posDM.push((upMove > downMove && upMove > 0) ? upMove : 0);
            negDM.push((downMove > upMove && downMove > 0) ? downMove : 0);
        }
    }
    
    // 3. Wilder平滑
    const trSmooth = wilderSmooth(tr, period);
    const posDMSmooth = wilderSmooth(posDM, period);
    const negDMSmooth = wilderSmooth(negDM, period);
    
    // 4. 计算+DI和-DI
    for (let i = period; i < data.length; i++) {
        posDI.push(100 * posDMSmooth[i] / trSmooth[i]);
        negDI.push(100 * negDMSmooth[i] / trSmooth[i]);
    }
    
    // 5. 计算DX
    for (let i = period; i < data.length; i++) {
        dx.push(100 * Math.abs(posDI[i] - negDI[i]) / (posDI[i] + negDI[i]));
    }
    
    // 6. 计算ADX
    const adxValues = wilderSmooth(dx, period);
    
    return { adx: adxValues, posDI: posDI, negDI: negDI };
}

function wilderSmooth(data, period) {
    const result = [];
    let sum = 0;
    
    for (let i = 0; i < data.length; i++) {
        if (i < period) {
            sum += data[i];
            result.push(null);
        } else {
            sum = sum - (sum / period) + data[i];
            result.push(sum / period);
        }
    }
    
    return result;
}
```

#### 7.2.5 KDJ计算
```javascript
function calculateKDJ(data, n, m1, m2) {
    const rsv = [];
    const k = [];
    const d = [];
    const j = [];
    
    // 1. 计算RSV
    for (let i = 0; i < data.length; i++) {
        if (i < n - 1) {
            rsv.push(null);
        } else {
            let lowest = parseFloat(data[i].low);
            let highest = parseFloat(data[i].high);
            
            for (let j = 0; j < n; j++) {
                lowest = Math.min(lowest, parseFloat(data[i - j].low));
                highest = Math.max(highest, parseFloat(data[i - j].high));
            }
            
            rsv.push(100 * (parseFloat(data[i].close) - lowest) / (highest - lowest));
        }
    }
    
    // 2. 计算K值
    for (let i = 0; i < data.length; i++) {
        if (i < n + m1 - 2) {
            k.push(null);
        } else if (i === n + m1 - 2) {
            k.push(50);  // 初始值
        } else {
            k.push((2/3) * k[i-1] + (1/3) * rsv[i]);
        }
    }
    
    // 3. 计算D值
    for (let i = 0; i < data.length; i++) {
        if (i < n + m1 + m2 - 3) {
            d.push(null);
        } else if (i === n + m1 + m2 - 3) {
            d.push(50);  // 初始值
        } else {
            d.push((2/3) * d[i-1] + (1/3) * k[i]);
        }
    }
    
    // 4. 计算J值
    for (let i = 0; i < data.length; i++) {
        if (d[i] === null) {
            j.push(null);
        } else {
            j.push(3 * k[i] - 2 * d[i]);
        }
    }
    
    return { k, d, j };
}
```

#### 7.2.6 VWAP计算
```javascript
function calculateVWAP(data, sessionReset) {
    const vwap = [];
    const typicalPrice = [];
    const priceVolProduct = [];
    const volSum = [];
    
    // 1. 计算典型价格
    for (let i = 0; i < data.length; i++) {
        typicalPrice.push((parseFloat(data[i].high) + parseFloat(data[i].low) + parseFloat(data[i].close)) / 3);
    }
    
    // 2. 计算价格和成交量的乘积
    for (let i = 0; i < data.length; i++) {
        priceVolProduct.push(typicalPrice[i] * parseFloat(data[i].vol));
    }
    
    // 3. 计算VWAP
    if (sessionReset) {
        // 会话VWAP：每日重置
        let currentDate = null;
        let sessionStart = 0;
        
        for (let i = 0; i < data.length; i++) {
            const date = data[i].trade_date.split(' ')[0];  // 假设日期格式包含时间
            
            if (date !== currentDate) {
                // 新的一天，重置
                currentDate = date;
                sessionStart = i;
            }
            
            // 计算从会话开始到当前的VWAP
            let sumProduct = 0;
            let sumVol = 0;
            for (let j = sessionStart; j <= i; j++) {
                sumProduct += priceVolProduct[j];
                sumVol += parseFloat(data[j].vol);
            }
            
            vwap.push(sumProduct / sumVol);
        }
    } else {
        // 滚动VWAP
        for (let i = 0; i < data.length; i++) {
            if (i === 0) {
                vwap.push(priceVolProduct[i] / parseFloat(data[i].vol));
            } else {
                let sumProduct = 0;
                let sumVol = 0;
                for (let j = 0; j <= i; j++) {
                    sumProduct += priceVolProduct[j];
                    sumVol += parseFloat(data[j].vol);
                }
                vwap.push(sumProduct / sumVol);
            }
        }
    }
    
    return vwap;
}
```

### 7.3 图表渲染核心代码

#### 7.3.1 初始化K线图
```javascript
function initChart() {
    const chart = LightweightCharts.createChart(document.getElementById('chart'), {
        width: document.getElementById('chart').clientWidth,
        height: 500,
        layout: {
            backgroundColor: '#0d1117',
            textColor: '#8b949e',
        },
        grid: {
            vertLines: { color: '#21262d' },
            horzLines: { color: '#21262d' },
        },
    });
    
    const candlestick = chart.addCandlestickSeries({
        upColor: '#ef5350',
        downColor: '#26a69a',
        borderUpColor: '#ef5350',
        borderDownColor: '#26a69a',
        wickUpColor: '#ef5350',
        wickDownColor: '#26a69a',
    });
    
    candlestick.setData(candleData);
    
    return { chart, candlestick };
}
```

#### 7.3.2 参数变化后重绘
```javascript
function onParameterChange() {
    // 1. 读取新参数
    const newPeriod = document.getElementById('rsi-period').value;
    
    // 2. 重新计算指标
    indicatorData.rsi.rsi14 = calculateRSI(stockData.data, newPeriod);
    
    // 3. 更新图表数据
    rsiSeries.setData(formatDataForChart(indicatorData.rsi.rsi14));
    
    // 4. 可选：只更新变化的图表，提高性能
}
```

---

## 8. 用户体验设计

### 8.1 加载提示
- 数据上传后显示"正在解析数据..."进度提示
- 指标计算时显示"正在计算指标..."提示
- 使用loading spinner或进度条

### 8.2 错误处理
- CSV文件格式错误：提示"文件格式不正确，请检查CSV文件"
- 数据缺失：提示"数据缺失，部分指标可能无法计算"
- 计算过程错误：提示"计算出错，请检查参数设置"

### 8.3 操作反馈
- 参数调节后，图表立即更新，无需点击"应用"按钮
- 鼠标悬停在K线上，显示详细数据tooltip
- 时间轴缩放/拖拽时，所有图表联动

### 8.4 响应式设计
- 图表宽度自适应浏览器窗口大小
- 参数面板在小屏幕上自动折叠
- 移动端：简化界面，隐藏部分高级功能

---

## 9. 后续扩展方向

### 9.1 功能扩展
- 支持更多技术指标（OBV、SAR等）
- 支持多股票对比（同一图表显示多只股票）
- 支持分时图、周线、月线
- 支持数据导出（PNG、PDF）

### 9.2 性能扩展
- Web Worker多线程计算，避免界面卡顿
- 数据分片加载，支持更大量级的数据

### 9.3 社交扩展
- 分享分析结果（生成图片或链接）
- 保存分析配置（参数预设）

---

## 10. 交付物清单

### 10.1 设计阶段交付物
- [x] 产品设计文档（本文档）
- [ ] 界面设计原型（HTML静态页面）

### 10.2 开发阶段交付物
- [ ] StockAnalyzer_Pro.html（最终产品）
- [ ] 使用说明文档
- [ ] 示例数据文件（5只股票CSV）

---

## 附录A：参考资料

### A.1 技术指标公式
- **MA**：MA(n) = (P1 + P2 + ... + Pn) / n
- **RSI**：RSI = 100 - 100 / (1 + RS), RS = AvgGain / AvgLoss
- **MACD**：DIF = EMA(fast) - EMA(slow), DEA = EMA(DIF, signal), Hist = DIF - DEA
- **布林带**：Middle = MA(n), Upper = Middle + k*σ, Lower = Middle - k*σ
- **ATR**：ATR = SMA(TR, n), TR = max(H-L, |H-PrevC|, |L-PrevC|)

### A.2 相关库文档
- Lightweight Charts：https://tradingview.github.io/lightweight-charts/
- TradingView技术指标说明：https://www.tradingview.com/wiki/Technical_Indicators

### A.3 设计灵感来源
- TradingView官网
- 同花顺、东方财富等股票软件界面
- 现有项目中的smic_dashboard.html

---

**文档版本**：v1.1  
**创建日期**：2026-07-04  
**更新日期**：2026-07-04  
**作者**：WorkBuddy AI Assistant
