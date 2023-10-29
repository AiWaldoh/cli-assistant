import os
import json
from core.ChatGPTBase import ChatGPTBase

SYSTEM_MESSAGE_CONTEXT = """
    You are a genius when it comes to understanding the context of a message.
    1. If the context of the message is telling you to execute a linux command, you will return that command in json format.
    2. If the context is not asking to execute a linux command, for example, asking for help regarding a command, respond as best possible.
    """


SYSTEM_MESSAGE_QA = """You Answer as a QA Chatbot"""

import json


class ChatbotHandler:
    def __init__(self, api_key):
        self.chatbot = ChatGPTBase(api_key)
        self.initialize_functions()  # Initialize custom functions

    def initialize_functions(self):
        # Define the custom functions
        custom_functions = [
            {
                "name": "execute_command",
                "description": "Determine if the message is a command.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "User input command.",
                        }
                    },
                },
            }
        ]
        # Add them to the base chatbot
        for func in custom_functions:
            self.chatbot.add_custom_function(func)

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
            prompt=context_string,
            system_message=SYSTEM_MESSAGE_QA,
            history=True,
            original_command=command,
            memory_template="""{{"result": {{"message_type": "normal", "reply": "{}"}}}}""",
        )
        return response, True

    def answer_or_execute_command(self, command):
        response_message = self.chatbot.ask_chatbot(command, SYSTEM_MESSAGE_CONTEXT)

        # Check if a function call was invoked
        if response_message.get("function_call"):
            # This is the part where the command logic will go, as the function has been triggered
            # You can extract relevant information from response_message["function_call"]
            function_name = response_message["function_call"]["name"]
            if function_name == "execute_command":
                return response_message["function_call"], True
            else:
                return response_message["content"], False
        else:
            return response_message["content"], False
