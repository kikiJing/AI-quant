# 🔧 清除浏览器缓存指南

## 问题描述
测试页面(test_csv_parse.html)可以成功加载CSV，但主页面(index.html)仍然报错。

## 原因
浏览器缓存了旧版本的index.html，导致代码没有更新。

---

## 解决方案：清除浏览器缓存

### 方法1: 强制刷新（推荐）
在index.html页面，按以下快捷键：
- **Mac**: `Cmd + Shift + R` 或 `Cmd + F5`
- **Windows**: `Ctrl + F5` 或 `Ctrl + Shift + R`

这会强制浏览器重新加载所有资源，不使用缓存。

---

### 方法2: 开发者工具禁用缓存
1. 在index.html页面按 `F12` 打开开发者工具
2. 切换到 **Network（网络）** 标签
3. 勾选 **Disable cache（禁用缓存）** 选项
4. 刷新页面（`Cmd + R` 或 `F5`）

---

### 方法3: 手动清除缓存
#### Chrome / Edge / Brave
1. 按 `Cmd + Shift + Delete`（Mac）或 `Ctrl + Shift + Delete`（Windows）
2. 选择时间范围：**全部时间**
3. 勾选 **缓存的图片和文件**
4. 点击 **清除数据**

#### Firefox
1. 按 `Cmd + Shift + Delete`（Mac）或 `Ctrl + Shift + Delete`（Windows）
2. 选择时间范围：**全部**
3. 勾选 **缓存**
4. 点击 **确定**

#### Safari（Mac）
1. 打开 **开发** 菜单（如果没有，先在 偏好设置 > 高级 中启用）
2. 点击 **清空缓存**
3. 或者按 `Cmd + Option + E`

---

## 验证是否成功

清除缓存后，访问主页面：
```
http://localhost:8000/index.html
```

在页面上：
1. 按 `F12` 打开开发者工具
2. 切换到 **Console（控制台）** 标签
3. 选择股票并点击"🔄 加载数据"
4. 查看控制台输出

**预期输出**（类似）：
```
正在加载: data/ningde_times_300750_daily.csv
CSV数据长度: 12345
CSV行数: 489
CSV表头: ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', ...]
使用日期列: trade_date
使用成交量列: vol
解析完成: 成功488条，跳过0条
```

如果没有错误，图表应该会正常显示。

---

## 如果仍然报错

### 1. 检查服务器是否运行
在终端运行：
```bash
cd /Users/kikijing/Desktop/AI\ quant/ai-quant-lab
python3 run.py
```

应该看到：
```
HTTP服务器启动在端口 8000
访问 http://localhost:8000/index.html
按 Ctrl+C 停止服务器
```

### 2. 直接访问测试URL
在浏览器访问：
```
http://localhost:8000/index.html?v=2.0
```
添加 `?v=2.0` 可以强制浏览器重新加载。

### 3. 查看具体错误信息
在控制台（F12）中，红色错误会告诉我们具体问题。请截图或复制错误信息发给我。

---

## 快速测试步骤

1. ✅ 启动服务器：`python3 run.py`
2. ✅ 清除浏览器缓存：`Cmd + Shift + R`
3. ✅ 访问主页面：`http://localhost:8000/index.html`
4. ✅ 打开控制台：`F12`
5. ✅ 选择股票 → 点击"🔄 加载数据"
6. ✅ 查看控制台输出

如果按照以上步骤操作仍然报错，请把**控制台截图**发给我，我会帮您进一步诊断。

---

## 提示
- 每次我修改index.html后，您都需要清除缓存才能看到更新
- 开发阶段，建议保持开发者工具打开，并勾选"Disable cache"
- 如果嫌麻烦，可以使用隐私/无痕模式打开页面（缓存独立）

---

**修改日期**: 2026-07-04
**版本**: v2.0（已移除alert对话框，改进错误处理）