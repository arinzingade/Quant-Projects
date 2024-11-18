
from helpers import close_all_positions, cancel_all_orders

if __name__ == "__main__":
    close_all_positions(1)
    cancel_all_orders(1)
    close_all_positions(2)
    cancel_all_orders(2)