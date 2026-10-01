const API = '/api/inventory';
let productosCache = [];
let selectedId = null;

function showAlert(msg, isError) {
  const container = document.getElementById('alertContainer');
  const alert = document.createElement('div');
  alert.className = 'alert ' + (isError ? 'alert-error' : 'alert-success');
  alert.innerHTML = '<span>' + msg + '</span><button class="alert-close" onclick="this.parentElement.remove()">×</button>';
  container.appendChild(alert);
  if (!isError) setTimeout(() => alert.remove(), 4000);
}

function esc(str) { return String(str).replace(/&/g,'&').replace(/</g,'<').replace(/>/g,'>').replace(/"/g,'"'); }

function fmt(val) { const n = parseFloat(val); if (isNaN(n)) return '—'; return '$' + n.toLocaleString('es-CL'); }

async function checkStatus() {
  const dot = document.getElementById('statusDot');
  const txt = document.getElementById('statusText');
  try {
    const r = await fetch(API + '/productos', { signal: AbortSignal.timeout(3000) });
    if (r.status === 401) { window.location.href = '/login'; return; }
    if (r.ok) { dot.classList.add('online'); txt.textContent = 'SERVIDOR ACTIVO'; }
    else throw new Error();
  } catch { dot.classList.remove('online'); txt.textContent = 'SIN CONEXIÓN'; }
}

function switchTab(tab) {
  document.querySelectorAll('.section-view').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + tab).classList.add('active');
  document.querySelector('[data-tab="' + tab + '"]').classList.add('active');
  if (tab === 'stock') cargarTablaStock();
  if (tab === 'pedido') cargarSelectorProductos();
}

async function cargarProductos() {
  try {
    const r = await fetch(API + '/productos');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    productosCache = await r.json();
    const tot = document.getElementById('totalProductos');
    if (tot) tot.textContent = productosCache.length;
    return productosCache;
  } catch (err) {
    showAlert('Error al conectar con el servidor.', true);
    return null;
  }
}

async function cargarTablaStock() {
  const tbody = document.getElementById('tablaStock');
  const sub = document.getElementById('stockSubtitle');
  tbody.innerHTML = '<tr class="skeleton-row"><td colspan="7"></td></tr><tr class="skeleton-row"><td colspan="7"></td></tr><tr class="skeleton-row"><td colspan="7"></td></tr>';
  const productos = await cargarProductos();
  if (!productos) {
    tbody.innerHTML = '<tr><td colspan="7"><div class="error-box">No se pudo conectar con el servidor.</div></td></tr>';
    sub.textContent = 'Error al cargar datos';
    return;
  }
  const criticos = productos.filter(p => p.stock < 25).length;
  sub.textContent = productos.length + ' producto' + (productos.length !== 1 ? 's' : '') + ' registrado' + (productos.length !== 1 ? 's' : '') + (criticos ? ' · <span style="color:var(--danger)">⚠ ' + criticos + ' crítico' + (criticos !== 1 ? 's' : '') + '</span>' : '');
  if (productos.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><div class="empty-icon">🎨</div><p>Sin productos registrados.</p></div></td></tr>';
    return;
  }
  tbody.innerHTML = productos.map((p, i) => {
    const esCritico = p.stock < 25;
    const esBajo = p.stock < 5;
    return '<tr class="' + (esCritico ? 'stock-critico' : '') + '">' +
      '<td style="color:var(--ink-light);font-family:var(--mono);font-size:0.8rem;">' + (i + 1) + '</td>' +
      '<td><strong>' + esc(p.name) + '</strong></td>' +
      '<td><span class="badge badge-tipo">' + esc(p.category || '—') + '</span></td>' +
      '<td><span class="badge badge-tipo">' + esc(p.tipoUnidad || '—') + '</span></td>' +
      '<td><span class="price-text">' + fmt(p.precio) + '</span></td>' +
      '<td><span class="stock-num ' + (esCritico ? 'badge badge-critico' : esBajo ? 'badge badge-low' : '') + '">' + (p.stock ?? '—') + '</span>' +
      (esCritico ? '<span class="badge badge-critico-texto">CRÍTICO</span>' : esBajo ? '<span style="font-size:0.7rem;color:var(--warning);margin-left:6px;">Stock bajo</span>' : '') + '</td>' +
      '<td><button class="btn btn-sm btn-outline" onclick="abrirEditarStock(' + p.id + ', ' + p.stock + ', \'' + esc(p.name) + '\')">Editar</button></td></tr>';
  }).join('');
}

async function agregarProducto() {
  const nombre = document.getElementById('inv_nombre').value.trim();
  const category = document.getElementById('inv_category').value;
  const tipo = document.getElementById('inv_tipo').value.trim();
  const desc = document.getElementById('inv_desc').value.trim();
  const precio = document.getElementById('inv_precio').value.trim();
  const stock = document.getElementById('inv_stock').value.trim();

  if (!nombre) { showAlert('El nombre del producto es obligatorio.', true); return; }
  if (precio === '') { showAlert('Ingresa el precio.', true); return; }
  if (!stock || parseInt(stock) < 1) { showAlert('La cantidad debe ser mayor a 0.', true); return; }

  const btn = document.getElementById('btnAgregar');
  btn.disabled = true;
  btn.textContent = 'Registrando…';

  try {
    const r = await fetch(API + '/productos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: nombre, category, tipoUnidad: tipo, desc, precio: parseFloat(precio), stock: parseInt(stock) })
    });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const data = await r.json();
    showAlert('✓ ' + data.mensaje);
    document.getElementById('inv_nombre').value = '';
    document.getElementById('inv_tipo').value = '';
    document.getElementById('inv_desc').value = '';
    document.getElementById('inv_precio').value = '';
    document.getElementById('inv_stock').value = '';
    await cargarProductos();
  } catch (err) {
    showAlert('Error al registrar: ' + err.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = '+ Registrar en Inventario';
  }
}

async function cargarSelectorProductos() {
  const sel = document.getElementById('productSelector');
  if (!sel) return;
  sel.innerHTML = '<div style="font-size:0.8rem;color:var(--ink-light);padding:10px;">Cargando…</div>';
  selectedId = null;
  const productos = await cargarProductos();
  if (!productos || productos.length === 0) {
    sel.innerHTML = '<div style="font-size:0.8rem;color:var(--ink-light);padding:10px;">No hay productos disponibles.</div>';
    return;
  }
  sel.innerHTML = productos.map(p => {
    const stockBajo = p.stock < 5;
    return '<div class="product-option' + (stockBajo ? ' stock-bajo' : '') + '" data-id="' + p.id + '" onclick="seleccionarProducto(' + p.id + ')">' +
      '<div><div class="po-name">' + esc(p.name) + (stockBajo ? ' <span class="badge badge-low" style="font-size:0.6rem;margin-left:6px;">Poco stock</span>' : '') + '</div>' +
      '<div class="po-info">' + esc(p.tipoUnidad || '—') + ' · Stock: ' + (p.stock ?? '?') + '</div></div>' +
      '<div class="po-price">' + fmt(p.precio) + '</div></div>';
  }).join('');
}

function seleccionarProducto(id) {
  document.querySelectorAll('.product-option').forEach(el => el.classList.remove('selected'));
  const el = document.querySelector('.product-option[data-id="' + id + '"]');
  if (el) el.classList.add('selected');
  selectedId = id;

  const prod = productosCache.find(p => p.id === id);
  if (prod && prod.stock < 5) {
    showAlert('⚠ Poco stock: "' + esc(prod.name) + '" tiene solo ' + prod.stock + ' unidades', true);
  }
}

function abrirEditarStock(id, stockActual, nombre) {
  const nuevoStock = prompt('Editar stock para: ' + nombre + '\nStock actual: ' + stockActual + '\n\nNuevo stock:', stockActual);
  if (nuevoStock === null) return;
  const stock = parseInt(nuevoStock);
  if (isNaN(stock) || stock < 0) { showAlert('Stock inválido. Debe ser un número mayor o igual a 0.', true); return; }
  editarStock(id, stock, nombre);
}

async function editarStock(id, stock, nombre) {
  try {
    const r = await fetch(API + '/productos/' + id + '/stock', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stock })
    });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.error || 'HTTP ' + r.status);
    }
    const data = await r.json();
    showAlert('✓ Stock de "' + esc(nombre) + '" actualizado a ' + stock);
    await cargarProductos();
    if (document.getElementById('tab-stock').classList.contains('active')) cargarTablaStock();
    if (document.getElementById('tab-pedido').classList.contains('active')) cargarSelectorProductos();
  } catch (err) {
    showAlert('Error al actualizar stock: ' + err.message, true);
  }
}

async function generarPedido() {
  const cliente = document.getElementById('ped_cliente').value.trim();
  const cantidad = parseInt(document.getElementById('ped_cantidad').value);

  if (!cliente) { showAlert('Ingresa el nombre del cliente.', true); return; }
  if (!selectedId) { showAlert('Selecciona un producto.', true); return; }
  if (!cantidad || cantidad < 1) { showAlert('La cantidad debe ser mayor a 0.', true); return; }

  const prod = productosCache.find(p => p.id === selectedId);
  if (!prod) { showAlert('Producto no encontrado.', true); return; }
  if (cantidad > prod.stock) { showAlert('Excede el stock del producto seleccionado', true); return; }

  const btn = document.getElementById('btnPedido');
  btn.disabled = true;
  btn.textContent = 'Procesando…';

  try {
    const r = await fetch(API + '/pedidos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cliente, productoId: selectedId, cantidad })
    });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.error || 'HTTP ' + r.status);
    }
    const data = await r.json();
    const ahora = new Date();
    const fecha = ahora.toLocaleDateString('es-CL', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' });
    const totalPago = cantidad * prod.precio;
    const nroBoleta = 'BOL-' + ahora.getFullYear() + String(ahora.getMonth()+1).padStart(2,'0') + String(ahora.getDate()).padStart(2,'0') + '-' + String(ahora.getHours()).padStart(2,'0') + String(ahora.getMinutes()).padStart(2,'0') + String(ahora.getSeconds()).padStart(2,'0');

    document.getElementById('boletaContainer').innerHTML =
      '<div class="boleta-wrap">' +
        '<div class="boleta-header"><div class="boleta-logo">ColorFood</div><div class="boleta-tagline">Distribuidora de Colorantes Alimenticios</div></div>' +
        '<div class="boleta-stripe"></div>' +
        '<div class="boleta-body">' +
          '<div class="boleta-meta"><div>Fecha<br><strong>' + fecha + '</strong></div><div style="text-align:right">Cliente<br><strong>' + esc(cliente) + '</strong></div></div>' +
          '<div class="boleta-row"><span class="label">N° Boleta</span><span class="val">' + esc(nroBoleta) + '</span></div>' +
          '<div class="boleta-row"><span class="label">Producto</span><span class="val">' + esc(prod.name) + '</span></div>' +
          '<div class="boleta-row"><span class="label">Tipo / Unidad</span><span class="val">' + esc(prod.tipoUnidad || '—') + '</span></div>' +
          '<div class="boleta-row"><span class="label">Cantidad</span><span class="val">' + cantidad + '</span></div>' +
          '<div class="boleta-row"><span class="label">Precio unitario</span><span class="val">' + fmt(prod.precio) + '</span></div>' +
          '<div class="boleta-total"><span class="total-label">TOTAL A PAGAR</span><span class="total-amount">' + fmt(totalPago) + '</span></div>' +
        '</div>' +
        '<div class="boleta-footer">Gracias por su compra · Stock restante: <strong>' + data.stockRestante + '</strong></div>' +
        '<div style="padding:0 32px 24px;text-align:center;"><button class="btn btn-outline" onclick="window.print()" style="font-size:0.75rem;padding:10px 24px;">🖨 Imprimir / Guardar PDF</button></div>' +
      '</div>';

    showAlert('✓ Boleta generada correctamente');
    document.getElementById('ped_cliente').value = '';
    document.getElementById('ped_cantidad').value = '';
    selectedId = null;
  } catch (err) {
    showAlert('Error: ' + err.message, true);
  } finally {
    btn.disabled = false;
    btn.textContent = '🧾 Generar Boleta';
    await cargarProductos();
    await cargarSelectorProductos();
  }
}

['inv_nombre','inv_tipo','inv_precio','inv_stock'].forEach(id => {
  document.getElementById(id)?.addEventListener('keydown', e => { if (e.key === 'Enter') agregarProducto(); });
});

checkStatus();
cargarProductos();
setInterval(checkStatus, 15000);