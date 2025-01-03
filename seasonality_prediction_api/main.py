from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from scipy.optimize import minimize
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json
import io

import warnings
warnings.filterwarnings("ignore")


app = FastAPI(title="Time Series Forecasting API",
              description="API for time series forecasting and optimization of pre-prepared food quantities")

class TimeSeriesData(BaseModel):
    dates: List[str]
    pre_prepared: List[float]
    consumption: List[float]

class ForecastParams(BaseModel):
    forecast_steps: int = 10
    sarima_order: tuple = (1, 1, 1)
    seasonal_order: tuple = (1, 1, 1, 7)

class ForecastResponse(BaseModel):
    forecast_dates: List[str]
    original_forecast: List[float]
    optimized_forecast: List[float]
    confidence_intervals: List[Dict[str, float]]

def prepare_data(data: TimeSeriesData) -> pd.DataFrame:
    """Convert input data to pandas DataFrame with datetime index."""
    df = pd.DataFrame({
        'Date': pd.to_datetime(data.dates),
        'Pre_Prepared': data.pre_prepared,
        'Consumption': data.consumption
    })
    df.set_index('Date', inplace=True)
    return df

def optimize_forecast(data: pd.DataFrame, forecast_mean: pd.Series) -> float:
    """Optimize the forecast to minimize leftover."""
    def objective(x, data, forecast_mean):
        adjusted_pre_prepared = forecast_mean + x
        predicted_leftover = data['Pre_Prepared'] - adjusted_pre_prepared
        return np.sum(predicted_leftover**2)
    
    result = minimize(objective, [0], args=(data, forecast_mean))
    return result.x[0]

@app.post("/forecast", response_model=ForecastResponse)
async def create_forecast(data: TimeSeriesData, params: ForecastParams):
    try:
        # Prepare the data
        df = prepare_data(data)
        
        # Fit SARIMA model
        model = SARIMAX(
            df['Pre_Prepared'],
            order=params.sarima_order,
            seasonal_order=params.seasonal_order
        )
        results = model.fit(disp=False)
        
        # Generate forecast
        forecast = results.get_forecast(steps=params.forecast_steps)
        forecast_mean = forecast.predicted_mean
        forecast_conf = forecast.conf_int()
        
        # Optimize forecast
        optimization_adjustment = optimize_forecast(df, forecast_mean)
        optimized_forecast = forecast_mean + optimization_adjustment
        
        # Prepare response
        forecast_dates = [(df.index[-1] + timedelta(days=i+1)).strftime('%Y-%m-%d') 
                         for i in range(params.forecast_steps)]
        
        confidence_intervals = [
            {
                "lower": float(forecast_conf.iloc[i, 0]),
                "upper": float(forecast_conf.iloc[i, 1])
            }
            for i in range(len(forecast_conf))
        ]
        
        return ForecastResponse(
            forecast_dates=forecast_dates,
            original_forecast=forecast_mean.tolist(),
            optimized_forecast=optimized_forecast.tolist(),
            confidence_intervals=confidence_intervals
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class VisualizationRequest(BaseModel):
    historical_data: Dict[str, List[float]]  # Dictionary with dates and values
    forecast_dates: List[str]
    original_forecast: List[float]
    optimized_forecast: List[float]
    confidence_intervals: List[Dict[str, float]]

@app.post("/visualize")
async def create_visualization(data: VisualizationRequest):
    try:
        plt.figure(figsize=(12, 6))
        
        # Convert historical data to DataFrame
        historical_df = pd.DataFrame(data.historical_data)
        historical_dates = pd.to_datetime(historical_df.index)
        
        # Convert forecast dates to datetime
        forecast_dates = pd.to_datetime(data.forecast_dates)
        
        # Plot historical data
        plt.plot(historical_dates, historical_df['Pre_Prepared'], 
                label='Historical Data', color='blue', marker='o')
        
        # Plot forecasts
        plt.plot(forecast_dates, data.original_forecast, 
                label='SARIMA Forecast', color='red', linestyle='--', marker='s')
        plt.plot(forecast_dates, data.optimized_forecast, 
                label='Optimized Forecast', color='green', linestyle='--', marker='^')
        
        # Plot confidence intervals
        lower_bound = [ci['lower'] for ci in data.confidence_intervals]
        upper_bound = [ci['upper'] for ci in data.confidence_intervals]
        plt.fill_between(forecast_dates, lower_bound, upper_bound, 
                        color='gray', alpha=0.2, label='95% Confidence Interval')
        
        # Customize the plot
        plt.title('Time Series Forecast Visualization', pad=20, size=14)
        plt.xlabel('Date', size=12)
        plt.ylabel('Values', size=12)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best', fontsize=10)
        plt.xticks(rotation=45)
        
        # Add summary statistics
        stats_text = f"""
        Average Forecast: {np.mean(data.original_forecast):.2f}
        Average Optimized: {np.mean(data.optimized_forecast):.2f}
        Forecast Range: [{min(data.original_forecast):.2f}, {max(data.original_forecast):.2f}]
        """
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                bbox=dict(facecolor='white', alpha=0.8),
                verticalalignment='top', fontsize=8)
        
        plt.tight_layout()
        
        # Convert plot to PNG image
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        return Response(content=buffer.getvalue(), media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/example")
async def example_usage():
    """Return example usage of the API."""
    return {
        "example_request": {
            "data": {
                "dates": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "pre_prepared": [100.0, 102.0, 98.0],
                "consumption": [95.0, 97.0, 94.0]
            },
            "params": {
                "forecast_steps": 10,
                "sarima_order": [1, 1, 1],
                "seasonal_order": [1, 1, 1, 7]
            }
        },
        "endpoint": "/forecast",
        "method": "POST"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)