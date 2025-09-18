import subprocess
import time
import shlex
import re
from dataclasses import dataclass
import json


@dataclass
class Curl:
    """Represents a single cURL command with its URL, full command string, and response output."""
    url: str
    curl: str
    response: str = ""
    error: str = ""

class MultiCurl:
    """Manages multiple cURL commands, allowing parsing, filtering, and execution with delays."""
    def __init__(self, curl_commands_string: str):
        """
        Initialize MultiCurl by parsing a string of cURL commands.
        
        Args:
            curl_commands_string (str): A string containing multiple cURL commands separated by 'curl '.
        """
        # Parse the curl_commands_string into a list of Curl instances
        command_tails = [cmd.strip().rstrip(';') for cmd in curl_commands_string.split('curl ') if cmd.strip()]
        self.curls = []
        for tail in command_tails:
            full_command = "curl " + tail
            # Extract URL: find the first non-option argument after 'curl'
            command_list = shlex.split(full_command)
            url = ""
            for arg in command_list[1:]:
                if not arg.startswith('-'):
                    url = arg
                    break
            self.curls.append(Curl(url=url, curl=full_command))
        
        self.curls_to_run = None
        self.has_run = False
    
    def run(self, delay: float = 0, url_filter: str = None):
        """
        Execute the cURL commands with optional filtering and delay.
        
        Args:
            delay (float): Seconds to wait between each command execution. Defaults to 0.
            url_filter (str): Substring to filter URLs. Only matching commands are run. Defaults to None.
        
        Returns:
            list[Curl]: List of Curl instances that were executed, with their responses populated.
        """
        # Filter curls if url_filter is provided
        if url_filter:
            self.curls_to_run = [curl for curl in self.curls if url_filter in curl.url]
        else:
            self.curls_to_run = self.curls
        
        if not self.curls_to_run:
            print("No cURL commands match the filter or found.")
            return self.curls_to_run
        
        print(f"Running {len(self.curls_to_run)} commands (out of {len(self.curls)}) with delay {delay}s.")
        
        for i, curl in enumerate(self.curls_to_run):
            print(f"[{i+1}/{len(self.curls_to_run)}] Running: {curl.url}")
            # Run the command and capture output
            result = subprocess.run(
                shlex.split(curl.curl),
                capture_output=True,
                text=True
            )
            curl.response = result.stdout
            curl.error = result.stderr.strip() if result.stderr else ""
            if result.returncode != 0:
                print(f"Error running command: {curl.error}")
            else:
                print(f"Response length: {len(curl.response)}, text: {curl.response[:100]}")
            time.sleep(delay)
        
        print("All matching commands executed.")
        self.has_run = True
        return self.curls_to_run
    
    def combined_json_by_key(self, key):
        if not self.has_run or self.curls_to_run is None:
            print("Curls have not yet run.")
            return None
        merged_list = []
        for curl_obj in self.curls_to_run:
            try:
                data = json.loads(curl_obj.response)
                if key in data and isinstance(data[key], list):
                    merged_list.extend(data[key])
            except Exception as e:
                print(f"Error parsing response: {e}")
        # Return the full JSON string with the key
        return json.dumps({key: merged_list})


# --- Script Logic (No need to edit below) ---

if __name__ == "__main__":
    multi_curl = MultiCurl(curl_commands_string)
    # results = multi_curl.run()
    # Optionally, print or process results here