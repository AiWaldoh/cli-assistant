from gpt.GPTBase import GPTBase


class GPTQuery(GPTBase):
    def __init__(self, system_prompt=f"""
        
You are a genius when it comes to understanding the context of a question.
If the context of the question is about executing a linux command, you will return that command in json format.
                 
Example: 
                 Question: run the ls command you
                 AI : {{"command": "ls"}}. 

If the context is not asking to execute a linux command, for example, asking for help regarding a command, respond as a CTF expert doing a penetration test without using json format.
Example: 
                 Question: what commands should I use to find the flag? 
                 AI: you can run <command> to find the flag.              
 """, available_tools=None):
        super().__init__(system_prompt=system_prompt)
        self.system_prompt = system_prompt
        self.available_tools = available_tools or []

    def get_response(self, question):

        prompt = f"""Question: {question}
Answer: """
        
        res = self.generate_message(prompt)
        # print(res)
        return res
