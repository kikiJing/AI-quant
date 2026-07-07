"""
回测引擎模块

模拟交易执行，计算策略净值曲线和交易记录
"""

import pandas as pd
import numpy as np


def run_backtest(df: pd.DataFrame, params: dict) -> dict:
    """
    执行回测
    
    参数：
        df: DataFrame，必须包含 'signal', 'close', 'trade_date' 列
        params: 策略参数字典，包含：
            - initial_capital: 初始资金
            - commission: 手续费率（如0.0003表示万三）
            - slippage: 滑点（如0.0001表示万一）
            - position_sizing: 仓位管理方式
                'full' - 全仓买卖（受 buy_ratio/sell_ratio 约束）
                'fixed_shares' - 固定数量
                'fixed_ratio' - 固定比例（受 buy_ratio/sell_ratio 约束）
            - fixed_shares: 固定数量（当position_sizing='fixed_shares'时）
            - fixed_ratio: 固定比例（当position_sizing='fixed_ratio'时）
            - buy_ratio: 买入时仓位比例（默认1.0 = 全仓买入）
            - sell_ratio: 卖出时仓位比例（默认1.0 = 全仓卖出）
    
    返回：
        字典，包含：
            - 'nav': 每日净值序列（pd.Series）
            - 'returns': 每日收益率序列（pd.Series）
            - 'trades': 交易记录（pd.DataFrame）
            - 'final_value': 最终净值
            - 'portfolio_value': 每日组合价值列表
            - 'transaction_costs': 交易成本统计字典
    """
    initial_capital = params['initial_capital']
    commission = params.get('commission', 0.0003)
    slippage = params.get('slippage', 0.0001)
    position_sizing = params.get('position_sizing', 'full')
    fixed_shares = params.get('fixed_shares', 100)
    fixed_ratio = params.get('fixed_ratio', 0.5)
    buy_ratio = params.get('buy_ratio', 1.0)    # 买入仓位比例
    sell_ratio = params.get('sell_ratio', 1.0)  # 卖出仓位比例
    
    cash = initial_capital
    position = 0  # 持仓数量（股）
    portfolio_value = []
    trades = []
    total_commission = 0.0      # 累计手续费
    total_slippage = 0.0        # 累计滑点成本
    total_transaction_cost = 0.0  # 累计交易成本（手续费+滑点）
    
    for i in range(len(df)):
        signal = df.iloc[i]['signal']
        price = df.iloc[i]['close']  # 信号触发时的理论价格
        date = df.iloc[i]['trade_date']
        
        if signal == 1 and position == 0:  # 买入信号，且当前空仓
            # 计算实际买入价格（含滑点）
            actual_buy_price = price * (1 + slippage)
            
            # 计算买入数量（受 buy_ratio 约束）
            if position_sizing == 'full':
                # 全仓买入（按 buy_ratio 比例）
                affordable_shares = int(cash * (1 - commission) / actual_buy_price)
                shares_to_buy = int(affordable_shares * buy_ratio)
            elif position_sizing == 'fixed_shares':
                # 固定数量
                shares_to_buy = min(fixed_shares, int(cash / actual_buy_price))
            elif position_sizing == 'fixed_ratio':
                # 固定比例（按 buy_ratio 比例）
                amount_to_invest = cash * fixed_ratio * buy_ratio
                shares_to_buy = int(amount_to_invest * (1 - commission) / actual_buy_price)
            else:
                shares_to_buy = 0
            
            if shares_to_buy > 0:
                # 计算成本
                commission_cost = shares_to_buy * actual_buy_price * commission
                slippage_cost = shares_to_buy * (actual_buy_price - price)  # 滑点成本
                total_cost = commission_cost + slippage_cost
                
                cost = shares_to_buy * actual_buy_price + commission_cost
                cash -= cost
                position += shares_to_buy
                
                total_commission += commission_cost
                total_slippage += slippage_cost
                total_transaction_cost += total_cost
                
                trades.append({
                    'date': date,
                    'type': 'BUY',
                    'signal_price': price,           # 信号价格（理论）
                    'execution_price': actual_buy_price,  # 实际执行价格
                    'shares': shares_to_buy,
                    'commission': commission_cost,
                    'slippage': slippage_cost,
                    'total_cost': total_cost,
                    'cash_after': cash,
                    'position_after': position
                })
        
        elif signal == -1 and position > 0:  # 卖出信号，且当前持仓
            # 计算实际卖出价格（含滑点）
            actual_sell_price = price * (1 - slippage)
            
            # 计算卖出数量（受 sell_ratio 约束）
            if position_sizing == 'full':
                # 全仓卖出（按 sell_ratio 比例）
                shares_to_sell = int(position * sell_ratio)
            elif position_sizing == 'fixed_shares':
                # 固定数量
                shares_to_sell = min(fixed_shares, position)
            elif position_sizing == 'fixed_ratio':
                # 固定比例（按 sell_ratio 比例）
                shares_to_sell = int(position * fixed_ratio * sell_ratio)
            else:
                shares_to_sell = 0
            
            if shares_to_sell > 0:
                # 计算收入和成本
                commission_cost = shares_to_sell * actual_sell_price * commission
                slippage_cost = shares_to_sell * (price - actual_sell_price)  # 滑点成本
                total_cost = commission_cost + slippage_cost
                
                revenue = shares_to_sell * actual_sell_price - commission_cost
                cash += revenue
                position -= shares_to_sell
                
                total_commission += commission_cost
                total_slippage += slippage_cost
                total_transaction_cost += total_cost
                
                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'signal_price': price,           # 信号价格（理论）
                    'execution_price': actual_sell_price,  # 实际执行价格
                    'shares': shares_to_sell,
                    'commission': commission_cost,
                    'slippage': slippage_cost,
                    'total_cost': total_cost,
                    'cash_after': cash,
                    'position_after': position
                })
        
        # 计算当前组合价值
        current_value = cash + position * price
        portfolio_value.append(current_value)
    
    # 构建结果
    nav = pd.Series(portfolio_value, index=df.index, name='nav')
    returns = nav.pct_change().fillna(0)
    
    transaction_costs = {
        'total_commission': total_commission,
        'total_slippage': total_slippage,
        'total_transaction_cost': total_transaction_cost,
        'num_trades': len(trades)
    }
    
    return {
        'nav': nav,
        'returns': returns,
        'trades': pd.DataFrame(trades),
        'final_value': portfolio_value[-1] if portfolio_value else initial_capital,
        'portfolio_value': portfolio_value,
        'transaction_costs': transaction_costs
    }


def run_buy_hold_backtest(df: pd.DataFrame, params: dict) -> dict:
    """
    执行BUY-HOLD策略回测（买入并持有）
    
    参数：
        df: DataFrame，必须包含 'close', 'trade_date' 列
        params: 策略参数字典，包含 initial_capital, commission, slippage
    
    返回：
        与 run_backtest 相同的字典结构
    """
    initial_capital = params['initial_capital']
    commission = params.get('commission', 0.001)
    slippage = params.get('slippage', 0.0)
    
    # 第一天全仓买入（含滑点）
    first_price = df.iloc[0]['close']
    actual_buy_price = first_price * (1 + slippage)
    
    shares = int(initial_capital * (1 - commission) / actual_buy_price)
    commission_cost = shares * actual_buy_price * commission
    slippage_cost = shares * (actual_buy_price - first_price)
    total_cost = commission_cost + slippage_cost
    
    cash = initial_capital - shares * actual_buy_price - commission_cost
    
    # 计算每日净值
    portfolio_value = []
    for i in range(len(df)):
        price = df.iloc[i]['close']
        current_value = cash + shares * price
        portfolio_value.append(current_value)
    
    # 构建结果
    nav = pd.Series(portfolio_value, index=df.index, name='buy_hold_nav')
    returns = nav.pct_change().fillna(0)
    
    trades = [{
        'date': df.iloc[0]['trade_date'],
        'type': 'BUY',
        'signal_price': first_price,
        'execution_price': actual_buy_price,
        'shares': shares,
        'commission': commission_cost,
        'slippage': slippage_cost,
        'total_cost': total_cost,
        'cash_after': cash,
        'position_after': shares
    }]
    
    transaction_costs = {
        'total_commission': commission_cost,
        'total_slippage': slippage_cost,
        'total_transaction_cost': total_cost,
        'num_trades': 1
    }
    
    return {
        'nav': nav,
        'returns': returns,
        'trades': pd.DataFrame(trades),
        'final_value': portfolio_value[-1] if portfolio_value else initial_capital,
        'portfolio_value': portfolio_value,
        'transaction_costs': transaction_costs
    }


if __name__ == '__main__':
    print("回测引擎模块加载成功")
    print("可用函数：")
    print("  - run_backtest(): 执行策略回测")
    print("  - run_buy_hold_backtest(): 执行BUY-HOLD回测")
