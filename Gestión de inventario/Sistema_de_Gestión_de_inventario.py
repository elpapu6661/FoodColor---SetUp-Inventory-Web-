from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

ARCHIVO = "productos.json"
PEDIDOS  = "pedidos.json"

# ── HELPERS ───────────────────────────────────────────────

def leer(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# ── PRODUCTOS ─────────────────────────────────────────────

@app.route("/productos", methods=["GET"])
def obtener_productos():
    return jsonify(leer(ARCHIVO))

@app.route("/productos", methods=["POST"])
def agregar_producto():
    nuevo   = request.json
    nombre  = nuevo.get("nombre", "").strip()
    tipo    = nuevo.get("tipo", "").strip()
    precio  = nuevo.get("precio")
    stock   = nuevo.get("stock", 0)

    if not nombre or precio is None:
        return jsonify({"error": "Faltan campos: nombre y precio son obligatorios"}), 400

    productos = leer(ARCHIVO)

    # Si ya existe, sumar stock y actualizar precio
    for p in productos:
        if p["nombre"].lower() == nombre.lower():
            p["stock"] += int(stock)
            p["precio"] = float(precio)
            if tipo:
                p["tipo"] = tipo
            guardar(ARCHIVO, productos)
            return jsonify({"mensaje": "Stock actualizado", "producto": p}), 200

    # Producto nuevo
    producto = {
        "nombre": nombre,
        "tipo":   tipo,
        "precio": float(precio),
        "stock":  int(stock)
    }
    productos.append(producto)
    guardar(ARCHIVO, productos)
    return jsonify({"mensaje": "Producto creado", "producto": producto}), 201

# ── PEDIDOS ───────────────────────────────────────────────

@app.route("/pedidos", methods=["POST"])
def crear_pedido():
    datos           = request.json
    cliente         = datos.get("cliente", "").strip()
    producto_idx    = datos.get("producto_idx")   # índice numérico en la lista
    cantidad_pedida = datos.get("cantidad")

    if not cliente or producto_idx is None or not cantidad_pedida:
        return jsonify({"error": "Faltan datos: cliente, producto_idx, cantidad"}), 400

    productos = leer(ARCHIVO)

    if producto_idx < 0 or producto_idx >= len(productos):
        return jsonify({"error": "Producto no encontrado"}), 404

    prod         = productos[producto_idx]
    stock_actual = prod.get("stock", 0)

    if cantidad_pedida > stock_actual:
        return jsonify({"error": "Stock insuficiente", "disponible": stock_actual}), 400

    # Descontar stock
    prod["stock"] -= cantidad_pedida
    guardar(ARCHIVO, productos)

    total_pago   = cantidad_pedida * prod["precio"]
    fecha_boleta = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    boleta = {
        "cliente":          cliente,
        "producto":         prod["nombre"],
        "detalle":          prod["tipo"],
        "cantidad_vendida": cantidad_pedida,
        "precio_unitario":  prod["precio"],
        "total_pago":       total_pago,
        "fecha":            fecha_boleta
    }

    # Guardar historial de pedidos
    pedidos = leer(PEDIDOS)
    pedidos.append(boleta)
    guardar(PEDIDOS, pedidos)

    return jsonify({
        "mensaje":        "Venta exitosa",
        "boleta":         boleta,
        "stock_restante": prod["stock"]
    }), 201

# ── PEDIDOS HISTORIAL ─────────────────────────────────────

@app.route("/pedidos", methods=["GET"])
def obtener_pedidos():
    return jsonify(leer(PEDIDOS))

# ── MAIN ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🎨 ColorFood — Sistema de Inventario")
    print("─" * 40)
    print(f"  Productos : {os.path.abspath(ARCHIVO)}")
    print(f"  Pedidos   : {os.path.abspath(PEDIDOS)}")
    print("  Servidor  : http://localhost:5000")
    print("─" * 40 + "\n")
    app.run(debug=True)