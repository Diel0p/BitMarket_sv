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

// ── BTC to USD conversion (El Salvador) ───────────────────
let btcUsdRate = null;
let lastFetchTime = 0;
const CACHE_DURATION = 60000; // 1 minuto

// Obtener precio BTC/USD en tiempo real
async function fetchBtcUsdRate() {
  const now = Date.now();
  // Usar cache si es reciente (menos de 1 minuto)
  if (btcUsdRate && (now - lastFetchTime) < CACHE_DURATION) {
    return btcUsdRate;
  }

  try {
    // API gratuita de CoinGecko (sin necesidad de API key)
    const res = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd');
    const data = await res.json();
    btcUsdRate = data.bitcoin.usd;
    lastFetchTime = now;
    return btcUsdRate;
  } catch (error) {
    console.warn('Error obteniendo precio BTC/USD:', error);
    // Fallback: usar precio aproximado si falla la API
    return btcUsdRate || 100000; // Precio de respaldo
  }
}

// Convertir satoshis a USD
function sats2usd(sats, rate) {
  if (!sats || !rate) return null;
  const btc = sats / 1e8;
  const usd = btc * rate;
  return usd.toFixed(2);
}

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
      <a href="/nosotros" class="navbar__link">Nosotros</a>
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
      <a href="/nosotros" class="navbar__link">Nosotros</a>
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

// ── Reusable UI states ───────────────────────────────────
function productGridSkeleton(count = 8) {
  return Array.from({ length: count }, () => `
    <div class="product-skeleton-card" aria-hidden="true">
      <div class="skeleton skeleton-media"></div>
      <div class="product-skeleton-card__body">
        <div class="skeleton skeleton-line skeleton-line--sm"></div>
        <div class="skeleton skeleton-line"></div>
        <div class="skeleton skeleton-line skeleton-line--lg"></div>
        <div class="product-skeleton-card__footer">
          <div class="skeleton skeleton-line skeleton-line--price"></div>
          <div class="skeleton skeleton-chip"></div>
        </div>
      </div>
    </div>
  `).join('');
}

function tableSkeleton(rows = 6, cols = 6) {
  const header = Array.from({ length: cols }, () => '<th><div class="skeleton skeleton-line skeleton-line--sm"></div></th>').join('');
  const body = Array.from({ length: rows }, () => `
    <tr>
      ${Array.from({ length: cols }, () => '<td><div class="skeleton skeleton-line"></div></td>').join('')}
    </tr>
  `).join('');

  return `
    <div class="table-wrap" aria-hidden="true">
      <table>
        <thead><tr>${header}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}

function cardListSkeleton(count = 3) {
  return Array.from({ length: count }, () => `
    <div class="card" style="margin-bottom:16px" aria-hidden="true">
      <div class="card-body">
        <div class="skeleton skeleton-line skeleton-line--lg" style="margin-bottom:12px"></div>
        <div class="skeleton skeleton-line" style="margin-bottom:8px"></div>
        <div class="skeleton skeleton-line" style="margin-bottom:8px"></div>
        <div class="skeleton skeleton-line skeleton-line--sm"></div>
      </div>
    </div>
  `).join('');
}

function emptyState(options = {}) {
  const icon = options.icon || '📭';
  const title = options.title || 'No hay resultados';
  const description = options.description || '';
  const actionHref = options.actionHref || '';
  const actionText = options.actionText || '';

  return `
    <div class="empty-state empty-state-card fade-in">
      <div class="empty-state__icon">${icon}</div>
      <h3 class="empty-state__title">${title}</h3>
      ${description ? `<p class="empty-state__desc">${description}</p>` : ''}
      ${actionHref && actionText ? `<a href="${actionHref}" class="btn btn-primary btn-sm">${actionText}</a>` : ''}
    </div>
  `;
}

window.ui = {
  productGridSkeleton,
  tableSkeleton,
  cardListSkeleton,
  emptyState,
};

// ── Toasts and confirms ───────────────────────────────────
function ensureToastRoot() {
  let root = document.getElementById('toast-root');
  if (root) return root;

  root = document.createElement('div');
  root.id = 'toast-root';
  root.className = 'toast-root';
  document.body.appendChild(root);
  return root;
}

function toast(message, type = 'info', timeout = 2800) {
  const root = ensureToastRoot();
  const item = document.createElement('div');
  item.className = `toast toast-${type}`;
  item.textContent = String(message || '');
  root.appendChild(item);

  setTimeout(() => {
    item.classList.add('toast-leave');
    setTimeout(() => item.remove(), 220);
  }, timeout);
}

window.showToast = toast;

function ensureConfirmModal() {
  let modal = document.getElementById('confirm-modal');
  if (modal) return modal;

  modal = document.createElement('div');
  modal.id = 'confirm-modal';
  modal.className = 'confirm-modal';
  modal.innerHTML = `
    <div class="confirm-card" role="dialog" aria-modal="true" aria-live="polite">
      <h3 id="confirm-title" class="confirm-title">Confirmar accion</h3>
      <p id="confirm-text" class="confirm-text">Estas seguro?</p>
      <div class="confirm-actions">
        <button id="confirm-cancel" class="btn btn-ghost btn-sm" type="button">Cancelar</button>
        <button id="confirm-accept" class="btn btn-primary btn-sm" type="button">Confirmar</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      modal.style.display = 'none';
      if (typeof modal._resolve === 'function') modal._resolve(false);
    }
  });

  return modal;
}

function confirmAction(message, opts = {}) {
  const modal = ensureConfirmModal();
  const titleEl = modal.querySelector('#confirm-title');
  const textEl = modal.querySelector('#confirm-text');
  const cancelBtn = modal.querySelector('#confirm-cancel');
  const acceptBtn = modal.querySelector('#confirm-accept');

  titleEl.textContent = opts.title || 'Confirmar accion';
  textEl.textContent = message || 'Estas seguro?';
  cancelBtn.textContent = opts.cancelText || 'Cancelar';
  acceptBtn.textContent = opts.confirmText || 'Confirmar';

  modal.style.display = 'flex';

  return new Promise((resolve) => {
    const clean = (value) => {
      modal.style.display = 'none';
      cancelBtn.onclick = null;
      acceptBtn.onclick = null;
      modal._resolve = null;
      resolve(value);
    };

    modal._resolve = clean;
    cancelBtn.onclick = () => clean(false);
    acceptBtn.onclick = () => clean(true);
  });
}

window.confirmAction = confirmAction;

// ── Product card builder ──────────────────────────────────
function productCard(p) {
  const emoji = { Electronics:'💻', Books:'📚', Art:'🎨', Gaming:'🎮', 'Art & Collectibles':'🎨' }[p.category] || '📦';
  const coverImage = p.images && p.images.length ? p.images[0] : null;
  const usdAmount = btcUsdRate ? sats2usd(p.price_sats, btcUsdRate) : null;
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
            <div style="display:flex;flex-direction:column;gap:2px">
              <span class="price-sats">⚡ ${formatSats(p.price_sats)}</span>
              ${usdAmount ? `<span class="text-muted text-xs" style="color:#16a34a">≈ $${usdAmount} USD</span>` : ''}
            </div>
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
