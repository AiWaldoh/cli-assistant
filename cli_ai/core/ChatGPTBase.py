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
        self,
        prompt,
        system_message,
        temperature=0,
        use_function_call=True,
        history=False,
        original_command=None,
        memory_template=None,
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

        res = None
        # print(response)
        # Check if a function call was invoked. Only use this for history. return response_message and
        if response.choices[0].message.get("function_call"):
            res = response.choices[0].message.get("function_call")
        else:
            res = response.choices[0].message["content"]
        # print(res)
        # History management
        # Apply memory template if provided
        if memory_template and isinstance(res, str):
            res = memory_template.format(res)

        # Handle history management
        if history:
            # Use the original command if provided, else use the prompt
            self.history.append(
                {
                    "role": "user",
                    "content": original_command if original_command else prompt,
                }
            )
            self.history.append({"role": "assistant", "content": res})
        return response.choices[0].message

        return response_message
