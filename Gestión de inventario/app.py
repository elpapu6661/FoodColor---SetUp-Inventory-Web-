from flask import Flask, jsonify, request, session, redirect, url_for, render_template, send_from_directory
from flask_cors import CORS
from functools import wraps
import json, os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)
app.secret_key = "cambia-esta-clave-en-produccion"

@app.route("/styles.css")
def estilos():
    # Sirve el mismo styles.css que usa el index principal
    return send_from_directory(BASE_DIR, "styles.css", mimetype="text/css")

# Credenciales del personal autorizado
USERS = {"admin": "foodcolor2026"}

def login_required(func=None, api=False):
    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not session.get("user"):
                if api:
                    return jsonify({"error": "No autorizado"}), 401
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapper
    # soporta @login_required y @login_required(api=True)
    if func is not None:
        return deco(func)
    return deco

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form.get("usuario", "")
        p = request.form.get("password", "")
        if USERS.get(u) == p:
            session["user"] = u
            return redirect(url_for("index"))
        error = "Usuario o contraseña incorrectos"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    # Solo personal autorizado accede al sistema
    return open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8").read()

SHARED_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
PRODUCTS_FILE = os.path.join(SHARED_DIR, "products.json")
PEDIDOS_FILE = os.path.join(SHARED_DIR, "pedidos.json")

def leer_json(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_json(archivo, datos):
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)

def next_id(productos):
    return max((p.get("id", 0) for p in productos), default=0) + 1

# ── PRODUCTOS ──

@app.route("/productos", methods=["GET"])
@login_required(api=True)
def obtener_productos():
    return jsonify(leer_json(PRODUCTS_FILE))

@app.route("/productos", methods=["POST"])
@login_required(api=True)
def agregar_producto():
    nuevo = request.json
    name = nuevo.get("name", "").strip()
    precio = nuevo.get("precio")

    if not name or precio is None:
        return jsonify({"error": "Faltan campos: name y precio son obligatorios"}), 400

    productos = leer_json(PRODUCTS_FILE)

    existente = next((p for p in productos if p["name"].lower() == name.lower()), None)
    if existente:
        existente["stock"] += int(nuevo.get("stock", 0))
        existente["precio"] = float(precio)
        if nuevo.get("tipo_unidad"):
            existente["tipo_unidad"] = nuevo["tipo_unidad"]
        if nuevo.get("category"):
            existente["category"] = nuevo["category"]
        guardar_json(PRODUCTS_FILE, productos)
        return jsonify({"mensaje": "Stock actualizado", "producto": existente}), 200

    producto = {
        "id": next_id(productos),
        "name": name,
        "category": nuevo.get("category", "colorantes"),
        "desc": nuevo.get("desc", ""),
        "img": nuevo.get("img", ""),
        "precio": float(precio),
        "stock": int(nuevo.get("stock", 0)),
        "tipo_unidad": nuevo.get("tipo_unidad", "")
    }
    productos.append(producto)
    guardar_json(PRODUCTS_FILE, productos)
    return jsonify({"mensaje": "Producto creado", "producto": producto}), 201

# ── PEDIDOS ──

@app.route("/pedidos", methods=["POST"])
@login_required(api=True)
def crear_pedido():
    datos = request.json
    cliente = datos.get("cliente", "").strip()
    producto_id = datos.get("producto_id")
    cantidad = datos.get("cantidad")

    if not cliente or not producto_id or not cantidad:
        return jsonify({"error": "Faltan datos: cliente, producto_id, cantidad"}), 400

    productos = leer_json(PRODUCTS_FILE)
    prod = next((p for p in productos if p["id"] == producto_id), None)
    if not prod:
        return jsonify({"error": "Producto no encontrado"}), 404

    if cantidad > prod.get("stock", 0):
        return jsonify({"error": "Stock insuficiente", "disponible": prod["stock"]}), 400

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

@app.route("/pedidos", methods=["GET"])
@login_required(api=True)
def obtener_pedidos():
    return jsonify(leer_json(PEDIDOS_FILE))

if __name__ == "__main__":
    print("\nInventario - http://localhost:5001")
    app.run(debug=True, port=5001)
