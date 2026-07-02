# ============================================================
# Cell 1：安装依赖
# ============================================================
import subprocess, sys

packages = [
    "tushare",
    "pandas",
    "numpy",
    "plotly",
    "requests",
]

for pkg in packages:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", pkg, "-q"],
        check=False
    )

print("✅ 依赖安装完成")

# ---- 初始化 Plotly 在 Jupyter 中的渲染器 ----
import plotly.io as pio
pio.renderers.default = "notebook_connected"  # Jupyter Lab / Notebook 均适用
print("✅ Plotly 渲染器已初始化")
