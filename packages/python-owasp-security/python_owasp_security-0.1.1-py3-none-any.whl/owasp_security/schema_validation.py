from flask import jsonify
import jsonschema

def schema_validation_middleware(req, schema):
    """
    Middleware genérico para validar payloads JSON contra un schema dado.
    - req: objeto Flask request
    - schema: diccionario con el JSON Schema

    Retorna:
      - None si el payload es válido o si el método no requiere validación.
      - Response (400) si el payload no cumple el schema.
    """
    if req.method in ["POST", "PUT"]:
        try:
            jsonschema.validate(instance=req.get_json(), schema=schema)
        except jsonschema.ValidationError as e:
            return jsonify({"error": "invalid_payload", "details": str(e)}), 400
    return None
