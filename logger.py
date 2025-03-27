import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

class Logger:
    def __init__(self, log_file="logs/system.log", max_bytes=5 * 1024 * 1024, backup_count=3):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        self.log_file = log_file

        self.logger = logging.getLogger("HomescannerLogger")
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")

        file_handler = RotatingFileHandler(self.log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(formatter)

        if not self.logger.hasHandlers():
            self.logger.addHandler(file_handler)

    def log(self, message, level="info"):
        level = level.lower()
        if level == "debug":
            self.logger.debug(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "critical":
            self.logger.critical(message)
        else:
            self.logger.info(message)

    def read_logs(self, lines=50):
        try:
            with open(self.log_file, "r") as f:
                return f.readlines()[-lines:]
        except FileNotFoundError:
            return ["Log file not found."]
