import socket
from urllib.parse import urlparse
import requests

class SSRFHttpClient:
    def __init__(self, allowed_hosts=None):
        # Lista blanca de hosts permitidos
        self.allowed_hosts = allowed_hosts or []

    def get(self, url: str):
        parsed = urlparse(url)
        host = parsed.hostname

        if not host:
            raise ValueError("Invalid URL: no host found")

        # Validar contra la lista blanca
        if host not in self.allowed_hosts:
            raise ValueError(f"SSRF blocked: {host} not allowed")

        # Resolver dirección IP
        try:
            ip = socket.gethostbyname(host)
        except socket.gaierror:
            raise ValueError(f"Cannot resolve host: {host}")

        # Validar que no sea privada o loopback
        if self._is_private_ip(ip):
            raise ValueError("SSRF blocked: private or loopback IP")

        # Finalmente, realizar la petición
        return requests.get(url)

    def _is_private_ip(self, ip: str) -> bool:
        """Chequea si la IP es privada o loopback"""
        return (
            ip.startswith("10.") or
            ip.startswith("192.168.") or
            ip.startswith("127.") or
            ip.startswith("172.") and 16 <= int(ip.split(".")[1]) <= 31 or
            ip == "::1"  # IPv6 loopback
        )
