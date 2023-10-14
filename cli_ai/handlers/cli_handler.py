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

        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

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


class CLIExecutor:
    def __init__(self, chatbot_handler):
        self.chatbot_handler = chatbot_handler

    def run_subprocess(self, command, stream=False):
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        if stream:
            for line in stdout.splitlines():
                print(line.strip())
        else:
            if stdout:
                print(stdout.strip())
            if stderr:
                print(f"{CLIView.Color.RED}{stderr.strip()}{CLIView.Color.END}")

    def handle_cd_command(self, target_dir):
        try:
            os.chdir(target_dir)
        except Exception as e:
            print(f"Error: {e}")

    def execute(
        self, command, from_ai=False
    ):  # Add a flag to indicate if the command comes from the AI
        if command.startswith(("mkdir", "rm", "touch", "cp", "mv", "ping", "apt-get")):
            print(command)
            self.run_subprocess(command)
        elif command.strip() == "ls":
            CLIView.enhanced_ls()
        elif command.split()[0] == "cd":
            target_dir = (
                command.split()[1] if len(command.split()) > 1 else os.getenv("HOME")
            )
            self.handle_cd_command(target_dir)
        elif command.startswith("ping"):
            CLIView.run_command_streaming_output(command)
        elif command.startswith("openvpn"):
            pass
        elif not from_ai:  # Only ask the AI if the command wasn't already from the AI
            response, is_command = self.chatbot_handler.ask_chatbot_for_command(command)

            if is_command:
                res = response["result"]
                self.execute(
                    res["reply"], from_ai=True
                )  # Set the flag to True when executing a command from the AI
            else:
                print(f"{CLIView.Color.MAGENTA}{response}{CLIView.Color.END}")
        else:
            # If the command comes from the AI and isn't explicitly handled, just execute it
            self.run_subprocess(command)
