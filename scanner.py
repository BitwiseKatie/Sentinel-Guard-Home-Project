import socket
import random
import logging

class NetworkScanner:
    COMMON_PORTS = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        139: "NetBIOS",
        143: "IMAP",
        443: "HTTPS",
        445: "SMB",
        3306: "MySQL",
        3389: "RDP",
        5900: "VNC",
        8080: "HTTP-Alt"
    }

    POTENTIAL_THREATS = {
        21: "Unencrypted FTP Detected",
        22: "Brute Force SSH Possible",
        23: "Telnet Exposure",
        25: "SMTP Relay Risk",
        53: "DNS Hijack Vector",
        80: "Web Server Exposure",
        139: "NetBIOS Leak",
        445: "SMB Vulnerability (EternalBlue?)",
        3306: "Exposed MySQL Instance",
        3389: "Open RDP - Lateral Movement Risk",
        5900: "VNC Access Detected",
        8080: "Unsecured Web Interface"
    }

    def __init__(self, target="127.0.0.1", ports=None, timeout=0.3):
        self.target = target
        self.ports = ports if ports else list(self.COMMON_PORTS.keys())
        self.timeout = timeout

    def scan(self):
        try:
            socket.gethostbyname(self.target)
        except socket.gaierror:
            logging.error(f"Unable to resolve target hostname: {self.target}")
            return ["DNS resolution failed for target"]

        logging.info(f"Starting scan on {self.target}")
        open_ports = self.detect_open_tcp_ports()
        threats = self.analyze_threats(open_ports)
        return threats

    def detect_open_tcp_ports(self):
        open_ports = []
        for port in self.ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(self.timeout)
                    if s.connect_ex((self.target, port)) == 0:
                        open_ports.append(port)
            except Exception as e:
                logging.warning(f"Error scanning port {port}: {e}")
        return open_ports

    def analyze_threats(self, open_ports):
        threats = []
        for port in open_ports:
            threat = self.POTENTIAL_THREATS.get(port, f"Unknown open port: {port}")
            threats.append(threat)
        return threats
