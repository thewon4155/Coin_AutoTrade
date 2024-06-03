import pyupbit
import datetime
import time
import auth
import numpy as np
import requests

# Function to post a message to Slack
def post_message(text):
    try:
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer " + auth.myToken},
            data={"channel": auth.channel, "text": text}
        )
        response_data = response.json()
        if not response_data.get("ok"):
            print(f"Error posting message to Slack: {response_data['error']}")
    except Exception as e:
        print(f"Exception posting message to Slack: {e}")

# Function to calculate the target price based on the given dataframe and K value
def get_targetPrice(df, K):
    price_range = df['high'][-2] - df['low'][-2]
    return df['open'][-1] + price_range * K

# Function to buy all available balance of a coin
def buy_all(coin):
    balance = upbit.get_balance("KRW") * 0.9995
    if balance >= 5000:
        print(upbit.buy_market_order(coin, balance))
        post_message(f"매수 체결.\n체결 단가: {pyupbit.get_current_price(coin)} 원")

# Function to sell all holdings of a coin
def sell_all(coin):
    balance = upbit.get_balance(coin)
    price = pyupbit.get_current_price(coin)
    if price * balance >= 5000:
        print(upbit.sell_market_order(coin, balance))
        post_message(f"매도 체결.\n체결 단가: {pyupbit.get_current_price(coin)} 원")

# Function to get the cumulative return rate (CRR)
def get_crr(df, fees, K):
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    df['targetPrice'] = df['open'] + df['range'] * K
    df['drr'] = np.where(df['high'] > df['targetPrice'], (df['close'] / (1 + fees)) / (df['targetPrice'] * (1 + fees)), 1)
    return df['drr'].cumprod()[-2]

# Function to find the best K value
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

# Bollinger Bands function
def bollinger_bands(data, window_size=30):
    rolling_mean = data['close'].rolling(window=window_size).mean()
    rolling_std = data['close'].rolling(window=window_size).std()
    data['UpperBand'] = rolling_mean + (2 * rolling_std)
    data['LowerBand'] = rolling_mean - (2 * rolling_std)
    return data

# RSI function
def RSI(data, window=14):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    RS = avg_gain / avg_loss
    RSI = 100 - (100 / (1 + RS))
    data['RSI'] = RSI
    data['Overbought'] = 70
    data['Oversold'] = 30
    return data

# Strategy function
def strategy(data):
    data = bollinger_bands(data)
    data = RSI(data)
    buy_price = []
    sell_price = []
    position = 0

    for i in range(len(data)):
        if data['close'][i] < data['LowerBand'][i] and data['RSI'][i] < data['Oversold'] and position == 0:
            position = 1
            buy_price.append(data['close'][i])
            sell_price.append(np.nan)
        elif data['close'][i] > data['UpperBand'][i] and data['RSI'][i] > data['Overbought'] and position == 1:
            position = 0
            sell_price.append(data['close'][i])
            buy_price.append(np.nan)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
    return buy_price, sell_price

if __name__ == '__main__':
    try:
        upbit = pyupbit.Upbit(auth.access, auth.secret)

        # Set variables
        coin = "KRW-BTC"
        fees = 0.0005
        K = 0.5
        
        start_balance = upbit.get_balance("KRW")
        df = pyupbit.get_ohlcv(coin, count=2, interval="minute1")
        targetPrice = get_targetPrice(df, get_best_K(coin, fees))
        print(f"{datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S')}\t\tBalance: {start_balance} KRW \t\tYield: {((start_balance / start_balance) - 1) * 100} % \t\tNew targetPrice: {targetPrice} KRW")
        post_message(f"자동매매를 시작합니다.\n잔액: {start_balance} 원\n목표매수가: {targetPrice} 원")

        while True:
            now = datetime.datetime.now()

            # Check for daily routine at 09:32
            if now.hour == 9 and now.minute == 32:
                sell_all(coin)
                time.sleep(10)

                df = pyupbit.get_ohlcv(coin, count=2, interval="minute1")
                targetPrice = get_targetPrice(df, get_best_K(coin, fees))

                cur_balance = upbit.get_balance("KRW")
                print(f"{now.strftime('%y/%m/%d %H:%M:%S')}\t\tBalance: {cur_balance} KRW \t\tYield: {((cur_balance / start_balance) - 1) * 100} % \t\tNew targetPrice: {targetPrice} KRW")
                post_message(f"새로운 장 시작\n수익률: {((cur_balance / start_balance) - 1) * 100} %\n잔액: {cur_balance} 원\n목표매수가: {targetPrice} 원")
                time.sleep(60)

            # Trading logic within each minute
            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(minutes=1)
            
            while datetime.datetime.now() < end_time:
                df = pyupbit.get_ohlcv(coin, interval="minute1", count=30)
                df = bollinger_bands(df)
                df = RSI(df)
                current_price = pyupbit.get_current_price(coin)
                
                if current_price < targetPrice and df['close'][-1] < df['LowerBand'][-1] and df['RSI'][-1] < df['Oversold'] and upbit.get_balance("KRW") >= 5000:
                    buy_all(coin)
                    time.sleep(1)
                elif current_price > targetPrice and df['close'][-1] > df['UpperBand'][-1] and df['RSI'][-1] > df['Overbought'] and upbit.get_balance(coin) * current_price >= 5000:
                    sell_all(coin)
                    time.sleep(1)

                time.sleep(1)

    except Exception as e:
        print(e)
        post_message(str(e))
        time.sleep(1)
