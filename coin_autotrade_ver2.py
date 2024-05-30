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
                current_price = pyupbit.get_current_price(coin)
                if targetPrice <= current_price:
                    buy_all(coin)
                    time.sleep(1)  # Sleep for a short while to avoid spamming requests

                # Add more conditions or logic as needed
                time.sleep(1)  # Check every second within the minute

            time.sleep(1)

    except Exception as e:
        print(e)
        post_message(str(e))
        time.sleep(1)
