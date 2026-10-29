import os
import json
import urllib.parse
import re
import html as html_lib
import base64

base_dir = r"C:\Portal"
noticias_dir = os.path.join(base_dir, "noticias")
os.makedirs(noticias_dir, exist_ok=True)

# 1. Leer articulos_portal
archivo_datos = None
for nombre in ["articulos_portal", "articulos_portal.json", "data.json"]:
    ruta = os.path.join(base_dir, nombre)
    if os.path.exists(ruta):
        archivo_datos = ruta
        break

if not archivo_datos:
    print("❌ No se encontró el archivo de datos articulos_portal.")
    exit(1)

with open(archivo_datos, "r", encoding="utf-8") as f:
    datos_raw = json.load(f)

articulos = list(datos_raw.values()) if isinstance(datos_raw, dict) else datos_raw

# Plantilla de puente estático 100% compatible con el depurador de Facebook (Sharing Debugger)
template_og_perfecto = """<!DOCTYPE html>
<html lang="es" prefix="og: https://ogp.me/ns#">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITULO_HTML__ - Portal Amazonía</title>
    
    <link rel="canonical" href="__URL_PAGINA__" />
    
    <!-- Open Graph estricto y validado para Meta -->
    <meta property="og:locale" content="es_BO" />
    <meta property="og:site_name" content="Portal Amazonía" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="__URL_PAGINA__" />
    <meta property="og:title" content="__TITULO_ATTR__" />
    <meta property="og:description" content="__DESCRIPCION_ATTR__" />
    <meta property="og:image" content="__IMAGEN_OG__" />
    <meta property="og:image:secure_url" content="__IMAGEN_OG__" />
    <meta property="og:image:type" content="image/jpeg" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta property="og:image:alt" content="__TITULO_ATTR__" />
    
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="__TITULO_ATTR__" />
    <meta name="twitter:description" content="__DESCRIPCION_ATTR__" />
    <meta name="twitter:image" content="__IMAGEN_OG__" />

    <style>
        body { background: #121212; color: #e5e5e5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px 20px; text-align: center; }
        .card { max-width: 650px; margin: 0 auto; background: #1e1e1e; padding: 30px; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.7); border: 1px solid #333; }
        h1 { color: #d4af37; font-size: 22px; margin-bottom: 15px; line-height: 1.4; }
        img { max-width: 100%; height: auto; max-height: 380px; object-fit: contain; border-radius: 6px; margin-bottom: 20px; background: #000; display: block; margin-left: auto; margin-right: auto; }
        p { font-size: 16px; line-height: 1.6; color: #cccccc; margin-bottom: 25px; }
        .btn { display: inline-block; background: #d4af37; color: #000; padding: 12px 28px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 16px; transition: 0.2s; }
        .btn:hover { background: #e5c158; }
    </style>

    <script>
        // Redirección controlada para humanos (los bots de Meta leen la página sin trabarse)
        window.addEventListener('load', function() {
            var ua = (navigator.userAgent || "").toLowerCase();
            var esBot = /bot|crawl|spider|facebookexternalhit|meta|whatsapp|instagram|tiktok|twitter|preview|headless|lighthouse|slurp|embed/i.test(ua);
            if (!esBot && !navigator.webdriver) {
                setTimeout(function() {
                    window.location.replace("../index.html?id=__ID_ART__&articulo=__ID_ART__");
                }, 1500);
            }
        });
    </script>
</head>
<body>
    <div class="card">
        <h1>__TITULO_HTML__</h1>
        <img src="__IMAGEN_OG__" alt="__TITULO_ATTR__">
        <p>__DESCRIPCION_HTML__</p>
        <a href="../index.html?id=__ID_ART__&articulo=__ID_ART__" class="btn">🚀 Abrir Lectura Inmersiva</a>
    </div>
</body>
</html>"""

contador = 0
for idx, art in enumerate(articulos):
    art_id = str(art.get("id") or art.get("id_art") or (idx + 1)).strip()
    titulo = str(art.get("titulo") or art.get("title") or "Portal Amazonía").strip()
    imagen = str(art.get("imagen") or art.get("img") or "images/default.jpg").strip()

    partes_txt = []
    for k, v in art.items():
        if k.lower() not in ("id", "id_art", "titulo", "title", "categoria", "tipo", "fecha", "fuente", "imagen", "img", "url", "audio", "video"):
            if isinstance(v, str) and v.strip() and not v.startswith("data:image") and not v.startswith("images/"):
                partes_txt.append(v.strip())
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str) and item.strip():
                        partes_txt.append(item.strip())

    texto_limpio = re.sub(r"<[^>]+>", " ", " ".join(partes_txt))
    texto_limpio = re.sub(r"\s+", " ", texto_limpio).strip()
    if not texto_limpio:
        texto_limpio = f"{titulo} - Portal Amazonía"
    extracto_og = texto_limpio[:280] + ("..." if len(texto_limpio) > 280 else "")

    # Forzar URL absoluta estricta HTTPS para og:image
    if imagen.startswith("data:image"):
        try:
            header, b64data = imagen.split(",", 1)
            ext = "png" if "png" in header else "jpg"
            nombre_img = f"img_art_{art_id}.{ext}"
            ruta_img_fisica = os.path.join(noticias_dir, nombre_img)
            with open(ruta_img_fisica, "wb") as f_img:
                f_img.write(base64.b64decode(b64data))
            img_og = f"https://portal-ia-web.web.app/noticias/{nombre_img}"
        except Exception:
            img_og = "https://portal-ia-web.web.app/images/default.jpg"
    elif imagen.startswith("http://") or imagen.startswith("https://"):
        img_og = imagen
    else:
        ruta_limpia = imagen.lstrip("./").lstrip("/")
        img_og = f"https://portal-ia-web.web.app/" + urllib.parse.quote(ruta_limpia, safe="/:_-.")

    url_pagina = f"https://portal-ia-web.web.app/noticias/articulo_{art_id}.html"

    html_pagina = (
        template_og_perfecto.replace("__TITULO_HTML__", html_lib.escape(titulo, quote=False))
        .replace("__TITULO_ATTR__", html_lib.escape(titulo, quote=True))
        .replace("__DESCRIPCION_ATTR__", html_lib.escape(extracto_og, quote=True))
        .replace("__DESCRIPCION_HTML__", html_lib.escape(extracto_og, quote=False))
        .replace("__IMAGEN_OG__", img_og)
        .replace("__URL_PAGINA__", url_pagina)
        .replace("__ID_ART__", urllib.parse.quote(art_id))
    )

    filepath = os.path.join(noticias_dir, f"articulo_{art_id}.html")
    with open(filepath, "w", encoding="utf-8") as f_art:
        f_art.write(html_pagina)
    contador += 1

print(f"✅ {contador} páginas estáticas generadas con Open Graph absoluto en C:\\Portal\\noticias")
