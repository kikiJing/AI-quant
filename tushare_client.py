"""
Tushare 数据客户端 — 量化项目的统一数据接口。

提供行情、财务、指数等数据的获取，统一处理 pro_bar 降级和错误。
"""

import pandas as pd
import tushare as ts
from config import TUSHARE_TOKEN

# 全局单例
_pro = None


def get_pro():
    """获取 Tushare Pro 客户端实例（单例）。"""
    global _pro
    if _pro is None:
        _pro = ts.pro_api(TUSHARE_TOKEN)
    return _pro


def check_connection() -> dict:
    """检测 Tushare Pro 连接是否正常。"""
    try:
        pro = get_pro()
        df = pro.stock_basic(list_status='L', fields='ts_code', limit=1)
        if df is not None and not df.empty:
            return {"ok": True, "msg": f"连接成功 ✓  — 可查询 {len(df)} 条股票基本信息"}
        return {"ok": False, "msg": "连接成功但查询返回为空"}
    except Exception as e:
        return {"ok": False, "msg": str(e)}


# ---- 行情 API ----

def daily(ts_code: str, start_date: str = None, end_date: str = None,
          **kwargs) -> pd.DataFrame:
    """获取 A 股日线行情。"""
    return get_pro().daily(ts_code=ts_code, start_date=start_date,
                           end_date=end_date, **kwargs)


def weekly(ts_code: str, start_date: str = None, end_date: str = None,
           **kwargs) -> pd.DataFrame:
    """获取 A 股周线行情。"""
    return get_pro().weekly(ts_code=ts_code, start_date=start_date,
                            end_date=end_date, **kwargs)


def monthly(ts_code: str, start_date: str = None, end_date: str = None,
            **kwargs) -> pd.DataFrame:
    """获取 A 股月线行情。"""
    return get_pro().monthly(ts_code=ts_code, start_date=start_date,
                             end_date=end_date, **kwargs)


def adj_factor(ts_code: str, start_date: str = None, end_date: str = None,
               **kwargs) -> pd.DataFrame:
    """获取复权因子。"""
    return get_pro().adj_factor(ts_code=ts_code, start_date=start_date,
                                end_date=end_date, **kwargs)


def trade_cal(exchange: str = 'SSE', start_date: str = None,
              end_date: str = None, **kwargs) -> pd.DataFrame:
    """获取交易日历。"""
    return get_pro().trade_cal(exchange=exchange, start_date=start_date,
                               end_date=end_date, **kwargs)


# ---- 股票基础 ----

def stock_basic(**kwargs) -> pd.DataFrame:
    """股票基本信息。"""
    return get_pro().stock_basic(**kwargs)


def namechange(ts_code: str = None, **kwargs) -> pd.DataFrame:
    """股票曾用名。"""
    return get_pro().namechange(ts_code=ts_code, **kwargs)


# ---- 财务数据 ----

def income(ts_code: str, start_date: str = None, end_date: str = None,
           **kwargs) -> pd.DataFrame:
    """利润表。"""
    return get_pro().income(ts_code=ts_code, start_date=start_date,
                            end_date=end_date, **kwargs)


def balancesheet(ts_code: str, start_date: str = None, end_date: str = None,
                 **kwargs) -> pd.DataFrame:
    """资产负债表。"""
    return get_pro().balancesheet(ts_code=ts_code, start_date=start_date,
                                  end_date=end_date, **kwargs)


def cashflow(ts_code: str, start_date: str = None, end_date: str = None,
             **kwargs) -> pd.DataFrame:
    """现金流量表。"""
    return get_pro().cashflow(ts_code=ts_code, start_date=start_date,
                              end_date=end_date, **kwargs)


def fina_indicator(ts_code: str, start_date: str = None, end_date: str = None,
                   **kwargs) -> pd.DataFrame:
    """财务指标（ROE/EPS 等）。"""
    return get_pro().fina_indicator(ts_code=ts_code, start_date=start_date,
                                    end_date=end_date, **kwargs)


# ---- 指数 ----

def index_basic(**kwargs) -> pd.DataFrame:
    """指数基本信息。"""
    return get_pro().index_basic(**kwargs)


def index_daily(ts_code: str, start_date: str = None, end_date: str = None,
                **kwargs) -> pd.DataFrame:
    """指数日线行情。"""
    return get_pro().index_daily(ts_code=ts_code, start_date=start_date,
                                 end_date=end_date, **kwargs)


def index_weight(index_code: str, trade_date: str = None, **kwargs) -> pd.DataFrame:
    """指数成分和权重。"""
    return get_pro().index_weight(index_code=index_code,
                                  trade_date=trade_date, **kwargs)


def index_classify(**kwargs) -> pd.DataFrame:
    """申万行业分类。"""
    return get_pro().index_classify(**kwargs)


# ---- 基金 ----

def fund_basic(**kwargs) -> pd.DataFrame:
    """基金基本信息。"""
    return get_pro().fund_basic(**kwargs)


def fund_daily(ts_code: str, start_date: str = None, end_date: str = None,
               **kwargs) -> pd.DataFrame:
    """基金日线行情。"""
    return get_pro().fund_daily(ts_code=ts_code, start_date=start_date,
                                end_date=end_date, **kwargs)


def fund_nav(ts_code: str, start_date: str = None, end_date: str = None,
             **kwargs) -> pd.DataFrame:
    """基金净值。"""
    return get_pro().fund_nav(ts_code=ts_code, start_date=start_date,
                              end_date=end_date, **kwargs)


def fund_portfolio(ts_code: str, **kwargs) -> pd.DataFrame:
    """基金持仓。"""
    return get_pro().fund_portfolio(ts_code=ts_code, **kwargs)


if __name__ == "__main__":
    result = check_connection()
    print(result["msg"])
