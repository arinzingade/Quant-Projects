
import requests
import json

def get_depth_update(contract_pair):
    if not contract_pair:
        print("Invalid contract pair. Please enter a valid contract pair (e.g., btc, eth).")
        return
    
    full_url = f"https://api.pi42.com/v1/market/depth/{contract_pair}"

    try:
        response = requests.get(full_url)
        response.raise_for_status()  
        response_data = response.json()

        print('Depth update fetched successfully:', json.dumps(response_data, indent=4))
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err.response.text if err.response else err}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def get_kline_data(pair, interval, limit_klines):
  try:
      # Prepare the request body (JSON)
      params = {
          'pair': pair,
          'interval': interval,
          'limit': limit_klines,
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
      print('Kline data fetched successfully:', json.dumps(response_data, indent=4))

  except ValueError:
      print("Please enter valid inputs for pair, interval.")
  except requests.exceptions.HTTPError as err:
      print(f"Error: {err.response.text if err.response else err}")
  except Exception as e:
      print(f"An unexpected error occurred: {str(e)}")




