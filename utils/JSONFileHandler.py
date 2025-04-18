import json
import logging
import os


class JSONFileHandler:
    def __init__(self, file_path: str) -> None:
        self.file_path = os.path.abspath(file_path)
        dir_name = os.path.dirname(self.file_path)
        if dir_name:
            try:
                os.makedirs(dir_name, exist_ok=True)
            except OSError as e:
                logging.error(
                    f"Fatal: failed to create required directory {dir_name}:\n{e}."
                )
                raise

    def read_json(self) -> list | dict:
        with open(self.file_path, mode="r", encoding="utf-8") as file:
            content = file.read()
            if not content:
                return []
            return json.loads(content)

    def write_json(self, value: list | dict) -> None:
        with open(self.file_path, mode="w", encoding="utf-8") as file:
            json.dump(value, file, indent=4)