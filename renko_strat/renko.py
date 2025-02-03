
import pandas as pd
import matplotlib.pyplot as plt

# Define the Renko transformation
class Renko:
    def __init__(self, atr_period=14):
        self.atr_period = atr_period  # Default ATR period
        self.renko_df = pd.DataFrame()

    def average_true_range(self, df):
        # Calculate True Range (TR)
        df['H-L'] = df['High'] - df['Low']
        df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
        
        # True Range is the maximum of these three values
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
        
        # Calculate the ATR over the rolling window
        df['ATR'] = df['TR'].rolling(window=self.atr_period).mean()
        
        return df

    def transform(self, df):
        # Calculate ATR first
        df = self.average_true_range(df)
        
        # Start Renko transformation using ATR as the brick size
        renko_bricks = []
        previous_close = df['Close'].iloc[0]
        for i, close in enumerate(df['Close']):
            brick_size = df['ATR'].iloc[i]  # Use ATR as the brick size for each period
            while abs(close - previous_close) >= brick_size:
                if close > previous_close:
                    renko_bricks.append({'Brick_Color': 'Green', 'Price': previous_close + brick_size})
                    previous_close += brick_size
                else:
                    renko_bricks.append({'Brick_Color': 'Red', 'Price': previous_close - brick_size})
                    previous_close -= brick_size
        
        self.renko_df = pd.DataFrame(renko_bricks)