import time
from core.logger import Logger
from core.scanner import NetworkScanner
from core.analysis import LogAnalyzer
from core.alerts import AlertManager
from core.database import IncidentDatabase
from api.server import run_api_server
from monitoring.process_monitor import ProcessMonitor

def main():
    logger = Logger()
    scanner = NetworkScanner()
    analyzer = LogAnalyzer()
    alert_manager = AlertManager()
    db = IncidentDatabase()
    process_monitor = ProcessMonitor()

    logger.log("SentinelGuard Pro: System initializing...")

    while True:
        logger.log("Running network scan...")
        threats = scanner.scan()

        for threat in threats:
            logger.log(f"Threat detected: {threat}")
            alert_manager.send_alert(threat)
            db.add_incident(threat)

        logger.log("Analyzing logs for anomalies...")
        anomalies = analyzer.analyze_logs()

        for anomaly in anomalies:
            logger.log(f"Log anomaly detected: {anomaly}")
            alert_manager.send_alert(anomaly)
            db.add_incident(anomaly)

        logger.log("Checking running processes...")
        suspicious_processes = process_monitor.check_processes()

        for proc in suspicious_processes:
            logger.log(f"Suspicious process detected: {proc}")
            alert_manager.send_alert(proc)
            db.add_incident(proc)

        logger.log("Sleeping for next scan cycle...")
        time.sleep(60)

if __name__ == "__main__":
    run_api_server()
    main()
