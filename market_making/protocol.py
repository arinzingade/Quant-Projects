import subprocess
import platform
import time
import os
import signal

# List of Python scripts to run
scripts = [
    "close.py",
    "close.py",
    "web_socket_1.py",
    "web_socket_2.py",
    "regular_update_websockets.py",
    "main.py",
    "fetch.py"
]

# Store the subprocess.Popen objects for tracking
processes = []

def run_scripts_in_new_terminals(script_list):
    system = platform.system()  # Check the operating system
    for script in script_list:
        try:
            print(f"Launching {script} in a new terminal...")
            if system == "Windows":
                # Open new terminal and run script on Windows
                process = subprocess.Popen(["start", "cmd", "/k", f"python {script}"], shell=True)
            elif system == "Linux":
                # Open new terminal and run script on Linux
                process = subprocess.Popen(["gnome-terminal", "--", "python3", script])
            elif system == "Darwin":  # macOS
                # Open new terminal and run script on macOS
                process = subprocess.Popen(["open", "-a", "Terminal.app", f"python3 {script}"])
            else:
                print(f"Unsupported operating system: {system}")
                continue

            # Add the process to the list for later management
            processes.append(process)
        except Exception as e:
            print(f"Error while launching {script}: {e}")

def close_all_processes():
    """Terminates all running processes associated with the terminals."""
    print("Closing all processes...")
    for process in processes:
        try:
            # On Linux and macOS, we can simply terminate the process.
            if platform.system() in ["Linux", "Darwin"]:
                process.terminate()
            elif platform.system() == "Windows":
                # On Windows, we may need to send a specific signal to close cmd processes.
                os.system(f"taskkill /PID {process.pid} /F")
            print(f"Closed process {process.pid}")
        except Exception as e:
            print(f"Error while closing process {process.pid}: {e}")

def main():
    run_scripts_in_new_terminals(scripts)

if __name__ == "__main__":
    main()
