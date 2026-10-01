from flask import Flask, jsonify, request, session, redirect, url_for, render_template, send_from_directory, g
from flask_cors import CORS
from functools import wraps
import json
import os
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

CORS(app, supports_credentials=True, origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(","))

app.secret_key = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    SESSION_COOKIE_NAME='foodcolor_session',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

USERS_FILE = os.path.join(BASE_DIR, "users.json")
SHARED_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "data"))
PRODUCTS_FILE = os.path.join(SHARED_DIR, "products.json")
PEDIDOS_FILE = os.path.join(SHARED_DIR, "pedidos.json")

RATE_LIMITS = {
    "default": 60,
    "login": 5,
    "api": 100,
    "contact": 10,
}
_rate_limit_store = {}

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading users: {e}")
    return {"admin": generate_password_hash(os.getenv("ADMIN_PASSWORD", "foodcolor2026"))}

def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

USERS = load_users()

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

def login_required(func=None, api=False):
    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not session.get("user"):
                if api:
                    return jsonify({"error": "No autorizado", "code": "UNAUTHORIZED"}), 401
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapper
    if func is not None:
        return deco(func)
    return deco

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

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "No autorizado", "code": "UNAUTHORIZED"}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({"error": "Acceso denegado", "code": "FORBIDDEN"}), 403

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

@app.route("/styles.css")
def estilos():
    return send_from_directory(BASE_DIR, "styles.css", mimetype="text/css")

@app.route("/login", methods=["GET", "POST"])
@rate_limit("login")
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("usuario", "").strip()
        p = request.form.get("password", "")
        
        if not u or not p:
            error = "Usuario y contraseña son requeridos"
        elif u in USERS and check_password_hash(USERS[u], p):
            session.permanent = True
            session["user"] = u
            logger.info(f"Successful login for user: {u}")
            return redirect(url_for("index"))
        else:
            logger.warning(f"Failed login attempt for user: {u}")
            error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    user = session.get("user")
    session.clear()
    if user:
        logger.info(f"User logged out: {user}")
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    return open(os.path.join(BASE_DIR, "index.html"), encoding="utf-8").read()

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

def next_id(productos):
    return max((p.get("id", 0) for p in productos), default=0) + 1

@app.route("/productos", methods=["GET"])
@login_required(api=True)
@rate_limit("api")
def obtener_productos():
    try:
        return jsonify(leer_json(PRODUCTS_FILE))
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({"error": "Error al obtener productos", "code": "FETCH_ERROR"}), 500

@app.route("/productos", methods=["POST"])
@login_required(api=True)
@rate_limit("api")
@validate_json(["name", "precio"])
def agregar_producto():
    try:
        nuevo = request.json
        name = nuevo.get("name", "").strip()
        precio = nuevo.get("precio")

        if not name:
            return jsonify({"error": "El nombre no puede estar vacío", "code": "INVALID_NAME"}), 400
        
        try:
            precio = float(precio)
            if precio < 0:
                return jsonify({"error": "El precio no puede ser negativo", "code": "INVALID_PRICE"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Precio inválido", "code": "INVALID_PRICE"}), 400

        stock = int(nuevo.get("stock", 0))
        if stock < 0:
            return jsonify({"error": "El stock no puede ser negativo", "code": "INVALID_STOCK"}), 400

        productos = leer_json(PRODUCTS_FILE)

        existente = next((p for p in productos if p["name"].lower() == name.lower()), None)
        if existente:
            existente["stock"] += stock
            existente["precio"] = precio
            if nuevo.get("tipo_unidad"):
                existente["tipo_unidad"] = nuevo["tipo_unidad"].strip()
            if nuevo.get("category"):
                existente["category"] = nuevo["category"].strip()
            if nuevo.get("desc"):
                existente["desc"] = nuevo["desc"].strip()
            if nuevo.get("img"):
                existente["img"] = nuevo["img"].strip()
            guardar_json(PRODUCTS_FILE, productos)
            return jsonify({"mensaje": "Stock actualizado", "producto": existente}), 200

        producto = {
            "id": next_id(productos),
            "name": name,
            "category": nuevo.get("category", "colorantes").strip(),
            "desc": nuevo.get("desc", "").strip(),
            "img": nuevo.get("img", "").strip(),
            "precio": precio,
            "stock": stock,
            "tipo_unidad": nuevo.get("tipo_unidad", "").strip()
        }
        productos.append(producto)
        guardar_json(PRODUCTS_FILE, productos)
        return jsonify({"mensaje": "Producto creado", "producto": producto}), 201
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return jsonify({"error": "Error al crear producto", "code": "CREATE_ERROR"}), 500

@app.route("/pedidos", methods=["POST"])
@login_required(api=True)
@rate_limit("api")
@validate_json(["cliente", "producto_id", "cantidad"])
def crear_pedido():
    try:
        datos = request.json
        cliente = datos.get("cliente", "").strip()
        producto_id = datos.get("producto_id")
        cantidad = datos.get("cantidad")

        if not cliente:
            return jsonify({"error": "El cliente es requerido", "code": "INVALID_CLIENT"}), 400

        try:
            producto_id = int(producto_id)
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            return jsonify({"error": "producto_id y cantidad deben ser números enteros", "code": "INVALID_TYPES"}), 400

        if cantidad <= 0:
            return jsonify({"error": "La cantidad debe ser mayor a 0", "code": "INVALID_QUANTITY"}), 400

        productos = leer_json(PRODUCTS_FILE)
        prod = next((p for p in productos if p["id"] == producto_id), None)
        if not prod:
            return jsonify({"error": "Producto no encontrado", "code": "PRODUCT_NOT_FOUND"}), 404

        if cantidad > prod.get("stock", 0):
            return jsonify({"error": "Stock insuficiente", "code": "INSUFFICIENT_STOCK", "disponible": prod["stock"]}), 400

        prod["stock"] -= cantidad
        guardar_json(PRODUCTS_FILE, productos)

        total = cantidad * prod["precio"]
        boleta = {
            "cliente": cliente,
            "producto": prod["name"],
            "detalle": prod.get("tipo_unidad", ""),
            "cantidad": cantidad,
            "precio_unitario": prod["precio"],
            "total": total,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }

        pedidos = leer_json(PEDIDOS_FILE)
        pedidos.append(boleta)
        guardar_json(PEDIDOS_FILE, pedidos)

        return jsonify({
            "mensaje": "Pedido creado",
            "boleta": boleta,
            "stock_restante": prod["stock"]
        }), 201
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({"error": "Error al crear pedido", "code": "CREATE_ERROR"}), 500

@app.route("/pedidos", methods=["GET"])
@login_required(api=True)
@rate_limit("api")
def obtener_pedidos():
    try:
        return jsonify(leer_json(PEDIDOS_FILE))
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({"error": "Error al obtener pedidos", "code": "FETCH_ERROR"}), 500

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    print("\nInventario - http://localhost:5001")
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode, port=5001, host="0.0.0.0")