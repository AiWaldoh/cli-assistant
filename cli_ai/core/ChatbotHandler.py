import os
import json
from core.ChatGPTBase import ChatGPTBase

SYSTEM_MESSAGE_CONTEXT = """
    You are a genius when it comes to understanding the context of a message.
    1. If the context of the message is telling you to execute a linux command, you will return that command in json format.
    2. If the context is not asking to execute a linux command, for example, asking for help regarding a command, respond as best possible.
    """


SYSTEM_MESSAGE_QA = """You Answer as a QA Chatbot"""


class ChatbotHandler:
    # init constructor below
    def __init__(self):
        self.chatbot = ChatGPTBase(os.getenv("OPENAI_API_KEY"))

    def answer_from_context(self, command):
        last_user_message = self.chatbot.history[-2]["content"]
        ai_response_json = json.loads(self.chatbot.history[-1]["content"])
        last_ai_reply = ai_response_json["result"]["reply"]
        context_string = f"""
            You are a genius at understanding context and you will answer the Human's question based on the following context:
            Question: {last_user_message} 
            Answer: {last_ai_reply}
            
            Answer this follow up question based on the previous interaction's context:
            Question:{command} 
            Answer:"""

        response = self.chatbot.ask_chatbot(
            prompt=context_string, system_message=SYSTEM_MESSAGE_QA, history=False
        )
        return response, True

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
            prompt=prompt_template,
            system_message=SYSTEM_MESSAGE_CONTEXT,
            original_command=command,
            history=True,
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
