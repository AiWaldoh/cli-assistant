import os
import json
from core.ChatGPTWrapper import ChatGPTWrapper

SYSTEM_MESSAGE = """
    You are a genius when it comes to understanding the context of a message.
    1. If the context of the message is telling you to execute a linux command, you will return that command in json format.
    2. If the context is not asking to execute a linux command, for example, asking for help regarding a command, respond as best possible.
    """


class ChatbotHandler:
    # init constructor below
    def __init__(self):
        self.chatbot = ChatGPTWrapper(os.getenv("OPENAI_API_KEY"))

    def answer_or_execute_command(self, command):
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

        response = self.chatbot.ask_chatbot(
            prompt=prompt_template, system_message=SYSTEM_MESSAGE, history=True
        )
        try:
            data = json.loads(response)
            print(data)
            res = data["result"]
            if res.get("message_type") == "command":
                return data, True
            else:
                return res["reply"], False
        except json.JSONDecodeError:
            return response, False
