import pandas as pd
from stocktrends import Renko

def build_renko_with_stocktrends(df, box_size):
    df = df.copy()
    df.columns = [col.lower() for col in df.columns]  # Convert to lowercase

    renko = Renko(df)
    renko.brick_size = box_size
    renko_chart = renko.get_ohlc_data()
    return renko_chart
