import subprocess
import os
import time
from core.Color import Color
from core.BaseCommandRunner import BaseCommandRunner

# global registry hack for now
command_registry = {}


def register(command):
    def decorator(func):
        command_registry[command] = func
        return func

    return decorator


class CommandRunner(BaseCommandRunner):
    def __init__(self):
        super().__init__()

    def execute(self, command_input):
        # First, try to find the command in the registry.
        for command, func in command_registry.items():
            if command_input.startswith(command):
                func(self, command_input)
                return  # Return early if the command is found and executed.

        # If no registered command matches, run the generic command.
        try:
            self.run_generic_command(command_input, stream=True, timeout=15)
        except KeyboardInterrupt:
            return
        except Exception as e:
            print(f"Error occurred: {e}")

    def get_colored_filename(self, line, filename):
        """Return the filename with appropriate color based on its properties."""
        if line.startswith("d"):
            return f"{Color.BLUE}{line}{Color.END}"
        elif filename.startswith("."):
            return f"{Color.CYAN}{line}{Color.END}"
        else:
            return f"{Color.WHITE}{line}{Color.END}"

    @register("openvpn")
    def run_openvpn_connect(self, command):
        success_detected = self.check_openvpn_success(command)
        if not success_detected:
            print("Connection timed out after 15 seconds.")

    def check_openvpn_success(self, command):
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
                    print(f"{Color.GREEN}openvpn connection successful{Color.END}")
                    return True
        except KeyboardInterrupt:
            pass

        return False

    @register("ping")
    def run_ping_streaming_output(self, command):
        print(f"Running ping command: {command}")
        _, stderr = self.run_generic_command(command, stream=True, timeout=5)

        if stderr:
            print(stderr.strip())

    @register("ls")
    def run_enhanced_ls(self, _=None):  # _ parameter is just a placeholder
        try:
            result = subprocess.run(
                "ls -lah", shell=True, capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) > 8:
                    filename = parts[-1]
                    print(self.get_colored_filename(line, filename))
        except Exception as e:
            print(f"{Color.RED}Error: {e}{Color.END}")

    @register("cd")
    def run_cd_command(self, command=None):
        target_dir = (
            command.split()[1] if len(command.split()) > 1 else os.getenv("HOME")
        )
        try:
            os.chdir(target_dir)
        except Exception as e:
            print(f"Error: {e}")

    @register("apt-get")
    def run_apt_get(self, command, stream=True):
        if not command.startswith("apt-get"):
            raise ValueError("This function is designed for apt-get commands only!")

        stdout, stderr = self.run_generic_command(command, apt_get=True, stream=stream)
        # Further processing can be added here if needed.
        return stdout, stderr
