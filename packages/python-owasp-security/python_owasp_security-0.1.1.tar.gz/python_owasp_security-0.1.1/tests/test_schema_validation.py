import pytest
import json
from flask import Flask, request
from owasp_security.schema_validation import schema_validation_middleware

# Schema de prueba
user_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "age": {"type": "integer", "minimum": 18}
    },
    "required": ["username", "age"]
}

@pytest.fixture
def client():
    app = Flask(__name__)

    # Usamos el middleware antes de cada request
    @app.before_request
    def validate():
        result = schema_validation_middleware(request, user_schema)
        if result:
            return result

    @app.route("/users", methods=["POST"])
    def create_user():
        return {"status": "ok"}, 200

    with app.test_client() as client:
        yield client


def test_valid_payload(client):
    payload = {"username": "jhoan", "age": 25}
    response = client.post("/users", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_invalid_payload(client):
    payload = {"username": "jhoan"}  # Falta "age"
    response = client.post("/users", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "invalid_payload"
