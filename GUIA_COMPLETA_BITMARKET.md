# 📘 Guía Completa - BitMarket SV

## 📌 ¿Qué es BitMarket SV?

BitMarket SV es un **marketplace multi-vendedor** desarrollado por estudiantes de Cubo+ que permite:
- 👤 Registro de compradores, vendedores y administradores
- 🛍️ Publicar y vender productos
- 💰 Pagos con Lightning Network (Bitcoin)
- 💵 **Conversión automática a dólares USD (El Salvador)** en tiempo real
- 📦 Gestión de órdenes y envíos
- 🖼️ Subida de imágenes de productos
- ⚡ **Sistema de donaciones** para apoyar el desarrollo

---

## 🔧 Requisitos Previos (Qué instalar)

### 1. **Python 3.11 o superior**
- Descargar desde: https://www.python.org/downloads/
- ✅ Durante la instalación, marcar "Add Python to PATH"

### 2. **PostgreSQL** (Base de datos)

#### Instalación en Windows:
1. Descargar desde: https://www.postgresql.org/download/windows/
2. Ejecutar el instalador
3. Durante la instalación:
   - **Puerto**: 5432 (dejar por defecto)
   - **Contraseña del superusuario (postgres)**: Anotar esta contraseña (ejemplo: `Eliza-2026p`)
   - **Locale**: Spanish, El Salvador o el que prefieras

#### Crear la base de datos:
Después de instalar PostgreSQL, abrir **pgAdmin 4** o **psql** y ejecutar:
```sql
CREATE DATABASE bitmarket;
```

### 3. **Git** (opcional, para clonar el proyecto)
- Descargar desde: https://git-scm.com/downloads

---

## 🚀 Instalación del Sistema

### Paso 1: Obtener el código
```powershell
# Opción A: Si tienes el proyecto en una carpeta
cd c:\Users\TU_USUARIO\Documents\BitMarket_sv_split

# Opción B: Si lo clonaste de Git
git clone [URL_DEL_REPOSITORIO]
cd BitMarket_sv_split
```

### Paso 2: Crear entorno virtual
```powershell
# Crear el entorno virtual
python -m venv .venv

# Activarlo
.\.venv\Scripts\Activate.ps1
```

> **Nota**: Si sale error de permisos en PowerShell, ejecutar:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Paso 3: Instalar dependencias
```powershell
pip install -r requirements.txt
```

---

## ⚙️ Configuración del Archivo .env

El archivo `.env` contiene todas las configuraciones importantes del sistema.

### 📝 Cómo editar el archivo .env

Abrir el archivo `.env` en la raíz del proyecto con un editor de texto (Notepad, VS Code, etc.)

### 🔑 Datos Importantes a Configurar:

#### 1. **Base de Datos (OBLIGATORIO)**
```env
DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@localhost:5432/bitmarket
```

**Cambiar**:
- `TU_CONTRASEÑA` → La contraseña que pusiste cuando instalaste PostgreSQL
- Ejemplo: `DATABASE_URL=postgresql://postgres:Eliza-2026p@localhost:5432/bitmarket`

#### 2. **Contraseña Secreta (SECRET_KEY)**
```env
SECRET_KEY=dev-secret-key-change-in-production-please
```

**Para producción**, cambiar por una contraseña fuerte generada aleatoriamente.
Puedes generarla con:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3. **Tiempo de Expiración del Token de Sesión**
```env
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```
- Por defecto: 10,080 minutos = 7 días
- Cambiar a un número menor para más seguridad (ejemplo: 60 = 1 hora)

#### 4. **Configuración de LNbits (Pagos Lightning)**

**Modo REAL** (con nodo Lightning real):
```env
LNBITS_URL=https://lnbits.daxsosa.com
LNBITS_ADMIN_KEY=050c5f69e7a14e4a9710e9a3b5c7ec1a
```

**Modo MOCK** (pruebas sin dinero real):
- Comentar las líneas de LNBITS_URL y LNBITS_ADMIN_KEY:
```env
#LNBITS_URL=https://lnbits.daxsosa.com
#LNBITS_ADMIN_KEY=050c5f69e7a14e4a9710e9a3b5c7ec1a
```

#### 5. **Tiempos de Espera**
```env
MOCK_CONFIRM_SECONDS=10       # Tiempo para confirmar pago en modo MOCK
INVOICE_EXPIRE_SECONDS=300    # Tiempo antes de expirar una factura (5 minutos)
```

#### 6. **Comisión de la Plataforma**
```env
MARKETPLACE_FEE_PERCENT=3     # 3% de comisión en cada venta
```

---

## 🗄️ Inicializar la Base de Datos

### Paso 1: Crear las tablas y el usuario administrador
```powershell
python app\bootstrap_db.py
```

Este comando:
- ✅ Crea todas las tablas necesarias en PostgreSQL
- ✅ Crea un usuario administrador por defecto

**Datos del usuario administrador por defecto:**
- Email: `admin@bitmarket.sv`
- Contraseña: `Admin1234!`

### Paso 2: (Opcional) Cargar datos de prueba
```powershell
python app\seed.py
```

Este comando crea:
- 3 usuarios de prueba (comprador, vendedor, admin)
- 15 productos de ejemplo
- Algunas órdenes de prueba

---

## ▶️ Cómo Ejecutar el Sistema

### Comando para iniciar el servidor:
```powershell
# Desde la raíz del proyecto
uvicorn app.main:app --reload
```

### Acceder al sistema:
- **Navegador web**: http://localhost:8000
- **API (documentación)**: http://localhost:8000/docs

### Para detener el servidor:
Presionar `Ctrl + C` en la terminal

---

## 👥 Usuarios de Prueba (después de ejecutar seed.py)

### 👨‍💼 Administrador
- Email: `admin@bitmarket.sv`
- Contraseña: `Admin1234!`
- Acceso a: Panel de administración completo

### 🛒 Comprador
- Email: `buyer@test.com`
- Contraseña: `Test1234!`
- Acceso a: Comprar productos, ver órdenes

### 🏪 Vendedor
- Email: `seller@test.com`
- Contraseña: `Test1234!`
- Acceso a: Crear productos, gestionar ventas

---

## ⏱️ Tiempos de Espera del Sistema

### 1. **Confirmación de Pagos (Modo MOCK)**
- **Tiempo de espera**: 10 segundos (configurable en `.env` con `MOCK_CONFIRM_SECONDS`)
- Después de crear una orden, el sistema simula un pago automáticamente

### 2. **Expiración de Facturas**
- **Tiempo**: 300 segundos (5 minutos)
- Si no se paga una factura en este tiempo, expira y debes crear una nueva orden

### 3. **Sesión de Usuario**
- **Duración**: 120 minutos (2 horas) por defecto
- Configurable en `.env` con `ACCESS_TOKEN_EXPIRE_MINUTES`

### 4. **Polling de Estado de Pago**
- **Frecuencia**: Cada 3 segundos
- El sistema verifica automáticamente si un pago fue confirmado

---

## 💵 Conversión Automática a Dólares (El Salvador)

### ✨ Funcionalidad Completa

El sistema ahora muestra la **conversión en tiempo real de satoshis a dólares USD** en toda la plataforma:

#### 🛒 Para **Compradores** (Buyers):
1. **Catálogo de productos** - Cada producto muestra su precio en sats y USD
2. **Detalle de producto** - Precio destacado en ambas monedas
3. **Carrito de compras** - Precio unitario y total en USD
4. **Checkout** - Confirmación final del monto en dólares

#### 🏪 Para **Vendedores** (Sellers):
1. **Al crear productos** - Conversión en tiempo real mientras escriben el precio
2. **Al editar productos** - Muestra USD del precio actual
3. **Tabla de productos** - Cada producto lista precio en sats y USD
4. **Dashboard** - Resumen de ingresos en ambas monedas

### 🔄 Características Técnicas

- **Actualización en tiempo real**: Usa la API de CoinGecko para obtener el precio actual de Bitcoin
- **Cache inteligente**: El precio se actualiza cada 1 minuto para no saturar la API
- **Sin configuración**: No requiere API key, funciona automáticamente
- **Precio de respaldo**: Si la API falla, usa $100,000 USD por BTC como fallback

### 💡 ¿Por qué es útil?

En El Salvador, el dólar estadounidense es la moneda oficial. Esta funcionalidad permite:
- **Compradores**: Entender rápidamente cuánto pagarán sin conocer Bitcoin
- **Vendedores**: Ajustar precios según el mercado local
- **Transparencia**: Todos ven el valor real en la moneda que usan diariamente

### 📸 Ejemplo Visual

#### En el Catálogo:
```
⚡ 50k sats
≈ $50.00 USD
```

#### Al Crear Producto (Vendedor):
```
Precio en satoshis: 50000
↓ En tiempo real mientras escribes:
≈ 0.00050000 BTC
≈ $50.00 USD (El Salvador)
```

#### En el Carrito:
```
Subtotal: ⚡ 150,000 sats
          ≈ $150.00 USD

Total:    ⚡ 150,000 sats
          $150.00 USD ← Destacado en verde
```

### ⚙️ Configuración

**No requiere configuración adicional**. La API de CoinGecko es gratuita y no necesita clave API.

**API usada**: `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`

---

## 🔄 Flujo Completo de una Compra

```
1. COMPRADOR se registra/inicia sesión
   ↓
2. Navega el catálogo de productos
   ↓
3. Agrega productos al carrito
   ↓
4. Va a checkout (finalizar compra)
   ↓
5. Sistema genera una factura Lightning (código QR)
   ↓
6. COMPRADOR escanea código QR con su wallet Lightning
   ↓
7. Sistema detecta el pago (en 3 segundos si es modo real, 10 seg en mock)
   ↓
8. Orden confirmada, stock descontado
   ↓
9. VENDEDOR ve la orden en su panel
   ↓
10. VENDEDOR actualiza estado: pending → processing → shipped → delivered
```

---

## 🛠️ Cómo Cambiar Datos Importantes

### Cambiar Contraseña del Administrador
```powershell
python app\bootstrap_db.py --email admin@bitmarket.sv --password "NuevaContraseña123!" --keep-password
```

### Cambiar Puerto del Servidor
En el archivo `.env`:
```env
APP_PORT=8080  # Cambiar de 8000 a 8080 o el que quieras
```

Luego ejecutar:
```powershell
uvicorn app.main:app --reload --port 8080
```

### Cambiar Base de Datos
Editar en `.env`:
```env
DATABASE_URL=postgresql://usuario:contraseña@servidor:puerto/nombre_db
```

---

## 📤 Compartir el Proyecto con un Compañero

### Opción 1: Compartir carpeta completa
1. Comprimir la carpeta `BitMarket_sv_split` en un archivo ZIP
2. Compartir el ZIP
3. Tu compañero debe:
   - Extraer el ZIP
   - Instalar Python y PostgreSQL
   - Crear la base de datos `bitmarket`
   - Editar el archivo `.env` con su contraseña de PostgreSQL
   - Seguir los pasos de instalación (entorno virtual, dependencias, bootstrap)

### Opción 2: Compartir por Git
```powershell
# Si tienes un repositorio Git
git add .
git commit -m "Versión compartible"
git push origin main
```

Tu compañero puede clonar:
```powershell
git clone [URL_DEL_REPO]
cd BitMarket_sv_split
```

### ⚠️ Importante: No compartir el archivo .env
El archivo `.env` contiene contraseñas y claves secretas. Tu compañero debe crear su propio `.env` con sus propios datos.

Puedes crear un archivo `.env.example` sin datos sensibles:
```env
# Copiar este archivo como .env y completar con tus datos

DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@localhost:5432/bitmarket
SECRET_KEY=generar-clave-secreta-unica
LNBITS_URL=https://tu-nodo.com
LNBITS_ADMIN_KEY=tu-clave-admin
```

---

## 🧪 Cómo Probar que Todo Funciona

### 1. Verificar base de datos
```powershell
python -c "from app.app.config.database import connect_db; import asyncio; asyncio.run(connect_db()); print('✅ Conexión exitosa')"
```

### 2. Ejecutar tests
```powershell
pytest unit_tests/
```

### 3. Verificar rutas API
Abrir navegador en: http://localhost:8000/docs
Deberías ver la documentación interactiva de Swagger

---

## 🆘 Problemas Comunes

### Error: "No module named 'app'"
**Solución**: Asegúrate de estar en la carpeta raíz del proyecto y de tener el entorno virtual activado.

### Error: "could not connect to server: Connection refused"
**Solución**: PostgreSQL no está corriendo. Iniciar el servicio:
```powershell
# Windows: Buscar "Services" y iniciar "postgresql-x64-XX"
# O reiniciar el servicio
net start postgresql-x64-XX
```

### Error: "Access is denied" al activar entorno virtual
**Solución**: Cambiar política de ejecución:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### La página no carga después de ejecutar uvicorn
**Solución**: 
1. Verificar que el puerto 8000 no esté ocupado
2. Probar con otro puerto: `uvicorn app.main:app --reload --port 8001`
3. Verificar que no haya errores en la terminal

---

## 📚 Estructura del Proyecto

```
BitMarket_sv_split/
│
├── .env                    ← Configuración (CAMBIAR AQUÍ)
├── requirements.txt        ← Dependencias Python
├── pytest.ini             ← Configuración de tests
│
├── app/
│   ├── main.py            ← Punto de entrada del servidor
│   ├── bootstrap_db.py    ← Script para inicializar DB
│   ├── seed.py            ← Script para datos de prueba
│   │
│   └── app/
│       ├── controllers/   ← Lógica de negocio
│       ├── services/      ← Servicios (pagos, productos, etc.)
│       ├── models/        ← Modelos de datos
│       ├── routes/        ← Rutas de la API
│       ├── templates/     ← Páginas HTML (Jinja2)
│       ├── static/        ← CSS, JS, imágenes
│       ├── config/        ← Configuración (DB, settings)
│       └── middleware/    ← Autenticación JWT
│
├── logic/                 ← Documentación técnica
└── unit_tests/           ← Tests automáticos
```

---

## 🚀 Comandos Rápidos (Resumen)

```powershell
# 1. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Inicializar base de datos
python app\bootstrap_db.py

# 4. Cargar datos de prueba (opcional)
python app\seed.py

# 5. Ejecutar servidor
uvicorn app.main:app --reload

# 6. Acceder al sistema
# Navegador: http://localhost:8000
```

---

## 📞 Contacto y Soporte

Para más información sobre el proyecto, revisar:
- `README.md` - Información general
- `logic/OPERATIONAL_MODEL.md` - Modelo operativo
- `logic/ARCHITECTURE.md` - Arquitectura técnica

---

## ✅ Checklist para Tu Compañero

- [ ] Instalar Python 3.11+
- [ ] Instalar PostgreSQL
- [ ] Crear base de datos `bitmarket`
- [ ] Obtener el código del proyecto
- [ ] Crear archivo `.env` con sus datos
- [ ] Crear entorno virtual (`.venv`)
- [ ] Instalar dependencias (`pip install -r requirements.txt`)
- [ ] Ejecutar `bootstrap_db.py`
- [ ] Ejecutar servidor (`uvicorn app.main:app --reload`)
- [ ] Probar login con admin@bitmarket.sv / Admin1234!

---

## ⚡ Apoyar el Proyecto

BitMarket SV es desarrollado por estudiantes de Cubo+ en El Salvador como un proyecto educativo y comunitario.

### 💛 ¿Cómo apoyar?

El proyecto incluye un **sistema de donaciones con Lightning Network**:

1. **Accede a la página de donaciones**: `http://localhost:8000/donate`
2. **Botón en el footer**: Visible en todas las páginas
3. **Página "Nosotros"**: Sección dedicada de apoyo

### 🎯 Características del Sistema de Donaciones:

- ⚡ **Pagos Lightning instantáneos**
- 📱 **QR code para escanear** con cualquier wallet
- 💵 **Montos sugeridos** con conversión USD en tiempo real
- 📋 **Copiar dirección Lightning** con un clic

### 💡 ¿Para qué se usan las donaciones?

- 🖥️ Mantenimiento de servidores y base de datos
- 🔧 Mejoras y nuevas funcionalidades
- 🐛 Corrección de errores y optimización
- 📚 Documentación y tutoriales
- ☕ Apoyo a los desarrolladores

### 🔧 Configurar tu Dirección de Donaciones:

Para personalizar la dirección Lightning de donaciones, edita el archivo [donate.html](app/app/templates/donate.html):

```html
<!-- Línea 30 aprox. -->
<div style="background:var(--bg-secondary);padding:12px 16px...">
  TU_LIGHTNING_ADDRESS@dominio.com
</div>
```

O puedes usar un **LNURL** o **Lightning Address** de tu wallet LNbits.

---

**Última actualización**: Junio 2026
**Versión del documento**: 1.1
