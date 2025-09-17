from hyperquant.core import Exchange
import json
import pandas as pd

data = json.load(open("deals.json", "r"))

data = data['data']['resultList']

data = data[::-1]  # 时间正序

e = Exchange([], fee=0, initial_balance=100, recorded=True)

for d in data:
    dir = 1 if d['tradeType'] == 'BUY' else -1
    symbol = d['symbol']
    time = pd.Timestamp(d['createTime'], unit='ms')
    check_time = pd.Timestamp("2025-09-08 23:39:50")
    if time < check_time:
        continue
    if symbol == 'OPEN_USDT':
        continue
    e.Trade(symbol, dir, float(d['price']), float(d['quantity']) , time = time)

print(e.stats)
# import pandas as pd

# df = pd.DataFrame(e.trades)
# # 过滤掉pos为0的行
# df = df[df['pos'] != 0]
# print(df)
# # 按照symbol分组，pos字段求和, pos_rate求平均
# summary = df.groupby('symbol').agg({'pos': 'sum', 'pos_rate': 'mean'}).reset_index()
# print(summary)