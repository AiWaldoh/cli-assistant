import subprocess
import os
import time
from core.Color import Color
from core.BaseCommandRunner import BaseCommandRunner
from core.ChatbotHandler import ChatbotHandler
from core.OutputFormatter import OutputFormatter
import json
from core.SearchResult import SearchResult

# global registry hack for now
command_registry = {}


def register(command):
    def decorator(func):
        command_registry[command] = func
        return func

    return decorator


def contains_search_result(lst):
    # Check if lst is a list
    if not isinstance(lst, list):
        return False

    # Check if any item in the list is an instance of SearchResult
    return any(isinstance(item, SearchResult) for item in lst)


class CommandRunner(BaseCommandRunner):
    def __init__(self):
        super().__init__()
        self.whitelist = [
            "mkdir",
            "rmdir",
            "rm",
            "touch",
            "cp",
            "clear",
            "mv",
            "cat",
            "ls",
            "git",
            "git clone",
            "git add",
            "git commit",
            "git push",
            "git pull",
            "git status",
        ]  # Add commands you want to whitelist here.
        self.chatbot_handler = ChatbotHandler(
            os.getenv("OPENROUTER_API_KEY")
        )  # Initialize your ChatbotHandler here.

    def execute(self, command_input, is_from_ai=False):
        # uses the history (previous messages) to determine context
        if command_input.startswith("h "):
            response, new_is_from_ai = self.chatbot_handler.answer_from_context(
                command_input[2:]
            )
            # tmpres = response  # json.loads(response)["result"]["reply"]
            # print(tmpres)
            # json_tmpres = json.loads(tmpres)
            answer = response["content"]
            print(OutputFormatter.ai_response(answer))
            # self.execute(response, is_from_ai=new_is_from_ai)
            return

        # Skip AI check if the command is from AI or if it's a registered or whitelisted command
        if (
            is_from_ai
            or self.is_registered_command(command_input)
            or self.is_whitelisted_command(command_input)
        ):
            pass
        else:
            # If none of the above conditions are met, consult the AI
            response, is_command = self.chatbot_handler.answer_or_execute_command(
                command_input
            )

            if is_command:
                # print(response)
                # Extract the command from the AI's response and execute it.
                arguments = json.loads(response.arguments)

                # Extract the command from the deserialized arguments
                command_to_execute = arguments["command"]
                print(
                    f"Running command {command_to_execute}"
                )  # Print the command_to_execute)
                self.execute(
                    command_to_execute, is_from_ai=True
                )  # Recursively call with the new command
                return
            else:
                if contains_search_result(response):
                    for item in response:
                        print(OutputFormatter.url_link(item.url))
                        print(OutputFormatter.description(item.description))
                # Print AI's response if it's not a command
                else:
                    print(OutputFormatter.ai_response(response))
                return

        # Check against registered commands
        for command, func in command_registry.items():
            if command_input.startswith(command):
                func(self, command_input)
                return

        # Check for whitelisted commands
        if self.is_whitelisted_command(command_input):
            self.run_generic_command(command_input, stream=True, timeout=30)
            return

        # If neither registered nor whitelisted, run the generic command
        self.run_generic_command(command_input, stream=True, timeout=30)

    def is_registered_command(self, command_input):
        return any(command_input.startswith(cmd) for cmd in command_registry)

    def is_whitelisted_command(self, command_input):
        return any(command_input.startswith(cmd) for cmd in self.whitelist)

    @register("sudo openvpn")
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
                    print(OutputFormatter.get_colored_filename(line, filename))
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
