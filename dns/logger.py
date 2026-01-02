import json
import time
from pathlib import Path

LOG_FILE = Path("logs/dns.log")


class DNSLogger:
    def __init__(self, log_file=LOG_FILE):
        log_file.parent.mkdir(exist_ok=True)
        self.log_file = log_file

    def log(self, event: dict):
        event["timestamp"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        )
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
