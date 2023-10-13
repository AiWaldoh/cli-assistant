import os
import subprocess
import time
import json
from gpt.GPTQuery import GPTQuery

from dotenv import load_dotenv

load_dotenv()
gpt_query = GPTQuery()

class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'

def get_custom_prompt():
    username = os.getenv('USER') or os.getenv('USERNAME')
    pwd = os.getcwd()
    return f"{Color.CYAN}[{Color.GREEN}{username}{Color.END}@python-cli {Color.MAGENTA}{pwd}{Color.CYAN}]{Color.END}$ "

def run_command_streaming_output(command):
    print(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Stream output in real-time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    
    # Print any remaining output after the command finishes
    _, stderr = process.communicate()
    if stderr:
        print(f"{Color.RED}{stderr.strip()}{Color.END}")


def run_command_realtime(command):
    #confirm if this gets called at all
    print(f"Running command: {command}")
    process = subprocess.Popen(command, shell=True)
    process.communicate()

def run_command(command):
    print(f"Running command: {command}")  # <-- Add this

    """Run command and display output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(f"{Color.RED}{result.stderr.strip()}{Color.END}")

def enhanced_ls():
    try:
        # Capture the detailed output of 'ls -lah'
        result = subprocess.run("ls -lah", shell=True, capture_output=True, text=True)
        
        # Process each line
        for line in result.stdout.splitlines():
            # Split the line to extract filename; this assumes a standard 'ls -l' format
            parts = line.split()
            if len(parts) > 8:  # Ensure the line has enough parts to extract a filename
                filename = parts[-1]
                
                if line.startswith('d'):  # Directories
                    print(f"{Color.BLUE}{line}{Color.END}")
                elif filename.startswith('.'):  # Hidden files
                    print(f"{Color.CYAN}{line}{Color.END}")  # Using CYAN as a placeholder for a grey-ish color
                else:  # Regular files
                    print(f"{Color.WHITE}{line}{Color.END}")
    except Exception as e:
        print(f"{Color.RED}Error: {e}{Color.END}")


def check_openvpn_success(command):
    success_phrase = "Initialization Sequence Completed"
    timeout = 15
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    start_time = time.time()

    try:
        while time.time() - start_time < timeout:
            line = process.stdout.readline()
            if success_phrase in line:
                print(f"{Color.GREEN}openvpn connection successful{Color.END}")
                return
    except KeyboardInterrupt:
        pass

    print("Connection timed out after 15 seconds.")

def handle_cd_command(command_parts):
    if len(command_parts) > 1:
        path = command_parts[1]
    else:
        # Fetch the original user's home directory
        sudo_user = os.getenv('SUDO_USER')
        if sudo_user:
            path = os.path.expanduser(f"~{sudo_user}")
        else:
            path = os.getenv('HOME')
    try:
        os.chdir(path)
    except Exception as e:
        print(f"Error: {e}")

def execute(command):

    # Handle predefined commands first:
    if command.startswith(('mkdir', 'rm', 'touch', 'cp', 'mv')):
        run_command(command)
        return
    elif "ping" in command:
        run_command_streaming_output(command)
        return
    
    if command.strip() == 'ls':
        enhanced_ls()
        return
    
    elif command.split()[0] == "cd":
        handle_cd_command(command.split())
        return
    
    elif "apt-get" in command:
        run_command_realtime(command)
        return
    elif command.startswith("openvpn"):
        check_openvpn_success(command)
        return

    # If the command isn't predefined, pass it to the AI:
    response = gpt_query.get_response(command)
    # print(response)  # This is for debugging, can be removed later
    try:
        data = json.loads(response)
        if "command" in data:
            # Command from GPT's response
            process_command(data["command"])  # assuming process_command is the refactored function to handle commands (ls, cd, etc.)
        else:
            # Non-command response from GPT
            print(f"{Color.MAGENTA}{data['response']}{Color.END}")
    except json.JSONDecodeError:
        # Non-JSON response from GPT, treat as advice or answer
        print(f"{Color.MAGENTA}{response}{Color.END}")

def process_command(command):
    if command.startswith(('mkdir', 'rm', 'touch', 'cp', 'mv')):
        run_command(command)
    elif command.strip() == 'ls':
        enhanced_ls()
    elif command.split()[0] == "cd":
        handle_cd_command(command.split())
    elif command.startswith("openvpn"):
        check_openvpn_success(command)
    else:
        run_command(command)



def main():
    while True:
        try:

            command = input(get_custom_prompt())
            if command.lower() == 'exit':
                break
            execute(command)
        except KeyboardInterrupt:
            # Allow Ctrl+C to interrupt a command without exiting the application
            print("\nCommand interrupted by user.")
            continue

if __name__ == "__main__":
    main()
