import time
from flask import request, jsonify

class RateLimiter:
    def __init__(self, limit_per_minute=60):
        self.limit = limit_per_minute
        self.calls = {}

    def middleware(self, app):
        @app.before_request
        def check_rate_limit():
            ip = request.remote_addr
            now = int(time.time() / 60)
            key = f"{ip}:{now}"
            self.calls[key] = self.calls.get(key, 0) + 1
            if self.calls[key] > self.limit:
                return jsonify({"error": "rate_limit_exceeded"}), 429
