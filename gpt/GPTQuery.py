from gpt.GPTBase import GPTBase


class GPTQuery(GPTBase):
    def __init__(self, system_prompt=f"""
        
You are a context analyzer. 
If the context is specifically asking to run a linux command, you will return that command in json format 
Example: if a user asks to run the ls command you will return : {{"command": "ls"}}. 

Otherwise, if the question is not about executing linux command, for example, asking for help regarding a command, respond as a CTF expert doing a penetration test without using json format.
Example: what commands should I use to find the flag? You will return: you can run <command> to find the flag.              
 """, available_tools=None):
        super().__init__(system_prompt=system_prompt)
        self.system_prompt = system_prompt
        self.available_tools = available_tools or []

    def get_response(self, question):

        prompt = f"""
        
{question}         
 """
        
        res = self.generate_message(prompt)
        # print(res)
        return res
