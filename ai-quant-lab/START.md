# 🚀 快速启动指南

## 问题：数据加载失败

如果您看到"加载数据失败，请确保CSV文件存在"的错误，原因是**浏览器安全限制**。

### ❌ 错误方式
直接双击打开 `index.html` 文件
- 浏览器URL以 `file://` 开头
- 由于CORS限制，无法加载CSV文件

### ✅ 正确方式
使用本地HTTP服务器

---

## 方法1：使用启动脚本（最简单，推荐）

### macOS / Linux
```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
python3 run.py
```

或
```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
./start.sh
```

### Windows
```bash
cd "C:\Users\你的用户名\Desktop\AI quant\ai-quant-lab"
python run.py
```

**脚本会自动：**
1. 启动本地服务器
2. 打开浏览器
3. 加载数据分析界面

---

## 方法2：手动启动服务器

### 步骤1：打开终端

### 步骤2：进入项目目录
```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
```

### 步骤3：启动服务器
```bash
python3 -m http.server 8000
```

### 步骤4：打开浏览器
访问：`http://localhost:8000/index.html`

---

## 方法3：使用诊断页面

如果您不确定问题出在哪里，可以先访问诊断页面：

1. 启动本地服务器（如上所述）
2. 在浏览器中访问：`http://localhost:8000/test.html`
3. 点击页面上的测试按钮，查看详细错误信息

---

## 🔍 诊断步骤

### 1. 检查浏览器URL
在浏览器中按 `F12` 打开开发者工具，查看地址栏：
- ✅ 正确：`http://localhost:8000/index.html`
- ❌ 错误：`file:///Users/kikijing/.../index.html`

如果是 `file://` 开头，说明您是直接双击打开的，请使用方法1或2。

### 2. 检查浏览器控制台
按 `F12` 打开开发者工具，查看 `Console` 标签页：
- 如果看到 `正在加载: data/xxx_daily.csv` → 说明开始加载
- 如果看到 `加载数据失败` → 查看详细错误信息

### 3. 检查CSV文件
确保 `data/` 目录下有CSV文件：
```bash
ls -l "/Users/kikijing/Desktop/AI quant/ai-quant-lab/data/"
```

应该看到类似：
```
ningde_times_300750_daily.csv
ping_an_601318_daily.csv
moutai_600519_daily.csv
...
```

### 4. 运行诊断脚本
```bash
cd "/Users/kikijing/Desktop/AI quant/ai-quant-lab"
python3 check_data.py
```

---

## 📁 项目文件清单

确保您的 `ai-quant-lab/` 目录包含以下文件：

```
ai-quant-lab/
├── index.html          # 主界面（必须用服务器访问）
├── test.html           # 诊断页面
├── run.py              # 启动脚本（推荐）
├── start.sh            # macOS/Linux启动脚本
├── check_data.py       # 数据检查脚本
├── README.md           # 项目说明
├── USAGE.md            # 使用指南
├── START.md            # 本文件
├── data/               # 数据目录（必须有CSV文件）
│   ├── ningde_times_300750_daily.csv
│   ├── ping_an_601318_daily.csv
│   ├── moutai_600519_daily.csv
│   ├── petro_china_601857_daily.csv
│   └── byd_002594_daily.csv
├── scripts/            # Python脚本
├── notebooks/          # Jupyter Notebooks
└── docs/               # 文档
```

---

## ⚠️ 常见问题

### Q1: 双击打开HTML文件，图表不显示
**A**: 必须使用本地服务器，不能直接双击打开。请运行 `python3 run.py`

### Q2: 提示"加载数据失败"
**A**: 
1. 确保通过 `http://localhost:8000` 访问（不是 `file://`）
2. 确保 `data/` 目录下有CSV文件
3. 查看浏览器控制台（F12）的详细错误

### Q3: 端口8000被占用
**A**: 修改 `run.py` 中的 `PORT = 8000` 为其他端口（如8001, 8080等）

### Q4: CSV文件有但加载失败
**A**: 可能是文件编码问题。运行 `python3 check_data.py` 检查

### Q5: 浏览器没有自动打开
**A**: 手动在浏览器中访问 `http://localhost:8000/index.html`

---

## 🎯 快速验证

启动成功后，您应该看到：

1. **终端输出**：
   ```
   🚀 正在启动本地服务器...
      地址: http://localhost:8000
   ✅ 服务器已启动！访问 http://localhost:8000/index.html
   ```

2. **浏览器页面**：
   - 标题：AI Quant Lab
   - 左侧：股票选择和技术指标参数
   - 主区域：K线图（加载后会显示图表）

3. **浏览器控制台（F12）**：
   ```
   正在加载: data/ningde_times_300750_daily.csv
   CSV数据长度: 43156
   CSV行数: 485
   解析后的数据条数: 484
   数据加载成功！
   ```

---

## 📞 需要帮助？

1. 查看 `USAGE.md` 了解详细使用说明
2. 查看 `README.md` 了解项目概况
3. 访问 `test.html` 进行诊断
4. 提交GitHub Issue

---

**祝您使用愉快！🎉**

**⚠️ 免责声明**：本工具仅供参考学习，不构成投资建议。投资有风险，入市需谨慎。
