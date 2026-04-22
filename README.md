# BitMarket SV ⚡

Marketplace multi-vendedor con pagos en Lightning Network.

BitMarket SV permite registrar compradores y vendedores, publicar productos, crear ordenes y gestionar pagos con modo mock o LNbits en vivo.

## 📌 Estado Del Proyecto

Proyecto funcional en desarrollo activo.

- ✅ Registro/login con roles (buyer, seller, admin)
- ✅ Panel de vendedor (crear, editar, eliminar productos)
- ✅ Flujo de orden + invoice + confirmacion
- ✅ Integracion LNbits y fallback mock
- ✅ Panel administrativo basico

## 🧩 Funcionalidades Principales

- 👤 Autenticacion JWT con control por roles
- 🛍️ Catalogo de productos con filtros
- 🧾 Checkout con invoice Lightning
- 💸 Payouts a vendedores con fee de plataforma
- 🧑‍💼 Dashboard de vendedor y panel admin
- 🖼️ Subida de imagenes para productos

## 🛠️ Stack Tecnologico

- Backend: FastAPI
- Base de datos: SQLite (document-store style)
- Auth: JWT + bcrypt
- Pagos: LNbits (live) / Mock mode
- Frontend: Jinja2 + JS + CSS
- Testing: pytest

## 📂 Estructura General

```text
app/
	main.py
	seed.py
	app/
		controllers/
		services/
		models/
		routes/
		templates/
		static/
```

## ✅ Requisitos

- Python 3.11 o superior
- pip

## 🚀 Instalacion Rapida

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
```

## ⚙️ Configuracion De Entorno

1. Crea el archivo .env desde .env.example.
2. Si no configuras LNbits, el sistema usa modo mock automaticamente.

Variables clave:

- LNBITS_URL
- LNBITS_ADMIN_KEY
- PLATFORM_COMMISSION_LIGHTNING_ADDRESS
- MARKETPLACE_FEE_PERCENT

## ▶️ Ejecutar Proyecto

```bash
uvicorn app.main:app --reload
```

Accesos:

- UI: http://localhost:8000/
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🌱 Datos Demo

Para cargar datos iniciales:

```bash
python app/seed.py
```

Usuarios demo generados por seed:

- admin@bitmarket.sv
- seller@bitmarket.sv
- buyer@bitmarket.sv

## 🧪 Tests

```bash
pytest unit_tests/ -v
```

## 📈 Proximos Mejoras Sugeridas

- Mejorar observabilidad (logs estructurados)
- Cobertura de pruebas para flujos de pago
- Hardening de validaciones y manejo de errores
- Mejoras UI/UX en panel admin y checkout

## 🤝 Contribucion

1. Crea una rama de trabajo.
2. Aplica cambios pequenos y claros.
3. Ejecuta tests antes de integrar.

---

Hecho con Bitcoin + FastAPI ⚡
