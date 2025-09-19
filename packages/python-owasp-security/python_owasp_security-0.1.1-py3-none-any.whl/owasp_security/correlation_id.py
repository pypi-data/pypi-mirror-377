import uuid
from flask import request, g

def correlation_id_middleware(app):
    @app.before_request
    def set_correlation_id():
        corr_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
        g.correlation_id = corr_id
