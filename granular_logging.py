import pyupbit
import datetime
import time
import auth
import numpy as np
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def post_message(text):
    try:
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": "Bearer " + auth.myToken},
            data={"channel": auth.channel, "text": text}
        )
        response_data = response.json()
        if not response_data.get("ok"):
            logging.error(f"Error posting message to Slack: {response_data['error']}")
    except Exception as e:
        logging.exception("Exception posting message to Slack: %s", e)

def get_target_price(df, best_K):
    """Calculate the target price using high-low range and best_K"""
    range = df['high'][-2] - df['low'][-2]
    target_price = df['close'][-2] + (range * best_K)
    return target_price

def bollinger_bands(df):
    """Calculate Bollinger Bands"""
    df['MiddleBand'] = df['close'].rolling(window=20).mean()
    df['UpperBand'] = df['MiddleBand'] + 2 * df['close'].rolling(window=20).std()
    df['LowerBand'] = df['MiddleBand'] - 2 * df['close'].rolling(window=20).std()
    return df

def RSI(df, period=14):
    """Calculate RSI"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    RS = gain / loss
    df['RSI'] = 100 - (100 / (1 + RS))
    return df

def buy_all(coin):
    """Buy all available KRW balance of the coin"""
    logging.info("Attempting to buy coin: %s", coin)
    balance = upbit.get_balance("KRW") * 0.9995
    if balance >= 5000:
        logging.info("Buying coin: %s with balance: %s KRW", coin, balance)
        try:
            response = upbit.buy_market_order(coin, balance)
            logging.info(f"Buy response: {response}")
            post_message(f"매수 체결.\n체결 단가: {pyupbit.get_current_price(coin)} 원")
        except Exception as e:
            logging.exception("Exception during buy order: %s", e)
            post_message(f"매수 에러: {e}")
    else:
        logging.info("Insufficient balance to buy")

def sell_all(coin):
    """Sell all available balance of the coin"""
    logging.info("Attempting to sell coin: %s", coin)
    balance = upbit.get_balance(coin)
    if balance * pyupbit.get_current_price(coin) >= 5000:
        logging.info("Selling coin: %s with balance: %s", coin, balance)
        try:
            response = upbit.sell_market_order(coin, balance)
            logging.info(f"Sell response: {response}")
            post_message(f"매도 체결.\n체결 단가: {pyupbit.get_current_price(coin)} 원")
        except Exception as e:
            logging.exception("Exception during sell order: %s", e)
            post_message(f"매도 에러: {e}")
    else:
        logging.info("Insufficient balance to sell")

# Main trading logic
if __name__ == '__main__':
    try:
        upbit = pyupbit.Upbit(auth.access, auth.secret)

        coin = "KRW-BTC"
        fees = 0.0005
        best_K = 0.4  # Adjusted K value

        start_balance = upbit.get_balance("KRW")
        df = pyupbit.get_ohlcv(coin, count=2, interval="minute1")
        target_price = get_target_price(df, best_K)
        logging.info(f"Start trading: Balance: {start_balance} KRW, New targetPrice: {target_price} KRW, Best K: {best_K}")
        post_message(f"자동매매를 시작합니다.\n잔액: {start_balance} 원\n목표매수가: {target_price} 원\nBest K: {best_K}")

        while True:
            now = datetime.datetime.now()

            if now.hour == 11 and now.minute == 55:
                sell_all(coin)
                time.sleep(10)

                df = pyupbit.get_ohlcv(coin, count=2, interval="minute1")
                target_price = get_target_price(df, best_K)

                cur_balance = upbit.get_balance("KRW")
                logging.info(f"New day: Balance: {cur_balance} KRW, Yield: {((cur_balance / start_balance) - 1) * 100} %, New targetPrice: {target_price} KRW, Best K: {best_K}")
                post_message(f"새로운 장 시작\n수익률: {((cur_balance / start_balance) - 1) * 100} %\n잔액: {cur_balance} 원\n목표매수가: {target_price} 원\nBest K: {best_K}")
                time.sleep(60)

            df = pyupbit.get_ohlcv(coin, interval="minute1", count=30)
            df = bollinger_bands(df)
            df = RSI(df)
            current_price = pyupbit.get_current_price(coin)

            logging.info(f"Current Price: {current_price}, Target Price: {target_price}, Best K: {best_K}")
            logging.info(f"Lower Band: {df['LowerBand'].iloc[-1]}, Upper Band: {df['UpperBand'].iloc[-1]}")
            logging.info(f"RSI: {df['RSI'].iloc[-1]}")
            logging.info(f"Balance (KRW): {upbit.get_balance('KRW')}, Balance (Coin): {upbit.get_balance(coin)}")

            # Conditions for buy
            if (current_price < target_price and 
                df['close'].iloc[-1] < df['LowerBand'].iloc[-1] and 
                df['RSI'].iloc[-1] < 30 and 
                upbit.get_balance("KRW") >= 5000):
                logging.info("Buying signal detected. Executing buy order.")
                buy_all(coin)
                time.sleep(1)

            # Conditions for sell
            if (current_price > target_price and 
                df['close'].iloc[-1] > df['UpperBand'].iloc[-1] and 
                df['RSI'].iloc[-1] > 70 and 
                upbit.get_balance(coin) * current_price >= 5000):
                logging.info("Selling signal detected. Executing sell order.")
                sell_all(coin)
                time.sleep(1)

            time.sleep(1)

    except Exception as e:
        logging.exception("Exception occurred: %s", e)
        post_message(str(e))
        time.sleep(1)
