import subprocess
import time
import shlex
import re
from dataclasses import dataclass


@dataclass
class Curl:
    """Represents a single cURL command with its URL, full command string, and response output."""
    url: str
    curl: str
    response: str = ""
    status_code: int = 0
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
        command_tails = [cmd.strip() for cmd in curl_commands_string.split('curl ') if cmd.strip()]
        self.curls = []
        for tail in command_tails:
            full_command = "curl " + tail
            # Extract URL: assume it's the first quoted string after "curl "
            url_match = re.search(r"'([^']+)'", full_command)
            url = url_match.group(1) if url_match else ""
            self.curls.append(Curl(url=url, curl=full_command))
    
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
            curls_to_run = [curl for curl in self.curls if url_filter in curl.url]
        else:
            curls_to_run = self.curls
        
        if not curls_to_run:
            print("No cURL commands match the filter or found.")
            return curls_to_run
        
        print(f"Running {len(curls_to_run)} commands (out of {len(self.curls)}) with delay {delay}s.")
        
        for i, curl in enumerate(curls_to_run):
            print(f"[{i+1}/{len(curls_to_run)}] Running: {curl.url}")
            # Modify command to capture status code
            modified_curl = curl.curl + ' -w "%{http_code}"'
            # Run the command and capture output
            result = subprocess.run(
                modified_curl,
                shell=True,
                capture_output=True,
                text=True
            )
            # Parse status code from the last line of stdout
            lines = result.stdout.strip().split('\n')
            if lines and lines[-1].isdigit():
                curl.status_code = int(lines[-1])
                curl.response = '\n'.join(lines[:-1])  # Exclude status code from response
            else:
                curl.response = result.stdout
            curl.error = result.stderr.strip() if result.stderr else ""
            time.sleep(delay)
        
        print("All matching commands executed.")
        return curls_to_run


# --- Script Logic (No need to edit below) ---

if __name__ == "__main__":
    multi_curl = MultiCurl(curl_commands_string)
    # results = multi_curl.run()
    # Optionally, print or process results here