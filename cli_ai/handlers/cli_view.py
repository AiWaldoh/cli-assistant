import os
import subprocess
import time


class CLIView:
    class Color:
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        WHITE = "\033[97m"
        END = "\033[0m"

    @staticmethod
    def get_custom_prompt():
        username = os.getenv("USER") or os.getenv("USERNAME")
        pwd = os.getcwd()
        return f"{CLIView.Color.CYAN}[{CLIView.Color.GREEN}{username}{CLIView.Color.END}@python-cli {CLIView.Color.MAGENTA}{pwd}{CLIView.Color.CYAN}]{CLIView.Color.END}$ "

    @staticmethod
    def check_openvpn_success(command):
        command += " &"
        success_phrase = "Initialization Sequence Completed"
        timeout = 15
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        start_time = time.time()

        try:
            while time.time() - start_time < timeout:
                line = process.stdout.readline()
                if success_phrase in line:
                    print(
                        f"{CLIView.Color.GREEN}openvpn connection successful{CLIView.Color.END}"
                    )
                    return
        except KeyboardInterrupt:
            pass

        print("Connection timed out after 15 seconds.")

    @staticmethod
    def run_ping_streaming_output(command):
        print(f"Running ping command: {command}")
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        start_time = time.time()  # Record the start time

        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

            # Check if 5 seconds have passed
            if time.time() - start_time > 5:
                print(
                    f"{CLIView.Color.YELLOW}Ping command terminated after 5 seconds.{CLIView.Color.END}"
                )
                process.terminate()  # Terminate the ping command
                return

        # Print any remaining output after the command finishes
        _, stderr = process.communicate()
        if stderr:
            print(f"{CLIView.Color.RED}{stderr.strip()}{CLIView.Color.END}")

    @staticmethod
    def enhanced_ls():
        try:
            result = subprocess.run(
                "ls -lah", shell=True, capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) > 8:
                    filename = parts[-1]
                    if line.startswith("d"):
                        print(f"{CLIView.Color.BLUE}{line}{CLIView.Color.END}")
                    elif filename.startswith("."):
                        print(f"{CLIView.Color.CYAN}{line}{CLIView.Color.END}")
                    else:
                        print(f"{CLIView.Color.WHITE}{line}{CLIView.Color.END}")
        except Exception as e:
            print(f"{CLIView.Color.RED}Error: {e}{CLIView.Color.END}")
