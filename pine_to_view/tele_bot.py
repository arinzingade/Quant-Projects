import requests
from dotenv import load_dotenv
import os


class TelegramBot:

    def __init__(self, symbol, side):
        self.symbol = symbol
        self.side = side
        self.execution_flow()

    def send_telegram_message(self, chat_id, message):
        
        load_dotenv()  
        bot_token = os.getenv("BOT_TOKEN")
        
        if not bot_token:
            raise ValueError("BOT_TOKEN is not set in the environment variables.")
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        
        response = requests.post(url, json=payload)
        return response.json()


    def make_message_for_signal(self, symbol, side):
        message = f"Signal Alert: {symbol} - {side}"

        return message
    
    def execution_flow(self):
        message = self.make_message_for_signal(self.symbol, self.side)
        print(self.send_telegram_message(os.getenv("CHAT_ID"), message))



