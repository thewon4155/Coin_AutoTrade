import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Load the backtesting results from the Excel file
df = pd.read_excel("crypto_history_with_best_K.xlsx")

# Set the correct column as the index for date
df.set_index('Unnamed: 0', inplace=True)
df.index = pd.to_datetime(df.index)

# Define the date range for the x-axis and convert to datetime
start_date = pd.to_datetime('2020-11-18')
end_date = pd.to_datetime('2024-06-03')

# Plotting Cumulative Rate of Return (CRR)
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['crr'], label='Cumulative Rate of Return (CRR)', color='blue')
plt.title('Cumulative Rate of Return (CRR) over Time')
plt.xlabel('Date')
plt.ylabel('CRR')
plt.legend()
plt.grid(True)
plt.xlim([start_date, end_date])
plt.show()

# Plotting Draw Down (DD)
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['dd'], label='Draw Down (DD)', color='red')
plt.title('Draw Down (DD) over Time')
plt.xlabel('Date')
plt.ylabel('DD')
plt.legend()
plt.grid(True)
plt.xlim([start_date, end_date])
plt.show()

# Plotting Closing price along with Bollinger Bands
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['close'], label='Closing Price', color='black')
plt.plot(df.index, df['UpperBand'], label='Upper Bollinger Band', color='green')
plt.plot(df.index, df['LowerBand'], label='Lower Bollinger Band', color='red')
plt.title('Closing Price with Bollinger Bands')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.xlim([start_date, end_date])
plt.show()

# Plotting RSI values over time
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['RSI'], label='RSI', color='purple')
plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
plt.title('RSI over Time')
plt.xlabel('Date')
plt.ylabel('RSI')
plt.legend()
plt.grid(True)
plt.xlim([start_date, end_date])
plt.show()

# Plotting DRR, CRR, and DD on the same chart with percentage
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['drr'] * 100, label='Daily Rate of Return (DRR)', color='blue', alpha=0.5)
plt.plot(df.index, df['crr'] * 100, label='Cumulative Rate of Return (CRR)', color='green')
plt.plot(df.index, df['dd'] * 100, label='Draw Down (DD)', color='red')
plt.title('DRR, CRR, and DD over Time')
plt.xlabel('Date')
plt.ylabel('Values (%)')
plt.legend()
plt.grid(True)
plt.xlim([start_date, end_date])
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter())
plt.show()
