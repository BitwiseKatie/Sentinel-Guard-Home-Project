import time
import threading
from core.logger import Logger
from core.scanner import NetworkScanner
from core.analysis import LogAnalyzer
from core.alerts import AlertManager
from core.database import IncidentDatabase
from monitoring.process_monitor import ProcessMonitor
from security.file_monitor import FileMonitor
from monitoring.disk_monitor import DiskMonitor
from system.uptime_monitor import UptimeMonitor
from monitoring.user_activity_monitor import UserActivityMonitor
from api.server import run_api_server
from cli.cli import HomescannerCLI

def build_components():
    logger = Logger()
    return {
        "logger": logger,
        "scanner": NetworkScanner(target="127.0.0.1"),
        "analyzer": LogAnalyzer(),
        "alert_manager": AlertManager(),
        "db": IncidentDatabase(),
        "process_monitor": ProcessMonitor(),
        "file_monitor": FileMonitor(),
        "disk_monitor": DiskMonitor(),
        "uptime_monitor": UptimeMonitor(),
        "user_activity_monitor": UserActivityMonitor()
    }

def main_loop(components):
    logger = components["logger"]
    logger.log("Homescanner initialized and running.", level="info")

    while True:
        start = time.time()
        logger.log("Starting scan cycle...", level="info")

        try:
            for monitor, label, handler in [
                (components["scanner"].scan, "network", "scanner"),
                (components["analyzer"].analyze_logs, "log", "log_analyzer"),
                (components["process_monitor"].check_processes, "process", "process_monitor"),
                (components["file_monitor"].check_files, "filesystem", "file_monitor"),
                (components["disk_monitor"].check_disk_usage, "disk", "disk_monitor"),
                (components["user_activity_monitor"].check_new_logins, "account", "user_monitor")
            ]:
                for item in monitor():
                    message = f"{label.capitalize()} issue detected: {item}" if label != "account" else f"New user login detected: {item}"
                    logger.log(message, level="warning")
                    components["alert_manager"].send_alert(message)
                    components["db"].add_incident(message, type=label, severity="warning", source=handler)

            logger.log(components["uptime_monitor"].get_uptime(), level="info")
            logger.log("Scan cycle complete. Sleeping...", level="info")
            time.sleep(max(0, 60 - (time.time() - start)))

        except Exception as e:
            logger.log(f"Error during scan cycle: {e}", level="error")

def health_check(components):
    logger = components["logger"]
    logger.log("Performing health check...", level="info")

    checks = {
        "Database": lambda: components["db"].get_connection() is not None,
        "Scanner": lambda: components["scanner"].scan() is not None,
        "File Monitor": lambda: components["file_monitor"].check_files() is not None,
        "Disk Monitor": lambda: components["disk_monitor"].check_disk_usage() is not None
    }

    for name, check in checks.items():
        try:
            logger.log(f"{name} check passed." if check() else f"{name} check failed.", level="info")
        except Exception as e:
            logger.log(f"{name} check error: {e}", level="error")

    if not components["alert_manager"].enabled:
        logger.log("Email alerts disabled or misconfigured.", level="warning")
    else:
        logger.log("AlertManager config OK.", level="info")

    logger.log("Health check complete.", level="info")

def run_all():
    components = build_components()
    cli = HomescannerCLI(
        components["uptime_monitor"],
        components["disk_monitor"],
        components["logger"],
        components["analyzer"],
        components["db"],
        components["file_monitor"],
        components["process_monitor"],
        components["scanner"],
        components["alert_manager"]
    )
    threading.Thread(target=run_api_server, daemon=True).start()
    threading.Thread(target=cli.start, daemon=True).start()
    main_loop(components)
