import socket
import ipaddress
from typing import Optional


def reverse_dns(ip: str) -> Optional[str]:
    try:
        ip_clean = ip.strip()
        ipaddress.ip_address(ip_clean)
        hostname, _, _ = socket.gethostbyaddr(ip_clean)
        return hostname
    except (ValueError, socket.herror, socket.gaierror):
        return None
