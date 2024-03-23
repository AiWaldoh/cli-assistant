from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from core.OutputFormatter import OutputFormatter
from core.CommandRunner import CommandRunner
import os
from dotenv import load_dotenv
import nltk

# nltk.download("punkt")
load_dotenv()

# Define style for prompt_toolkit
style = Style.from_dict(
    {
        "username": "#44ff44",
        "at": "#ffffff",
        "colon": "#ffffff",
        "path": "#ff44ff",
        "pound": "#ffffff",
    }
)


def get_custom_prompt():
    username = os.getenv("USER") or os.getenv("USERNAME")
    pwd = os.getcwd()
    return [
        ("class:username", f"{username}"),
        ("class:at", "@"),
        ("class:colon", "python-cli "),
        ("class:path", f"{pwd}"),
        ("class:pound", "$ "),
    ]


def main():
    runner = CommandRunner()

    # Initialize prompt_toolkit session and autocompleter
    session = PromptSession()
    completer = WordCompleter(["exit"], ignore_case=True)

    while True:
        try:
            command = session.prompt(get_custom_prompt(), style=style)

            if command.lower() == "exit":
                break

            runner.execute(command)

        except KeyboardInterrupt:
            print("\nCommand interrupted by user.")
            continue


if __name__ == "__main__":
    main()
