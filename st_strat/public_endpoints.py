
import requests
import json

def get_24hr_ticker_update(contract_pair):

    # Validate the input
    if not contract_pair:
        print("Invalid contract pair. Please enter a valid contract pair (e.g., btc, eth).")
        return

    # Construct the full URL for the API request using the provided contract pair
    full_url = f"https://api.pi42.com/v1/market/ticker24Hr/{contract_pair}"

    try:
        # Send the GET request to the API
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an error for HTTP 4xx/5xx responses

        # Parse the JSON response data
        response_data = response.json()

        return response_data
    except requests.exceptions.HTTPError as err:
        # Handle HTTP errors specifically
        print(f"Error: {err.response.text if err.response else err}")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {str(e)}")
    

def get_kline_data(pair, interval = "1m", limit = 1):
    try:
        # User inputs
        # Prepare the request body (JSON)
        params = {
            'pair': pair,
            'interval': interval,
            'limit': limit
        }

        # Headers for the POST request (no API key or signature required)
        headers = {
            'Content-Type': 'application/json'
        }

        # Construct the full URL for the Kline endpoint
        kline_url = "https://api.pi42.com/v1/market/klines"

        # Send the POST request to get Kline data
        response = requests.post(kline_url, json=params, headers=headers)
        response.raise_for_status() # Raises an error for 4xx/5xx responses
        response_data = response.json()
        
        return response_data

    except ValueError:
        print("Please enter valid inputs for pair, interval.")
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err.response.text if err.response else err}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

print(get_kline_data('BTCUSDT'))
