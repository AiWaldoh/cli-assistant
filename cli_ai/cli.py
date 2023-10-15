import os
from dotenv import load_dotenv
from cli_ai.core.chatbot import ChatbotHandler
from cli_ai.handlers.cli_executor import CLIExecutor
from cli_ai.handlers.cli_view import CLIView

load_dotenv()


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    SYSTEM_MESSAGE = """
    You are a genius when it comes to understanding the context of a message.
    1. If the context of the message is telling you to execute a linux command, you will return that command in json format.
    2. If the context is not asking to execute a linux command, for example, asking for help regarding a command, respond as best possible.
    """
    chatbot = ChatbotHandler(api_key, SYSTEM_MESSAGE)
    cli_executor = CLIExecutor(
        chatbot
    )  # Instantiate the CLIExecutor with the chatbot handler
    while True:
        try:
            command = input(
                CLIView.get_custom_prompt()
            )  # Use the static method from CLIView
            if command.lower() == "exit":
                break
            cli_executor.execute(command)  # Use the execute method from CLIExecutor
        except KeyboardInterrupt:
            print("\nCommand interrupted by user.")
            continue


if __name__ == "__main__":
    main()
