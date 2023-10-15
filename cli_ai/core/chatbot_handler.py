from cli_ai.core.chat_gpt_wrapper import ChatGPTWrapper
import json

SYSTEM_MESSAGE = """
    You are a genius when it comes to understanding the context of a message.
    1. If the context of the message is telling you to execute a linux command, you will return that command in json format.
    2. If the context is not asking to execute a linux command, for example, asking for help regarding a command, respond as best possible.
    """


class ChatbotHandler:
    def __init__(self, api_key):
        self.gpt_query = ChatGPTWrapper(api_key)
        self.qa_chatbot = ChatGPTWrapper(api_key)

    def get_history(self):
        return self.gpt_query.history

    def needs_context(self, user_message):
        decision_prompt = f"""Given the user message '{user_message}' from an ongoing conversation, does this message require the previous message from this conversation to be understood? You must answer in valid json.
        *Note: Remember that if message asking to execute a linux command, you must answer no.
        Example JSON reply: {{"answer:": ""<yes or no>"", "explanation": "<explanation of why>"}}"""

        # print(decision_prompt)
        decision_response = self.gpt_query.ask_chatbot(
            decision_prompt, SYSTEM_MESSAGE, temperature=0
        )
        # print(decision_response)
        return json.loads(decision_response)

    def ask_chatbot_for_command(
        self, command, system_prompt=SYSTEM_MESSAGE, prompt_template=""
    ):
        response = self.gpt_query.ask_chatbot(
            prompt_template,
            system_message=system_prompt,
            original_command=command,
            history=True,
        )
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
