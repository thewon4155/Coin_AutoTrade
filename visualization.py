import pandas as pd
import matplotlib.pyplot as plt

# Load the backtesting results from the Excel file
df = pd.read_excel("crypto_history_with_best_K.xlsx")

# Plotting Cumulative Rate of Return (CRR)
plt.figure(figsize=(14, 7))
plt.plot(df['Unnamed: 0'], df['crr'], label='Cumulative Rate of Return (CRR)', color='blue')
plt.title('Cumulative Rate of Return (CRR) over Time')
plt.xlabel('Date')
plt.ylabel('CRR')
plt.legend()
plt.grid(True)
plt.show()

# Plotting Draw Down (DD)
plt.figure(figsize=(14, 7))
plt.plot(df['Unnamed: 0'], df['dd'], label='Draw Down (DD)', color='red')
plt.title('Draw Down (DD) over Time')
plt.xlabel('Date')
plt.ylabel('DD')
plt.legend()
plt.grid(True)
plt.show()

# Plotting Closing price along with Bollinger Bands
plt.figure(figsize=(14, 7))
plt.plot(df['Unnamed: 0'], df['close'], label='Closing Price', color='black')
plt.plot(df['Unnamed: 0'], df['UpperBand'], label='Upper Bollinger Band', color='green')
plt.plot(df['Unnamed: 0'], df['LowerBand'], label='Lower Bollinger Band', color='red')
plt.title('Closing Price with Bollinger Bands')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()

# Plotting RSI values over time
plt.figure(figsize=(14, 7))
plt.plot(df['Unnamed: 0'], df['RSI'], label='RSI', color='purple')
plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
plt.title('RSI over Time')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.legend()
plt.grid(True)
plt.show()

# Plotting DRR, CRR, and DD on the same chart
plt.figure(figsize=(14, 7))
plt.plot(df['Unnamed: 0'], df['drr'], label='Daily Rate of Return (DRR)', color='blue', alpha=0.5)
plt.plot(df['Unnamed: 0'], df['crr'], label='Cumulative Rate of Return (CRR)', color='green')
plt.plot(df['Unnamed: 0'], df['dd'], label='Draw Down (DD)', color='red')
plt.title('DRR, CRR, and DD over Time')
plt.xlabel('Date')
plt.ylabel('Values')
plt.legend()
plt.grid(True)
plt.show()
