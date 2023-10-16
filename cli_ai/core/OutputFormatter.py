from core.Color import Color
import os


class OutputFormatter:
    def __init__(self):
        pass

    @staticmethod
    def error(text):
        return f"{Color.RED}{text}{Color.END}"

    @staticmethod
    def success(text):
        return f"{Color.GREEN}{text}{Color.END}"

    @staticmethod
    def ai_response(text):
        return f"{Color.MAGENTA}{text}{Color.END}"

    def get_custom_prompt():
        username = os.getenv("USER") or os.getenv("USERNAME")
        pwd = os.getcwd()
        return f"{Color.CYAN}[{Color.GREEN}{username}{Color.END}@python-cli {Color.MAGENTA}{pwd}{Color.CYAN}]{Color.END}$ "
