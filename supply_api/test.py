import matplotlib.pyplot as plt
import numpy as np

input_dates = [
    "2023-10-01", "2023-10-02", "2023-10-03", "2023-10-04", "2023-10-05", "2023-10-06",
    "2023-10-07", "2023-10-08", "2023-10-09", "2023-10-10", "2023-10-11", "2023-10-12",
    "2023-10-13", "2023-10-14", "2023-10-15", "2023-10-16", "2023-10-17", "2023-10-18",
    "2023-10-19", "2023-10-20", "2023-10-21", "2023-10-22", "2023-10-23", "2023-10-24",
    "2023-10-25", "2023-10-26", "2023-10-27", "2023-10-28", "2023-10-29", "2023-10-30", "2023-10-31"
]

input_array = [
    150.0, 100.0, 120.0, 110.0, 90.0, 130.0, 160.0, 180.0, 90.0, 110.0, 100.0,
    120.0, 130.0, 140.0, 200.0, 110.0, 95.0, 105.0, 115.0, 125.0, 135.0, 190.0, 
    85.0, 95.0, 105.0, 115.0, 125.0, 150.0, 170.0, 100.0, 110.0
]

forecast_dates = [
    "2023-11-01", "2023-11-02", "2023-11-03", "2023-11-04", "2023-11-05",
    "2023-11-06", "2023-11-07", "2023-11-08", "2023-11-09", "2023-11-10"
]

original_forecast = [
    104.8835884987418, 111.89719872916908, 126.7534118892947, 150.61330810176787, 172.1813388889132,
    99.52627269112935, 109.85999115311992, 105.91378620970222, 110.42995712833384, 127.78393023485057
]
optimized_forecast = [
    104.8835884987418, 111.89719872916908, 126.7534118892947, 150.61330810176787, 172.1813388889132,
    99.52627269112935, 109.85999115311992, 105.91378620970222, 110.42995712833384, 127.78393023485057
]
confidence_intervals_lower = [
    76.67255265425788, 83.72332011558554, 98.54654337149564, 122.4450527391817, 144.0104106950896,
    71.35535796656927, 81.68907088131343, 71.47444788899388, 76.1335651679531, 93.45391316815719
]
confidence_intervals_upper = [
    133.09462434322572, 140.07107734275263, 154.96028040709376, 178.78156346435404, 200.35226708273677,
    127.69718741568943, 138.03091142492642, 140.35312453041058, 144.72634908871458, 162.11394730154396
]

# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the input array (actual data)
ax.plot(input_dates, input_array, label='Input Data', marker='o', color='red')

# Plot the original and optimized forecasts
ax.plot(forecast_dates, original_forecast, label='Original Forecast', marker='o', color='blue')
ax.plot(forecast_dates, optimized_forecast, label='Optimized Forecast', marker='o', color='green')

# Plot the confidence intervals
ax.fill_between(forecast_dates, confidence_intervals_lower, confidence_intervals_upper, 
                color='gray', alpha=0.3, label='Confidence Interval')

# Formatting the plot
ax.set_xlabel('Date')
ax.set_ylabel('Forecast / Input Value')
ax.set_title('Forecast vs Input Data with Confidence Intervals')
ax.legend(loc='upper left', fontsize=10)
ax.set_xticklabels(input_dates + forecast_dates, rotation=45)  # Combine the dates

# Display the plot
plt.tight_layout()
plt.show()
