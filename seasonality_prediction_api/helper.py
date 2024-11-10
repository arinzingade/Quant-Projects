import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from scipy.optimize import minimize

def optimize_pre_prepared(Date, Pre_Prepared, Leftover):
    # Convert Date to datetime and set as index
    df = pd.DataFrame({'Date': Date, 'Pre_Prepared': Pre_Prepared, 'Leftover': Leftover})
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d")
    df.set_index('Date', inplace=True)
    df.index.freq = 'D'  # Explicitly set the frequency to daily

    # Fit a SARIMA model to the 'Pre_Prepared' time series
    model = SARIMAX(df['Pre_Prepared'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
    results = model.fit(disp=False)

    # Forecast the next 10 periods
    forecast = results.get_forecast(steps=10)
    forecast_mean = forecast.predicted_mean

    # Define the objective function to minimize leftover
    def objective(x, data, forecast_mean):
        adjusted_pre_prepared = forecast_mean + x
        predicted_leftover = data['Pre_Prepared'] - adjusted_pre_prepared
        return sum(predicted_leftover**2)  # Minimize the sum of squared differences

    # Initial guess
    initial_guess = [0]

    # Use minimize to optimize the objective function
    result = minimize(objective, initial_guess, args=(df, forecast_mean))

    # Get the optimized prediction
    optimized_pre_prepared = forecast_mean + result.x
    forecast_conf_int = forecast.conf_int()

    return optimized_pre_prepared, forecast_conf_int

def plot_forecast_and_optimized(df, forecast_mean, optimized_pre_prepared, forecast_conf_int):
    # Plotting the observed data, SARIMA forecast, and optimized pre-prepared values
    plt.figure(figsize=(10, 6))
    df['Pre_Prepared'].plot(label='Observed', color='blue')
    forecast_mean.plot(label='SARIMA Forecast', color='red')
    plt.plot(forecast_mean.index, optimized_pre_prepared, label='Optimized Pre_Prepared', color='green')

    # Confidence intervals
    plt.fill_between(forecast_conf_int.index, forecast_conf_int.iloc[:, 0], forecast_conf_int.iloc[:, 1], color='gray', alpha=0.2)

    plt.legend()
    plt.title('SARIMA Forecast with Optimized Pre_Prepared')

    # Save plot to file and close
    plt.savefig('result.jpeg')
    plt.close()

