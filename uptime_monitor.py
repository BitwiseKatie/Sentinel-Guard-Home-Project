import time
import logging
from datetime import timedelta, datetime
from threading import Lock
import platform
import json

class UptimeMonitor:
    def __init__(self, log_file=None):
        self.boot_time_monotonic = time.monotonic()
        self.wall_start = datetime.utcnow()
        self.hostname = platform.node()
        self._lock = Lock()
        self.logger = self._setup_logger(log_file)

    def _setup_logger(self, log_file):
        logger = logging.getLogger(f"UptimeMonitor:{self.hostname}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.FileHandler(log_file, encoding="utf-8") if log_file else logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def get_uptime(self, raw=False):
        with self._lock:
            elapsed = timedelta(seconds=time.monotonic() - self.boot_time_monotonic)
        total_seconds = int(elapsed.total_seconds())
        if raw:
            return total_seconds
        return self._format_uptime(total_seconds)

    def _format_uptime(self, seconds):
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
        segments = []
        if days:
            segments.append(f"{days}d")
        if hours or days:
            segments.append(f"{hours}h")
        if minutes or hours or days:
            segments.append(f"{minutes}m")
        segments.append(f"{secs}s")
        return f"System uptime: {' '.join(segments)}"

    def get_start_time(self, iso=False):
        return self.wall_start.isoformat(timespec="seconds") + "Z" if iso else self.wall_start.strftime("%Y-%m-%d %H:%M:%S UTC")

    def report(self, include_host=True):
        uptime = self.get_uptime()
        start_time = self.get_start_time()
        report = f"{uptime} (since {start_time})"
        if include_host:
            report = f"[{self.hostname}] {report}"
        self.logger.info(report)
        return report

    def export_status(self, file_path):
        status = {
            "hostname": self.hostname,
            "uptime_seconds": self.get_uptime(raw=True),
            "uptime_text": self.get_uptime(),
            "start_time": self.get_start_time(iso=True),
            "checked_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"
        }
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2)
            self.logger.info(f"Uptime status exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export uptime status: {e}")
