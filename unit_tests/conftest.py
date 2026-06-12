import os

# Fuerza a que las pruebas corran en modo simulado (Mock Mode)
# sin importar las credenciales configuradas en el archivo .env local.
os.environ["LNBITS_URL"] = ""
os.environ["LNBITS_ADMIN_KEY"] = ""
