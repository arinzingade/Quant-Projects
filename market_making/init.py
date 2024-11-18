
import subprocess
import platform

# List of Python scripts to run
scripts = [
    "web_socket_1.py",
    "web_socket_2.py",
    "regular_update_websockets.py",
    "main.py"
]

def run_scripts_in_new_terminals(script_list):
    system = platform.system()  # Check the operating system
    for script in script_list:
        try:
            print(f"Launching {script} in a new terminal...")
            if system == "Windows":
                # Open new terminal and run script on Windows
                subprocess.Popen(["start", "cmd", "/k", f"python {script}"], shell=True)
            elif system == "Linux":
                # Open new terminal and run script on Linux
                subprocess.Popen(["gnome-terminal", "--", "python3", script])
            elif system == "Darwin":  # macOS
                # Open new terminal and run script on macOS
                subprocess.Popen(["open", "-a", "Terminal.app", f"python3 {script}"])
            else:
                print(f"Unsupported operating system: {system}")
        except Exception as e:
            print(f"Error while launching {script}: {e}")

if __name__ == "__main__":
    run_scripts_in_new_terminals(scripts)
