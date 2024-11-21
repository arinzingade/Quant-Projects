
import subprocess
from time import sleep

if __name__ == "__main__":
    while (True):
        subprocess.run("init.py", check = True)
        sleep(900)