from flask import Flask, render_template, request, jsonify, g
import json
import os
import logging
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

RATE_LIMITS = {
    "default": 60,
    "api": 100,
    "contact": 10,
}
_rate_limit_store = {}

def check_rate_limit(key, limit, window=60):
    now = datetime.now().timestamp()
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < window]
    if len(_rate_limit_store[key]) >= limit:
        return False
    _rate_limit_store[key].append(now)
    return True

def rate_limit(endpoint_type="default"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()
            key = f"{endpoint_type}:{client_ip}"
            limit = RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])
            if not check_rate_limit(key, limit):
                logger.warning(f"Rate limit exceeded for {key}")
                return jsonify({"error": "Demasiadas solicitudes. Intente más tarde.", "code": "RATE_LIMIT_EXCEEDED"}), 429
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_json(required_fields=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.method in ["POST", "PUT", "PATCH"]:
                if not request.is_json:
                    return jsonify({"error": "Content-Type debe ser application/json", "code": "INVALID_CONTENT_TYPE"}), 400
                try:
                    data = request.get_json()
                    if data is None:
                        return jsonify({"error": "JSON inválido", "code": "INVALID_JSON"}), 400
                except Exception:
                    return jsonify({"error": "JSON malformado", "code": "MALFORMED_JSON"}), 400
                
                if required_fields:
                    missing = [field for field in required_fields if not data.get(field)]
                    if missing:
                        return jsonify({"error": f"Campos requeridos faltantes: {', '.join(missing)}", "code": "MISSING_FIELDS", "fields": missing}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.before_request
def before_request():
    g.start_time = datetime.now()
    logger.info(f"{request.method} {request.path} - IP: {request.headers.get('X-Forwarded-For', request.remote_addr)}")

@app.after_request
def after_request(response):
    duration = (datetime.now() - g.start_time).total_seconds() * 1000
    logger.info(f"{request.method} {request.path} - Status: {response.status_code} - Duration: {duration:.2f}ms")
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    
    if request.is_secure:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    
    return response

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Solicitud inválida", "code": "BAD_REQUEST", "details": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado", "code": "NOT_FOUND"}), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({"error": "Demasiadas solicitudes", "code": "RATE_LIMIT_EXCEEDED"}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({"error": "Error interno del servidor", "code": "INTERNAL_ERROR"}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled exception: {error}", exc_info=True)
    return jsonify({"error": "Error interno del servidor", "code": "INTERNAL_ERROR"}), 500

def leer_json(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {archivo}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading {archivo}: {e}")
            return []
    return []

def guardar_json(archivo, datos):
    try:
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error writing {archivo}: {e}")
        raise

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/productos", methods=["GET"])
@rate_limit("api")
def obtener_productos():
    try:
        category = request.args.get("category", "all")
        search = request.args.get("q", "").lower().strip()
        
        if len(search) > 100:
            return jsonify({"error": "Búsqueda demasiado larga", "code": "SEARCH_TOO_LONG"}), 400
        
        productos = leer_json(PRODUCTS_FILE)
        
        if category != "all":
            productos = [p for p in productos if p.get("category") == category]
        
        if search:
            productos = [p for p in productos if search in p.get("name", "").lower()]
        
        return jsonify(productos)
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({"error": "Error al obtener productos", "code": "FETCH_ERROR"}), 500

@app.route("/api/contact", methods=["POST"])
@rate_limit("contact")
@validate_json(["name", "email", "message"])
def contact():
    try:
        payload = request.get_json()
        
        name = payload.get("name", "").strip()
        email = payload.get("email", "").strip()
        message = payload.get("message", "").strip()
        
        if len(name) > 100:
            return jsonify({"error": "Nombre demasiado largo", "code": "NAME_TOO_LONG"}), 400
        
        if len(email) > 254 or "@" not in email:
            return jsonify({"error": "Email inválido", "code": "INVALID_EMAIL"}), 400
        
        if len(message) > 5000:
            return jsonify({"error": "Mensaje demasiado largo", "code": "MESSAGE_TOO_LONG"}), 400
        
        logger.info(f"New contact: {name} - {email}")
        
        return jsonify({"ok": True, "message": "Mensaje enviado correctamente"})
    except Exception as e:
        logger.error(f"Error processing contact: {e}")
        return jsonify({"error": "Error al procesar contacto", "code": "PROCESS_ERROR"}), 500

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    print(f"\nPágina Principal - http://localhost:{port}")
    app.run(debug=debug_mode, port=port, host="0.0.0.0")