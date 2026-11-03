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

articulos = sorted(articulos, key=lambda x: int(x.get("id", 1)) if str(x.get("id", 1)).isdigit() else 1, reverse=True)

memoria_dict = {}
tarjetas_lista = []

for art in articulos:
    art_id = str(art.get('id', '1'))
    titulo = art.get('titulo', '')
    titulo_attr = titulo.replace('"', '&quot;')
    resumen = art.get('resumen', '')
    resumen_html = resumen.replace('"', '&quot;')
    
    img_raw = art.get("imagen", "/images/default.jpg")
    if img_raw.startswith("http"):
        img_absoluta = img_raw
    else:
        img_limpia = img_raw if img_raw.startswith("/") else "/" + img_raw
        img_absoluta = "https://portal-ia-web.web.app" + img_limpia

    fecha = art.get('fecha', '')
    fuente = art.get('fuente', '')
    fecha_txt = f"{fecha} | Fuente: {fuente}" if fuente else fecha
    categoria = art.get('categoria', 'NOTICIA')
    categoria_html = categoria.upper()
    likes = art.get('likes', 0)
    sads = art.get('sads', 0)

    memoria_dict[art_id] = {
        "id": art_id,
        "titulo": titulo,
        "resumen": resumen,
        "texto": art.get("texto", ""),
        "categoria": categoria_html,
        "fecha": fecha,
        "fuente": fuente,
        "imagen": img_absoluta,
        "likes": likes,
        "sads": sads,
        "formato": art.get("formato", "")
    }

    # Generar página HTML individual con Open Graph exacto apuntando al ID
    html_articulo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo} | Portal Amazonía</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{titulo}">
    <meta property="og:description" content="{resumen}">
    <meta property="og:image" content="{img_absoluta}">
    <meta property="og:url" content="https://portal-ia-web.web.app/noticias/articulo_{art_id}.html">
    <meta property="og:site_name" content="Portal Amazonía">
    <link rel="stylesheet" href="/w3.css">
    <link rel="stylesheet" href="/amazonia.css">
</head>
<body style="background:#0a0a0a; color:#e0e0e0; font-family:Arial, sans-serif; padding:20px;">
    <div style="max-width:800px; margin:40px auto; background:#121212; padding:30px; border-radius:8px; border:1px solid #333;">
        <a href="/" style="color:#ffb81c; text-decoration:none; font-weight:bold; display:inline-block; margin-bottom:20px;">← Volver al Portal</a>
        <div style="margin-bottom:20px; text-align:center;">
            <img src="{img_absoluta}" style="width:100%; max-height:450px; object-fit:contain; background:#000; border-radius:4px;" alt="{titulo}">
        </div>
        <span style="background:#ffb81c; color:black; font-weight:bold; font-size:10px; padding:4px 8px; border-radius:3px; text-transform:uppercase;">{categoria_html}</span>
        <p style="color:#888; font-size:12px; margin:10px 0;">{fecha_txt}</p>
        <h1 style="color:white; font-size:26px; font-weight:800; line-height:1.3; margin-bottom:20px;">{titulo}</h1>
        <div style="font-size:16px; line-height:1.7; color:#ddd; white-space:pre-wrap;">{art.get('texto', '') or resumen}</div>
    </div>
</body>
</html>
"""
    with open(os.path.join(noticias_dir, f"articulo_{art_id}.html"), "w", encoding="utf-8") as f:
        f.write(html_articulo)

    # Crear tarjeta con llamada directa al ID en el botón de compartir
    tarjeta = f"""
            <article class="articulo-mosaico {art.get('formato', '')}" id="card-{art_id}" data-categoria="{categoria_html}">
                <div class="badge" id="badge-{art_id}">{categoria_html}</div>
                <div class="mosaico-img-container">
                    <img src="{img_absoluta}" id="img-{art_id}" class="mosaico-img" alt="{titulo_attr}" loading="lazy" onerror="this.onerror=null; this.src='/images/default.jpg';">
                </div>
                <div class="texto-container">
                    <span class="fecha-tarjeta" id="fecha-{art_id}">{fecha_txt}</span>
                    <h3 id="titulo-{art_id}">{titulo_attr}</h3>
                    <p id="resumen-{art_id}">{resumen_html}</p>
                </div>
                <div class="tarjeta-footer">
                    <div class="botones-principales-tarjeta">
                        <button class="btn-leer" onclick="abrirLectura('{art_id}')">Leer Artículo</button>
                        <button class="btn-compartir-tarjeta" id="share-{art_id}" onclick="compartirArticulo('{art_id}')" title="Compartir">🔗</button>
                    </div>
                    <div class="reacciones-bar">
                        <button id="btn-card-likes-{art_id}" onclick="reaccionar('{art_id}', 'likes')" class="btn-reaccion" title="Me gusta">👍 <span id="likes-{art_id}">{likes}</span></button>
                        <button id="btn-card-sads-{art_id}" onclick="reaccionar('{art_id}', 'sads')" class="btn-reaccion" title="Qué tristeza">😢 <span id="sads-{art_id}">{sads}</span></button>
                    </div>
                </div>
            </article>"""
    tarjetas_lista.append(tarjeta)

tarjetas_html = "\n".join(tarjetas_lista)
json_memoria = json.dumps(memoria_dict, ensure_ascii=False).replace("</script>", "<\\/script>")

# Estructura limpia del index.html con la función compartirArticulo corregida
plantilla_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Portal Amazonía | Vanguardia y Territorio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/w3.css">
    <link rel="stylesheet" href="/amazonia.css">
    <link rel="stylesheet" href="/font-awesome.min.css">
    <style>
        .mosaico-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap: 25px; max-width: 1400px; margin: 40px auto; padding: 0 20px; }
        .articulo-mosaico { position: relative; border-radius: 6px; background: #111111; border: 1px solid #FFFFFF; box-shadow: 0 6px 20px rgba(255,255,255,0.12); padding: 20px; display: flex; flex-direction: column; justify-content: flex-start; gap: 15px; box-sizing: border-box; transition: all 0.4s ease; height: 100%; }
        .articulo-mosaico:hover { transform: translateY(-6px); border-color: var(--accent-gold); z-index: 50; }
        .mosaico-img-container { width: 100%; display: flex; align-items: center; justify-content: center; background: #080808; border-radius: 4px; padding: 8px; box-sizing: border-box; }
        .mosaico-img { width: 100%; height: auto; max-height: 400px; object-fit: contain; }
        .texto-container h3 { margin: 0 0 10px 0; font-size: 20px; font-weight: 800; color: white; }
        .fecha-tarjeta { font-size: 11px; color: #888; margin-bottom: 8px; display: block; text-transform: uppercase; letter-spacing: 1px; }
        .texto-container p { margin: 0; font-size: 14px; line-height: 1.6; color: #ccc; display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }
        .tarjeta-footer { margin-top: auto; display: flex; flex-direction: column; gap: 15px; padding-top: 15px; }
        .botones-principales-tarjeta { display: flex; gap: 10px; align-items: center; }
        .btn-leer { padding: 10px 20px; background: var(--accent-gold); color: black; border: none; font-weight: 900; font-size: 11px; cursor: pointer; border-radius: 4px; text-transform: uppercase; flex-grow: 1; text-align: center; }
        .btn-compartir-tarjeta { background: #222; color: white; border: 1px solid #444; padding: 9px 15px; border-radius: 4px; font-size: 16px; cursor: pointer; }
        .badge { position: absolute; top: 25px; left: 25px; background: var(--accent-gold); color: black; font-weight: 900; font-size: 10px; padding: 6px 12px; border-radius: 4px; text-transform: uppercase; z-index: 10; }
        .reacciones-bar { display: flex; gap: 10px; border-top: 1px solid #333; padding-top: 15px; }
        .btn-reaccion { background: transparent; border: 1px solid #444; color: #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 18px; font-weight: bold; cursor: pointer; min-height: 48px; padding: 8px 10px; flex-grow: 1; }
        .btn-reaccion.activo { background: rgba(255,184,28,0.2); border-color: var(--accent-gold); color: var(--accent-gold); }
    </style>
</head>
<body>
    <header style="text-align:center; padding:40px 20px 20px 20px;">
        <h1 style="font-size:36px; font-weight:900; color:white; margin:0;">PORTAL AMAZONÍA</h1>
        <p style="color:#888; font-size:14px; margin-top:10px; letter-spacing:2px; text-transform:uppercase;">Vanguardia y Territorio</p>
    </header>

    <div id="mosaico" class="mosaico-container">
        __TARJETAS_HTML__
    </div>

    <!-- Modal Inmersivo de Lectura -->
    <div id="modal-lectura" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:1000; overflow-y:auto; padding:40px 20px;">
        <div style="max-width:900px; margin:0 auto; background:#121212; padding:40px; border-radius:8px; border:1px solid #333; position:relative; color:white;">
            <button onclick="cerrarLectura()" style="position:absolute; top:20px; right:20px; background:#222; color:white; border:none; padding:10px 15px; border-radius:4px; cursor:pointer; font-weight:bold;">✕ Cerrar</button>
            <div style="margin-bottom:25px;">
                <img id="lectura-img" src="" style="width:100%; max-height:450px; object-fit:contain; background:#000; border-radius:6px;">
            </div>
            <span id="lectura-categoria" class="badge" style="position:relative; top:0; left:0; display:inline-block; margin-bottom:15px;"></span>
            <span id="lectura-fecha" class="fecha-tarjeta"></span>
            <h1 id="lectura-titulo" style="font-size:30px; font-weight:800; margin-bottom:15px; line-height:1.3;"></h1>
            <div id="lectura-texto" style="font-size:17px; line-height:1.8; color:#ddd; margin-bottom:30px; white-space:pre-wrap;"></div>

            <div style="margin-top: 30px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                <button style="padding: 12px 20px; background: #25D366; color: white; font-weight: bold; border-radius: 4px; border: none; cursor: pointer;" onclick="compartirWhatsApp()">💬 WhatsApp</button>
                <button style="padding: 12px 20px; background: #1877F2; color: white; font-weight: bold; border-radius: 4px; border: none; cursor: pointer;" onclick="compartirFacebookModal()">📘 Facebook</button>
            </div>
        </div>
    </div>

    <script>
        const memoriaArticulos = __JSON_MEMORIA__;
        let articuloActivoId = null;

        function abrirLectura(id) {
            const art = memoriaArticulos[id];
            if (!art) return;
            articuloActivoId = id;
            document.getElementById('lectura-img').src = art.imagen;
            document.getElementById('lectura-categoria').innerText = art.categoria;
            document.getElementById('lectura-fecha').innerText = art.fuente ? `${art.fecha} | Fuente: ${art.fuente}` : art.fecha;
            document.getElementById('lectura-titulo').innerText = art.titulo;
            document.getElementById('lectura-texto').innerText = art.texto || art.resumen;
            document.getElementById('modal-lectura').style.display = 'block';
            document.body.style.overflow = 'hidden';
        }

        function cerrarLectura() {
            document.getElementById('modal-lectura').style.display = 'none';
            document.body.style.overflow = 'auto';
            articuloActivoId = null;
        }

        function compartirArticulo(id) {
            const urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + id + ".html";
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(urlArt).catch(() => {});
            }
            const fbUrl = "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt);
            const fbWin = window.open(fbUrl, '_blank', 'width=650,height=600');
            if (!fbWin || fbWin.closed || typeof fbWin.closed == 'undefined') {
                alert("Enlace copiado al portapapeles:\n" + urlArt);
            }
        }

        window.compartirWhatsApp = function() {
            if (!articuloActivoId) return;
            const art = memoriaArticulos[articuloActivoId];
            const urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + articuloActivoId + ".html";
            const texto = encodeURIComponent("📰 *" + art.titulo + "*\n\n👉 " + urlArt);
            window.open("https://api.whatsapp.com/send?text=" + texto, "_blank");
        };

        window.compartirFacebookModal = function() {
            if (articuloActivoId) {
                compartirArticulo(articuloActivoId);
            }
        };

        function reaccionar(id, tipo) {
            console.log("Reacción:", id, tipo);
        }
    </script>
</body>
</html>
"""

html_completo = plantilla_html.replace("__TARJETAS_HTML__", tarjetas_html).replace("__JSON_MEMORIA__", json_memoria)

with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_completo)

with open(os.path.join(public_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_completo)

print("✅ Script ejecutado con éxito: IDs inyectados directamente en los botones de compartir.")
