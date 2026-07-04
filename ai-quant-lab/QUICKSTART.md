# 🎯 如何正确使用 AI Quant Lab

## ⚠️ 重要：不要直接双击打开HTML文件！

由于浏览器的安全限制，直接双击打开HTML文件会导致**无法加载CSV数据**。

您必须通过**本地HTTP服务器**访问。

---

## ✅ 正确启动方式（3种方法任选其一）

### 🚀 方法1：使用 run.py（最简单，推荐）

**步骤：**
1. 打开终端
2. 输入以下命令：

```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
python3 run.py
```

**效果：**
- 终端显示启动信息
- 浏览器自动打开 `http://localhost:8000/index.html`
- 可以看到K线图和指标图

**按 `Ctrl+C` 停止服务器**

---

### 🐧 方法2：使用 start.sh（macOS/Linux）

```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
./start.sh
```

---

### 🌐 方法3：手动启动服务器

```bash
# 步骤1：进入项目目录
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"

# 步骤2：启动服务器
python3 -m http.server 8000

# 步骤3：打开浏览器，访问
http://localhost:8000/index.html
```

---

## 🔍 如何判断是否正确启动？

### ✅ 正确的状态

**浏览器地址栏显示：**
```
http://localhost:8000/index.html
```

**浏览器控制台（F12）显示：**
```
正在加载: data/ningde_times_300750_daily.csv
CSV数据长度: 43156
数据加载成功！
```

**页面显示：**
- K线图（红色和绿色的蜡烛图）
- 成交量柱状图
- RSI指标图
- MACD指标图

### ❌ 错误的状态

**浏览器地址栏显示：**
```
file:///Users/kikijing/Desktop/AI quant/ai-quant-lab/index.html
```

→ 这是直接双击打开的，**无法加载数据**！

**解决方法：**
关闭浏览器，回到终端，运行 `python3 run.py`

---

## 📊 启动成功后的界面

### 左侧面板
- **数据选择**：下拉框选择股票
- **技术指标**：勾选框和参数输入

### 主图表区
- **K线图**：显示价格走势
- **成交量**：K线图下方的柱状图
- **RSI图**：相对强弱指标
- **MACD图**：移动平均收敛发散

### 统计面板
- 最新收盘价
- 涨跌幅
- 平均价、最高/最低价
- 平均成交量

---

## 🎮 交互操作

### 图表操作
- **鼠标滚轮**：缩放
- **鼠标拖拽**：平移
- **鼠标悬停**：显示十字光标和数值

### 参数调节
1. 在左侧面板修改参数
2. 点击 **"🔄 更新图表"**
3. 图表立即重绘

### 示例：修改RSI周期
1. 左侧找到"RSI"
2. 修改"周期"为 `7`
3. 点击"更新图表"
4. 观察RSI图变化（更敏感）

---

## ⚠️ 常见问题

### Q: 还是显示"加载数据失败"？
**A:** 
1. 确保浏览器地址以 `http://` 开头（不是 `file://`）
2. 查看浏览器控制台（F12）的详细错误
3. 访问 `http://localhost:8000/test.html` 进行诊断

### Q: 端口8000被占用？
**A:** 
修改 `run.py` 文件，将 `PORT = 8000` 改为 `PORT = 8001`，然后重新启动

### Q: 浏览器没有自动打开？
**A:** 
手动在浏览器中输入：`http://localhost:8000/index.html`

### Q: 终端显示"Address already in use"？
**A:** 
说明8000端口被占用，要么关闭其他服务器，要么修改端口号

---

## 📝 快速命令参考

```bash
# 进入项目目录
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"

# 启动服务器（推荐）
python3 run.py

# 或手动启动
python3 -m http.server 8000

# 检查CSV文件
python3 check_data.py

# 查看使用指南
cat USAGE.md

# 查看启动指南
cat START.md
```

---

## 🎉 现在就开始！

**最简单的方式：**
```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
python3 run.py
```

然后等待浏览器自动打开，您就能看到真实的K线图了！📈

---

## 📞 需要帮助？

1. 查看 `USAGE.md` - 详细使用指南
2. 查看 `START.md` - 启动问题排查
3. 查看 `FIX_SUMMARY.md` - 问题修复说明
4. 访问 `test.html` - 在线诊断工具

---

**祝您使用愉快！🚀**

**⚠️ 免责声明**：本工具仅供参考学习，不构成投资建议。投资有风险，入市需谨慎。
