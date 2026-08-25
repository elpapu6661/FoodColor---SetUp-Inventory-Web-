from flask import Flask, render_template, request, jsonify
import json, os

app = Flask(__name__)

DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

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

# ── PÁGINA PRINCIPAL ──

@app.route("/")
def index():
    return render_template("index.html")

# ── API PRODUCTOS (solo lectura) ──

@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    category = request.args.get("category", "all")
    search = request.args.get("q", "").lower()
    productos = leer_json(PRODUCTS_FILE)
    if category != "all":
        productos = [p for p in productos if p.get("category") == category]
    if search:
        productos = [p for p in productos if search in p.get("name", "").lower()]
    return jsonify(productos)

# ── API CONTACTO ──

@app.route("/api/contact", methods=["POST"])
def contact():
    payload = request.get_json(force=True)
    required = ["name", "email", "message"]
    if not all(payload.get(k) for k in required):
        return jsonify({"ok": False, "error": "Campos incompletos"}), 400
    print("Nuevo contacto:", payload)
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
