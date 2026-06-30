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
