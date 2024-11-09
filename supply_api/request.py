import requests
import json

def test_api():
    # Test health endpoint
    health_response = requests.get("http://127.0.0.1:8000/health")
    print("Health check response:", health_response.json())

    # Test forecast endpoint
    forecast_data = {
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
    }

    forecast_response = requests.post(
        "http://127.0.0.1:8000/forecast",
        json=forecast_data
    )
    
    print("\nForecast response:", json.dumps(forecast_response.json(), indent=2))

if __name__ == "__main__":
    test_api()