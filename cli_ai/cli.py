from core.OutputFormatter import OutputFormatter
from core.CommandRunner import CommandRunner
from dotenv import load_dotenv

load_dotenv()


def main():
    runner = CommandRunner()

    while True:
        try:
            command = input(OutputFormatter.get_custom_prompt())

            if command.lower() == "exit":
                break

            runner.execute(command)

        except KeyboardInterrupt:
            print("\nCommand interrupted by user.")
            continue


if __name__ == "__main__":
    main()
