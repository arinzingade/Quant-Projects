import numpy as np
import pandas as pd
import warnings
from tqdm import tqdm
from untrade.client import Client
import ta
from ta.trend import ADXIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands
import uuid
import os
warnings.filterwarnings("ignore")
def calculate_supertrend(data, atr_period=14, multiplier=1.5):
    """
    Calculates the Supertrend indicator.
    """
    data['atr'] = data['High'].rolling(window=atr_period).max() - data['Low'].rolling(window=atr_period).min()
    data['basic_upper_band'] = (data['High'] + data['Low']) / 2 + multiplier * data['atr']
    data['basic_lower_band'] = (data['High'] + data['Low']) / 2 - multiplier * data['atr']

    # Initialize Supertrend
    data['final_upper_band'] = data['basic_upper_band']
    data['final_lower_band'] = data['basic_lower_band']
    data['supertrend'] = 0

    for i in range(1, len(data)):
        if data['Close'][i - 1] > data['final_upper_band'][i - 1]:
            data['final_upper_band'][i] = min(data['basic_upper_band'][i], data['final_upper_band'][i - 1])
        if data['Close'][i - 1] < data['final_lower_band'][i - 1]:
            data['final_lower_band'][i] = max(data['basic_lower_band'][i], data['final_lower_band'][i - 1])

        if data['Close'][i] > data['final_upper_band'][i - 1]:
            data['supertrend'][i] = data['final_lower_band'][i]
        else:
            data['supertrend'][i] = data['final_upper_band'][i]

    # Create Supertrend signal (True for uptrend)
    data['supertrend_signal'] = data['Close'] > data['supertrend']
    return data
def calculate_entropy(series, window=14):
    """
    Calculate the Shannon entropy of a given volume series in a rolling window.
    """
    # Bin the data into 10 discrete values
    hist, bin_edges = np.histogram(series, bins=10, density=True)
    hist = hist[hist > 0]  # Remove zero values to avoid log(0)
    # Calculate the Shannon entropy
    entropy = -np.sum(hist * np.log2(hist))
    return entropy

# Function to calculate entropy and add it as a new column to a CSV
def add_entropy_to_csv(df, window=30):
    # Check if the necessary columns are in the dataframe (OHLC + volume)
    if 'log_returns' not in df.columns:
        raise ValueError("CSV file must contain a 'volume' column.")
    
    # Apply entropy calculation in a rolling window
    df['log_returns_entropy'] = df['log_returns'].rolling(window=window).apply(lambda x: calculate_entropy(x, window), raw=False)
    return df
  # Replace with your actual CSV file path

def calculate_dema(df, column='Close', window=20):
    # Calculate the first EMA
    ema1 = df[column].ewm(span=window, adjust=False).mean()
    # Calculate the second EMA on the first EMA
    ema2 = ema1.ewm(span=window, adjust=False).mean()
    # Calculate DEMA
    df['DEMA'] = 2 * ema1 - ema2
    return df
