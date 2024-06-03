import pyupbit
import pandas as pd
import numpy as np
import time

# drr = Daily Rate Of Return
# crr = Cumulative Rate Of Return
# mdd = Max Draw Down, dd = Draw Down

coin = "KRW-BTC"
interval = "day"
fees = 0.0005
day_count = 1300

date = None
dfs = []

for i in range(day_count // 200 + 1):
    if i < day_count // 200 :
        df = pyupbit.get_ohlcv(coin, to = date, interval = interval)
        date = df.index[0]
    elif day_count % 200 != 0 :
        df = pyupbit.get_ohlcv(coin, to = date, interval = interval, count = day_count % 200)
    else :
        break
    dfs.append(df)
    time.sleep(0.1)

df = pd.concat(dfs).sort_index()

def bollinger_bands(df, window=20):
    df['MA20'] = df['close'].rolling(window).mean()
    df['STD20'] = df['close'].rolling(window).std()
    df['UpperBand'] = df['MA20'] + (df['STD20'] * 2)
    df['LowerBand'] = df['MA20'] - (df['STD20'] * 2)
    return df

def RSI(df, window=14):
    delta = df['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    RS = gain / loss
    df['RSI'] = 100 - (100 / (1 + RS))
    df['Overbought'] = 70
    df['Oversold'] = 30
    return df

def get_crr(df, fees, K):
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    df['targetPrice'] = df['open'] + df['range'] * K
    df['drr'] = np.where(df['high'] > df['targetPrice'], (df['close'] / (1 + fees)) / (df['targetPrice'] * (1 + fees)) - 1 , 0)
    return (df['drr'] + 1).cumprod()[-2]

def get_best_K(coin, fees):
    df = pyupbit.get_ohlcv(coin, interval="minute1", count=21)
    max_crr = 0
    best_K = 0.5
    for k in np.arange(0.0, 1.0, 0.1):
        crr = get_crr(df, fees, k)
        if crr > max_crr:
            max_crr = crr
            best_K = k
    return best_K

best_K = get_best_K(coin, fees)
df['range'] = df['high'].shift(1) - df['low'].shift(1)
df['targetPrice'] = df['open'] + df['range'] * best_K
df['drr'] = np.where(df['high'] > df['targetPrice'], (df['close'] / (1 + fees)) / (df['targetPrice'] * (1 + fees)) - 1 , 0)

df['crr'] = (df['drr'] + 1).cumprod() - 1
df['dd'] = -(((df['crr'] + 1).cummax() - (df['crr'] + 1)) / (df['crr'] + 1).cummax())

df = bollinger_bands(df)
df = RSI(df)

print("기간수익률 :", df['crr'][-1] * 100, "% , 최대손실률 :", df['dd'].min() * 100, "% , 수수료 :", fees * 100, "%")
print("알고리즘 적용 없을 시 수익률 :", ((df['close'][-1]/(1+fees))/(df['open'][0]*(1+fees))-1) * 100,"%")

df.to_excel("crypto_history_with_best_K.xlsx")
