import pyupbit
import datetime
import time
import auth
import numpy as np
import requests
import sqlite3

# Connect to SQLite database and create table
conn = sqlite3.connect('trading_signals.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        action TEXT,
        coin TEXT,
        price REAL,
        amount REAL,
        balance REAL
    )
''')
conn.commit()

# Function to post a message to Slack with additional information
def post_message(text, additional_info=None):
    message = text
    if additional_info:
        message += "\n" + "\n".join(f"{key}: {value}" for key, value in additional_info.items())
    
    try:
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer " + auth.myToken},
            data={"channel": auth.channel, "text": message}
        )
        response_data = response.json()
        if not response_data.get("ok"):
            raise ValueError(f"Error posting message to Slack: {response_data['error']}")
    except Exception as e:
        print(f"Exception posting message to Slack: {e}")

# Function to calculate the target price based on the given dataframe and K value
def get_targetPrice(df, K):
    if len(df) < 2:
        raise ValueError("DataFrame does not contain enough data")
    price_range = df['high'].iloc[-2] - df['low'].iloc[-2]
    return df['open'].iloc[-1] + price_range * K

# Function to save signals to the database
def save_signal_to_db(action, coin, price, amount, balance):
    conn = sqlite3.connect('trading_signals.db')
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO signals (timestamp, action, coin, price, amount, balance)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, action, coin, price, amount, balance))
    
    conn.commit()
    conn.close()

# Function to buy all available balance of a coin
def buy_all(coin):
    balance = upbit.get_balance("KRW") * 0.9995
    if balance >= 5000:
        buy_response = upbit.buy_market_order(coin, balance)
        price = pyupbit.get_current_price(coin)
        post_message(
            f"매수 체결.",
            {
                "체결 단가": price,
                "잔액": balance,
                "Response": buy_response
            }
        )
        save_signal_to_db("buy", coin, price, balance, upbit.get_balance("KRW"))
        print(buy_response)

# Function to sell all holdings of a coin
def sell_all(coin):
    balance = upbit.get_balance(coin)
    price = pyupbit.get_current_price(coin)
    if price * balance >= 5000:
        sell_response = upbit.sell_market_order(coin, balance)
        post_message(
            f"매도 체결.",
            {
                "체결 단가": price,
                "잔액": balance * price,
                "Response": sell_response
            }
        )
        save_signal_to_db("sell", coin, price, balance, upbit.get_balance("KRW"))
        print(sell_response)

# Function to get the cumulative return rate (CRR)
def get_crr(df, fees, K):
    df['range'] = df['high'].shift(1) - df['low'].shift(1)
    df['targetPrice'] = df['open'] + df['range'] * K
    df['drr'] = np.where(df['high'] > df['targetPrice'], (df['close'] / (1 + fees)) / (df['targetPrice'] * (1 + fees)), 1)
    return df['drr'].cumprod().iloc[-2]

# Function to find the best K value
def get_best_K(coin, fees):
    df = pyupbit.get_ohlcv(coin, interval="minute1", count=21)
    if len(df) < 21:
        raise ValueError("Not enough data to determine the best K value")
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
        if data['close'].iloc[i] < data['LowerBand'].iloc[i] and data['RSI'].iloc[i] < data['Oversold'].iloc[i] and position == 0:
            position = 1
            buy_price.append(data['close'].iloc[i])
            sell_price.append(np.nan)
        elif data['close'].iloc[i] > data['UpperBand'].iloc[i] and data['RSI'].iloc[i] > data['Overbought'].iloc[i] and position == 1:
            position = 0
            sell_price.append(data['close'].iloc[i])
            buy_price.append(np.nan)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
    return buy_price, sell_price

if __name__ == '__main__':
    try:
        upbit = pyupbit.Upbit(auth.access, auth.secret)

        coin = "KRW-BTC"
        fees = 0.0005

        start_balance = upbit.get_balance("KRW")
        df = pyupbit.get_ohlcv(coin, count=2, interval="minute1")
        best_K = get_best_K(coin, fees)
        targetPrice = get_targetPrice(df, best_K)

        initial_message = (
            f"자동매매를 시작합니다.\n잔액: {start_balance} 원\n"
            f"목표매수가: {targetPrice} 원\n"
            f"Best K: {best_K}"
        )
        post_message(initial_message)

        while True:
            now = datetime.datetime.now()

            if now.hour == 9 and now.minute == 2:
                sell_all(coin)
                time.sleep(10)

                df = pyupbit.get_ohlcv(coin, count=2, interval="minute1")
                best_K = get_best_K(coin, fees)
                targetPrice = get_targetPrice(df, best_K)

                cur_balance = upbit.get_balance("KRW")
                daily_message = (
                    f"새로운 장 시작\n수익률: {((cur_balance / start_balance) - 1) * 100} %\n"
                    f"잔액: {cur_balance} 원\n목표매수가: {targetPrice} 원\n"
                    f"Best K: {best_K}"
                )
                post_message(daily_message)
                time.sleep(60)

            if now.minute == 0:
                df = pyupbit.get_ohlcv(coin, count=2, interval="minute1")
                best_K = get_best_K(coin, fees)
                targetPrice = get_targetPrice(df, best_K)

            df = pyupbit.get_ohlcv(coin, interval="minute1", count=30)
            df = bollinger_bands(df)
            df = RSI(df)
            current_price = pyupbit.get_current_price(coin)

            if current_price < targetPrice and df['close'].iloc[-1] < df['LowerBand'].iloc[-1] and df['RSI'].iloc[-1] < df['Oversold'].iloc[-1] and upbit.get_balance("KRW") >= 5000:
                buy_all(coin)
            elif current_price > targetPrice and df['close'].iloc[-1] > df['UpperBand'].iloc[-1] and df['RSI'].iloc[-1] > df['Overbought'].iloc[-1] and upbit.get_balance(coin) * current_price >= 5000:
                sell_all(coin)

            if now.minute == 30:  # Send updates every 30 minutes
                current_balance = upbit.get_balance("KRW")
                update_message = {
                    "Current Price": current_price,
                    "Balance": current_balance,
                    "Best K": best_K,
                    "Target Price": targetPrice
                }
                post_message("Update:", update_message)

            time.sleep(1)

    except Exception as e:
        print(e)
        post_message(str(e))
        time.sleep(1)