
import threading
from generate_listen import update_listen_key_expiry

def call_functions():
    update_listen_key_expiry(1)
    #update_listen_key_expiry(2)

    threading.Timer(120, call_functions).start()

if __name__ == "__main__":
    call_functions()