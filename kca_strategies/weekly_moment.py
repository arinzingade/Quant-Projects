
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings

import warnings
warnings.filterwarnings("ignore")


start_date = '2024-04-01'
end_date = datetime.now().strftime('%Y-%m-%d')
capital = 100000
country_code = ".NS"
tp_pct = 0.15
sl_pct = -0.05
max_holding_period = 9
invested = capital / 6

stock_universe = list(pd.read_html('https://en.wikipedia.org/wiki/NIFTY_50')[1]['Symbol'])

valid_stock_array = []
for i in range(1, len(stock_universe)):
    stock_ticker = stock_universe[i] + country_code
    valid_stock_array.append(stock_ticker)

stock_list = ['ABB.NS', 'ACC.NS', 'AIAENG.NS', 'APLAPOLLO.NS', 'AUBANK.NS', 'AARTIIND.NS']
df = yf.download(valid_stock_array, start=start_date, end=end_date, interval = '1wk')

pct_df = pd.DataFrame()

for stock in valid_stock_array:
    close_array_0 = df['Close'][stock]
    close_array_1 = df['Close'][stock].shift(1)
    pct_change = (close_array_0 - close_array_1) / close_array_1
    
    pct_df[stock] = pct_change

max_date_stock_pct_array = []
for i in range(1, len(pct_df)):
    date_max = pct_df.index[i]
    
    max_pct_stock_array = np.max(pct_df.iloc[i])
    max_stock_symbol = pct_df.columns[pct_df.iloc[i].argmax()]

    if max_pct_stock_array > 0:
        max_date_stock_pct_array.append([date_max, max_pct_stock_array, max_stock_symbol])


profits = 0
losses = 0

pnl = 0
pnl_array = []
portfolio = [capital]
weeks_held = []
min_pct_for_zero = 0.9

for max_data in max_date_stock_pct_array:
    max_start_date = max_data[0]
    max_stock = max_data[2]

    # Get the start price on the max_start_date
    start_price = df.loc[max_start_date]['Close'][max_stock]
    holding_period = 0

    close = 0
    last_change = 0
    invested = capital / 6
    print("Analyzing: ", max_stock)
    print("Invested", invested)
    weekss = 0

    max_pct_reached = 0
    for week in range(1, max_holding_period + 1):
        current_date = max_start_date + pd.Timedelta(weeks = week)
        
        if current_date not in df.index:
            continue  

        current_price = df.loc[current_date]['Close'][max_stock]
        change = (current_price - start_price) / start_price

        print(current_date, current_price, change)
        if change >= tp_pct:
            pnl += invested * tp_pct
            capital += invested * tp_pct
            print(max_stock,start_date, current_date, pnl)
            print("Profit Taken")
            close = 1
            profits += 1
            break
        
        elif change <= sl_pct:
            pnl += invested * sl_pct
            capital += invested * sl_pct
            print(max_stock,start_date, current_date, pnl)
            print("Loss Taken")
            losses += 1
            close = 1
            break

        weekss += 1
        last_change = change
        max_pct_reached = max(change, max_pct_reached)
    
    if (close == 0):
        if last_change > 0: profits += 1
        else: losses += 1
        pnl += last_change * invested
        capital += invested * last_change
        print("Booked for days thresh")
    
    
    print("Max pct reached: ", max_pct_reached)
    pnl_array.append(pnl)
    portfolio.append(capital)
    weeks_held.append(weekss)

    print("Final PNL: ", pnl)
    print("----------------------------------------------------------------------------")

print('Final Capital' , capital)

df_nifty = (yf.download('^NSEI', start = start_date, end = end_date, interval='1wk')['Close'])
df_nifty["pct_change"] = df_nifty.pct_change()
pct_change_nifty = list(df_nifty['pct_change'])

scaled_nifty = [1]
for i in range(1, len(pct_change_nifty)):
    current_nifty = (1 + pct_change_nifty[i]) * scaled_nifty[i-1]
    scaled_nifty.append(current_nifty)

pct_change_portfolio = list(pd.Series(portfolio).pct_change())
scaled_portfolio = [1]
for i in range(1, len(pct_change_portfolio)):
    current_port = (1 + pct_change_portfolio[i]) * scaled_portfolio[i-1]
    scaled_portfolio.append(current_port)

plt.style.use("dark_background")
plt.plot(scaled_portfolio, color="yellow", label="KCA")  
plt.plot(scaled_nifty, color="green", label="NIFTY")
plt.title("PnL Curve", color="white")
plt.xlabel("Time", color="white")
plt.ylabel("PnL", color="white")
plt.legend()
plt.show()

print(weeks_held)
print(np.mean(weeks_held))

print("Min Stock:", max_date_stock_pct_array)
print("Max Stock:", max_date_stock_pct_array[len(max_date_stock_pct_array) - 1])