from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from flask import Response

class SecurityMetrics:
    def __init__(self):
        self.invalid_payloads = Counter(
            "security_payload_invalid_count",
            "Número de requests rechazados por payload inválido"
        )
        self.ratelimit_blocked = Counter(
            "security_ratelimit_blocked_count",
            "Número de requests bloqueados por rate limiting"
        )
        self.ssrf_blocked = Counter(
            "security_ssrf_blocked_count",
            "Número de requests bloqueados por SSRF"
        )

    def metrics_endpoint(self):
        """
        Devuelve las métricas en formato Prometheus para ser expuestas en /metrics
        """
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
