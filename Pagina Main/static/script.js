// SLIDER
let slideIndex = 0;
const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.dot');

function showSlide(n) {
  slides.forEach(s => s.classList.remove('active'));
  dots.forEach(d => d.classList.remove('active'));
  slideIndex = (n + slides.length) % slides.length;
  slides[slideIndex].classList.add('active');
  dots[slideIndex].classList.add('active');
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
  const res = await fetch(`/api/productos?category=${currentCat}&q=${search.value}`);
  const data = await res.json();
  renderGrid(data);
}

function renderGrid(data) {
  grid.innerHTML = data.map(p => {
    const imgHtml = p.img
      ? `<img src="${p.img}" alt="${p.name}">`
      : `<div class="card-img-placeholder" style="background:linear-gradient(135deg,var(--primary),var(--secondary));height:160px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;font-weight:700;color:#fff;">${p.name.charAt(0)}</div>`;
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
  // animación de entrada escalonada
  document.querySelectorAll('.card').forEach((c, i) => {
    setTimeout(() => c.classList.add('show'), i * 100);
  });
}

filterBtns.forEach(btn => btn.addEventListener('click', () => {
  filterBtns.forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
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
  const res = await fetch('/api/contact', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  status.textContent = data.ok ? '✅ Mensaje enviado' : '❌ ' + data.error;
  if (data.ok) form.reset();
});

// scroll suave
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    document.querySelector(a.getAttribute('href')).scrollIntoView({behavior:'smooth'});
  });
});

loadProducts();