"""
Script para convertir GUIA_COMPLETA_BITMARKET.md a HTML (listo para imprimir a PDF)
"""
import markdown2
from pathlib import Path

# Leer el archivo markdown
md_file = Path("GUIA_COMPLETA_BITMARKET.md")
html_file = Path("GUIA_COMPLETA_BITMARKET.html")

print(f"📄 Leyendo {md_file}...")
md_content = md_file.read_text(encoding='utf-8')

# Convertir markdown a HTML
print("🔄 Convirtiendo markdown a HTML...")
html_content = markdown2.markdown(
    md_content,
    extras=["tables", "fenced-code-blocks", "task_list", "header-ids"]
)

# Crear HTML completo con estilos
full_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guía Completa BitMarket SV</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-after: avoid;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            page-break-after: avoid;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
            page-break-after: avoid;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        pre code {{
            background-color: transparent;
            color: #f8f8f2;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        table, th, td {{
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #ecf0f1;
            font-style: italic;
        }}
        hr {{
            border: none;
            border-top: 2px solid #bdc3c7;
            margin: 30px 0;
        }}
        .emoji {{
            font-size: 1.2em;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        @media print {{
            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
            pre {{
                page-break-inside: avoid;
            }}
            h1, h2, h3 {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""

# Guardar HTML
print("💾 Guardando HTML...")
html_file.write_text(full_html, encoding='utf-8')
print(f"✅ ¡HTML generado exitosamente! → {html_file}")
print(f"📍 Ubicación: {html_file.absolute()}")
print("\n📝 CÓMO GENERAR EL PDF:")
print("   1. Abre el archivo HTML en tu navegador (doble clic)")
print("   2. Presiona Ctrl+P (o Cmd+P en Mac)")
print("   3. En 'Destino', selecciona 'Guardar como PDF'")
print("   4. Ajusta márgenes y configuración si es necesario")
print("   5. Haz clic en 'Guardar'")
print("\n🎨 El HTML tiene estilos profesionales listos para imprimir")

# Intentar abrir el HTML automáticamente
try:
    import webbrowser
    webbrowser.open(str(html_file.absolute()))
    print("\n🌐 Abriendo HTML en tu navegador...")
except:
    pass
