#!/usr/bin/env python3
"""组装 notebook_cells/ 下的代码文件为完整的 .ipynb"""
import nbformat
from nbformat import v4 as nbf
import os

CELL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebook_cells")
OUT_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smic_analysis.ipynb")

nb = nbf.new_notebook()

# ---- Cell 0：标题 Markdown ----
nb.cells.append(nbf.new_markdown_cell(
    "# 中芯国际（688981.SH）行情分析 Notebook\n"
    "\n"
    "本 Notebook 可在 Jupyter Lab / Jupyter Notebook 中完整复现以下流程：\n"
    "\n"
    "1. 通过 Tushare 获取近一年日线数据\n"
    "2. 数据清洗 + 技术指标计算（MA / RSI / MACD）\n"
    "3. Plotly 交互式 K 线图 + 成交量图\n"
    "4. RSI / MACD 指标图\n"
    "5. 自动技术分析结论与买卖建议\n"
    "\n"
    "> ⚠️ Tushare token 已内置，如需更换请修改 **Cell 2** 中的 `TUSHARE_TOKEN` 变量\n"
    "> 📦 依赖：tushare / pandas / numpy / plotly / requests"
))

# ---- 按顺序读取 cell 代码文件 ----
cell_files = sorted(f for f in os.listdir(CELL_DIR) if f.endswith(".py"))
for fname in cell_files:
    fpath = os.path.join(CELL_DIR, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        code = f.read()
    nb.cells.append(nbf.new_code_cell(code))
    print(f"  ✓ {fname}（{len(code.splitlines())} 行）")

# ---- 写入 .ipynb ----
with open(OUT_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"\n✅ Notebook 已生成：{OUT_PATH}")
print(f"   共 {len(nb.cells)} 个 Cell（1 个 Markdown + {len(cell_files)} 个 Code）")
