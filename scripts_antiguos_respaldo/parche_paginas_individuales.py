import os

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Vamos a inyectar la lógica de generación de páginas individuales de noticias dentro de generar_html_estatico.py
    # Primero, verificamos si ya existe la función de creación de páginas individuales
    if "def generar_paginas_individuales" not in code:
        
        funcion_individual = """
def generar_paginas_individuales(articulos):
    for art in articulos:
        art_id = art.get('id', '1')
        titulo = art.get('titulo', 'Portal Amazonía')
        texto = art.get('texto', '')
        imagen = art.get('imagen', 'images/logo.png')
        fuente = art.get('fuente', 'Redacción Amazonía')
        fecha = art.get('fecha', '')
        
        # Asegurar ruta absoluta de imagen para Open Graph de Facebook
        img_og = imagen if imagen.startswith('http') else "https://portal-ia-web.web.app/" + imagen

        html_art = f\"\"\"<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo} - Portal Amazonía</title>
    
    <!-- Open Graph para Facebook y WhatsApp -->
    <meta property="og:title" content="{titulo}" />
    <meta property="og:description" content="{texto[:150]}..." />
    <meta property="og:image" content="{img_og}" />
    <meta property="og:url" content="https://portal-ia-web.web.app/articulo_{art_id}.html" />
    <meta property="og:type" content="article" />

    <link rel="stylesheet" href="w3.css">
    <link rel="stylesheet" href="amazonia.css">
    <style>
        body {{ background: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }}
        .header-nav {{ background: #1f1f1f; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d4af37; }}
        .header-nav a {{ color: #d4af37; text-decoration: none; font-weight: bold; font-size: 18px; }}
        .container {{ max-width: 800px; margin: 40px auto; background: #1e1e1e; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
        h1 {{ color: #d4af37; font-size: 28px; margin-bottom: 10px; }}
        .meta {{ color: #888; font-size: 14px; margin-bottom: 20px; }}
        img {{ width: 100%; max-height: 450px; object-fit: cover; border-radius: 6px; margin-bottom: 25px; }}
        .texto-articulo {{ font-size: 18px; line-height: 1.7; color: #dcdcdc; white-space: pre-line; }}
        .acciones {{ margin-top: 40px; display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }}
        .btn {{ padding: 12px 25px; font-weight: bold; border-radius: 4px; text-decoration: none; border: none; cursor: pointer; }}
        .btn-ws {{ background: #25D366; color: white; }}
        .btn-fb {{ background: #1877F2; color: white; }}
        .btn-volver {{ background: #d4af37; color: black; }}
    </style>
</head>
<body>
    <div class="header-nav">
        <a href="index.html">⬅ Volver al Portal Amazonía</a>
        <a href="index.html">Inicio</a>
    </div>

    <div class="container">
        <h1>{titulo}</h1>
        <div class="meta">📅 {fecha} &nbsp;|&nbsp; ✍️ {fuente}</div>
        <img src="{imagen}" alt="{titulo}">
        <div class="texto-articulo">{texto}</div>

        <div class="acciones">
            <a href="https://api.whatsapp.com/send?text={titulo}%20-%20https://portal-ia-web.web.app/articulo_{art_id}.html" target="_blank" class="btn btn-ws">💬 Compartir en WhatsApp</a>
            <a href="https://www.facebook.com/sharer/sharer.php?u=https://portal-ia-web.web.app/articulo_{art_id}.html" target="_blank" class="btn btn-fb">📘 Compartir en Facebook</a>
            <a href="index.html" class="btn btn-volver">🏠 Ir al Inicio</a>
        </div>
    </div>
</body>
</html>
\"\"\"
        
        filepath = os.path.join(base_dir, f"articulo_{art_id}.html")
        with open(filepath, "w", encoding="utf-8") as f_art:
            f_art.write(html_art)
"""
        code = code + "\n\n" + funcion_individual

    # Asegurar que se llame a esta función dentro del script principal
    if "generar_paginas_individuales(" not in code:
        # Buscar el punto donde guarda el index.html y agregar la llamada
        code = code.replace("with open(", "generar_paginas_individuales(articulos)\n    with open(", 1)

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)

print("¡Generador de páginas individuales de artículos integrado con éxito!")
