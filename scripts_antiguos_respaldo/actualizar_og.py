import os
import json

base_dir = r"C:\Portal"
public_dir = os.path.join(base_dir, "public")
noticias_dir = os.path.join(public_dir, "noticias")

if not os.path.exists(noticias_dir):
    os.makedirs(noticias_dir)

json_path = os.path.join(base_dir, "articulos_portal.json")
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        articulos = json.load(f)
else:
    articulos = []

for art in articulos:
    art_id = str(art.get('id', '1'))
    
    # Asegurar URL absoluta y limpia para la imagen
    img_raw = art.get("imagen", "/images/default.jpg")
    if img_raw.startswith("http"):
        img_absoluta = img_raw
    else:
        img_limpia = img_raw if img_raw.startswith("/") else "/" + img_raw
        img_absoluta = "https://portal-ia-web.web.app" + img_limpia

    titulo = art.get("titulo", "Portal Amazonía")
    resumen = art.get("resumen", "Noticias y actualidad de la Amazonía.")
    
    html_articulo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo} | Portal Amazonía</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Open Graph / Facebook / WhatsApp -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{titulo}">
    <meta property="og:description" content="{resumen}">
    <meta property="og:image" content="{img_absoluta}">
    <meta property="og:image:secure_url" content="{img_absoluta}">
    <meta property="og:image:type" content="image/jpeg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:url" content="https://portal-ia-web.web.app/noticias/articulo_{art_id}.html">
    <meta property="og:site_name" content="Portal Amazonía">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{titulo}">
    <meta name="twitter:description" content="{resumen}">
    <meta name="twitter:image" content="{img_absoluta}">

    <link rel="stylesheet" href="/w3.css">
    <link rel="stylesheet" href="/amazonia.css">
</head>
<body style="background:#0a0a0a; color:#e0e0e0; font-family:Arial, sans-serif; padding:20px;">
    <div style="max-width:800px; margin:40px auto; background:#121212; padding:30px; border-radius:8px; border:1px solid #333;">
        <a href="/" style="color:#ffb81c; text-decoration:none; font-weight:bold; display:inline-block; margin-bottom:20px;">← Volver al Portal</a>
        <div style="margin-bottom:20px; text-align:center;">
            <img src="{img_absoluta}" style="width:100%; max-height:450px; object-fit:contain; background:#000; border-radius:4px;" alt="{titulo}">
        </div>
        <span style="background:#ffb81c; color:black; font-weight:bold; font-size:10px; padding:4px 8px; border-radius:3px; text-transform:uppercase;">{art.get('categoria', 'NOTICIA')}</span>
        <p style="color:#888; font-size:12px; margin:10px 0;">{art.get('fecha', '')} {('| Fuente: ' + art.get('fuente', '')) if art.get('fuente') else ''}</p>
        <h1 style="color:white; font-size:26px; font-weight:800; line-height:1.3; margin-bottom:20px;">{titulo}</h1>
        <div style="font-size:16px; line-height:1.7; color:#ddd; white-space:pre-wrap;">{art.get('texto', '') or resumen}</div>
    </div>
</body>
</html>
"""
    ruta_noticia = os.path.join(noticias_dir, f"articulo_{art_id}.html")
    with open(ruta_noticia, "w", encoding="utf-8") as f:
        f.write(html_articulo)

print("✅ Páginas actualizadas con Open Graph y especificaciones completas de imagen.")
