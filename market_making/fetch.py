from helpers import get_open_orders, fetch_positions
from time import sleep
import subprocess
import winsound
import pyttsx3

def cross_check():
    open_orders_account_1 = get_open_orders(1)
    open_orders_account_2 = get_open_orders(2)
    open_pos_account_1 = fetch_positions(1, 'BTCUSDT', 'OPEN')
    open_pos_account_2 = fetch_positions(2, 'BTCUSDT', 'OPEN')

    current_state = [open_orders_account_1, open_orders_account_2, open_pos_account_1, open_pos_account_2]

    print("Open Orders in Account 1:", open_orders_account_1)
    print("Open Orders in Account 2:", open_orders_account_2)
    print("---------------------------------------------------------")
    print("Open Positions in Account 1:", open_pos_account_1)
    print("Open Positions in Account 2:", open_pos_account_2)

    valid_states = [[2, 0, 0, 0], [2, 2, 1, 1]]
    if current_state not in valid_states:
        sleep(7)
        open_orders_account_1 = get_open_orders(1)
        open_orders_account_2 = get_open_orders(2)
        open_pos_account_1 = fetch_positions(1, 'BTCUSDT', 'OPEN')
        open_pos_account_2 = fetch_positions(2, 'BTCUSDT', 'OPEN')
        
        after_state = [open_orders_account_1, open_orders_account_2, open_pos_account_1, open_pos_account_2]

        if after_state not in valid_states:
            pyttsx3.speak("Positions are not Normal")
            for _ in range(3):  
                subprocess.run(["python", "close.py"], check=True)
                pyttsx3.speak("Closed all the Positions")
                
            subprocess.run(["python", "main.py"])
            pyttsx3.speak("Restarted the Process")
    
    else:
        print("Positions are Spruce!")
        print("---------------------------------------------------------")

if __name__ == "__main__":
    try:
        while True:
            cross_check()
            sleep(30)
    except KeyboardInterrupt:
        print("Exiting...")
