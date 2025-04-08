import time
import logging
import platform
import json
from datetime import timedelta, datetime
from threading import Lock
from pathlib import Path

class UptimeMonitor:
    def __init__(self, log_file=None, snapshot_dir="snapshots/uptime"):
        self._boot_time_monotonic = time.monotonic()
        self._wall_start = datetime.utcnow()
        self._hostname = platform.node()
        self._lock = Lock()
        self._snapshot_dir = Path(snapshot_dir)
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        self._logger = self._setup_logger(log_file)

    def _setup_logger(self, log_file):
        logger = logging.getLogger(f"UptimeMonitor:{self._hostname}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.FileHandler(log_file, encoding="utf-8") if log_file else logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def get_uptime(self, raw=False):
        with self._lock:
            elapsed = timedelta(seconds=time.monotonic() - self._boot_time_monotonic)
        return int(elapsed.total_seconds()) if raw else self._format_duration(elapsed)

    def _format_duration(self, delta):
        total_seconds = int(delta.total_seconds())
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if days: parts.append(f"{days}d")
        if hours or days: parts.append(f"{hours}h")
        if minutes or hours or days: parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")
        return "System uptime: " + " ".join(parts)

    def get_start_time(self, iso=False):
        return self._wall_start.isoformat(timespec="seconds") + "Z" if iso else self._wall_start.strftime("%Y-%m-%d %H:%M:%S UTC")

    def report(self, include_host=True):
        uptime_str = self.get_uptime()
        start_time = self.get_start_time()
        prefix = f"[{self._hostname}] " if include_host else ""
        report = f"{prefix}{uptime_str} (since {start_time})"
        self._logger.info(report)
        return report

    def export_status(self, output_path=None):
        status = {
            "hostname": self._hostname,
            "uptime_seconds": self.get_uptime(raw=True),
            "uptime_text": self.get_uptime(),
            "boot_time": self.get_start_time(iso=True),
            "exported_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"
        }
        try:
            path = Path(output_path) if output_path else self._snapshot_dir / f"{int(time.time())}_uptime.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2)
            self._logger.info(f"Uptime status exported to {path}")
        except Exception as e:
            self._logger.error(f"Failed to export uptime status: {e}")

    def is_uptime_exceeding(self, threshold_seconds):
        """Check if uptime exceeds a specified threshold."""
        return self.get_uptime(raw=True) > threshold_seconds

    def time_since(self, timestamp_str):
        """Compute time since a given ISO timestamp."""
        try:
            past = datetime.fromisoformat(timestamp_str.replace("Z", ""))
            delta = datetime.utcnow() - past
            return self._format_duration(delta)
        except Exception as e:
            self._logger.error(f"Invalid timestamp format: {timestamp_str} — {e}")
            return "Invalid timestamp"
