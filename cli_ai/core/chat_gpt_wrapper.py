import openai

default_system_message = "You are a helpful assistant."


class ChatGPTWrapper:
    def __init__(self, api_key, system_message=default_system_message):
        openai.api_key = api_key
        self.history = []
        self.system_message = system_message

    def ask_chatbot(self, prompt, temperature=0):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        self.history.append({"role": "user", "content": prompt})
        self.history.append(
            {"role": "assistant", "content": response.choices[0].message["content"]}
        )

        return response.choices[0].message["content"]
