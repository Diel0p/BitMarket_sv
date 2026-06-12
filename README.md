# BitMarket SV ⚡

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Lightning Network](https://img.shields.io/badge/Payments-Lightning_Network-F7931A?style=for-the-badge&logo=lightning&logoColor=white)](https://lightning.network/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

**BitMarket SV** es un marketplace multi-vendedor diseñado con el contexto salvadoreño en mente, permitiendo realizar transacciones comerciales utilizando **Bitcoin Lightning Network** con conversión y visualización en tiempo real a dólares estadounidenses (USD).

El sistema incluye soporte para registrar compradores y vendedores, crear y gestionar catálogos de productos, realizar el flujo de checkout mediante facturas Lightning (reales o simuladas), cobrar comisiones automáticas de la plataforma y donar de forma directa para apoyar el desarrollo.

---

## 📌 Características Principales

*   👤 **Control de Acceso Basado en Roles:** Registro e inicio de sesión seguro con tokens JWT para tres roles diferenciados (`buyer`, `seller`, `admin`).
*   🛍️ **Catálogo y Gestión de Productos:** Los vendedores disponen de un panel dedicado para crear, editar, eliminar y subir imágenes de sus productos.
*   🧾 **Checkout con Facturas Lightning:** Generación dinámica de facturas en código QR (BOLT11) compatibles con cualquier wallet de Lightning Network (Phoenix, Muun, Zeus, Breez, etc.).
*   💸 **Distribución de Fondos y Comisiones:** División automática de pagos cobrando un porcentaje configurable para la plataforma (`MARKETPLACE_FEE_PERCENT`) antes del desembolso al vendedor.
*   💵 **Conversión a USD en Tiempo Real:** Integración con la API de CoinGecko para convertir satoshis a USD en las vistas del catálogo, carrito de compras, checkout y paneles de administración, usando un sistema de cache de 1 minuto para optimizar el rendimiento.
*   ⚡ **Donaciones Integradas:** Página `/donate` accesible desde cualquier parte de la plataforma para recibir donaciones directas.
*   ⚙️ **Modo Híbrido (Live / Mock):** Fallback automático a modo de simulación si no se configuran credenciales de LNbits.

---

## 🛠️ Stack Tecnológico

*   **Backend:** FastAPI (Python 3.11+) & Pydantic v2.
*   **Base de Datos:** PostgreSQL utilizando un modelo de almacenamiento de documentos mediante `JSONB` y consultas optimizadas con índices GIN.
*   **Sesiones y Autenticación:** JSON Web Tokens (JWT) firmados con algoritmo HS256 y contraseñas cifradas con `bcrypt`.
*   **Front-End:** Plantillas Jinja2 dinámicas con interacción de Vanilla JavaScript y estilos CSS personalizados.
*   **Procesamiento de QR:** Generación de códigos QR en backend usando la biblioteca `segno`.
*   **Pruebas unitarias:** Suite de tests automatizados con `pytest` y `pytest-asyncio`.

---

## 📂 Estructura del Repositorio

```text
BitMarket_sv_split/
│
├── .env                        # Configuración activa del entorno (Excluido de Git)
├── .env.example                # Plantilla de configuración documentada
├── pytest.ini                  # Configuración de ejecución de pytest
├── requirements.txt            # Dependencias del proyecto
├── BitMarkerSV.pdf             # Especificación del proyecto en formato PDF
│
├── app/                        # Módulo del servidor y utilidades
│   ├── main.py                 # Punto de entrada de FastAPI
│   ├── bootstrap_db.py         # Script de inicialización de la base de datos y superusuario
│   ├── seed.py                 # Carga de datos de prueba (comprador, vendedor, admin y productos)
│   │
│   └── app/                    # Código principal de la aplicación
│       ├── config/             # Configuración de base de datos y variables de entorno
│       ├── controllers/        # Controladores e interceptores de peticiones HTTP
│       ├── middleware/         # Cifrado de contraseñas y guardas de roles JWT
│       ├── models/             # Esquemas de entrada y salida Pydantic
│       ├── routes/             # Enrutadores de endpoints de la API y páginas HTML
│       ├── services/           # Lógica de negocio (Servicio de pagos, catálogo, usuarios)
│       ├── static/             # Archivos estáticos (JavaScript, CSS, imágenes subidas)
│       └── templates/          # Vistas HTML renderizadas mediante Jinja2
│
├── logic/                      # Documentación detallada del modelo operacional y arquitectura
│   ├── ARCHITECTURE.md         # Diagramas y responsabilidades de capas
│   ├── OPERATIONAL_MODEL.md    # Flujo de transacciones y ciclo de vida de datos
│   └── PRODUCTION_ROADMAP.md   # Hoja de ruta para el despliegue a producción
│
└── unit_tests/                 # Suite de pruebas automatizadas
```

---

## 🚀 Instalación y Puesta en Marcha

### 📋 Requisitos Previos
1.  **Python 3.11 o superior** (Marcar *"Add Python to PATH"* durante la instalación).
2.  **PostgreSQL** con una base de datos vacía llamada `bitmarket`. Puedes crearla ejecutando en la consola de PostgreSQL:
    ```sql
    CREATE DATABASE bitmarket;
    ```

---

### 💻 Guía de Inicio Rápido por Consola

Selecciona la pestaña correspondiente a tu sistema operativo y shell de preferencia:

### 🗟 PowerShell (Windows)
```powershell
# 1) Ir al directorio del proyecto
cd c:\Users\cruzz\Documents\BitMarket_sv_split

# 2) Crear el entorno virtual de Python
python -m venv .venv

# 3) Activar el entorno virtual
.\.venv\Scripts\Activate.ps1
# Nota: Si obtienes un error de permisos en PowerShell, ejecuta:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4) Instalar las dependencias requeridas
pip install -r requirements.txt

# 5) Crear el archivo .env a partir de la plantilla
Copy-Item .env.example .env

# 6) Configurar e inicializar las tablas de la DB y el Superusuario
python app\bootstrap_db.py

# 7) (Opcional) Cargar datos semilla de prueba
python app\seed.py

# 8) Iniciar el servidor local en modo recarga automática
uvicorn app.main:app --reload
```

### 🗟 Consola de Comandos (CMD - Windows)
```bat
REM 1) Ir al directorio del proyecto
cd /d c:\Users\cruzz\Documents\BitMarket_sv_split

REM 2) Crear el entorno virtual
python -m venv .venv

REM 3) Activar el entorno virtual
.venv\Scripts\activate.bat

REM 4) Instalar dependencias
pip install -r requirements.txt

REM 5) Crear el archivo .env
copy .env.example .env

REM 6) Inicializar base de datos y superusuario
python app\bootstrap_db.py

REM 7) Cargar datos de prueba
python app\seed.py

REM 8) Ejecutar servidor
uvicorn app.main:app --reload
```

### 🗟 Terminal (Linux / macOS)
```bash
# 1) Ir al directorio del proyecto
cd /ruta/al/proyecto/BitMarket_sv_split

# 2) Crear el entorno virtual
python3 -m venv .venv

# 3) Activar el entorno virtual
source .venv/bin/activate

# 4) Instalar dependencias
pip install -r requirements.txt

# 5) Crear el archivo .env
cp .env.example .env

# 6) Inicializar base de datos y superusuario
python app/bootstrap_db.py

# 7) Cargar datos de prueba
python app/seed.py

# 8) Iniciar el servidor
uvicorn app.main:app --reload
```

---

## ⚙️ Explicación de Variables de Entorno (`.env`)

El archivo `.env` permite desacoplar los secretos y la configuración del servidor. A continuación se detallan las variables clave que soporta el sistema:

### Servidor y Depuración
*   `APP_NAME`: Nombre de la aplicación (Por defecto: `"BitMarket SV"`).
*   `APP_VERSION`: Versión del software expuesta en la API (Por defecto: `1.0.0`).
*   `APP_HOST`: Dirección IP donde escucha el servicio (Por defecto: `0.0.0.0` para admitir conexiones de red local).
*   `APP_PORT`: Puerto TCP donde corre el servidor (Por defecto: `8000`).
*   `DEBUG`: Bandera booleana para mostrar errores detallados (`true` / `false`).

### Persistencia (Base de Datos)
*   `DATABASE_URL`: URI de conexión a PostgreSQL.
    *   *Ejemplo local:* `postgresql://postgres:postgres@localhost:5432/bitmarket`
    *   *Ejemplo de producción:* `postgresql://usuario_seguro:clave_segura@servidor_db:5432/bitmarket`

### Seguridad y Sesiones
*   `SECRET_KEY`: Cadena aleatoria larga utilizada para firmar tokens JWT.
*   `ALGORITHM`: Algoritmo criptográfico utilizado para cifrar JWT (Por defecto: `HS256`).
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración del token JWT (Por defecto: `10080` minutos = 7 días).

### Inicialización Automática (Superusuario)
*   `SUPERUSER_NAME`: Nombre del administrador creado por defecto.
*   `SUPERUSER_EMAIL`: Correo electrónico del superusuario administrador para iniciar sesión.
*   `SUPERUSER_PASSWORD`: Contraseña del superusuario administrador.

### Integración de Pagos Lightning
*   `LNBITS_URL`: Dirección de la API de su nodo o billetera LNbits. Si se deja en blanco, el sistema correrá en **Modo Mock** automáticamente.
*   `LNBITS_ADMIN_KEY`: Clave de administrador (Admin Key) de la billetera LNbits emisora y recaudadora.
*   `PLATFORM_COMMISSION_LIGHTNING_ADDRESS`: Enlace LNURLp o dirección de retiro para depositar las comisiones obtenidas por la plataforma de forma automática.
*   `MOCK_CONFIRM_SECONDS`: Segundos requeridos para que un pago ficticio pase a estado confirmado en modo simulación (Por defecto: `10` segundos).
*   `INVOICE_EXPIRE_SECONDS`: Segundos permitidos para el pago de una factura Lightning antes de marcarla como expirada (Por defecto: `600` segundos = 10 minutos).
*   `MARKETPLACE_FEE_PERCENT`: Porcentaje que el mercado retiene de cada transacción (Por defecto: `5.0`%).

### Intercambio de Recursos de Origen Cruzado (CORS)
*   `ALLOWED_ORIGINS`: Lista de dominios permitidos para conectar clientes externos (Por defecto: `http://localhost:3000,http://localhost:5173`).

---

## 🌱 Credenciales de Prueba (Luego de ejecutar `seed.py`)

Para probar las funcionalidades de inmediato, el comando `python app/seed.py` crea los siguientes usuarios en el sistema:

| Rol de Usuario | Correo Electrónico | Contraseña | Acciones Permitidas |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@bitmarket.sv` | `Admin1234!` | Dashboard global, gestionar usuarios, aprobar/rechazar productos. |
| **Vendedor** | `seller@test.com` | `Test1234!` | Crear productos, editar catálogo, subir imágenes, gestionar envíos. |
| **Comprador** | `buyer@test.com` | `Test1234!` | Buscar productos, agregar al carrito, pagar con Lightning. |

---

## 🧪 Pruebas Unitarias e Integración

Para ejecutar la suite de pruebas unitarias y verificar el correcto funcionamiento de la base de datos, servicios y flujo de checkout, use el siguiente comando con el entorno virtual activo:

```bash
pytest unit_tests/ -v
```

---

## 🤝 Contribuir al Desarrollo

1.  Crea una rama de trabajo a partir del repositorio: `git checkout -b feature/nueva-mejora`
2.  Desarrolla tus cambios manteniendo el formato de código y comentando las secciones críticas.
3.  Asegúrate de que pasen todos los tests ejecutando `pytest`.
4.  Realiza un push e inicia una solicitud de extracción (Pull Request) hacia la rama principal.

---

⚡ **BitMarket SV** — Desarrollado con dedicación para impulsar la adopción de Lightning Network en El Salvador.
