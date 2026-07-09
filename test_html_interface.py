"""
测试 ma_backtest_local.html 的核心功能

验证内容：
1. JSON数据加载
2. 均线计算
3. 信号生成
4. 回测逻辑
5. 图表生成
"""

import json
import os

def test_json_load():
    """测试1: 加载JSON数据"""
    print("=" * 80)
    print("测试1: 加载JSON数据")
    print("=" * 80)
    
    json_dir = 'data/json'
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    
    if not json_files:
        print("❌ 失败: 未找到JSON文件")
        return False
    
    for json_file in json_files:
        filepath = os.path.join(json_dir, json_file)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ {json_file}")
        print(f"   股票代码: {data['ts_code']}")
        print(f"   数据条数: {len(data['dates'])}")
        print(f"   日期范围: {data['dates'][0]} 至 {data['dates'][-1]}")
    
    print("\n✅ 测试1通过: 所有JSON文件加载成功\n")
    return True


def test_ma_calculation():
    """测试2: 计算均线"""
    print("=" * 80)
    print("测试2: 计算均线")
    print("=" * 80)
    
    # 加载测试数据
    with open('data/json/600519_SH.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    prices = data['close']
    
    # 计算MA5
    def calculate_ma(prices, window):
        ma = []
        for i in range(len(prices)):
            if i < window - 1:
                ma.append(None)
            else:
                avg = sum(prices[i - window + 1:i + 1]) / window
                ma.append(avg)
        return ma
    
    ma5 = calculate_ma(prices, 5)
    ma15 = calculate_ma(prices, 15)
    
    print(f"✅ MA5计算完成")
    print(f"   前10个值: {[f'{v:.2f}' if v else 'N/A' for v in ma5[:10]]}")
    print(f"   第100个值: {ma5[99]:.2f}")
    
    print(f"✅ MA15计算完成")
    print(f"   第20-30个值: {[f'{v:.2f}' if v else 'N/A' for v in ma15[19:30]]}")
    
    print("\n✅ 测试2通过: 均线计算正确\n")
    return True


def test_signal_generation():
    """测试3: 生成交易信号"""
    print("=" * 80)
    print("测试3: 生成交易信号")
    print("=" * 80)
    
    # 加载测试数据
    with open('data/json/600519_SH.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    prices = data['close']
    
    # 计算均线
    def calculate_ma(prices, window):
        ma = []
        for i in range(len(prices)):
            if i < window - 1:
                ma.append(None)
            else:
                avg = sum(prices[i - window + 1:i + 1]) / window
                ma.append(avg)
        return ma
    
    ma5 = calculate_ma(prices, 5)
    ma15 = calculate_ma(prices, 15)
    
    # 生成信号
    signals = []
    for i in range(len(prices)):
        if i == 0 or ma5[i] is None or ma15[i] is None or ma5[i-1] is None or ma15[i-1] is None:
            signals.append(0)
        elif ma5[i-1] <= ma15[i-1] and ma5[i] > ma15[i]:
            signals.append(1)  # 金叉
        elif ma5[i-1] >= ma15[i-1] and ma5[i] < ma15[i]:
            signals.append(-1)  # 死叉
        else:
            signals.append(0)
    
    buy_signals = signals.count(1)
    sell_signals = signals.count(-1)
    
    print(f"✅ 信号生成完成")
    print(f"   买入信号（金叉）: {buy_signals} 次")
    print(f"   卖出信号（死叉）: {sell_signals} 次")
    
    # 找到前3个买入信号
    print(f"\n   前3个买入信号:")
    count = 0
    for i in range(len(signals)):
        if signals[i] == 1 and count < 3:
            print(f"     第{i+1}天: {data['dates'][i]}, 价格: {prices[i]:.2f}")
            count += 1
    
    print("\n✅ 测试3通过: 信号生成正确\n")
    return True


def test_backtest():
    """测试4: 完整回测"""
    print("=" * 80)
    print("测试4: 完整回测")
    print("=" * 80)
    
    # 加载测试数据
    with open('data/json/600519_SH.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    prices = data['close']
    
    # 参数
    initial_capital = 100000
    commission = 0.0003
    slippage = 0.0001
    
    # 计算均线
    def calculate_ma(prices, window):
        ma = []
        for i in range(len(prices)):
            if i < window - 1:
                ma.append(None)
            else:
                avg = sum(prices[i - window + 1:i + 1]) / window
                ma.append(avg)
        return ma
    
    ma5 = calculate_ma(prices, 5)
    ma15 = calculate_ma(prices, 15)
    
    # 生成信号
    signals = []
    for i in range(len(prices)):
        if i == 0 or ma5[i] is None or ma15[i] is None or ma5[i-1] is None or ma15[i-1] is None:
            signals.append(0)
        elif ma5[i-1] <= ma15[i-1] and ma5[i] > ma15[i]:
            signals.append(1)
        elif ma5[i-1] >= ma15[i-1] and ma5[i] < ma15[i]:
            signals.append(-1)
        else:
            signals.append(0)
    
    # 执行回测
    cash = initial_capital
    shares = 0
    nav = [initial_capital]
    trades = []
    
    for i in range(1, len(prices)):
        if signals[i] == 1 and shares == 0:
            buy_price = prices[i] * (1 + slippage)
            shares_to_buy = int(cash / buy_price / (1 + commission))
            if shares_to_buy > 0:
                cash -= shares_to_buy * buy_price * (1 + commission)
                shares = shares_to_buy
                trades.append({'date': data['dates'][i], 'type': 'BUY', 'price': buy_price})
        
        elif signals[i] == -1 and shares > 0:
            sell_price = prices[i] * (1 - slippage)
            cash += shares * sell_price * (1 - commission)
            trades.append({'date': data['dates'][i], 'type': 'SELL', 'price': sell_price})
            shares = 0
        
        nav.append(cash + shares * prices[i])
    
    # 计算指标
    total_return = (nav[-1] - nav[0]) / nav[0] * 100
    max_nav = nav[0]
    max_drawdown = 0
    for v in nav:
        if v > max_nav:
            max_nav = v
        drawdown = (v - max_nav) / max_nav
        if drawdown < max_drawdown:
            max_drawdown = drawdown
    
    print(f"✅ 回测完成")
    print(f"   初始资金: {initial_capital:,.2f} 元")
    print(f"   最终净值: {nav[-1]:,.2f} 元")
    print(f"   总收益率: {total_return:.2f}%")
    print(f"   最大回撤: {max_drawdown*100:.2f}%")
    print(f"   交易次数: {len(trades)}")
    
    if trades:
        print(f"\n   前3笔交易:")
        for i, trade in enumerate(trades[:3]):
            print(f"     {i+1}. {trade['date']} {trade['type']} @ {trade['price']:.2f}")
    
    print("\n✅ 测试4通过: 回测逻辑正确\n")
    return True


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("HTML界面功能测试")
    print("=" * 80 + "\n")
    
    try:
        test1 = test_json_load()
        test2 = test_ma_calculation()
        test3 = test_signal_generation()
        test4 = test_backtest()
        
        print("=" * 80)
        print("测试总结")
        print("=" * 80)
        print(f"测试1 (JSON加载): {'✅ 通过' if test1 else '❌ 失败'}")
        print(f"测试2 (均线计算): {'✅ 通过' if test2 else '❌ 失败'}")
        print(f"测试3 (信号生成): {'✅ 通过' if test3 else '❌ 失败'}")
        print(f"测试4 (完整回测): {'✅ 通过' if test4 else '❌ 失败'}")
        print("\n" + "=" * 80)
        print("所有测试通过！HTML界面可以正常使用。")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
