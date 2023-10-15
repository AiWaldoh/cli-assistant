import os
import subprocess
import time
from cli_ai.handlers.cli_view import CLIView
from cli_ai.core.chatbot_handler import ChatbotHandler

import json


class CLIExecutor:
    def __init__(self, chatbot_handler: ChatbotHandler):
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
                print(f"{CLIView.Color.GREEN}{line.strip()}{CLIView.Color.END}")
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
                print(line)
                if success_phrase in line:
                    print(
                        f"{CLIView.Color.GREEN}openvpn connection successful{CLIView.Color.END}"
                    )
                    return
        except KeyboardInterrupt:
            pass

        print("Connection timed out after 15 seconds.")

    def execute(
        self, command, from_ai=False
    ):  # Add a flag to indicate if the command comes from the AI
        gpt_response = self.chatbot_handler.needs_context(command)
        print(f"""GPT response: {gpt_response["answer"]}""")
        is_haha = False
        if str(gpt_response["answer"]) == "yes":
            last_user_message = self.chatbot_handler.gpt_query.history[-2]["content"]
            is_haha = True
            # Parsing the AI's response to extract only the 'reply' key
            ai_response_json = json.loads(
                self.chatbot_handler.gpt_query.history[-1]["content"]
            )
            last_ai_reply = ai_response_json["result"]["reply"]

            # Formatting the message
            context_string = f"""
            You are a genius at understanding context and you will answer the Human's question based on the following context:
            Question: {last_user_message} 
            Answer: {last_ai_reply}
            
            Answer this follow up question based on the previous interaction's context:
            Question:{command} 
            Answer:"""

            print(f"New command: {context_string}")

        if command.startswith(("mkdir", "rm", "touch", "cp", "mv", "apt-get")):
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
            CLIView.run_ping_streaming_output(command)
        elif command.startswith("openvpn"):
            self.check_openvpn_success(command)
        elif not from_ai:  # Only ask the AI if the command wasn't already from the AI
            prompt_template = f"""
                    Given the following user cli input that is directed to a cli AI : {command} 
                    Determine if the message is giving directives for a command to be executed or asking for help regarding a command. If neither, respond with a helpful message.

                    Example command JSON response:
                    {{
                        "result": {{
                            "message_type": "command",
                            "explanation": "<explanation of what the command will do>"
                            "reply": "<linux command>"
                        }},
                    }}

                    Example question JSON response:
                    {{
                        "result": {{
                            "message_type": "normal",
                            "explanation": "<explanation of message>"
                            "reply": "<helpful response>"
                        }},
                    }}

                """

            if is_haha:
                print("is haha")
                response, is_command = self.chatbot_handler.ask_chatbot_for_command(
                    command,
                    "You Answer as a QA Chatbot",
                    prompt_template=context_string,
                )
            else:
                response, is_command = self.chatbot_handler.ask_chatbot_for_command(
                    command, prompt_template=prompt_template
                )

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
