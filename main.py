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
from api.server import run_api_server
from cli.cli import HomescannerCLI

def build_components():
    logger = Logger()
    scanner = NetworkScanner(target="127.0.0.1")
    analyzer = LogAnalyzer()
    alert_manager = AlertManager()
    db = IncidentDatabase()
    process_monitor = ProcessMonitor()
    file_monitor = FileMonitor()
    disk_monitor = DiskMonitor()
    uptime_monitor = UptimeMonitor()
    return {
        "logger": logger,
        "scanner": scanner,
        "analyzer": analyzer,
        "alert_manager": alert_manager,
        "db": db,
        "process_monitor": process_monitor,
        "file_monitor": file_monitor,
        "disk_monitor": disk_monitor,
        "uptime_monitor": uptime_monitor
    }

def main_loop(components):
    logger = components["logger"]
    scanner = components["scanner"]
    analyzer = components["analyzer"]
    alert_manager = components["alert_manager"]
    db = components["db"]
    process_monitor = components["process_monitor"]
    file_monitor = components["file_monitor"]
    disk_monitor = components["disk_monitor"]
    uptime_monitor = components["uptime_monitor"]

    logger.log("Homescanner: System initializing...", level="info")
    logger.log("Homescanner: System is up and running.", level="info")

    try:
        while True:
            cycle_start = time.time()
            logger.log("Starting scan cycle...", level="info")

            try:
                logger.log("Running network scan...", level="info")
                threats = scanner.scan()
                for threat in threats:
                    logger.log(f"Threat detected: {threat}", level="warning")
                    alert_manager.send_alert(threat)
                    db.add_incident(threat)

                logger.log("Analyzing logs for anomalies...", level="info")
                anomalies = analyzer.analyze_logs()
                for anomaly in anomalies:
                    logger.log(f"Log anomaly detected: {anomaly}", level="warning")
                    alert_manager.send_alert(anomaly)
                    db.add_incident(anomaly)

                logger.log("Checking running processes...", level="info")
                suspicious_processes = process_monitor.check_processes()
                for proc in suspicious_processes:
                    logger.log(f"Suspicious process detected: {proc}", level="warning")
                    alert_manager.send_alert(proc)
                    db.add_incident(proc)

                logger.log("Scanning files for suspicious modifications...", level="info")
                modified_files = file_monitor.check_files()
                for file in modified_files:
                    logger.log(f"Modified file detected: {file}", level="warning")
                    alert_manager.send_alert(file)
                    db.add_incident(file)

                logger.log("Checking disk usage...", level="info")
                disk_warnings = disk_monitor.check_disk_usage()
                for warning in disk_warnings:
                    logger.log(f"Disk warning: {warning}", level="warning")
                    alert_manager.send_alert(warning)
                    db.add_incident(warning)

                uptime = uptime_monitor.get_uptime()
                logger.log(f"{uptime}", level="info")

                logger.log("Scan cycle complete. Sleeping...", level="info")
                elapsed = time.time() - cycle_start
                sleep_time = max(0, 60 - elapsed)
                time.sleep(sleep_time)

            except Exception as scan_error:
                logger.log(f"Error during scan cycle: {scan_error}", level="error")

    except KeyboardInterrupt:
        logger.log("Homescanner: Shutdown requested via keyboard interrupt.", level="info")
    except Exception as fatal_error:
        logger.log(f"Homescanner: Critical error in main loop: {fatal_error}", level="critical")
        raise

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
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    cli_thread = threading.Thread(target=cli.start, daemon=True)
    api_thread.start()
    cli_thread.start()
    main_loop(components)

