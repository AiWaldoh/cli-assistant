import openai
import json


class ChatGPTBase:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.history = []

    def ask_chatbot(
        self,
        prompt,
        system_message,
        temperature=0,
        original_command=None,
        history=False,
        memory_template=None,
    ):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        # Save the AI's response
        res = response.choices[0].message["content"]
        if memory_template:
            res = json.dumps(res)
            res = memory_template.format(res[1:-1])
            # print(res)

        # print(response)
        if history:
            # Save the original command if provided
            if original_command:
                self.history.append({"role": "user", "content": original_command})

            self.history.append({"role": "assistant", "content": res})

        return res
