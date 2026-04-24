# Production Roadmap

## Estado actual

BitMarket SV es un MVP de demostración. Funciona correctamente para:
- Mostrar el flujo completo de la aplicación
- Evaluación y presentación
- Desarrollo y pruebas locales

**No está listo para producción** por las limitaciones descritas abajo.

## Limitaciones actuales y soluciones

| # | Limitación | Impacto | Solución |
|---|-----------|---------|---------|
| 1 | SQLite (escritura única) | Se rompe con múltiples workers/procesos | Migrar `database.py` a PostgreSQL o MongoDB |
| 2 | Pagos en mock mode | No procesa Bitcoin real | Configurar LNbits, Alby o Strike |
| 3 | Sin atomicidad en stock | Dos compradores pueden comprar el mismo último producto | Usar transacciones DB o Redis lock |
| 4 | Sin rate limiting | Vulnerable a abuso / DDoS básico | Agregar `slowapi` |
| 5 | Sin imágenes reales | Solo campo placeholder en productos | Integrar almacenamiento S3-compatible |
| 6 | Sin notificaciones | Vendedor no se entera de nuevas órdenes | Agregar WebSockets o email (SendGrid) |

## Pasos para ir a producción (orden de prioridad)

### 1. Migrar la base de datos
Reemplazar los 4 helpers en `app/app/config/database.py`:
- `db_insert`, `db_find_one`, `db_find_all`, `db_update`

Opciones:
- **PostgreSQL** con SQLAlchemy async — robusto, gratuito, self-hosted
- **MongoDB Atlas** con Motor async — más cercano al diseño original

Servicios y controladores **no requieren cambios**.

### 2. Activar pagos Lightning reales
Configurar variables de entorno en `.env`:
```
LNBITS_URL=https://your-lnbits-instance.com
LNBITS_ADMIN_KEY=your_admin_key
MOCK_CONFIRM_SECONDS=0
```
Alternativas a LNbits: **Alby**, **OpenNode**, **Strike** — solo cambia `payment_service.py`.

### 3. Hacer el stock atómico
En `order_service.py`, envolver el check + decremento de stock en una transacción o lock:
- Con PostgreSQL: transacción `SELECT FOR UPDATE`
- Con MongoDB: transacción multi-documento
- Opción intermedia: lock con **Redis** (`redis-py`)

### 4. Agregar rate limiting
```bash
pip install slowapi
```
Aplicar límites en los endpoints de auth y checkout para evitar abuso.

### 5. Configurar servidor de producción
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```
Poner **nginx** como reverse proxy delante.

### 6. Imágenes de productos
- Integrar `python-multipart` para upload de archivos
- Almacenar en **S3**, **Cloudflare R2** o disco con nginx sirviendo estáticos

### 7. Notificaciones
- Email con **SendGrid** o **Resend** cuando llega una nueva orden
- O WebSockets para dashboard en tiempo real

## Infraestructura mínima recomendada para producción

| Componente | Opción económica | Opción robusta |
|-----------|-----------------|----------------|
| API server | 1 vCPU / 1GB RAM (Fly.io, Railway) | 2 vCPU / 2GB RAM |
| Base de datos | PostgreSQL en Railway / Supabase free | PostgreSQL dedicado |
| Pagos | LNbits self-hosted en VPS $5/mes | Nodo Lightning dedicado |
| Imágenes | Cloudflare R2 (free tier) | AWS S3 |
| Reverse proxy | nginx | nginx + CDN |

## Commits sugeridos al iniciar la migración

```bash
git commit -m "feat(db): migrate database.py to PostgreSQL with SQLAlchemy async"
git commit -m "feat(payments): connect LNbits live mode, remove mock default"
git commit -m "feat(stock): add atomic stock decrement with DB transaction"
git commit -m "feat(security): add slowapi rate limiting on auth and checkout"
git commit -m "feat(uploads): add product image upload to S3-compatible storage"
git commit -m "ops: add gunicorn + nginx production config"
```
