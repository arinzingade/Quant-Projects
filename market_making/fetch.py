
from helpers import get_open_orders, fetch_positions
import os


if __name__ == "__main__":
    open_orders_account_1 = get_open_orders(1)
    open_orders_account_2 = get_open_orders(2)
    open_pos_account_1 = fetch_positions(1, 'BTCUSDT', 'OPEN')
    open_pos_account_2 = fetch_positions(2, 'BTCUSDT', 'OPEN')

    prev_state = [open_orders_account_1, open_orders_account_2, open_pos_account_1, open_pos_account_2]

    print("Open Orders in Account 1: ", open_orders_account_1)
    print("Open Orders in Account 2: ", open_orders_account_2)
    print("---------------------------------------------------------")
    print("Open Positions in Account 1:", open_pos_account_1)
    print("Open Positions in Account 2:", open_pos_account_2)

    if (prev_state == [2,0,0,0] or prev_state == [2,2,1,1] or prev_state == [0,0,0,0]):
        print("Positions are Spruce!")
    else:
        open_orders_account_1 = get_open_orders(1)
        open_orders_account_2 = get_open_orders(2)
        open_pos_account_1 = fetch_positions(1, 'BTCUSDT', 'OPEN')
        open_pos_account_2 = fetch_positions(2, 'BTCUSDT', 'OPEN')

        after_state = [open_orders_account_1, open_orders_account_2, open_pos_account_1, open_pos_account_2]

        if (after_state == [2,0,0,0] or after_state == [2,1,1,1] or after_state == [0,0,0,0]):
            pass
        else:    
            os.system('python close.py')
