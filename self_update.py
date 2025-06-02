import os
import sys
import subprocess
import requests
import shutil
import zipfile
from tempfile import NamedTemporaryFile, TemporaryDirectory
from core.logger import Logger

class SelfUpdater:
    def __init__(self, update_url: str, version_file: str = "VERSION"):
        self.update_url = update_url
        self.version_file = version_file
        self.logger = Logger()

    def get_local_version(self) -> str:
        try:
            with open(self.version_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "0.0.0"

    def get_remote_version(self) -> str:
        try:
            response = requests.get(f"{self.update_url}/latest_version.txt", timeout=5)
            if response.status_code == 200:
                return response.text.strip()
            return "0.0.0"
        except Exception as e:
            self.logger.log(f"Failed to fetch remote version: {e}", level="error")
            return "0.0.0"

    def is_update_available(self) -> bool:
        local = self.get_local_version()
        remote = self.get_remote_version()
        return self._compare_versions(remote, local)

    def _replace_files(self, source_dir: str):
        for root, _, files in os.walk(source_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), source_dir)
                dest_path = os.path.join(os.getcwd(), rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(os.path.join(root, file), dest_path)

    def restart_application(self):
        self.logger.log("Restarting application...", level="info")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def run(self, auto_restart=True):
        if not self.is_update_available():
            self.logger.log("No update available.", level="info")
            return
        self.logger.log("New version available. Starting update...", level="info")
        update_zip = self.download_update()
        if update_zip:
            self.apply_update(update_zip)
            if auto_restart:
                self.restart_application()
