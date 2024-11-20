from helpers import get_open_orders, fetch_positions
from time import sleep
import subprocess
import winsound

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

    valid_states = [[2, 0, 0, 0], [2, 2, 1, 1], [0, 0, 0, 0]]
    if current_state not in valid_states:
        sleep(5)
        open_orders_account_1 = get_open_orders(1)
        open_orders_account_2 = get_open_orders(2)
        open_pos_account_1 = fetch_positions(1, 'BTCUSDT', 'OPEN')
        open_pos_account_2 = fetch_positions(2, 'BTCUSDT', 'OPEN')
        
        after_state = [open_orders_account_1, open_orders_account_2, open_pos_account_1, open_pos_account_2]

        if after_state not in valid_states:
            for _ in range(3):  
                subprocess.run(["python", "close.py"], check=True)
                frequency = 750
                duration = 300
                winsound.Beep(frequency, duration)
                winsound.Beep(frequency, duration)
                winsound.Beep(frequency, duration)
                winsound.Beep(frequency, duration)
                winsound.Beep(frequency, duration)
                            
            subprocess.run(["python", "main.py"])
    
    else:
        print("Positions are Spruce!")

if __name__ == "__main__":
    try:
        while True:
            cross_check()
            sleep(30)
    except KeyboardInterrupt:
        print("Exiting...")
