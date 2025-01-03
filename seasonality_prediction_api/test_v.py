import requests
import json
from PIL import Image
import io
import base64

def test_forecast_and_visualize():
    # 1. First get the forecast
    forecast_data = {
        "data": {
            "dates": [
                "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05",
                "2024-01-02", "2024-01-07", "2024-01-08", "2024-01-09", "2024-01-10"
            ],
            "pre_prepared": [100.0, 102.0, 98.0, 103.0, 97.0, 95.0, 99.0, 101.0, 96.0, 98.0],
            "consumption": [95.0, 97.0, 94.0, 98.0, 93.0, 91.0, 95.0, 97.0, 92.0, 94.0]
        },
        "params": {
            "forecast_steps": 7,
            "sarima_order": [1, 1, 1],
            "seasonal_order": [1, 1, 1, 7]
        }
    }

    forecast_response = requests.post(
        "http://127.0.0.1:8000/forecast",
        json=forecast_data
    )
    
    if forecast_response.status_code != 200:
        print("Forecast Error:", forecast_response.text)
        return

    forecast_result = forecast_response.json()

    # 2. Then visualize the results
    visualization_data = {
        "historical_data": {
            "Pre_Prepared": forecast_data["data"]["pre_prepared"]
        },
        "forecast_dates": forecast_result["forecast_dates"],
        "original_forecast": forecast_result["original_forecast"],
        "optimized_forecast": forecast_result["optimized_forecast"],
        "confidence_intervals": forecast_result["confidence_intervals"]
    }

    # Get PNG image directly
    vis_response = requests.post(
        "http://127.0.0.1:8000/visualize",
        json=visualization_data
    )
    
    if vis_response.status_code == 200:
        # Save the PNG image
        with open("forecast_visualization.png", "wb") as f:
            f.write(vis_response.content)
        print("Visualization saved as 'forecast_visualization.png'")
    
    # Alternative: Get base64 encoded image
    vis_base64_response = requests.post(
        "http://127.0.0.1:8000/visualize/base64",
        json=visualization_data
    )
    
    if vis_base64_response.status_code == 200:
        result = vis_base64_response.json()
        # Save the image from base64
        image_data = base64.b64decode(result["image"])
        image = Image.open(io.BytesIO(image_data))
        image.save("forecast_visualization_base64.png")
        print("Base64 visualization saved as 'forecast_visualization_base64.png'")

if __name__ == "__main__":
    test_forecast_and_visualize()