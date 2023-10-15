from cli_ai.core.chat_gpt_wrapper import ChatGPTWrapper
import json


class ChatbotHandler:
    def __init__(self, api_key, system_message):
        self.gpt_query = ChatGPTWrapper(api_key, system_message=system_message)

    def ask_chatbot_for_command(self, command):
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
        response = self.gpt_query.ask_chatbot(prompt_template)
        # print(response)
        try:
            data = json.loads(response)
            # print(data)
            res = data["result"]
            if res.get("message_type") == "command":
                return data, True
            else:
                return res["reply"], False
        except json.JSONDecodeError:
            return response, False
