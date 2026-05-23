/* ── BitMarket SV — Frontend JS ──────────────────────────── */

const API = '/api';

function formatApiError(detail) {
  if (!detail) return 'Error';
  if (typeof detail === 'string') return detail;

  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (!item) return null;
        if (typeof item === 'string') return item;
        if (typeof item === 'object') {
          const field = Array.isArray(item.loc) ? item.loc.filter(p => p !== 'body').join('.') : '';
          const message = item.msg || item.message;
          if (field && message) return `${field}: ${message}`;
          if (message) return message;
        }
        return String(item);
      })
      .filter(Boolean);
    return parts.length ? parts.join(' | ') : 'Validation error';
  }

  if (typeof detail === 'object') {
    if (typeof detail.message === 'string') return detail.message;
    if (typeof detail.msg === 'string') return detail.msg;
    try {
      return JSON.stringify(detail);
    } catch {
      return 'Error';
    }
  }

  return String(detail);
}

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
  if (!res.ok) throw { status: res.status, message: formatApiError(data.detail || data.message || data) };
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
      ${u.role === 'buyer'  ? '<a href="/cart" class="navbar__link navbar__cart-link" title="Carrito"><span class="cart-icon-wrap">🛒<span id="cart-count-badge" class="cart-count-badge">0</span></span></a>' : ''}
      <button class="navbar__link" onclick="logout()">Logout</button>
    `;
    refreshCartCount();
  } else {
    el.innerHTML = `
      <a href="/login"    class="navbar__link">Login</a>
      <a href="/register" class="navbar__btn">Sign up</a>
    `;
    updateCartIndicators(0);
  }
}

function getCartItemCount(cart) {
  const items = cart?.items || [];
  return items.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
}

function ensureFloatingCartButton() {
  let floating = document.getElementById('floating-cart-link');
  if (floating) return floating;

  floating = document.createElement('a');
  floating.id = 'floating-cart-link';
  floating.className = 'floating-cart-link';
  floating.href = '/cart';
  floating.innerHTML = '🛒 <span id="floating-cart-count" class="floating-cart-count">0</span>';
  floating.style.display = 'none';
  document.body.appendChild(floating);
  return floating;
}

function updateCartIndicators(count) {
  const badge = document.getElementById('cart-count-badge');
  if (badge) {
    badge.textContent = String(count);
    badge.style.display = 'inline-flex';
  }

  const floating = ensureFloatingCartButton();
  const floatingCount = document.getElementById('floating-cart-count');
  const showFloating = auth.isLoggedIn() && auth.role() === 'buyer' && !window.location.pathname.startsWith('/cart');

  floating.style.display = showFloating ? 'inline-flex' : 'none';
  if (floatingCount) floatingCount.textContent = String(count);
}

async function refreshCartCount() {
  if (!auth.isLoggedIn() || auth.role() !== 'buyer') {
    updateCartIndicators(0);
    return 0;
  }

  try {
    const data = await apiFetch('/cart');
    const count = getCartItemCount(data?.cart);
    updateCartIndicators(count);
    return count;
  } catch (_) {
    updateCartIndicators(0);
    return 0;
  }
}

window.refreshCartCount = refreshCartCount;

function logout() {
  auth.clear();
  window.location.href = '/';
}

// ── Error display ─────────────────────────────────────────
function showError(containerId, msg) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const text = typeof msg === 'string'
    ? msg
    : formatApiError(msg);
  el.textContent = '';
  const box = document.createElement('div');
  box.className = 'alert alert-error';
  box.textContent = text || 'Error';
  el.appendChild(box);
}
function showSuccess(containerId, msg) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.textContent = '';
  const box = document.createElement('div');
  box.className = 'alert alert-success';
  box.textContent = String(msg || '');
  el.appendChild(box);
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
  refreshCartCount();

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
