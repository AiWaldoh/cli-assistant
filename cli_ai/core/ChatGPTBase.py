import openai
import json
import os


import openai
import json


class ChatGPTBase:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key
        self.history = []
        self.custom_functions = []

    def add_custom_function(self, custom_function):
        self.custom_functions.append(custom_function)

    def ask_chatbot(
        self, prompt, system_message, temperature=0, use_function_call=True
    ):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=messages,
            temperature=temperature,
            functions=self.custom_functions if use_function_call else None,
            function_call="auto" if use_function_call else None,
        )

        return response.choices[0].message

        return response_message
