from cli_ai.core.chat_gpt_wrapper import ChatGPTWrapper
import json


class ChatbotHandler:
    def __init__(self, api_key, system_message):
        self.gpt_query = ChatGPTWrapper(api_key, system_message=system_message)

    def ask_chatbot_for_command(self, command):
        response = self.gpt_query.ask_chatbot(command, temperature=0)
        try:
            data = json.loads(response)
            if "command" in data:
                return data["command"], True
            else:
                return data["response"], False
        except json.JSONDecodeError:
            return response, False
