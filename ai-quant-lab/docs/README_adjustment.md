# 股票数据诊断与复权处理 — 使用说明

## 问题描述

Tushare的`adj_factor`（复权因子）接口有严格的频率限制：**1次/小时**。这意味着我们无法在一次运行中获取所有5只股票的复权因子。

## 解决方案

我们提供了3个脚本来分步完成数据处理：

### 脚本1：`diagnose_and_adjust_stocks.py`
**功能**：诊断分析股票数据（检查缺失值、描述性统计量、价格合理性）

**运行方式**：
```bash
python3 diagnose_and_adjust_stocks.py
```

**输出**：
- 控制台会显示每只股票的诊断报告
- 诊断内容包括：记录数、字段列表、缺失值检查、描述性统计量、复权检查、价格合理性检查

### 脚本2：`fetch_adj_factors.py`
**功能**：分步获取复权因子（每次运行获取1只股票）

**运行方式**：
```bash
python3 fetch_adj_factors.py
```

**重要提示**：
- ⚠️ 每次运行只能获取1只股票的复权因子
- ⚠️ 需要等待**1小时**后才能再次运行（避免API频率限制）
- ✅ 脚本会自动检查哪些股票已获取，只获取未获取的

**工作流程**：
1. 第一次运行：获取第1只股票的复权因子
2. 等待1小时
3. 第二次运行：获取第2只股票的复权因子
4. 重复直到所有5只股票都获取完成

**输出**：
- 复权因子保存在：`data/adj_factors/` 目录
- 文件命名：`{股票名称}_{代码}_adj_factor.csv`

### 脚本3：`apply_adjustment.py`
**功能**：使用已保存的复权因子对数据进行复权处理

**运行方式**：
```bash
python3 apply_adjustment.py
```

**前提条件**：
- 需要先运行 `fetch_adj_factors.py` 获取至少1只股票的复权因子

**输出**：
- 复权后的数据保存在：`data/adjusted/` 目录
- 文件命名：`{股票名称}_{代码}_daily_adjusted.csv`

## 完整工作流程

### 第一步：诊断分析（已完成 ✅）
```bash
python3 diagnose_and_adjust_stocks.py
```
- 这个步骤不需要调用`adj_factor` API，所以不会遇到频率限制
- 已经完成，可以看到所有5只股票的诊断报告

### 第二步：获取复权因子（需要5小时 ⏳）
需要分5次运行 `fetch_adj_factors.py`，每次间隔1小时：

```bash
# 第1次运行（例如：上午10:00）
python3 fetch_adj_factors.py
# 输出：成功获取第1只股票的复权因子

# 等待1小时...

# 第2次运行（例如：上午11:00）
python3 fetch_adj_factors.py
# 输出：成功获取第2只股票的复权因子

# 等待1小时...

# 第3次运行（例如：下午12:00）
python3 fetch_adj_factors.py
# 输出：成功获取第3只股票的复权因子

# 等待1小时...

# 第4次运行（例如：下午13:00）
python3 fetch_adj_factors.py
# 输出：成功获取第4只股票的复权因子

# 等待1小时...

# 第5次运行（例如：下午14:00）
python3 fetch_adj_factors.py
# 输出：成功获取第5只股票的复权因子
```

### 第三步：应用复权处理
当所有复权因子都获取完成后：
```bash
python3 apply_adjustment.py
```
- 这个脚本会自动找到所有已获取复权因子的股票
- 对这些股票进行前复权处理
- 保存复权后的数据到 `data/adjusted/` 目录

## 当前状态

✅ **诊断分析已完成**
- 5只股票的数据质量检查完成
- 无缺失值
- 价格关系合理
- 数据未复权（需要复权处理）

⏳ **复权因子获取**
- 当前状态：0/5 只股票已获取
- 需要运行 `fetch_adj_factors.py` 5次（每次间隔1小时）

## 建议

### 方案A：分步获取（免费方案）
按照上述工作流程，分5次运行 `fetch_adj_factors.py`，每次间隔1小时。

**优点**：不需要付费
**缺点**：需要5小时才能完成所有数据的获取

### 方案B：升级Tushare账号（推荐 ⭐）
访问 https://tushare.pro/register 注册/登录，查看付费方案。

付费账号通常有更高的API调用频率限制，可以在一次运行中获取所有数据。

### 方案C：使用未复权数据（临时方案）
如果复权不是必须的，可以直接使用 `data/` 目录下的原始数据。

**注意**：未复权数据在股票发生除权除息（分红、送股等）时，价格会不连续，可能影响技术分析的准确性。

## 文件清单

### 原始数据（已生成 ✅）
- `data/ningde_times_300750_daily.csv`
- `data/ping_an_601318_daily.csv`
- `data/moutai_600519_daily.csv`
- `data/petro_china_601857_daily.csv`
- `data/byd_002594_daily.csv`

### 复权因子（待获取 ⏳）
保存位置：`data/adj_factors/`
- `data/adj_factors/ningde_times_300750_adj_factor.csv` （待获取）
- `data/adj_factors/ping_an_601318_adj_factor.csv` （待获取）
- `data/adj_factors/moutai_600519_adj_factor.csv` （待获取）
- `data/adj_factors/petro_china_601857_adj_factor.csv` （待获取）
- `data/adj_factors/byd_002594_adj_factor.csv` （待获取）

### 复权后数据（待生成 ⏳）
保存位置：`data/adjusted/`
- 在这些文件生成之前，需要先获取复权因子并应用复权处理

## 常见问题

### Q1: 为什么不能直接获取所有股票的复权因子？
A: 因为Tushare的`adj_factor`接口有严格的频率限制（1次/小时）。这是Tushare对免费账号的限制。

### Q2: 复权处理重要吗？
A: 对于长期持有的股票，如果期间发生了除权除息（分红、送股等），未复权的数据会出现价格跳变，影响技术分析和回测的准确性。如果是短期数据分析，影响可能较小。

### Q3: 如何检查我的数据是否需要复权？
A: 可以对比股票的实际价格走势图。如果数据中出现了明显的价格跳变（例如从100元突然变成50元），说明需要复权处理。

### Q4: 我可以跳过复权处理吗？
A: 可以。如果您的分析不依赖于连续的价格序列（例如只分析最近几天的数据），可以直接使用未复权的数据。

## 联系信息

如有问题，请查看：
- Tushare官方文档：https://tushare.pro/document/1?doc_id=108
- Tushare频次限制说明：https://tushare.pro/document/1?doc_id=108

---

**最后更新**：2026-07-04
