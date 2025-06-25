import os
import platform
import socket
import shutil
import multiprocessing
from typing import Dict


def get_env_info() -> Dict[str, str]:
    try:
        return {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "arch": platform.machine(),
            "hostname": platform.node(),
            "ip": _local_ip(),
            "cpus": str(multiprocessing.cpu_count()),
            "cwd": os.getcwd(),
            "virtualized": _is_virtualized(),
            "shell": os.environ.get("SHELL", "unknown"),
            "term": os.environ.get("TERM", "unknown"),
            "disk_gb": _disk_gb(),
            "python": platform.python_version()
        }
    except Exception as e:
        return {"error": str(e)}


def _local_ip() -> str:
    try:
        with socket.create_connection(("8.8.8.8", 80), 1) as s:
            return s.getsockname()[0]
    except:
        return "unknown"
