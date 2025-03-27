import asyncio
import socket
import logging
from datetime import datetime

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
        22: "SSH Brute Force Risk",
        23: "Legacy Telnet Exposure",
        25: "SMTP Relay Open",
        53: "DNS Abuse Possibility",
        80: "Public Web Server Found",
        110: "POP3 Credentials Leak",
        139: "NetBIOS Enumeration Risk",
        143: "Unsecured IMAP Detected",
        443: "HTTPS Server Exposed",
        445: "Potential EternalBlue SMB",
        3306: "MySQL Open To Public",
        3389: "RDP Lateral Movement Vector",
        5900: "VNC Exposed Interface",
        8080: "Unsecured Alt-Web Interface"
    }

    def __init__(self, target="127.0.0.1", ports=None, timeout=1.0):
        self.target = target
        self.ports = ports if ports else list(self.COMMON_PORTS.keys())
        self.timeout = timeout
        self.results = []

    async def scan(self):
        try:
            socket.gethostbyname(self.target)
        except socket.gaierror:
            logging.error(f"DNS resolution failed for {self.target}")
            return [{"error": "Unresolved hostname"}]

        logging.info(f"Initiating async scan on {self.target}")
        start_time = datetime.utcnow()
        await self._scan_ports()
        duration = (datetime.utcnow() - start_time).total_seconds()
        logging.info(f"Scan completed in {duration:.2f} seconds")
        return self.results

    async def _scan_ports(self):
        tasks = [self._scan_port(port) for port in self.ports]
        await asyncio.gather(*tasks)

    async def _scan_port(self, port):
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.target, port), timeout=self.timeout
            )
            banner = await self._grab_banner(reader)
            writer.close()
            await writer.wait_closed()

            service = self.COMMON_PORTS.get(port, "Unknown")
            threat = self._analyze_threat(port, banner)
            self.results.append({
                "port": port,
                "service": service,
                "banner": banner.strip() if banner else "N/A",
                "threat": threat
            })
        except (asyncio.TimeoutError, ConnectionRefusedError):
            pass
        except Exception as e:
            logging.warning(f"Unexpected error on port {port}: {e}")

    async def _grab_banner(self, reader):
        try:
            banner = await asyncio.wait_for(reader.read(1024), timeout=0.5)
            return banner.decode(errors="ignore")
        except Exception:
            return ""

    def _analyze_threat(self, port, banner):
        base_threat = self.POTENTIAL_THREATS.get(port)
        if not base_threat:
            return f"Open port {port}, unknown service"

        if banner:
            banner_lower = banner.lower()
            if "unauthorized" in banner_lower or "login" in banner_lower:
                return f"{base_threat} + Possible weak authentication"
            if "apache" in banner_lower or "nginx" in banner_lower:
                return f"{base_threat} + Public web stack exposed"
        return base_threat
