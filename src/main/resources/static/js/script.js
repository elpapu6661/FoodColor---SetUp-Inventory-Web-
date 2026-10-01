// SLIDER
let slideIndex = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');

function showSlide(n) {
  slides.forEach(s => s.classList.remove('active'));
  dots.forEach(d => {
    d.classList.remove('active');
    d.setAttribute('aria-selected', 'false');
  });
  slideIndex = (n + slides.length) % slides.length;
  slides[slideIndex].classList.add('active');
  dots[slideIndex].classList.add('active');
  dots[slideIndex].setAttribute('aria-selected', 'true');
}

dots.forEach(d => d.addEventListener('click', () => showSlide(parseInt(d.dataset.slide))));
setInterval(() => showSlide(slideIndex + 1), 4000);

const grid = document.getElementById('grid');
const search = document.getElementById('search');
const filterBtns = document.querySelectorAll('.filters button');
let currentCat = 'all';

function fmtPrice(val) {
  const n = parseFloat(val);
  if (isNaN(n)) return '';
  return '$' + n.toLocaleString('es-CL');
}

async function loadProducts() {
  try {
    const res = await fetch(`/api/public/productos?category=${currentCat}&q=${encodeURIComponent(search.value)}`);
    const data = await res.json();
    renderGrid(data);
  } catch (err) {
    console.error('Error cargando productos:', err);
    grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;padding:40px;color:var(--ink-mid);">Error al cargar productos</p>';
  }
}

function renderGrid(data) {
  grid.innerHTML = data.map(p => {
    const imgHtml = p.img
      ? `<img src="${p.img}" alt="${p.name}">`
      : `<div class="card-img-placeholder" style="background:linear-gradient(135deg,var(--primary),var(--secondary));height:180px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;font-weight:700;color:#fff;">${p.name.charAt(0)}</div>`;
    return `<div class="card">
      ${imgHtml}
      <h3>${p.name}</h3>
      <p>${p.desc || ''}</p>
      <div class="card-footer">
        <span class="card-price">${fmtPrice(p.precio)}</span>
        <span class="card-stock">Stock: ${p.stock ?? '—'}</span>
      </div>
    </div>`;
  }).join('');
  document.querySelectorAll('.card').forEach((c, i) => {
    setTimeout(() => c.classList.add('show'), i * 100);
  });
}

filterBtns.forEach(btn => btn.addEventListener('click', () => {
  filterBtns.forEach(b => {
    b.classList.remove('active');
    b.setAttribute('aria-pressed', 'false');
  });
  btn.classList.add('active');
  btn.setAttribute('aria-pressed', 'true');
  currentCat = btn.dataset.cat;
  loadProducts();
}));

search.addEventListener('input', () => loadProducts());

// formulario contacto
document.getElementById('contact-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const payload = Object.fromEntries(new FormData(form));
  const status = document.getElementById('form-status');
  try {
    const res = await fetch('/api/public/contact', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    status.textContent = data.ok ? '✅ Mensaje enviado' : '❌ ' + data.error;
    status.className = data.ok ? 'ok' : 'error';
    if (data.ok) form.reset();
  } catch (err) {
    status.textContent = '❌ Error de conexión';
    status.className = 'error';
  }
});

// scroll suave
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    const target = document.querySelector(a.getAttribute('href'));
    if (target) target.scrollIntoView({behavior:'smooth'});
  });
});

loadProducts();