import sys
import json
from .._bode_logger import get_logger


def try_json(message: str) -> str | None:
    try:
        return json.loads(message)
    except json.decoder.JSONDecodeError:
        return None


class CustomStream:
    def __init__(self, original_stdout, logger):
        self.original_stdout = original_stdout
        self.logger = logger

    def write(self, message):
        if message != "\n":
            json_message = try_json(message)
            if json_message is not None and all(
                [
                    x in json_message.keys()
                    for x in ["severity", "time", "request_id", "message"]
                ]
            ):
                self.original_stdout.write(message)
            else:
                self.logger.log(20, message.rstrip("\n"))

    def flush(self):
        self.original_stdout.flush()


def add_structure_to_raw_logs():
    sys.stdout = CustomStream(sys.stdout, get_logger())
    sys.stderr = CustomStream(sys.stderr, get_logger())
