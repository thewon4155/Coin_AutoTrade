# Coin_AutoTrade

Coin AutoTrading program using Python


# 0. Project Abstract (2024.05.13 ~ 2024.06.12)

an AutoTrading program for designated Coin with multiple algorithms using Upbit and Slack

![image](https://github.com/thewon4155/Coin_AutoTrade/assets/99013724/5f655c9c-dd3b-4c68-b001-ddd732eb6a3b)

![image](https://github.com/thewon4155/Coin_AutoTrade/assets/99013724/76ac024e-2a08-466b-b7c1-0fea530e309a)



# 1. Version upgrades:

coin_autotrade_ver1: Default K for Volatility Strategy

coin_autotrade_ver2: adjustable K for Volatility Strategy

coin_autotrade_ver3: adjustable K, Bollinger Band, RSI Strategy applied

coin_autotrade_ver4: ver3 + comparison adjustments for pandas series using iloc (have same structure with ver3)

coin_autotrade_ver5: ver4 + more messages on Slack + DB for buy/sell signals using SQLite3


# 2. Software used:

Main Framework: Python

Open API: pyupbit, Slack, Google Sheets

Backtesting: Python, Excel

Server: Google Cloud Platform(GCP)

DB: SQLite3

Visualization: matplotlib, Django

Main Module: pyupbit, openpyxl, requests, pandas


# 3. Backtesting(20201112-20240528):

OHLCV sample data of 1300 days that are included in pyupbit applied to each version algorithm


# 4. Algorithm Functions:

알고리즘 정리
- 저장된 샘플 데이터로부터 최근의 High, Low, Open 값을 통해 최적의 K와 target_price 설정
- Bollinger Band를 통해 변동성에 의한 Upper Band, Lower Band 범위를 설정
- RSI 지수로 과매수(Overbought) / 과매도(Oversold) 수준을 결정

백테스팅
- 각 알고리즘 마다 1300일치의 OHLCV 값을 적용하여 분석
- DRR: 하루동안의 수익률
- CRR: 누적수익률
- DD: 손실률
- 세 가지 지표를 만들어 알고리즘의 적용 단계 해석

매수:
- Best K가 적용된 상태에서,
- Price < Lower Band,
- RSI = Oversold 라고 인식이 되어야 upbit에 매수 신호 전달 → Slack으로 잔액/체결량 등의 내용 전달

매도:
- Best K가 다시 적용된 상태에서(매수와 다를 수 있으므로),
- Price > Upper Band,
- RSI = Overbought 라고 인식이 되어야 upbit에 매도 신호 전달 → Slack에 잔액/수익률 등의 내용 전달


# 5. How it Works:

Message alerts from Slack
![스크린샷 2024-05-30 092344](https://github.com/thewon4155/Coin_AutoTrade/assets/99013724/8fae155a-ada9-4a49-8441-097dd58e6bf3)


# 6. GCP VM: SSH Connection
also needed to be created in a virtual environment + every function must be executed with sudo(admin execution).
SSH are made with Ubuntu and python version must be updated to 3.12.1 (given status-quo is python 3.11.2).

sudo python3 -m venv .venv
sudo -s
source .venv/bin/activate

python3.12 get-pip.py
upload 3 files of auth, coin_autotrade_ver5.py, requirements.txt

pip install -r requirements.txt                                 <- this will allow pip install pandas, requests, openpyxl, pyupbit, matplotlib
sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime       <- set local time to Korea
nohup python3.12 coin_autotrade_ver5. py                        <- Then, run the codes on the GCP server without interruption.


# 7. TroubleShooting / S.A.
https://turquoise-winter-de1.notion.site/5-407f257cf79f4e55b54b1c3c9fe03aa1?pvs=4
