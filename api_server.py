"""
Flask API 服务器 - 均线策略回测系统

提供以下API端点：
- GET  /api/stocks          - 获取股票列表
- POST /api/backtest        - 执行回测，返回结果（JSON）
- GET  /api/chart/<path>    - 获取图表HTML文件
"""

from flask import Flask, request, jsonify, send_from_directory
import os
import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategy import (
    generate_signals,
    run_backtest,
    run_buy_hold_backtest,
    calculate_metrics,
    format_metrics_report
)

# ============================================================================
# 配置
# ============================================================================

app = Flask(__name__)

# 数据目录
DATA_DIR = 'data/adjusted'
OUTPUT_DIR = 'outputs/ma_backtest'
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')

# 确保输出目录存在
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# 股票列表
STOCKS = [
    {'ts_code': '300750.SZ', 'name': '宁德时代', 'industry': '科技/新能源'},
    {'ts_code': '601318.SH', 'name': '中国平安', 'industry': '金融'},
    {'ts_code': '600519.SH', 'name': '贵州茅台', 'industry': '消费'},
    {'ts_code': '601857.SH', 'name': '中国石油', 'industry': '能源'},
    {'ts_code': '002594.SZ', 'name': '比亚迪', 'industry': '制造'}
]

# 文件映射
FILE_MAP = {
    '300750.SZ': 'ningde_times_300750_daily_adjusted.csv',
    '601318.SH': 'ping_an_601318_daily_adjusted.csv',
    '600519.SH': 'moutai_600519_daily_adjusted.csv',
    '601857.SH': 'petro_china_601857_daily_adjusted.csv',
    '002594.SZ': 'byd_002594_daily_adjusted.csv'
}

# ============================================================================
# 工具函数
# ============================================================================

def load_stock_data(ts_code, start_date=None, end_date=None):
    """加载股票数据"""
    filename = FILE_MAP.get(ts_code)
    if not filename:
        return None
    
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return None
    
    df = pd.read_csv(filepath)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    if start_date:
        df = df[df['trade_date'] >= pd.to_datetime(start_date)].copy()
    if end_date:
        df = df[df['trade_date'] <= pd.to_datetime(end_date)].copy()
    
    df = df.reset_index(drop=True)
    return df


def run_backtest_for_api(ts_code, params):
    """
    执行回测（供API调用）
    
    返回：
        dict: 包含回测结果的字典
    """
    try:
        # 加载数据
        df = load_stock_data(ts_code, params.get('start_date'), params.get('end_date'))
        if df is None or len(df) == 0:
            return {'error': f'无法加载股票数据: {ts_code}'}
        
        # 获取股票信息
        stock_info = next((s for s in STOCKS if s['ts_code'] == ts_code), None)
        if not stock_info:
            return {'error': f'未找到股票信息: {ts_code}'}
        
        # 生成信号
        df = generate_signals(df, params)
        
        # 执行策略回测
        backtest_result = run_backtest(df, params)
        
        # 执行BUY-HOLD回测
        buy_hold_result = run_buy_hold_backtest(df, params)
        
        # 计算指标
        metrics = calculate_metrics(backtest_result, buy_hold_result, df)
        
        # 生成图表
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.7, 0.3],
            subplot_titles=(
                f"{stock_info['name']} ({ts_code}) - 均线策略回测",
                '策略净值 vs BUY-HOLD'
            )
        )
        
        # K线图
        fig.add_trace(
            go.Candlestick(
                x=df['trade_date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='股价',
                increasing_line_color='red',
                decreasing_line_color='green',
            ),
            row=1, col=1
        )
        
        # 短均线
        fig.add_trace(
            go.Scatter(
                x=df['trade_date'],
                y=df['short_ma'],
                mode='lines',
                name=f"短均线({params['short_window']})",
                line=dict(color='orange', width=1.5)
            ),
            row=1, col=1
        )
        
        # 长均线
        fig.add_trace(
            go.Scatter(
                x=df['trade_date'],
                y=df['long_ma'],
                mode='lines',
                name=f"长均线({params['long_window']})",
                line=dict(color='blue', width=1.5)
            ),
            row=1, col=1
        )
        
        # 趋势均线（如果启用）
        if params.get('trend_filter') and 'trend_ma' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['trade_date'],
                    y=df['trend_ma'],
                    mode='lines',
                    name=f"趋势均线({params['trend_window']})",
                    line=dict(color='purple', width=1.5, dash='dash')
                ),
                row=1, col=1
            )
        
        # 买入信号
        buy_signals = df[df['signal'] == 1]
        if len(buy_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals['trade_date'],
                    y=buy_signals['close'],
                    mode='markers',
                    name='买入信号',
                    marker=dict(symbol='triangle-up', size=12, color='green')
                ),
                row=1, col=1
            )
        
        # 卖出信号
        sell_signals = df[df['signal'] == -1]
        if len(sell_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals['trade_date'],
                    y=sell_signals['close'],
                    mode='markers',
                    name='卖出信号',
                    marker=dict(symbol='triangle-down', size=12, color='red')
                ),
                row=1, col=1
            )
        
        # 净值曲线
        fig.add_trace(
            go.Scatter(
                x=df['trade_date'],
                y=backtest_result['nav'].values,
                mode='lines',
                name='策略净值',
                line=dict(color='blue', width=2)
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['trade_date'],
                y=buy_hold_result['nav'].values,
                mode='lines',
                name='BUY-HOLD',
                line=dict(color='gray', width=2, dash='dash')
            ),
            row=2, col=1
        )
        
        # 更新布局
        fig.update_layout(
            height=800,
            template='plotly_white',
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        fig.update_yaxis(title_text="价格（元）", row=1, col=1)
        fig.update_yaxis(title_text="净值（元）", row=2, col=1)
        
        # 保存图表
        chart_filename = f"{stock_info['name']}_{ts_code}_backtest.html"
        chart_path = os.path.join(CHARTS_DIR, chart_filename)
        fig.write_html(chart_path)
        
        # 准备返回数据
        result = {
            'success': True,
            'stock_info': stock_info,
            'metrics': {
                'strategy_total_return': float(metrics['strategy_total_return']),
                'strategy_annual_return': float(metrics['strategy_annual_return']) if not pd.isna(metrics['strategy_annual_return']) else None,
                'strategy_max_drawdown': float(metrics['strategy_max_drawdown']),
                'strategy_sharpe': float(metrics['strategy_sharpe']),
                'strategy_win_rate': float(metrics['strategy_win_rate']) if not pd.isna(metrics['strategy_win_rate']) else None,
                'bh_total_return': float(metrics['bh_total_return']),
                'excess_return': float(metrics['excess_return']),
                'num_trades': int(metrics['num_trades'])
            },
            'chart_url': f'/api/chart/{chart_filename}',
            'trades': backtest_result['trades'].to_dict('records') if len(backtest_result['trades']) > 0 else []
        }
        
        return result
        
    except Exception as e:
        return {'error': str(e)}


# ============================================================================
# API 路由
# ============================================================================

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """获取股票列表"""
    return jsonify({'success': True, 'stocks': STOCKS})


@app.route('/api/backtest', methods=['POST'])
def backtest():
    """执行回测"""
    try:
        data = request.get_json()
        
        ts_code = data.get('ts_code')
        if not ts_code:
            return jsonify({'error': '缺少 ts_code 参数'}), 400
        
        # 构建策略参数
        params = {
            'short_window': int(data.get('short_window', 5)),
            'long_window': int(data.get('long_window', 15)),
            'ma_type': data.get('ma_type', 'MA'),
            'trend_filter': bool(data.get('trend_filter', True)),
            'trend_window': int(data.get('trend_window', 120)),
            'atr_filter': bool(data.get('atr_filter', True)),
            'atr_window': int(data.get('atr_window', 14)),
            'atr_percentile': float(data.get('atr_percentile', 20)),
            'atr_lookback': int(data.get('atr_lookback', 100)),
            'initial_capital': float(data.get('initial_capital', 100000)),
            'commission': float(data.get('commission', 0.0003)),
            'slippage': float(data.get('slippage', 0.0001)),
            'position_sizing': data.get('position_sizing', 'full'),
            'fixed_shares': int(data.get('fixed_shares', 100)),
            'fixed_ratio': float(data.get('fixed_ratio', 0.5)),
            'buy_ratio': float(data.get('buy_ratio', 1.0)),
            'sell_ratio': float(data.get('sell_ratio', 1.0)),
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date')
        }
        
        # 执行回测
        result = run_backtest_for_api(ts_code, params)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart/<filename>', methods=['GET'])
def get_chart(filename):
    """获取图表HTML文件"""
    return send_from_directory(CHARTS_DIR, filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': '均线策略回测API正常运行'})


# ============================================================================
# 主函数
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("均线策略回测系统 - API 服务器")
    print("=" * 80)
    print("\n启动中...")
    print("  API文档:")
    print("    GET  /api/stocks       - 获取股票列表")
    print("    POST /api/backtest     - 执行回测")
    print("    GET  /api/chart/<file> - 获取图表")
    print("    GET  /api/health       - 健康检查")
    print("\n请在浏览器中打开: http://localhost:5000")
    print("=" * 80)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
