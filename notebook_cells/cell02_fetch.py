# ============================================================
# Cell 2：配置与获取数据
# ============================================================
import requests
import json
import pandas as pd
from datetime import datetime, timedelta

# ---- 配置 ----
TUSHARE_TOKEN = "023457f3e3911d11db046cb10165c91ade16348d70ee76af3102262c"
TS_CODE        = "688981.SH"     # 中芯国际 A 股
DAYS           = 365

# ---- 代理绕过（兼容 Mac 系统代理）----
def fetch_tushare(api_name, params, token=TUSHARE_TOKEN):
    """通过 HTTP 直接调用 Tushare Pro API，绕过本地代理问题"""
    proxies = {"http": None, "https": None}   # 强制不走系统代理
    payload = {
        "api_name": api_name,
        "token":    token,
        "params":   params,
        "fields":   "",
    }
    r = requests.post(
        "http://api.tushare.pro",
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        proxies=proxies,
        timeout=30,
    )
    result = r.json()
    if result.get("code") != 0:
        raise RuntimeError(f"Tushare 错误：{result.get('msg')}")
    cols = result["data"]["fields"]
    data = result["data"]["items"]
    return pd.DataFrame(data, columns=cols)

# ---- 日期范围 ----
end_date   = datetime.today()
start_date = end_date - timedelta(days=DAYS)
start_str  = start_date.strftime("%Y%m%d")
end_str    = end_date.strftime("%Y%m%d")

print(f"获取区间：{start_str} ~ {end_str}")
print(f"股票代码：{TS_CODE}\n")

# ---- 获取日线 ----
df = fetch_tushare(
    api_name="daily",
    params={"ts_code": TS_CODE, "start_date": start_str, "end_date": end_str},
)
print(f"✅ 获取到 {len(df)} 条日线记录")
df.head()
