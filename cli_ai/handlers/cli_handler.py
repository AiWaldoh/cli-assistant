import os
import subprocess


class CLIHandler:
    class Color:
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        MAGENTA = "\033[95m"
        CYAN = "\033[96m"
        WHITE = "\033[97m"
        END = "\033[0m"

    def __init__(self, chatbot_handler):
        self.chatbot_handler = chatbot_handler
        self.command_handlers = {
            "mkdir": self.run_subprocess,
            "rm": self.run_subprocess,
            "touch": self.run_subprocess,
            "cp": self.run_subprocess,
            "mv": self.run_subprocess,
            "ping": self.run_subprocess_with_stream,
            "apt-get": self.run_subprocess,
            "ls": self.enhanced_ls,
            "cd": self.handle_cd_command
            # ... add other commands and their handlers here
        }

    def get_custom_prompt(self):
        username = os.getenv("USER") or os.getenv("USERNAME")
        pwd = os.getcwd()
        return f"{self.Color.CYAN}[{self.Color.GREEN}{username}{self.Color.END}@python-cli {self.Color.MAGENTA}{pwd}{self.Color.CYAN}]{self.Color.END}$ "

    def run_subprocess(self, command):
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        if stdout:
            print(stdout.strip())
        if stderr:
            print(f"{self.Color.RED}{stderr.strip()}{self.Color.END}")

    def run_subprocess_with_stream(self, command):
        print(f"Running command: {command}")
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
            print(f"{self.Color.RED}{stderr.strip()}{self.Color.END}")

    def enhanced_ls(self, command=None):
        try:
            result = subprocess.run(
                "ls -lah", shell=True, capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) > 8:
                    filename = parts[-1]
                    if line.startswith("d"):
                        print(f"{self.Color.BLUE}{line}{self.Color.END}")
                    elif filename.startswith("."):
                        print(f"{self.Color.CYAN}{line}{self.Color.END}")
                    else:
                        print(f"{self.Color.WHITE}{line}{self.Color.END}")
        except Exception as e:
            print(f"{self.Color.RED}Error: {e}{self.Color.END}")

    def handle_cd_command(self, command):
        target_dir = (
            command.split()[1] if len(command.split()) > 1 else os.getenv("HOME")
        )
        try:
            os.chdir(target_dir)
        except Exception as e:
            print(f"Error: {e}")

    def execute(self, command):
        cmd_key = command.split()[0]
        handler = self.command_handlers.get(cmd_key)

        if handler:
            handler(command)
        elif cmd_key == "openvpn":
            pass
        else:
            response, is_command = self.chatbot_handler.ask_chatbot_for_command(command)
            if is_command:
                self.execute(response)
            else:
                print(f"{self.Color.MAGENTA}{response}{self.Color.END}")
