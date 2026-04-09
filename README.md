# BitMarket SV

Proyecto en desarrollo.

## Requisitos
- Python 3.11+

## Instalacion
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Ejecutar
```bash
uvicorn app.main:app --reload
```

## Tests
```bash
pytest unit_tests/ -v
```
