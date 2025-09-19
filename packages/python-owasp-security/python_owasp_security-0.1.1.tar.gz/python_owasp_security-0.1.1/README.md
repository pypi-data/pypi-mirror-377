# 🛡️ OWASP Security for Python

Un **middleware de seguridad para APIs en Python** que aplica de forma **transversal** prácticas recomendadas por [OWASP Top 10](https://owasp.org/Top10/).  
Provee validaciones, headers de seguridad, rate limiting, protección SSRF, correlation IDs y métricas listas para usar.

Compatible con **Flask** y otras APIs Python modernas.

---

## Características

- ✅ **Validación de payloads JSON** usando **JSON Schema**.
- ✅ **Protección contra SSRF** (validación de hosts permitidos + bloqueo de IP privadas).
- ✅ **Rate limiting** con [rate-limiter-flexible](https://pypi.org/project/rate-limiter-flexible/) equivalente en Python.
- ✅ **Correlation IDs (`X-Correlation-Id`)** automáticos para trazabilidad.
- ✅ **Headers de seguridad**: HSTS, CSP, X-Frame-Options, etc.
- ✅ **Métricas Prometheus** vía [`prometheus-client`](https://pypi.org/project/prometheus-client/).

---

## 📦 Instalación

1. **Puedes instalar la librería directamente desde PyPI usando pip:**

`pip install owasp-security`

La librería requiere Python 3.9 o superior. Las dependencias incluyen Flask, pydantic, jsonschema, prometheus-client y requests.

## 🛠️ Componentes y Uso

La librería owasp-security incluye los siguientes componentes de seguridad listos para usar:

### 1. Middleware de Validación de Esquemas

Valida los payloads JSON de los requests HTTP (métodos POST y PUT) contra un JSON Schema para prevenir ataques de inyección y asegurar la integridad de los datos.

    Uso:
    ```Python

    from flask import Flask, jsonify, request
    from owasp_security import schema_validation_middleware

    # Importa tu JSON schema, por ejemplo, desde un archivo
    user_schema = {
      "type": "object",
      "properties": {
        "username": { "type": "string" },
        "age": { "type": "integer", "minimum": 18 }
      },
      "required": ["username", "age"]
    }

    app = Flask(__name__)

    @app.before_request
    def validate_payload():
        return schema_validation_middleware(request, user_schema)

    @app.route("/users", methods=["POST"])
    def create_user():
        # El payload ya está validado
        return jsonify(request.get_json()), 201

    if __name__ == "__main__":
        app.run()```

### 2. Protección contra SSRF (Server-Side Request Forgery)

Proporciona una clase SSRFHttpClient que valida las URLs para prevenir peticiones maliciosas hacia direcciones IP privadas o no autorizadas.

    Uso:
    ```Python

    from owasp_security import SSRFHttpClient

    # Define una lista blanca de hosts permitidos
    allowed_hosts = ["api.example.com", "public-data.com"]
    http_client = SSRFHttpClient(allowed_hosts=allowed_hosts)

    try:
        response = http_client.get("https://api.example.com/data")
        print(response.text)
    except ValueError as e:
        print(f"Error: {e}")

    # Este intento fallará, ya que es una IP privada
    try:
        http_client.get("http://192.168.1.1/internal-resource")
    except ValueError as e:
        print(f"Error: {e}")```

### 3. Middleware de Rate Limiting

Limita el número de peticiones por minuto por dirección IP para proteger tu API de ataques de fuerza bruta o de denegación de servicio.

    Uso:
    ```Python

    from flask import Flask
    from owasp_security import RateLimiter

    app = Flask(__name__)

    # Configura el Rate Limiter con un límite de 60 peticiones por minuto
    rate_limiter = RateLimiter(limit_per_minute=60)
    rate_limiter.middleware(app)

    @app.route("/data")
    def get_data():
        return "Este es un recurso limitado", 200

    if __name__ == "__main__":
        app.run()```

### 4. Middleware de Encabezados de Seguridad (Security Headers)

Añade encabezados HTTP de seguridad a las respuestas para prevenir ataques comunes como Clickjacking y XSS.

    Uso:
    ```Python

    from flask import Flask
    from owasp_security import security_headers_middleware

    app = Flask(__name__)
    security_headers_middleware(app)

    @app.route("/")
    def index():
        return "Hola, con encabezados de seguridad!", 200

    if __name__ == "__main__":
        app.run()```

### 5. Generación de ID de Correlación

Añade un ID de correlación único a cada request para facilitar el rastreo y la depuración en los logs de tu aplicación.

    Uso:
    ```Python

    from flask import Flask, g
    from owasp_security import correlation_id_middleware

    app = Flask(__name__)
    correlation_id_middleware(app)

    @app.route("/")
    def index():
        print(f"ID de correlación para este request: {g.correlation_id}")
        return f"Tu ID de correlación es: {g.correlation_id}", 200

    if __name__ == "__main__":
        app.run()```

### 6. Métricas de Seguridad con Prometheus

Proporciona contadores para registrar métricas de seguridad que pueden ser monitoreadas con Prometheus.

    Uso:
    ```Python

    from flask import Flask
    from owasp_security import SecurityMetrics

    app = Flask(__name__)
    metrics = SecurityMetrics()```

# Por ejemplo, incrementa los contadores cuando una validación falla
```@app.route("/metrics")
def metrics_endpoint():
    return metrics.metrics_endpoint()

if __name__ == "__main__":
    app.run()```
