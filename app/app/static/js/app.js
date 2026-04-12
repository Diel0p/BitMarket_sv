/* ── BitMarket SV — Frontend JS ──────────────────────────── */

const API = '/api';

// ── Token helpers ─────────────────────────────────────────
const auth = {
  get token() { return localStorage.getItem('bm_token'); },
  get user()  { return JSON.parse(localStorage.getItem('bm_user') || 'null'); },
  set(token, user) {
    localStorage.setItem('bm_token', token);
    localStorage.setItem('bm_user', JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem('bm_token');
    localStorage.removeItem('bm_user');
  },
  isLoggedIn() { return !!this.token; },
  role() { return this.user?.role || null; },
};

// ── Fetch wrapper ─────────────────────────────────────────
async function apiFetch(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...opts.headers };
  if (auth.token) headers['Authorization'] = `Bearer ${auth.token}`;
  const res = await fetch(API + path, { ...opts, headers });
  const data = await res.json();
  if (!res.ok) throw { status: res.status, message: data.detail || data.message || 'Error' };
  return data;
}

// ── Format helpers ────────────────────────────────────────
function formatSats(n) {
  if (!n && n !== 0) return '—';
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(2) + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(0) + 'k';
  return n.toLocaleString();
}

function sats2btc(s) { return (s / 1e8).toFixed(8); }

function statusPill(status) {
  const map = {
    paid: 'pill-paid', confirmed: 'pill-paid', delivered: 'pill-paid',
    active: 'pill-active',
    failed: 'pill-failed', cancelled: 'pill-failed', rejected: 'pill-failed',
    shipped: 'pill-shipped',
  };
  const cls = map[status] || 'pill-pending';
  return `<span class="pill ${cls}">${status}</span>`;
}

function timeAgo(dateStr) {
  const d = new Date(dateStr), now = Date.now();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return Math.floor(diff/60) + 'm ago';
  if (diff < 86400) return Math.floor(diff/3600) + 'h ago';
  return Math.floor(diff/86400) + 'd ago';
}

// ── Navbar hydration ──────────────────────────────────────
function hydrateNavbar() {
  const el = document.getElementById('navbar-auth');
  if (!el) return;
  if (auth.isLoggedIn()) {
    const u = auth.user;
    if (!u) {
      auth.clear();
      return hydrateNavbar();
    }
    const roleClass = `badge-${u.role}`;
    el.innerHTML = `
      <span class="navbar__role-badge ${roleClass}">${u.role}</span>
      <div class="navbar__avatar" title="${u.name}">${u.name[0].toUpperCase()}</div>
      ${u.role === 'seller' ? '<a href="/seller" class="navbar__link">Dashboard</a>' : ''}
      ${u.role === 'admin'  ? '<a href="/admin"  class="navbar__link">Admin</a>' : ''}
      ${u.role === 'buyer'  ? '<a href="/orders" class="navbar__link">Orders</a>' : ''}
      <button class="navbar__link" onclick="logout()">Logout</button>
    `;
  } else {
    el.innerHTML = `
      <a href="/login"    class="navbar__link">Login</a>
      <a href="/register" class="navbar__btn">Sign up</a>
    `;
  }
}

function logout() {
  auth.clear();
  window.location.href = '/';
}

// ── Error display ─────────────────────────────────────────
function showError(containerId, msg) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = `<div class="alert alert-error">${msg}</div>`;
}
function showSuccess(containerId, msg) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = `<div class="alert alert-success">${msg}</div>`;
}
function clearMsg(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = '';
}

// ── Product card builder ──────────────────────────────────
function productCard(p) {
  const emoji = { Electronics:'💻', Books:'📚', Art:'🎨', Gaming:'🎮', 'Art & Collectibles':'🎨' }[p.category] || '📦';
  const coverImage = p.images && p.images.length ? p.images[0] : null;
  return `
    <div class="product-card fade-in">
      <div class="product-card__img">${coverImage
        ? `<img src="${coverImage}" alt="${p.title}" style="width:100%;height:100%;object-fit:cover;border-radius:inherit" />`
        : emoji}
      </div>
      <div class="product-card__body">
        <p class="product-card__cat">${p.category}</p>
        <h3 class="product-card__title">${p.title}</h3>
        <p class="product-card__seller">by ${p.seller_name || 'Unknown'}</p>
        <div class="product-card__footer">
          <div>
            <span class="price-sats">⚡ ${formatSats(p.price_sats)}</span>
            <span class="price-unit"> sats</span>
          </div>
          <a href="/products/${p.id}" class="btn btn-sm btn-outline">View</a>
        </div>
      </div>
    </div>
  `;
}

// ── Run on every page ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  hydrateNavbar();

  // Navbar search
  const searchForm = document.getElementById('search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', e => {
      e.preventDefault();
      const q = document.getElementById('search-input').value.trim();
      if (q) window.location.href = `/products?q=${encodeURIComponent(q)}`;
    });
  }
});
