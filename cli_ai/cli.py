import os
from dotenv import load_dotenv
from cli_ai.core.chatbot import ChatbotHandler
from cli_ai.handlers.cli_handler import CLIHandler

load_dotenv()


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    SYSTEM_MESSAGE = """
    You are a genius when it comes to understanding the context of a question.
    If the context of the question is about running a linux command, you will return that command in json format.
    Example: 
    Question: run the ls command
    AI : {"command": "ls"}. 
    If the context is not asking to run a linux command, for example, asking for help regarding a command, respond as a CTF expert doing a penetration test without using json format.
    Example: 
    Question: what commands should I use to find the flag? 
    AI: you can run <command> to find the flag.
    """
    chatbot = ChatbotHandler(api_key, SYSTEM_MESSAGE)
    cli = CLIHandler(chatbot)
    while True:
        try:
            command = input(cli.get_custom_prompt())
            if command.lower() == "exit":
                break
            cli.execute(command)
        except KeyboardInterrupt:
            print("\nCommand interrupted by user.")
            continue


if __name__ == "__main__":
    main()
