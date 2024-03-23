import subprocess
import time
import threading


class BaseCommandRunner:
    def __init__(self):
        pass

    # Method to run a generic command using subprocess.
    # Parameters:
    # - command: The shell command to run.
    # - stream: If True, prints the output in real-time.
    # - timeout: If set, terminates the command after the given number of seconds.
    # - process_line: An optional callback function to process each line of output.
    # - apt_get: If True, prints the output (useful for commands like apt-get).

    def run_generic_command(
        self, command, stream=False, timeout=None, process_line=None, apt_get=False
    ):
        # Start the command using subprocess.
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Record the starting time.
        start_time = time.time()
        # List to store output lines.
        lines = []
        is_done = False
        try:
            # Read the command's output line by line.
            while True:
                line = process.stdout.readline()
                # If there's no more output and the process has finished, break.
                if line == "" and process.poll() is not None:
                    break
                if line:
                    lines.append(line)
                    # If streaming or apt_get, print the line.
                    if stream or apt_get:
                        print(line.strip())
                    # If a line processing function is provided, call it.
                    if process_line:
                        process_line(line)

                # If the command exceeds the timeout, terminate it.
                if timeout and time.time() - start_time > timeout:
                    print(f"Command '{command}' terminated after {timeout} seconds.")
                    process.terminate()
                    break
        except KeyboardInterrupt:
            # Handle keyboard interrupts gracefully.
            pass

        # Wait for the command to complete and retrieve any remaining output.
        stdout, stderr = process.communicate()

        # If not streaming or apt_get, print the collected lines.
        if not (stream or apt_get):
            print("\n".join([line.strip() for line in lines]))

        # Print any errors from the command.
        if stderr:
            print(f"Error: {stderr.strip()}")

        # Return the full stdout and stderr.
        return stdout, stderr
