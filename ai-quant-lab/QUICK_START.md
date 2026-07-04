# 快速启动指南

## 🎯 最终的网页在这里！

### 方法1：自动启动（最简单）

**双击运行**：
```
/Users/kikijing/Desktop/AI quant/ai-quant-lab/start.sh
```

或者右键点击 `start.sh` → "打开方式" → "终端"

---

### 方法2：手动启动

#### 步骤1：打开终端
- 按 `Cmd + 空格`
- 输入 `Terminal`
- 回车

#### 步骤2：进入目录
```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
```

#### 步骤3：启动服务器
```bash
python3 run.py
```

或者直接：
```bash
python3 -m http.server 8000
```

#### 步骤4：访问网页
在浏览器中访问：
```
http://localhost:8000/index.html
```

---

## 🌐 网页地址

**主界面**：
```
http://localhost:8000/index.html
```

**测试页面**（如果主界面失败）：
```
http://localhost:8000/test_csv_parse.html
```

**启动指南**（这个HTML文件）：
```
http://localhost:8000/start_here.html
```

---

## 📂 文件位置

**最终的网页文件**：
```
/Users/kikijing/Desktop/AI quant/ai-quant-lab/index.html
```

**数据文件**：
```
/Users/kikijing/Desktop/AI quant/ai-quant-lab/data/*.csv
```

---

## ⚠️ 为什么加载数据失败？

### 原因1：没有启动本地服务器

**错误做法**：直接双击打开 `index.html`
- 浏览器地址栏显示：`file:///Users/kikijing/Desktop/AI quant/ai-quant-lab/index.html`
- 结果：❌ 无法加载CSV数据（浏览器安全限制）

**正确做法**：通过HTTP服务器访问
- 浏览器地址栏显示：`http://localhost:8000/index.html`
- 结果：✅ 可以加载CSV数据

### 原因2：服务器未运行

如果终端关闭了，服务器就停止了，需要重新启动。

### 原因3：端口被占用

如果8000端口被占用，需要换一个端口：
```bash
python3 -m http.server 8080
```

然后访问：`http://localhost:8080/index.html`

---

## 🔍 如何验证服务器是否运行？

### 方法1：查看终端输出

终端应该显示：
```
Serving HTTP on 0.0.0.0 port 8000 ...
```

### 方法2：访问测试页面

在浏览器中访问：
```
http://localhost:8000/start_here.html
```

如果能看到启动指南页面，说明服务器运行正常。

---

## 🚀 现在就启动！

### 最简单的方式：

1. 打开终端
2. 复制粘贴以下命令：
```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab" && python3 run.py
```
3. 回车
4. 等待浏览器自动打开

---

## 📸 成功标志

### 浏览器地址栏显示：
```
http://localhost:8000/index.html
```

### 页面显示：
- ✅ K线图（红色/绿色蜡烛图）
- ✅ 成交量图
- ✅ RSI指标图
- ✅ MACD指标图
- ✅ 描述性统计面板

### 浏览器控制台（F12）显示：
```
CSV表头: ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount
✅ 所有必需的列都存在
数据加载成功！
```

---

## 🆘 如果还是失败

### 1. 截图错误信息
按F12打开控制台，截图红色错误信息

### 2. 检查CSV文件
在终端运行：
```bash
head -2 "/Users/kikijing/Desktop/AI quant/ai-quant-lab/data/ningde_times_300750_daily.csv"
```

### 3. 重新启动服务器
```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
python3 run.py
```

---

## 💡 提示

### 每次使用都需要启动服务器

**不要关闭终端窗口**，保持服务器运行。

如果关闭了，需要重新启动。

### 创建桌面快捷方式（可选）

1. 在桌面创建 `start.sh` 的快捷方式
2. 下次双击即可启动

---

**现在请启动服务器，然后访问 http://localhost:8000/index.html！** 🚀
