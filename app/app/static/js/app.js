/* ── BitMarket SV — Frontend JS ──────────────────────────── */

const API = '/api';

// ── Lightweight i18n (ES/EN) ───────────────────────────
const I18N = {
  en: {
    'nav.about': 'About us',
    'nav.login': 'Login',
    'nav.signup': 'Sign up',
    'nav.dashboard': 'Dashboard',
    'nav.admin': 'Admin',
    'nav.orders': 'Orders',
    'nav.cart': 'Cart',
    'nav.logout': 'Logout',
    'nav.search_placeholder': 'Search products...',
    'footer.built_by': 'Built by Cubo+ students.',
    'footer.support_project': 'Support the project',
    'footer.lightning_donations': 'Bitcoin Lightning donations',
    'home.badge': 'Powered by Bitcoin Lightning',
    'home.title_line_1': 'The marketplace',
    'home.title_line_2': 'for the Bitcoin economy',
    'home.subtitle': 'Buy and sell products with instant Bitcoin Lightning payments.',
    'home.subtitle_2': 'No banks. No waiting. No borders.',
    'home.browse_products': 'Browse products ->',
    'home.start_selling': 'Start selling',
    'home.perk_instant': 'Instant settlement',
    'home.perk_self_custodial': 'Self-custodial',
    'home.perk_built_sv': 'Built for El Salvador',
    'home.perk_low_fees': 'Near-zero fees',
    'home.browse_categories': 'Browse categories',
    'home.latest_products': 'Latest products',
    'home.see_all': 'See all ->',
    'home.cta_title': 'Start accepting Bitcoin today',
    'home.cta_text': 'Join hundreds of sellers already using Lightning payments.',
    'home.create_seller_account': 'Create seller account',
    'home.no_products': 'No products yet',
    'home.no_products_desc': 'Start the marketplace by publishing the first product.',
    'home.first_seller': 'Be the first seller',
    'home.load_error': 'Could not load products',
    'home.load_error_desc': 'Try reloading this page in a few seconds.',
    'about.kicker': 'Meet BitMarket SV',
    'about.title': 'Local commerce with Lightning payments, simple and real.',
    'about.subtitle_1': 'BitMarket connects buyers and sellers to power the local economy with Bitcoin Lightning:',
    'about.subtitle_2': 'instant payments, low fees, and a clear experience for everyone.',
    'about.cta_products': 'Browse products',
    'about.cta_sell': 'I want to sell',
    'about.mission_title': 'Our mission',
    'about.mission_text_1': 'Give small and medium sellers a modern digital storefront, with Bitcoin Lightning payments',
    'about.mission_text_2': 'that confirm in seconds and enable frictionless selling.',
    'about.how_title': 'How it works',
    'about.step_explore_label': 'Explore:',
    'about.step_explore_text': 'the buyer finds products in the catalog.',
    'about.step_pay_label': 'Pay:',
    'about.step_pay_text': 'a Lightning invoice is generated for fast payment.',
    'about.step_receive_label': 'Receive:',
    'about.step_receive_text': 'the order is confirmed and the seller manages shipping.',
    'about.trust_title': 'Transparency and security',
    'about.trust_text_1': 'BitMarket keeps basic traceability for orders and payments so each operation has a clear status.',
    'about.trust_text_2': 'Our goal is to make buying and selling trustworthy from the first click.',
    'about.contact_title': 'Contact and support',
    'about.contact_text': 'We are building together with the Bitcoin community of El Salvador.',
    'about.contact_email': 'Email:',
    'about.support_title': 'Support development',
    'about.support_text': 'This project is developed by students. Your support helps us maintain and improve it.',
    'about.support_cta': 'Donate with Lightning',
    'donate.page_title': 'Support the Project',
    'donate.hero_title': 'Support BitMarket SV',
    'donate.hero_text_1': 'This project is developed by Cubo+ students in El Salvador.',
    'donate.hero_text_2': 'Your support helps us maintain and improve the platform.',
    'donate.form_title': 'Donate with Lightning Network',
    'donate.amount_label': 'Enter donation amount (satoshis):',
    'donate.amount_suggested': 'Or choose a suggested amount:',
    'donate.generate': 'Generate Invoice',
    'donate.scanner_title': 'Scan to pay',
    'donate.amount_to_pay': 'Amount to donate:',
    'donate.copy_invoice': 'Copy Invoice',
    'donate.waiting': 'Waiting for payment...',
    'donate.change_amount': 'Change amount',
    'donate.success_title': 'Donation Received!',
    'donate.success_subtitle': 'Thank you for supporting BitMarket SV',
    'donate.you_donated': 'You donated:',
    'donate.success_text_1': 'Your support helps us maintain and improve this platform.',
    'donate.success_text_2': 'Every satoshi counts!',
    'donate.new_donation': 'Make another donation',
    'donate.uses_title': 'What are donations used for?',
    'donate.use_1': 'Server and database maintenance',
    'donate.use_2': 'Improvements and new features',
    'donate.use_3': 'Bug fixes and optimization',
    'donate.use_4': 'Documentation and tutorials',
    'donate.use_5': 'Coffee for developers',
    'donate.thanks_title': 'Thank you for your support!',
    'donate.thanks_text_1': 'Every satoshi counts and motivates us to keep building useful tools',
    'donate.thanks_text_2': 'for the Bitcoin community in El Salvador.',
    'donate.back_home': 'Back to home',
    'donate.alert_invalid_amount': 'Please enter a valid amount (minimum 1,000 sats).',
    'donate.loading': 'Generating...',
    'donate.error_generate': 'Error generating invoice',
    'donate.error_generate_retry': 'Error generating invoice. Please try again.',
    'donate.memo': 'Donation to BitMarket SV',
    'donate.expires_in': 'Expires in',
    'donate.alert_expired': 'The invoice has expired. Please generate a new one.',
    'donate.confirmed_log': 'Donation confirmed!',
    'donate.alert_copied': 'Invoice copied to clipboard!',
    'donate.error_copy': 'Error copying invoice:',
    'common.validation_error': 'Validation error',
    'common.error': 'Error',
    'common.just_now': 'just now',
    'common.minutes_ago': 'm ago',
    'common.hours_ago': 'h ago',
    'common.days_ago': 'd ago',
    'common.no_results': 'No results',
    'confirm.title': 'Confirm action',
    'confirm.message': 'Are you sure?',
    'confirm.cancel': 'Cancel',
    'confirm.accept': 'Confirm',
    'product.by': 'by',
    'product.unknown_seller': 'Unknown',
    'product.view': 'View',
    'checkout.subtitle': 'Review your order and pay with Lightning',
    'checkout.emptyTitle': 'Empty cart',
    'checkout.viewProducts': 'View products',
    'checkout.orderSummary': 'Order summary',
    'checkout.total': 'Total',
    'checkout.shippingAddress': 'Shipping Address',
    'checkout.fullName': 'Full name',
    'checkout.street': 'Street / Address',
    'checkout.city': 'City',
    'checkout.country': 'Country',
    'checkout.postalCode': 'Postal Code (optional)',
    'checkout.notes': 'Notes (optional)',
    'checkout.generateInvoice': 'Generate Lightning Invoice →',
    'checkout.generatingInvoice': 'Generating invoice…',
    'checkout.error_generateFailed': 'Error generating invoice',
    'checkout.amountToPay': 'Amount to pay',
    'checkout.sats': 'sats',
    'checkout.copyInvoice': '📋 Copy invoice',
    'checkout.cancelInvoice': '❌ Cancel invoice',
    'checkout.awaitingPayment': 'Awaiting payment...',
    'checkout.awaitingLightning': 'Awaiting Lightning payment…',
    'checkout.invoiceExpires': 'Invoice expires in',
    'checkout.invoiceExpired': 'Invoice expired',
    'checkout.mockMode': 'Mock mode',
    'checkout.mockInfo': 'payment will confirm automatically in',
    'checkout.mockSeconds': 'seconds',
    'checkout.mockConfirming': 'confirming in',
    'checkout.paymentConfirmed': 'Payment confirmed!',
    'checkout.orderSuccess': 'Your order has been successfully recorded.',
    'checkout.viewOrders': 'View my orders',
    'checkout.continueShopping': 'Continue shopping',
    'checkout.invoiceTitle': 'Invoice Expired',
    'checkout.invoiceExpiredMsg': 'The time to pay this invoice has expired (5 minutes). Your cart remains intact so you can generate a new invoice.',
    'checkout.retry': '🔄 Retry',
    'checkout.backCart': '🛒 Back to cart',
    'checkout.shopping': '🏠 Continue shopping',
    'checkout.error_noInvoice': 'No active invoice to cancel',
    'checkout.cancelConfirm': 'This invoice will be cancelled and your products will remain in your cart. Do you want to continue?',
    'checkout.cancelTitle': 'Cancel invoice',
    'checkout.yes': 'Yes, cancel',
    'checkout.cancelSuccess': 'Invoice cancelled. Your cart remains intact.',
    'checkout.error_cancelFailed': 'Could not cancel the invoice',
    'checkout.error_retryFailed': 'Could not generate a new invoice',
    'checkout.invoiceCopied': 'Invoice copied',
    'checkout.error_nameRequired': 'Name is required.',
    'checkout.error_addressRequired': 'Address is required.',
    'checkout.error_cityRequired': 'City is required.',
    'checkout.error_countryRequired': 'Country is required.',
    'checkout.error_invalidChars': 'contains invalid characters.',
    'checkout.error_tooShort': 'is too short.',
    'checkout.error_tooLong': 'exceeds the maximum allowed.',
    'common.no': 'No',
  },
  es: {
    'nav.about': 'Nosotros',
    'nav.login': 'Iniciar sesion',
    'nav.signup': 'Crear cuenta',
    'nav.dashboard': 'Panel',
    'nav.admin': 'Admin',
    'nav.orders': 'Pedidos',
    'nav.cart': 'Carrito',
    'nav.logout': 'Cerrar sesion',
    'nav.search_placeholder': 'Buscar productos...',
    'footer.built_by': 'Creado por estudiantes de Cubo+.',
    'footer.support_project': 'Apoyar el proyecto',
    'footer.lightning_donations': 'Donaciones con Bitcoin Lightning',
    'home.badge': 'Impulsado por Bitcoin Lightning',
    'home.title_line_1': 'El marketplace',
    'home.title_line_2': 'para la economia Bitcoin',
    'home.subtitle': 'Compra y vende productos con pagos instantaneos en Bitcoin Lightning.',
    'home.subtitle_2': 'Sin bancos. Sin esperas. Sin fronteras.',
    'home.browse_products': 'Ver productos ->',
    'home.start_selling': 'Empezar a vender',
    'home.perk_instant': 'Liquidacion instantanea',
    'home.perk_self_custodial': 'Autocustodia',
    'home.perk_built_sv': 'Creado para El Salvador',
    'home.perk_low_fees': 'Comisiones minimas',
    'home.browse_categories': 'Explorar categorias',
    'home.latest_products': 'Ultimos productos',
    'home.see_all': 'Ver todo ->',
    'home.cta_title': 'Empieza a aceptar Bitcoin hoy',
    'home.cta_text': 'Unete a cientos de vendedores que ya usan Lightning.',
    'home.create_seller_account': 'Crear cuenta de vendedor',
    'home.no_products': 'Aun no hay productos',
    'home.no_products_desc': 'Inicia el marketplace publicando el primer producto.',
    'home.first_seller': 'Se el primer vendedor',
    'home.load_error': 'No se pudieron cargar los productos',
    'home.load_error_desc': 'Intenta recargar la pagina en unos segundos.',
    'about.kicker': 'Conoce BitMarket SV',
    'about.title': 'Comercio local con pagos Lightning, simple y real.',
    'about.subtitle_1': 'BitMarket conecta compradores y vendedores para mover la economia local con Bitcoin Lightning:',
    'about.subtitle_2': 'pagos instantaneos, comisiones bajas y una experiencia clara para todos.',
    'about.cta_products': 'Ver productos',
    'about.cta_sell': 'Quiero vender',
    'about.mission_title': 'Nuestra mision',
    'about.mission_text_1': 'Dar a pequenos y medianos vendedores una vitrina digital moderna, con pagos en Bitcoin Lightning',
    'about.mission_text_2': 'que se confirman en segundos y permiten vender sin friccion.',
    'about.how_title': 'Como funciona',
    'about.step_explore_label': 'Explora:',
    'about.step_explore_text': 'el comprador encuentra productos en el catalogo.',
    'about.step_pay_label': 'Paga:',
    'about.step_pay_text': 'se genera una factura Lightning para pago rapido.',
    'about.step_receive_label': 'Recibe:',
    'about.step_receive_text': 'la orden se confirma y el vendedor gestiona el envio.',
    'about.trust_title': 'Transparencia y seguridad',
    'about.trust_text_1': 'BitMarket mantiene trazabilidad basica de ordenes y pagos para que cada operacion tenga un estado claro.',
    'about.trust_text_2': 'Nuestro objetivo es que comprar y vender sea confiable desde el primer clic.',
    'about.contact_title': 'Contacto y apoyo',
    'about.contact_text': 'Estamos construyendo junto a la comunidad Bitcoin de El Salvador.',
    'about.contact_email': 'Correo:',
    'about.support_title': 'Apoya el desarrollo',
    'about.support_text': 'Este proyecto es desarrollado por estudiantes. Tu apoyo nos ayuda a mantenerlo y mejorarlo.',
    'about.support_cta': 'Donar con Lightning',
    'donate.page_title': 'Apoyar el Proyecto',
    'donate.hero_title': 'Apoya BitMarket SV',
    'donate.hero_text_1': 'Este proyecto es desarrollado por estudiantes de Cubo+ en El Salvador.',
    'donate.hero_text_2': 'Tu apoyo nos ayuda a mantener y mejorar la plataforma.',
    'donate.form_title': 'Donar con Lightning Network',
    'donate.amount_label': 'Ingresa el monto a donar (satoshis):',
    'donate.amount_suggested': 'O elige un monto sugerido:',
    'donate.generate': 'Generar Invoice',
    'donate.scanner_title': 'Escanea para pagar',
    'donate.amount_to_pay': 'Monto a donar:',
    'donate.copy_invoice': 'Copiar Invoice',
    'donate.waiting': 'Esperando pago...',
    'donate.change_amount': 'Cambiar monto',
    'donate.success_title': 'Donacion Recibida!',
    'donate.success_subtitle': 'Gracias por apoyar BitMarket SV',
    'donate.you_donated': 'Has donado:',
    'donate.success_text_1': 'Tu apoyo nos ayuda a mantener y mejorar esta plataforma.',
    'donate.success_text_2': 'Cada satoshi cuenta!',
    'donate.new_donation': 'Hacer otra donacion',
    'donate.uses_title': 'Para que se usan las donaciones?',
    'donate.use_1': 'Mantenimiento de servidores y base de datos',
    'donate.use_2': 'Mejoras y nuevas funcionalidades',
    'donate.use_3': 'Correccion de errores y optimizacion',
    'donate.use_4': 'Documentacion y tutoriales',
    'donate.use_5': 'Cafe para los desarrolladores',
    'donate.thanks_title': 'Gracias por tu apoyo!',
    'donate.thanks_text_1': 'Cada satoshi cuenta y nos motiva a seguir construyendo herramientas utiles',
    'donate.thanks_text_2': 'para la comunidad Bitcoin de El Salvador.',
    'donate.back_home': 'Volver al inicio',
    'donate.alert_invalid_amount': 'Por favor ingresa un monto valido (minimo 1,000 sats).',
    'donate.loading': 'Generando...',
    'donate.error_generate': 'Error al generar invoice',
    'donate.error_generate_retry': 'Error al generar el invoice. Por favor intenta de nuevo.',
    'donate.memo': 'Donacion a BitMarket SV',
    'donate.expires_in': 'Expira en',
    'donate.alert_expired': 'El invoice ha expirado. Por favor genera uno nuevo.',
    'donate.confirmed_log': 'Donacion confirmada!',
    'donate.alert_copied': 'Invoice copiado al portapapeles!',
    'donate.error_copy': 'Error al copiar invoice:',
    'common.validation_error': 'Error de validacion',
    'common.error': 'Error',
    'common.just_now': 'justo ahora',
    'common.minutes_ago': 'min',
    'common.hours_ago': 'h',
    'common.days_ago': 'd',
    'common.no_results': 'No hay resultados',
    'confirm.title': 'Confirmar accion',
    'confirm.message': 'Estas seguro?',
    'confirm.cancel': 'Cancelar',
    'confirm.accept': 'Confirmar',
    'product.by': 'por',
    'product.unknown_seller': 'Desconocido',
    'product.view': 'Ver',
    'checkout.subtitle': 'Revisa tu pedido y paga con Lightning',
    'checkout.emptyTitle': 'Carrito vacío',
    'checkout.viewProducts': 'Ver productos',
    'checkout.orderSummary': 'Resumen del pedido',
    'checkout.total': 'Total',
    'checkout.shippingAddress': 'Dirección de envío',
    'checkout.fullName': 'Nombre completo',
    'checkout.street': 'Calle / Dirección',
    'checkout.city': 'Ciudad',
    'checkout.country': 'País',
    'checkout.postalCode': 'Código postal (opcional)',
    'checkout.notes': 'Notas (opcional)',
    'checkout.generateInvoice': 'Generar invoice Lightning →',
    'checkout.generatingInvoice': 'Generando invoice…',
    'checkout.error_generateFailed': 'Error al generar invoice',
    'checkout.amountToPay': 'Monto a pagar',
    'checkout.sats': 'sats',
    'checkout.copyInvoice': '📋 Copiar invoice',
    'checkout.cancelInvoice': '❌ Cancelar invoice',
    'checkout.awaitingPayment': 'Esperando pago…',
    'checkout.awaitingLightning': 'Esperando pago Lightning…',
    'checkout.invoiceExpires': 'Invoice expira en',
    'checkout.invoiceExpired': 'Invoice expirada',
    'checkout.mockMode': 'Modo Mock',
    'checkout.mockInfo': 'el pago se confirma automáticamente en',
    'checkout.mockSeconds': 'segundos',
    'checkout.mockConfirming': 'confirmando en',
    'checkout.paymentConfirmed': '¡Pago confirmado!',
    'checkout.orderSuccess': 'Tu pedido ha sido registrado exitosamente.',
    'checkout.viewOrders': 'Ver mis pedidos',
    'checkout.continueShopping': 'Seguir comprando',
    'checkout.invoiceTitle': 'Invoice Expirado',
    'checkout.invoiceExpiredMsg': 'El tiempo para pagar este invoice ha expirado (5 minutos). Tu carrito se mantiene intacto para que puedas generar un nuevo invoice.',
    'checkout.retry': '🔄 Reintentar',
    'checkout.backCart': '🛒 Volver al carrito',
    'checkout.shopping': '🏠 Seguir comprando',
    'checkout.error_noInvoice': 'No hay invoice activa para cancelar',
    'checkout.cancelConfirm': 'Se cancelará este invoice y tus productos seguirán en el carrito. ¿Deseas continuar?',
    'checkout.cancelTitle': 'Cancelar invoice',
    'checkout.yes': 'Sí, cancelar',
    'checkout.cancelSuccess': 'Invoice cancelada. Tu carrito sigue intacto.',
    'checkout.error_cancelFailed': 'No se pudo cancelar la invoice',
    'checkout.error_retryFailed': 'No se pudo generar un nuevo invoice',
    'checkout.invoiceCopied': 'Invoice copiada',
    'checkout.error_nameRequired': 'El nombre es obligatorio.',
    'checkout.error_addressRequired': 'La dirección es obligatoria.',
    'checkout.error_cityRequired': 'La ciudad es obligatoria.',
    'checkout.error_countryRequired': 'El país es obligatorio.',
    'checkout.error_invalidChars': 'contiene caracteres no permitidos.',
    'checkout.error_tooShort': 'es demasiado corto.',
    'checkout.error_tooLong': 'excede el máximo permitido.',
    'common.no': 'No',
  },

};

function getLang() {
  const saved = localStorage.getItem('bm_lang');
  return saved === 'es' || saved === 'en' ? saved : 'en';
}

function setLang(lang) {
  const nextLang = lang === 'es' ? 'es' : 'en';
  localStorage.setItem('bm_lang', nextLang);
  applyTranslations();
  hydrateNavbar();
}

function t(key, fallback = '') {
  const lang = getLang();
  return I18N[lang]?.[key] || I18N.en[key] || fallback || key;
}

function languageSwitcherMarkup() {
  const current = getLang();
  return `
    <label class="navbar__lang" title="Language">
      <select id="lang-switcher" class="navbar__lang-select" onchange="window.i18nSetLang(this.value)">
        <option value="en" ${current === 'en' ? 'selected' : ''}>EN</option>
        <option value="es" ${current === 'es' ? 'selected' : ''}>ES</option>
      </select>
    </label>
  `;
}

function applyTranslations() {
  document.documentElement.setAttribute('lang', getLang());

  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    const fallback = el.getAttribute('data-i18n-fallback') || el.textContent;
    el.textContent = t(key, fallback);
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder');
    const fallback = el.getAttribute('placeholder') || '';
    el.setAttribute('placeholder', t(key, fallback));
  });

  document.querySelectorAll('[data-i18n-title]').forEach((el) => {
    const key = el.getAttribute('data-i18n-title');
    const fallback = el.getAttribute('title') || '';
    el.setAttribute('title', t(key, fallback));
  });
}

window.i18nSetLang = setLang;

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
    return parts.length ? parts.join(' | ') : t('common.validation_error', 'Validation error');
  }

  if (typeof detail === 'object') {
    if (typeof detail.message === 'string') return detail.message;
    if (typeof detail.msg === 'string') return detail.msg;
    try {
      return JSON.stringify(detail);
    } catch {
      return t('common.error', 'Error');
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
  if (diff < 60) return t('common.just_now', 'just now');
  if (diff < 3600) return Math.floor(diff/60) + ' ' + t('common.minutes_ago', 'm ago');
  if (diff < 86400) return Math.floor(diff/3600) + ' ' + t('common.hours_ago', 'h ago');
  return Math.floor(diff/86400) + ' ' + t('common.days_ago', 'd ago');
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
      <a href="/nosotros" class="navbar__link">${t('nav.about', 'About us')}</a>
      <span class="navbar__role-badge ${roleClass}">${u.role}</span>
      <div class="navbar__avatar" title="${u.name}">${u.name[0].toUpperCase()}</div>
      ${u.role === 'seller' ? `<a href="/seller" class="navbar__link">${t('nav.dashboard', 'Dashboard')}</a>` : ''}
      ${u.role === 'admin'  ? `<a href="/admin"  class="navbar__link">${t('nav.admin', 'Admin')}</a>` : ''}
      ${u.role === 'buyer'  ? `<a href="/orders" class="navbar__link">${t('nav.orders', 'Orders')}</a>` : ''}
      ${u.role === 'buyer'  ? `<a href="/cart" class="navbar__link navbar__cart-link" title="${t('nav.cart', 'Cart')}"><span class="cart-icon-wrap">🛒<span id="cart-count-badge" class="cart-count-badge">0</span></span></a>` : ''}
      ${languageSwitcherMarkup()}
      <button class="navbar__link" onclick="logout()">${t('nav.logout', 'Logout')}</button>
    `;
    refreshCartCount();
  } else {
    el.innerHTML = `
      <a href="/nosotros" class="navbar__link">${t('nav.about', 'About us')}</a>
      <a href="/login"    class="navbar__link">${t('nav.login', 'Login')}</a>
      <a href="/register" class="navbar__btn">${t('nav.signup', 'Sign up')}</a>
      ${languageSwitcherMarkup()}
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
  const title = options.title || t('common.no_results', 'No results');
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
      <h3 id="confirm-title" class="confirm-title">${t('confirm.title', 'Confirm action')}</h3>
      <p id="confirm-text" class="confirm-text">${t('confirm.message', 'Are you sure?')}</p>
      <div class="confirm-actions">
        <button id="confirm-cancel" class="btn btn-ghost btn-sm" type="button">${t('confirm.cancel', 'Cancel')}</button>
        <button id="confirm-accept" class="btn btn-primary btn-sm" type="button">${t('confirm.accept', 'Confirm')}</button>
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

  titleEl.textContent = opts.title || t('confirm.title', 'Confirm action');
  textEl.textContent = message || t('confirm.message', 'Are you sure?');
  cancelBtn.textContent = opts.cancelText || t('confirm.cancel', 'Cancel');
  acceptBtn.textContent = opts.confirmText || t('confirm.accept', 'Confirm');

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
        ? `<img src="${coverImage}" alt="${p.title}" style="width:100%;height:100%;object-fit:cover;border-radius:inherit" onerror="this.parentElement.textContent='${emoji}'" />`
        : emoji}
      </div>
      <div class="product-card__body">
        <p class="product-card__cat">${p.category}</p>
        <h3 class="product-card__title">${p.title}</h3>
        <p class="product-card__seller">${t('product.by', 'by')} ${p.seller_name || t('product.unknown_seller', 'Unknown')}</p>
        <div class="product-card__footer">
          <div>
            <div style="display:flex;flex-direction:column;gap:2px">
              <span class="price-sats">⚡ ${formatSats(p.price_sats)}</span>
              ${usdAmount ? `<span class="text-muted text-xs" style="color:#16a34a">≈ $${usdAmount} USD</span>` : ''}
            </div>
          </div>
          <a href="/products/${p.id}" class="btn btn-sm btn-outline">${t('product.view', 'View')}</a>
        </div>
      </div>
    </div>
  `;
}

// ── Mobile nav / drawers (hamburger menu, dashboard sidebar, filters) ──
function setupMobileDrawers() {
  const overlay = document.getElementById('page-overlay');
  const searchMobile = document.getElementById('search-form-mobile');
  const drawers = [];

  function closeAll() {
    drawers.forEach(d => {
      d.panel.classList.remove('open');
      d.toggle.classList.remove('is-open');
      d.toggle.setAttribute('aria-expanded', 'false');
    });
    overlay?.classList.remove('open');
    searchMobile?.classList.remove('open');
  }

  function register(toggle, panel) {
    if (!toggle || !panel) return;
    drawers.push({ toggle, panel });
    toggle.addEventListener('click', () => {
      const willOpen = !panel.classList.contains('open');
      closeAll();
      if (willOpen) {
        panel.classList.add('open');
        toggle.classList.add('is-open');
        toggle.setAttribute('aria-expanded', 'true');
        overlay?.classList.add('open');
      }
    });
  }

  overlay?.addEventListener('click', closeAll);
  window.closeMobileDrawers = closeAll;

  // Hamburger -> nav menu
  register(document.getElementById('navbar-hamburger'), document.getElementById('navbar-auth'));

  // Dashboard sidebar (seller/admin pages) — inject a toggle button if present
  const dashSidebar = document.querySelector('.dash-sidebar');
  if (dashSidebar) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'dash-mobile-toggle btn btn-outline btn-sm';
    btn.setAttribute('aria-label', 'Abrir menu del panel');
    btn.innerHTML = '☰ Menu';
    dashSidebar.insertAdjacentElement('beforebegin', btn);
    register(btn, dashSidebar);
  }

  // Products filters sidebar — inject a toggle button if present
  const filtersSidebar = document.querySelector('.filters-sidebar');
  if (filtersSidebar) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'filters-mobile-toggle btn btn-outline btn-sm';
    btn.setAttribute('aria-label', 'Abrir filtros');
    btn.innerHTML = '⚙ Filtros';
    filtersSidebar.insertAdjacentElement('beforebegin', btn);
    register(btn, filtersSidebar);
  }

  // Navbar search icon toggle (mobile)
  const searchToggle = document.getElementById('navbar-search-toggle');
  if (searchToggle && searchMobile) {
    searchToggle.addEventListener('click', () => {
      const willOpen = !searchMobile.classList.contains('open');
      closeAll();
      if (willOpen) {
        searchMobile.classList.add('open');
        document.getElementById('search-input-mobile')?.focus();
      }
    });
  }

  window.addEventListener('resize', () => {
    if (window.innerWidth > 900) closeAll();
  });
}

// ── Run on every page ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Sync lang selector with saved preference BEFORE applying translations
  const savedLang = getLang();
  const switcher = document.getElementById('lang-switcher');
  if (switcher) switcher.value = savedLang;

  applyTranslations();
  hydrateNavbar();
  refreshCartCount();
  setupMobileDrawers();

  // Navbar search (desktop)
  const searchForm = document.getElementById('search-form');
  if (searchForm) {
    searchForm.addEventListener('submit', e => {
      e.preventDefault();
      const q = document.getElementById('search-input').value.trim();
      if (q) window.location.href = `/products?q=${encodeURIComponent(q)}`;
    });
  }

  // Navbar search (mobile)
  const searchFormMobile = document.getElementById('search-form-mobile');
  if (searchFormMobile) {
    searchFormMobile.addEventListener('submit', e => {
      e.preventDefault();
      const q = document.getElementById('search-input-mobile').value.trim();
      if (q) window.location.href = `/products?q=${encodeURIComponent(q)}`;
    });
  }
});
