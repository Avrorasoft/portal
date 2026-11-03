import os
import json

base_dir = r"C:\Portal"
public_dir = os.path.join(base_dir, "public")
if not os.path.exists(public_dir):
    os.makedirs(public_dir)

json_path = os.path.join(base_dir, "articulos_portal.json")
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        articulos = json.load(f)
else:
    articulos = []

articulos = sorted(articulos, key=lambda x: int(x.get("id", 1)) if str(x.get("id", 1)).isdigit() else 1, reverse=True)

memoria_dict = {}
for art in articulos:
    art_id = str(art.get('id', '1'))
    memoria_dict[art_id] = {
        "id": art_id,
        "titulo": art.get("titulo", ""),
        "resumen": art.get("resumen", ""),
        "texto": art.get("texto", ""),
        "categoria": art.get("categoria", "NOTICIA"),
        "fecha": art.get("fecha", ""),
        "fuente": art.get("fuente", ""),
        "imagen": art.get("imagen", "/images/default.jpg"),
        "likes": art.get("likes", 0),
        "sads": art.get("sads", 0),
        "formato": art.get("formato", "")
    }

tarjetas_lista = []
for art in articulos:
    id_art = str(art.get('id', '1'))
    titulo = art.get('titulo', '')
    titulo_attr = titulo.replace('"', '&quot;')
    titulo_js = titulo.replace("'", "\\'")
    resumen = art.get('resumen', '')
    resumen_html = resumen.replace('"', '&quot;')
    imagen = art.get('imagen', '/images/default.jpg')
    imagen_real = imagen if imagen.startswith('http') or imagen.startswith('/') else '/' + imagen
    fecha = art.get('fecha', '')
    fuente = art.get('fuente', '')
    fecha_txt = f"{fecha} | Fuente: {fuente}" if fuente else fecha
    categoria = art.get('categoria', 'NOTICIA')
    categoria_html = categoria.upper()
    likes = art.get('likes', 0)
    sads = art.get('sads', 0)

    tarjeta = f"""
            <article class="articulo-mosaico {art.get('formato', '')}" id="card-{id_art}" data-categoria="{categoria_html}">
                <div class="badge" id="badge-{id_art}">{categoria_html}</div>
                <div class="mosaico-img-container">
                    <img src="{imagen_real}" id="img-{id_art}" class="mosaico-img" alt="{titulo_attr}" loading="lazy" onerror="this.onerror=null; this.src='/images/default.jpg';">
                </div>
                <div class="texto-container">
                    <span class="fecha-tarjeta" id="fecha-{id_art}">{fecha_txt}</span>
                    <h3 id="titulo-{id_art}">{titulo_attr}</h3>
                    <p id="resumen-{id_art}">{resumen_html}</p>
                </div>
                <div class="tarjeta-footer">
                    <div class="botones-principales-tarjeta">
                        <button class="btn-leer" onclick="abrirLectura('{id_art}')">Leer Artículo</button>
                        <button class="btn-compartir-tarjeta" id="share-{id_art}" onclick="compartirNativo('{titulo_js}', event)" title="Compartir">🔗</button>
                    </div>
                    <div class="reacciones-bar">
                        <button id="btn-card-likes-{id_art}" onclick="reaccionar('{id_art}', 'likes')" class="btn-reaccion" title="Me gusta">👍 <span id="likes-{id_art}">{likes}</span></button>
                        <button id="btn-card-sads-{id_art}" onclick="reaccionar('{id_art}', 'sads')" class="btn-reaccion" title="Qué tristeza">😢 <span id="sads-{id_art}">{sads}</span></button>
                    </div>
                </div>
            </article>"""
    tarjetas_lista.append(tarjeta)

tarjetas_html = "\n".join(tarjetas_lista)
json_memoria = json.dumps(memoria_dict, ensure_ascii=False).replace("</script>", "<\\/script>")

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
        .mosaico-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); grid-auto-rows: auto; grid-auto-flow: dense; gap: 25px; max-width: 1400px; margin: 40px auto; padding: 0 20px; }
        .articulo-mosaico { position: relative; border-radius: 6px; background: #111111; border: 1px solid #FFFFFF; box-shadow: 0 6px 20px rgba(255,255,255,0.12), 0 10px 25px rgba(0,0,0,0.9); padding: 20px; display: flex; flex-direction: column; justify-content: flex-start; gap: 15px; box-sizing: border-box; transition: all 0.4s ease; height: 100%; }
        .articulo-mosaico:hover { transform: translateY(-6px); box-shadow: 0 8px 30px rgba(255,255,255,0.18), 0 15px 40px rgba(0,0,0,1); border-color: var(--accent-gold); z-index: 50; }
        .mosaico-img-container { width: 100%; display: flex; align-items: center; justify-content: center; background: #080808; border-radius: 4px; box-shadow: inset 0 0 10px rgba(0,0,0,0.9); padding: 8px; position: relative; box-sizing: border-box; flex-shrink: 0; }
        .mosaico-img { width: 100%; height: auto; max-height: 400px; object-fit: contain; box-shadow: 0 4px 15px rgba(255,255,255,0.08), 0 8px 25px rgba(0,0,0,0.8); transition: transform 0.5s ease; }
        .articulo-mosaico:hover .mosaico-img { transform: scale(1.03); }
        .texto-container { display: flex; flex-direction: column; justify-content: flex-start; flex-grow: 0; }
        .texto-container h3 { margin: 0 0 10px 0; font-size: 20px; font-weight: 800; color: white; line-height: 1.2; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }
        .fecha-tarjeta { font-size: 11px; color: #888; margin-bottom: 8px; display: block; text-transform: uppercase; letter-spacing: 1px; }
        .texto-container p { margin: 0; font-size: 14px; line-height: 1.6; color: #ccc; display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden; }
        .tarjeta-footer { margin-top: auto; display: flex; flex-direction: column; gap: 15px; padding-top: 15px; }
        .botones-principales-tarjeta { display: flex; gap: 10px; align-items: center; }
        .btn-leer { padding: 10px 20px; background: var(--accent-gold); color: black; border: none; font-weight: 900; font-size: 11px; cursor: pointer; border-radius: 4px; text-transform: uppercase; box-shadow: 0 4px 10px rgba(0,0,0,0.5); transition: background 0.3s; flex-grow: 1; text-align: center; }
        .btn-leer:hover { background: white; }
        .btn-compartir-tarjeta { background: #222; color: white; border: 1px solid #444; padding: 9px 15px; border-radius: 4px; font-size: 16px; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .btn-compartir-tarjeta:hover { background: var(--accent-gold); color: black; border-color: var(--accent-gold); }
        .badge { position: absolute; top: 25px; left: 25px; background: var(--accent-gold); color: black; font-weight: 900; font-size: 10px; padding: 6px 12px; border-radius: 4px; text-transform: uppercase; z-index: 10; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .reacciones-bar { display: flex; gap: 10px; border-top: 1px solid #333; padding-top: 15px; }
        .btn-reaccion { background: transparent; border: 1px solid #444; color: #ccc; border-radius: 8px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 18px; font-weight: bold; cursor: pointer; transition: all 0.3s; min-height: 48px; padding: 8px 10px; flex-grow: 1; }
        .btn-reaccion:hover { background: rgba(255,255,255,0.1); border-color: var(--accent-gold); color: white; }
        .btn-reaccion.activo { background: rgba(255,184,28,0.2); border-color: var(--accent-gold); color: var(--accent-gold); }

        @media (min-width: 851px) {
            .span-big { grid-column: span 2; grid-row: span 2; }
            .span-big .mosaico-img-container { flex-grow: 1; min-height: 350px; }
            .span-big .mosaico-img { max-height: 100%; height: 100%; object-fit: cover; }
            .span-v { grid-row: span 2; }
        }

        #btn-ir-footer {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--accent-gold, #ffb81c);
            color: black;
            border: none;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
            z-index: 99;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        #btn-ir-footer:hover { transform: scale(1.1); background: white; }
    </style>
</head>
<body>
    <button id="btn-ir-footer" onclick="scrollToFooter()" title="Ir al pie de página">⬇</button>

    <header style="text-align:center; padding:40px 20px 20px 20px;">
        <h1 style="font-size:36px; font-weight:900; color:white; margin:0; text-shadow:0 2px 10px rgba(255,184,28,0.3);">PORTAL AMAZONÍA</h1>
        <p style="color:#888; font-size:14px; margin-top:10px; letter-spacing:2px; text-transform:uppercase;">Vanguardia y Territorio</p>
    </header>

    <div id="mosaico" class="mosaico-container">
        __TARJETAS_HTML__
    </div>

    <footer id="portal-footer" style="background:#111; color:#aaa; text-align:center; padding:40px 20px; border-top:1px solid #333; margin-top:60px;">
        <p style="margin:0; font-size:14px;">Portal Amazonía &copy; 2026 — Vanguardia y Territorio</p>
    </footer>

    <!-- Modal Inmersivo de Lectura -->
    <div id="modal-lectura" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:1000; overflow-y:auto; padding:40px 20px;">
        <div class="lectura-box" style="max-width:900px; margin:0 auto; background:#121212; padding:40px; border-radius:8px; border:1px solid #333; position:relative;">
            <button onclick="cerrarLectura()" style="position:absolute; top:20px; right:20px; background:#222; color:white; border:none; padding:10px 15px; border-radius:4px; cursor:pointer; font-weight:bold;">✕ Cerrar</button>
            <div style="margin-bottom:25px;">
                <img id="lectura-img" src="" style="width:100%; max-height:450px; object-fit:contain; background:#000; border-radius:6px;" onerror="this.onerror=null; this.src='/images/default.jpg';">
            </div>
            <span id="lectura-categoria" class="badge" style="position:relative; top:0; left:0; display:inline-block; margin-bottom:15px;"></span>
            <span id="lectura-fecha" class="fecha-tarjeta"></span>
            <h1 id="lectura-titulo" style="font-size:30px; font-weight:800; color:white; margin-bottom:15px; line-height:1.3;"></h1>
            <span id="lectura-fuente" style="display:block; margin-bottom:20px; color:#888; font-size:13px;"></span>
            
            <div id="lectura-texto" style="font-size:17px; line-height:1.8; color:#ddd; margin-bottom:30px; white-space:pre-wrap;"></div>

            <div style="margin-top: 30px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                <button class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: #25D366; color: white; font-weight: bold; border-radius: 4px; border: none; cursor: pointer;" onclick="compartirWhatsApp()">💬 WhatsApp</button>
                <button class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: #1877F2; color: white; font-weight: bold; border-radius: 4px; border: none; cursor: pointer;" onclick="compartirFacebook()">📘 Facebook</button>
                <button id="btn-audio-inmersivo" class="btn-audio" style="padding: 12px 20px; font-size: 15px; background: transparent; color: var(--accent-gold); border: 1px solid var(--accent-gold); font-weight: bold; border-radius: 4px; cursor: pointer;" onclick="toggleAudioInmersivo()">🔊 Escuchar Artículo</button>
            </div>

            <div class="reacciones-bar" style="margin-top: 25px; border-top: 1px solid #333; padding-top: 25px;">
                <button id="btn-like-inmersivo" class="btn-reaccion" onclick="reaccionarModal('likes')">👍 Me Gusta</button>
                <button id="btn-sad-inmersivo" class="btn-reaccion" onclick="reaccionarModal('sads')">😢 Qué Tristeza</button>
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

            document.getElementById('lectura-img').src = art.imagen || '/images/default.jpg';
            document.getElementById('lectura-categoria').innerText = art.categoria || 'NOTICIA';
            document.getElementById('lectura-fecha').innerText = art.fuente ? `${art.fecha || ''} | Fuente: ${art.fuente}` : (art.fecha || '');
            document.getElementById('lectura-titulo').innerText = art.titulo || '';
            document.getElementById('lectura-fuente').innerText = art.fuente ? `Fuente: ${art.fuente}` : '';
            document.getElementById('lectura-texto').innerText = art.texto || art.resumen || '';

            document.getElementById('modal-lectura').style.display = 'block';
            document.body.style.overflow = 'hidden';

            actualizarEstadoBotonesReaccion(id);
        }

        function cerrarLectura() {
            if(window.speechSynthesis) window.speechSynthesis.cancel();
            document.getElementById('modal-lectura').style.display = 'none';
            document.body.style.overflow = 'auto';
            articuloActivoId = null;
        }

        function reaccionar(id, tipo) {
            const key = "reaccion_" + id;
            const actual = localStorage.getItem(key);
            if (!memoriaArticulos[id]) return;

            if (actual === tipo) return;

            if (actual === 'likes' && tipo === 'sads') {
                memoriaArticulos[id].likes = Math.max(0, (memoriaArticulos[id].likes || 1) - 1);
                memoriaArticulos[id].sads = (memoriaArticulos[id].sads || 0) + 1;
            } else if (actual === 'sads' && tipo === 'likes') {
                memoriaArticulos[id].sads = Math.max(0, (memoriaArticulos[id].sads || 1) - 1);
                memoriaArticulos[id].likes = (memoriaArticulos[id].likes || 0) + 1;
            } else if (!actual) {
                if (tipo === 'likes') memoriaArticulos[id].likes = (memoriaArticulos[id].likes || 0) + 1;
                if (tipo === 'sads') memoriaArticulos[id].sads = (memoriaArticulos[id].sads || 0) + 1;
            }

            localStorage.setItem(key, tipo);

            const lSpan = document.getElementById(`likes-${id}`);
            const sSpan = document.getElementById(`sads-${id}`);
            if (lSpan) lSpan.innerText = memoriaArticulos[id].likes;
            if (sSpan) sSpan.innerText = memoriaArticulos[id].sads;

            const bL = document.getElementById(`btn-card-likes-${id}`);
            const bS = document.getElementById(`btn-card-sads-${id}`);
            if (bL) bL.className = "btn-reaccion " + (tipo === 'likes' ? 'activo' : '');
            if (bS) bS.className = "btn-reaccion " + (tipo === 'sads' ? 'activo' : '');

            if (articuloActivoId === id) {
                actualizarEstadoBotonesReaccion(id);
            }
        }

        function reaccionarModal(tipo) {
            if (articuloActivoId) {
                reaccionar(articuloActivoId, tipo);
            }
        }

        function actualizarEstadoBotonesReaccion(id) {
            const art = memoriaArticulos[id];
            if (!art) return;
            const rUser = localStorage.getItem("reaccion_" + id);
            
            const bL = document.getElementById('btn-like-inmersivo');
            const bS = document.getElementById('btn-sad-inmersivo');
            if (bL) {
                bL.className = "btn-reaccion " + (rUser === 'likes' ? 'activo' : '');
                bL.innerHTML = `👍 Me Gusta (${art.likes || 0})`;
            }
            if (bS) {
                bS.className = "btn-reaccion " + (rUser === 'sads' ? 'activo' : '');
                bS.innerHTML = `😢 Qué Tristeza (${art.sads || 0})`;
            }
        }

        function scrollToFooter() {
            const footer = document.getElementById('portal-footer');
            if (footer) footer.scrollIntoView({ behavior: 'smooth' });
        }

        window.compartirNativo = function(t, ev) {
            let idArt = "1";
            try {
                if (ev && ev.target) {
                    let btn = ev.target.closest('button');
                    if (btn && btn.id && btn.id.startsWith('share-')) {
                        idArt = btn.id.replace('share-', '');
                    }
                }
            } catch(err) {}
            
            const urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(urlArt).catch(() => {});
            }
            const fbWin = window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
            if (!fbWin || fbWin.closed || typeof fbWin.closed == 'undefined') {
                alert("Enlace copiado al portapapeles. Pégalo directamente en la publicación de tu página de Facebook.");
            }
        };

        window.compartirWhatsApp = function() {
            const titulo = document.getElementById('lectura-titulo') ? document.getElementById('lectura-titulo').innerText : "Portal Amazonía";
            const idArt = articuloActivoId || "1";
            const urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
            const texto = encodeURIComponent("📰 *" + titulo + "*\n\n👉 " + urlArt);
            window.open("https://api.whatsapp.com/send?text=" + texto, "_blank");
        };

        window.compartirFacebook = function() {
            const idArt = articuloActivoId || "1";
            const urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(urlArt).catch(() => {});
            }
            const fbWin = window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), "_blank", 'width=650,height=600');
            if (!fbWin || fbWin.closed || typeof fbWin.closed == 'undefined') {
                alert("Enlace copiado al portapapeles. Pégalo directamente en la publicación de tu página de Facebook.");
            }
        };

        window.toggleAudioInmersivo = function() {
            const txt = document.getElementById('lectura-texto').innerText;
            if(!txt) return;
            if(window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
                return;
            }
            const msg = new SpeechSynthesisUtterance(txt);
            msg.lang = 'es-ES';
            window.speechSynthesis.speak(msg);
        };
    </script>
</body>
</html>
"""

html_completo = plantilla_html.replace("__TARJETAS_HTML__", tarjetas_html).replace("__JSON_MEMORIA__", json_memoria)

# Guardar tanto en raíz como en public
with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_completo)

with open(os.path.join(public_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_completo)

print(f"✅ index.html regenerado exitosamente con los {len(articulos)} artículos completos.")
