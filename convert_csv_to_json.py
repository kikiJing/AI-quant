"""
将CSV股票数据转换为JSON格式
供HTML界面直接加载使用（无需API服务器）
"""

import pandas as pd
import json
import os

# 文件映射
file_map = {
    '300750.SZ': 'ningde_times_300750_daily_adjusted.csv',
    '601318.SH': 'ping_an_601318_daily_adjusted.csv',
    '600519.SH': 'moutai_600519_daily_adjusted.csv',
    '601857.SH': 'petro_china_601857_daily_adjusted.csv',
    '002594.SZ': 'byd_002594_daily_adjusted.csv'
}

# 创建输出目录
output_dir = 'data/json'
os.makedirs(output_dir, exist_ok=True)

# 转换每个文件
for ts_code, filename in file_map.items():
    filepath = f'data/adjusted/{filename}'
    if not os.path.exists(filepath):
        print(f'文件不存在: {filepath}')
        continue
    
    # 读取CSV
    df = pd.read_csv(filepath)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df = df.sort_values('trade_date').reset_index(drop=True)
    
    # 转换为JSON格式
    data = {
        'ts_code': ts_code,
        'name': filename.split('_')[0],
        'dates': df['trade_date'].dt.strftime('%Y-%m-%d').tolist(),
        'open': df['open'].tolist(),
        'high': df['high'].tolist(),
        'low': df['low'].tolist(),
        'close': df['close'].tolist(),
        'volume': df['vol'].tolist() if 'vol' in df.columns else df['volume'].tolist()
    }
    
    # 保存JSON（文件名中的点替换为下划线）
    safe_ts_code = ts_code.replace('.', '_')
    output_path = f'{output_dir}/{safe_ts_code}.json'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f'✅ 已转换: {ts_code} ({len(df)} 条记录) → {output_path}')

print('\n✅ 所有文件转换完成！')
print(f'JSON文件已保存到: {output_dir}/')
