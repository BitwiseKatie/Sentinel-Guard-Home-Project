Sentinel-Guard-Home-Project is a security monitoring system that keeps a constant watch on network activity, system logs, running processes, and file modifications. The goal is to catch anything suspicious before it turns into a real problem. It logs security events, triggers alerts when needed, and provides an API to access incident reports. 

When you start it up, it kicks off a bunch of core components. The network scanner checks for open ports and detects common attack methods like brute-force attempts, SQL injections, and unauthorized access. The log analyzer goes through system logs, looking for any patterns that suggest suspicious activity, like failed SSH logins or unusual command executions. The process monitor scans for running programs that have sketchy names—things like "trojan" or "keylogger." The file monitor watches for unexpected file modifications, keeping track of any changes that might indicate tampering. Every security event gets logged, and if something serious is detected, an alert is sent out through email—assuming you’ve got an SMTP server configured. Everything is stored in a SQLite database for later review.

The whole system runs in a loop, scanning and analyzing continuously. Every minute, it checks the network, processes logs, monitors active programs, and verifies file integrity. Any threats it finds are logged and stored, and alerts are sent if necessary. It also includes a built-in API server, which lets you pull incident reports through a simple HTTP request. If you prefer to interact with it manually, there’s a command-line interface that allows you to check the system status or trigger certain functions directly.

To get it running, you just need to execute main.py. That starts up the API server, launches the CLI, and begins the monitoring process. The system doesn’t need much configuration, but if you want to tweak settings, you can modify the scanner’s detection patterns, adjust file monitoring parameters, or update the suspicious process keywords by editing the respective modules.

Logs are written to logs/system.log, and all detected incidents are stored in data/incidents.db. The system creates the database automatically if it doesn’t already exist, so you don’t have to worry about setting it up manually. If you want email alerts, you’ll need to provide SMTP credentials. Without them, the system will still detect threats and log them, but you won’t get notifications.

This isn’t meant to replace a full enterprise security suite, but it’s a solid, lightweight monitoring tool that does the job well. It’s designed to be simple and efficient while still catching real threats in real time. If you’re using this in a production environment, keep in mind that active network scanning and process monitoring might trigger alerts in other security systems, so use it wisely.

04/02/2025
What's New:
Homescanner has been expanded with several new capabilities designed to make it more reliable, more actionable, and better suited for long-term use in personal or semi-professional environments.

User Activity Monitoring
The system now tracks who logs into the machine. If a new user appears—either legitimately or as the result of an intrusion—it logs the event, stores it in the database, and optionally sends an alert via email. This feature is critical for detecting lateral movement, compromised credentials, or brute-forced accounts.

Uptime Tracking
A built-in uptime monitor records how long the system has been running. This makes it easy to detect crashes, reboots, or any unexpected resets. The current uptime is shown directly in the CLI and also logged regularly as part of the monitoring cycle.

Health Check System
Before entering the monitoring loop, the system runs a health check to validate that core components are working. This includes verifying access to the incident database, confirming file system paths are available, ensuring the network scanner can run, and checking that alert delivery is properly configured. If any of these checks fail, the system logs a detailed error and does not proceed blindly.

Updated Command-Line Interface
The CLI has been fully updated to support manual interactions. It now allows the user to trigger scans, view recent logs, check disk health, see system uptime, and query incident data without writing any code or querying the database directly. It uses color output where supported and provides clear feedback on each command.

Configuration and Modularity
All runtime behavior is now controlled through a single configuration file located at config/config.yml. This includes all thresholds, paths, detection parameters, and alert settings. Each monitoring module is self-contained and loads only the settings it needs. The project structure was updated to allow for better testability and reuse of components.

Installation
Setup is handled by a single script: install.sh. It creates the Python virtual environment, installs dependencies, sets up folders, writes default configs, and gives you a fully working environment in one step. Once installed, you can launch the system by running python main.py, which starts the CLI, the API server, and the full monitoring loop.
