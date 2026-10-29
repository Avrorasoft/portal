import os
import json
import re
import shutil
import unicodedata

def normalizar_texto(texto):
    if not texto: return ""
    texto = str(texto).lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', texto).strip('-')

def asegurar_imagen_default(base_dir):
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    default_path = os.path.join(images_dir, "default.jpg")
    if not os.path.isfile(default_path):
        portada = os.path.join(images_dir, "1003202605032026la-amazonia-al-bordeP.jpg")
        if os.path.isfile(portada):
            shutil.copyfile(portada, default_path)

def buscar_imagen_articulo(art, base_dir):
    id_str = str(art.get("id", "")).strip()
    img_json = str(art.get("imagen", "")).strip()
    
    if img_json.startswith(("http", "data:")):
        return img_json
        
    candidatas = [
        img_json,
        f"imagenes_articulos/{id_str}_imagenes_articulos/{id_str}_imagen_principal.jpg",
        f"imagenes_articulos/{id_str}_imagenes_articulos/{id_str}.jpg",
        f"imagenes_reportajes/{id_str}_imagenes_reportajes/{id_str}_imagen_principal.jpg",
        f"imagenes_reportajes/{id_str}_imagenes_reportajes/{id_str}.jpg",
        f"images/{id_str}.jpg",
        f"images/{id_str}_imagen_principal.jpg"
    ]
    
    for c in candidatas:
        if c and c != "images/default.jpg":
            ruta = os.path.join(base_dir, c.replace("/", os.sep))
            if os.path.isfile(ruta):
                return c.replace("\\", "/")
                
    for root, dirs, files in os.walk(base_dir):
        if '.git' in root or 'node_modules' in root: continue
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                if f.startswith(f"{id_str}_") or f.startswith(f"{id_str}-") or f == f"{id_str}.jpg":
                    return os.path.relpath(os.path.join(root, f), base_dir).replace("\\", "/")
    
    return "images/default.jpg"

def generar_index_estatico():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "articulos_portal.json")
    
    if not os.path.exists(json_path):
        print("ERROR: No existe articulos_portal.json.")
        return

    asegurar_imagen_default(base_dir)

    with open(json_path, "r", encoding="utf-8") as f:
        articulos = json.load(f)

    tarjetas_lista = []
    memoria_dict = {}

    for index, art in enumerate(articulos):
        if art.get("eliminado") is True: 
            continue
            
        id_art = str(art.get("id", index))
        titulo = art.get("titulo", "Sin título")
        resumen = art.get("resumen", "")
        fecha = art.get("fecha", "")
        fuente = art.get("fuente", "Varia")
        categoria = art.get("categoria", "NOTICIA")
        formato = art.get("formato", "")
        likes = art.get("likes", 0)
        sads = art.get("sads", 0)
        
        imagen_real = buscar_imagen_articulo(art, base_dir)
        art["imagen"] = imagen_real
        memoria_dict[id_art] = art

        titulo_attr = titulo.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        titulo_js = titulo.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
        resumen_html = resumen.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        categoria_html = categoria.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        fecha_txt = f"{fecha} | Fuente: {fuente}" if fuente else fecha
        ocultar_etnia = 'style="display:none;"' if categoria.upper() == "ETNIA" else ""

        tarjeta = f"""
            <article class="articulo-mosaico {formato}" id="card-{id_art}" data-id="{id_art}" data-categoria="{categoria_html}" {ocultar_etnia}>
                <div class="admin-controls">
                    <button class="btn-accion" onclick="abrirEditorExistente('{id_art}')">✏️ Editar</button>
                    <button class="btn-accion btn-eliminar" onclick="eliminarNoticia('{id_art}')">🗑️ Borrar</button>
                </div>
                <div class="badge" id="badge-{id_art}">{categoria_html}</div>
                <div class="mosaico-img-container">
                    <img src="{imagen_real}" id="img-{id_art}" class="mosaico-img" alt="{titulo_attr}" loading="lazy" onerror="this.onerror=null; this.src='images/default.jpg';">
                </div>
                <div class="texto-container">
                    <span class="fecha-tarjeta" id="fecha-{id_art}">{fecha_txt}</span>
                    <h3 id="titulo-{id_art}">{titulo_attr}</h3>
                    <p id="resumen-{id_art}">{resumen_html}</p>
                </div>
                <div class="tarjeta-footer">
                    <div class="botones-principales-tarjeta">
                        <button class="btn-leer" onclick="abrirLectura('{id_art}')">Leer Artículo</button>
                        <button class="btn-compartir-tarjeta" id="share-{id_art}" onclick="compartirNativo('{titulo_js}')" title="Compartir">🔗</button>
                    </div>
                    <div class="reacciones-bar">
                        <button id="btn-card-likes-{id_art}" onclick="reaccionar('{id_art}', 'likes')" class="btn-reaccion" title="Me gusta">👍 <span id="likes-{id_art}">{likes}</span></button>
                        <button id="btn-card-sads-{id_art}" onclick="reaccionar('{id_art}', 'sads')" class="btn-reaccion" title="Qué tristeza">😢 <span id="sads-{id_art}">{sads}</span></button>
                    </div>
                </div>
            </article>"""
        tarjetas_lista.append(tarjeta)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(articulos, f, ensure_ascii=False, indent=4)

    tarjetas_html = "\n".join(tarjetas_lista)
    json_memoria = json.dumps(memoria_dict, ensure_ascii=False).replace("</script>", "<\\/script>")
    total_art = str(len(tarjetas_lista))

    plantilla_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Portal Amazonía | Vanguardia y Territorio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="w3.css">
    <link rel="stylesheet" href="amazonia.css">
    <link rel="stylesheet" href="font-awesome.min.css">
    <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-firestore.js"></script>
    <style>
        :root { --deep-green: #0A3D0A; --vibrant-green: #1D9A4C; --accent-gold: #FFB81C; --dark-bg: #121212; --panel-bg: #1e1e1e; --text-main: #E0E0E0; --glass: rgba(25, 25, 25, 0.95); }
        body { font-family: 'Segoe UI', Roboto, sans-serif; background-color: var(--dark-bg); color: var(--text-main); margin: 0; scroll-behavior: smooth; overflow-x: hidden; }
        nav { position: sticky; top: 0; background: rgba(0, 0, 0, 0.95); backdrop-filter: blur(10px); z-index: 2000; box-shadow: 0 4px 20px rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: space-between; padding: 10px 20px; flex-wrap: wrap; }
        .nav-brand { display: flex; align-items: center; gap: 12px; color: white; text-decoration: none; font-weight: 900; font-size: 16px; letter-spacing: 1px; white-space: nowrap; }
        .nav-brand img { height: 35px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); }
        .nav-links-container { display: flex; flex-grow: 1; justify-content: flex-end; gap: 10px; overflow-x: auto; white-space: nowrap; -webkit-overflow-scrolling: touch; padding: 5px 0; scrollbar-width: none; }
        .nav-links-container::-webkit-scrollbar { display: none; }
        .nav-links-container a { color: #ddd; text-decoration: none; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; padding: 8px 12px; border-radius: 4px; transition: all 0.3s; }
        .nav-links-container a:hover { color: var(--accent-gold); background: rgba(255,255,255,0.1); }
        .hero { height: 80vh; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; text-align: center; color: white; background: #000; margin-bottom: 5px; }
        .hero-img { position: absolute; width: 100%; height: 100%; object-fit: cover; opacity: 0.5; }
        .hero-content { position: relative; z-index: 10; max-width: 900px; padding: 20px; }
        .hero-content h1 { font-size: clamp(35px, 7vw, 75px); font-weight: 900; line-height: 1; margin: 0; text-shadow: 0 5px 30px rgba(0,0,0,0.9); text-transform: uppercase; }
        .hero-resumen { font-size: clamp(16px, 3vw, 20px); line-height: 1.6; margin-top: 25px; font-weight: 300; color: #eee; text-shadow: 0 2px 10px rgba(0,0,0,0.9); }
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
            <button type="button" class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: var(--accent-gold); color: black; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;" onclick="window.compartirNoticiaPortal('copiar')">🔗 Copiar Enlace para Página</button>
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
            .span-h-izq, .span-h-der { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr auto; gap: 15px 25px; height: 100%; }
            .span-h-izq .mosaico-img-container { grid-column: 1 / 2; grid-row: 1 / 3; height: 100%; }
            .span-h-izq .texto-container { grid-column: 2 / 3; grid-row: 1 / 2; padding: 0; }
            .span-h-izq .tarjeta-footer { grid-column: 2 / 3; grid-row: 2 / 3; padding-top: 15px; margin-top: auto; }
            .span-h-der .mosaico-img-container { grid-column: 2 / 3; grid-row: 1 / 3; height: 100%; }
            .span-h-der .texto-container { grid-column: 1 / 2; grid-row: 1 / 2; padding: 0; }
            .span-h-der .tarjeta-footer { grid-column: 1 / 2; grid-row: 2 / 3; padding-top: 15px; margin-top: auto; }
        }

        .admin-controls { position: absolute; top: 20px; right: 20px; z-index: 20; display: none; gap: 8px; }
        body.modo-admin .admin-controls { display: flex; }
        .btn-accion { background: rgba(0,0,0,0.85); color: white; border: 1px solid rgba(255,255,255,0.4); padding: 6px 10px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 11px; transition: all 0.3s; }
        .btn-accion:hover { background: var(--accent-gold); color: black; }
        .btn-eliminar:hover { background: #ff4444; color: white; border-color: transparent; }

        .admin-toolbar { display: none; justify-content: center; align-items: center; gap: 15px; flex-wrap: wrap; margin: 20px auto; padding: 15px 20px; max-width: 1100px; background: rgba(29, 154, 76, 0.12); border: 1px solid var(--vibrant-green); border-radius: 8px; }
        body.modo-admin .admin-toolbar { display: flex; }
        .btn-toolbar { background: var(--vibrant-green); color: white; border: none; padding: 12px 22px; border-radius: 4px; font-weight: bold; font-size: 13px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.5); transition: all 0.3s; }
        .btn-toolbar:hover { background: var(--accent-gold); color: black; }

        .modal-inmersivo { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: #000000; z-index: 4000; align-items: flex-start; justify-content: center; overflow-y: auto; overflow-x: hidden; box-sizing: border-box; }
        .lectura-box { background: #111111; color: var(--text-main); width: 100%; max-width: 900px; min-height: 100%; position: relative; box-shadow: 0 0 50px rgba(0,0,0,1); display: flex; flex-direction: column; border-left: 1px solid #222; border-right: 1px solid #222; box-sizing: border-box; }
        .btn-cerrar-lectura, .btn-pin { position: fixed; top: 20px; background: rgba(0, 0, 0, 0.4); color: rgba(255, 255, 255, 0.8); border: none; border-radius: 50%; width: 45px; height: 45px; font-size: 22px; font-weight: bold; cursor: pointer; z-index: 4100; transition: all 0.3s; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); backdrop-filter: blur(5px); }
        .btn-cerrar-lectura { right: 20px; }
        .btn-cerrar-lectura:hover { background: rgba(0,0,0,0.8); color: white; transform: scale(1.1); }
        .btn-pin { left: 20px; }
        .btn-pin:hover { background: rgba(0,0,0,0.8); color: white; }
        .btn-pin.activo { background: rgba(0,0,0,0.7); color: var(--accent-gold); }
        
        .lectura-hero-container { padding: 30px 40px 10px 40px; background: #111111; position: relative; display: flex; justify-content: center; }
        .foto-clavada { position: sticky; top: 0; z-index: 100; }
        .lectura-hero { width: 100%; height: auto; max-height: 65vh; object-fit: contain; display: block; box-shadow: 0 8px 30px rgba(255,255,255,0.12), 0 15px 40px rgba(0,0,0,0.9); border-radius: 6px; background-color: #080808; border: 1px solid rgba(255,255,255,0.15); transition: all 0.3s ease; }
        .lectura-body { padding: 20px 60px 60px 60px; flex-grow: 1; position: relative; z-index: 10; background: #111111; }
        .lectura-body h1 { color: white; font-weight: 900; margin-top: 15px; margin-bottom: 10px; font-size: clamp(26px, 4vw, 40px); line-height: 1.15; }
        .lectura-fuente { font-size: 13px; color: var(--accent-gold); font-weight: bold; margin-bottom: 30px; display: block; text-transform: uppercase; letter-spacing: 1px; }
        .lectura-texto { font-size: 21px; line-height: 1.8; color: #E5E5E5; text-align: justify; }

        .seccion-comentarios { margin-top: 50px; border-top: 1px solid #333; padding-top: 30px; }
        .seccion-comentarios h3 { color: var(--accent-gold); font-weight: bold; font-size: 24px; margin-bottom: 25px; }
        .form-comentario { display: flex; flex-direction: column; gap: 15px; margin-bottom: 40px; }
        .input-comentario { background: var(--panel-bg); border: 1px solid #444; color: white; padding: 15px; border-radius: 8px; font-family: inherit; font-size: 18px; transition: border-color 0.3s; }
        .input-comentario:focus { outline: none; border-color: var(--vibrant-green); }
        .btn-enviar-comentario { align-self: flex-end; background: var(--vibrant-green); color: white; border: none; padding: 15px 35px; font-weight: bold; font-size: 16px; border-radius: 6px; cursor: pointer; transition: 0.3s; }
        .btn-enviar-comentario:hover { background: var(--deep-green); }
        .comentario-item { background: #1a1a1a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid var(--accent-gold); }
        .comentario-autor { font-weight: bold; color: white; margin-bottom: 8px; font-size: 16px; }
        .comentario-fecha { font-size: 12px; color: #888; margin-bottom: 12px; }
        .comentario-texto { color: #ccc; font-size: 17px; line-height: 1.6; margin: 0; }

        .btn-volver-arriba { display: none; position: fixed; bottom: 30px; right: 30px; background: rgba(0, 0, 0, 0.4); color: rgba(255, 255, 255, 0.6); border: none; border-radius: 50%; width: 45px; height: 45px; font-size: 20px; font-weight: bold; cursor: pointer; z-index: 4200; box-shadow: 0 4px 10px rgba(0,0,0,0.3); align-items: center; justify-content: center; transition: all 0.3s ease; opacity: 0; backdrop-filter: blur(5px); }
        .btn-volver-arriba:hover { background: rgba(0,0,0,0.8); color: white; transform: scale(1.1); }

        .modal-base { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(8px); z-index: 5000; align-items: center; justify-content: center; padding: 20px; box-sizing: border-box; }
        .admin-box { background: var(--glass); padding: 35px; border-radius: 12px; width: 100%; max-width: 680px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.9); border: 1px solid #333; max-height: 92vh; overflow-y: auto; }
        .admin-box h2 { color: var(--accent-gold); font-weight: 900; margin-bottom: 15px; margin-top: 0; }
        .admin-label { display: block; text-align: left; font-size: 11px; color: var(--accent-gold); font-weight: bold; text-transform: uppercase; margin-top: 10px; margin-bottom: 2px; letter-spacing: 0.5px; }
        .admin-input { width: 100%; padding: 12px; margin: 4px 0 8px 0; border: 1px solid #444; background: var(--panel-bg); color: var(--text-main); border-radius: 6px; font-size: 14px; font-family: inherit; box-sizing: border-box; }
        .btn-admin { background: var(--vibrant-green); color: white; border: none; padding: 15px 30px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 15px; font-size: 15px; transition: all 0.3s; }
        .btn-admin:hover { background: var(--accent-gold); color: black; }
        .preview-img-box { width: 100%; max-height: 180px; object-fit: contain; background: #080808; border: 1px solid #333; border-radius: 6px; margin-top: 6px; display: none; }
        
        .cms-toast { position: fixed; bottom: 30px; left: 30px; background: var(--vibrant-green); color: white; padding: 12px 22px; border-radius: 6px; font-weight: bold; font-size: 13px; z-index: 6000; box-shadow: 0 6px 20px rgba(0,0,0,0.8); display: none; }
        footer { background: #080808; color: #666; text-align: center; padding: 50px 20px; margin-top: 40px; border-top: 1px solid #1a1a1a; }
        .btn-panel-secreto { background: transparent; border: 1px solid #333; color: #555; padding: 8px 15px; font-size: 11px; cursor: pointer; margin-bottom: 20px; border-radius: 4px; }

        @media (max-width: 850px) {
            .nav-brand { width: 100%; justify-content: center; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 10px; }
            .nav-links-container { justify-content: center; flex-wrap: wrap; gap: 8px; }
            .nav-links-container a { padding: 10px 12px; font-size: 12px; }
            .mosaico-container { gap: 20px; padding: 0 15px; }
            .span-big, .span-h-izq, .span-h-der, .span-v { grid-column: span 1; grid-row: span 1; display: flex; flex-direction: column; height: auto; }
            .span-h-izq .mosaico-img-container, .span-h-der .mosaico-img-container { width: 100%; height: auto; margin-bottom: 15px; }
            .span-h-izq .texto-container, .span-h-der .texto-container { width: 100%; padding: 0; }
            .span-h-izq .tarjeta-footer, .span-h-der .tarjeta-footer { width: 100%; padding: 15px 0 0 0; flex-direction: column; align-items: stretch; border-top: none; }
            .lectura-box { border: none; } 
            .lectura-hero-container { padding: 15px; }
            .lectura-body { padding: 20px 15px 40px 15px; }
            .lectura-texto { font-size: 17px; line-height: 1.6; }
            .lectura-body h1 { font-size: 26px; }
            .btn-cerrar-lectura { top: 15px; right: 15px; width: 40px; height: 40px; font-size: 20px; }
            .btn-pin { top: 15px; left: 15px; width: 40px; height: 40px; font-size: 18px; }
        }
    </style>
</head>
<body>

<nav>
    <a href="#" class="nav-brand">
        <img src="images/logo1.png" alt="Logo" onerror="this.style.display='none'">
        AMAZONÍA
    </a>
    <div class="nav-links-container">
        <a href="#hero">Inicio</a>
        <a href="#mosaico">Noticias</a>
        <a href="indigenas.html">Mapa Indígena</a>
        <a href="#turismo">Turismo</a>
        <a href="#economia">Economía</a>
    </div>
</nav>

<section class="hero" id="hero">
    <img src="images/1003202605032026la-amazonia-al-bordeP.jpg" class="hero-img" alt="Portada Amazonía" onerror="this.style.display='none'">
    <div class="hero-content">
        <div class="badge" style="position:relative; top:0; left:0; display:inline-block; margin-bottom:20px;">EXPLORACIÓN</div>
        <h1>LA AMAZONÍA BOLIVIANA</h1>
        <p class="hero-resumen">Una guía indispensable para su viaje ancestral. Descubra el territorio más espectacular de América del Sur.</p>
    </div>
</section>

<!-- BARRA ADMIN CMS (Visible solo con sesión iniciada) -->
<div class="admin-toolbar" id="barra-admin-cms">
    <button class="btn-toolbar" onclick="abrirEditorNuevo()">+ CREAR NUEVA NOTICIA</button>
    <button class="btn-toolbar" style="background:#FFB81C; color:black;" onclick="exportarBaseDatosJSON()">💾 DESCARGAR RESPALDO (.JSON)</button>
    <button class="btn-toolbar" style="background:#333; border:1px solid #666;" onclick="cerrarSesionAdmin()">🔒 SALIR DE MODO ADMIN</button>
</div>

<div class="mosaico-container" id="mosaico">
__TARJETAS_HTML__
</div>

<div id="cms-toast" class="cms-toast">Cambios guardados</div>
<button class="btn-volver-arriba" id="btn-volver-arriba" onclick="scrollToTop()">↑</button>

<div id="modal-lectura" class="modal-inmersivo">
    <button class="btn-cerrar-lectura" onclick="cerrarLectura()">×</button>
    <button class="btn-pin" id="btn-fijar-foto" onclick="togglePinFoto()" title="Fijar Fotografía">📌</button>
    
    <div class="lectura-box">
        <div class="lectura-hero-container" id="contenedor-foto-inmersiva">
            <img id="lectura-img" src="" class="lectura-hero" alt="Imagen del Artículo" onerror="this.onerror=null; this.src='images/default.jpg';">
        </div>
        <div class="lectura-body">
            <span id="lectura-categoria" class="badge" style="position:relative; top:0; left:0; margin-bottom: 15px; display:inline-block;"></span>
            <span id="lectura-fecha" class="fecha-tarjeta" style="margin-bottom:15px;"></span>
            <h1 id="lectura-titulo"></h1>
            <span id="lectura-fuente" class="lectura-fuente"></span>
            <button id="btn-audio-inmersivo" class="btn-audio" onclick="toggleAudioInmersivo()">🔊 Escuchar Artículo</button>
            
            <div id="lectura-texto" class="lectura-texto"></div>

            <div style="margin-top: 30px; text-align: center;">
                <div style="margin-top: 30px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
            <button type="button" class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: #25D366; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;" onclick="window.compartirNoticiaPortal('whatsapp')">💬 Compartir en WhatsApp</button>
            <button type="button" class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: #1877F2; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;" onclick="window.compartirNoticiaPortal('facebook')">📘 Compartir en Facebook</button>
            <button type="button" class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: var(--accent-gold); color: black; border: none; border-radius: 6px; font-weight: bold; cursor: pointer;" onclick="window.compartirNoticiaPortal('copiar')">🔗 Copiar Enlace para Página</button>
                    <button id="btn-audio-inmersivo" class="btn-audio" style="padding: 12px 20px; font-size: 15px; background: transparent; color: var(--accent-gold); border: 1px solid var(--accent-gold); font-weight: bold; border-radius: 4px; cursor: pointer;" onclick="toggleAudioInmersivo()">🔊 Escuchar Artículo</button>
                </div>
            </div>

            <div class="reacciones-bar" style="margin-top: 25px; border-top: 1px solid #333; padding-top: 25px;">
                <button id="btn-like-inmersivo" class="btn-reaccion">👍 Me Gusta</button>
                <button id="btn-sad-inmersivo" class="btn-reaccion">😢 Qué Tristeza</button>
            </div>

            <div class="seccion-comentarios">
                <h3>Comentarios</h3>
                <div class="form-comentario">
                    <input type="text" id="comentario-nombre" class="input-comentario" placeholder="Tu nombre..." onfocus="ajustarTeclado(this)">
                    <textarea id="comentario-texto" class="input-comentario" rows="3" placeholder="Escribe tu opinión aquí..." onfocus="ajustarTeclado(this)"></textarea>
                    <button class="btn-enviar-comentario" onclick="publicarComentario()">Publicar Comentario</button>
                </div>
                <div id="lista-comentarios"></div>
            </div>
        </div>
    </div>
</div>

<div id="modal-admin" class="modal-base">
    <div class="admin-box" id="vista-login">
        <h2>Acceso Restringido</h2>
        <p style="color:#aaa; margin-bottom:20px;">Ingrese su clave de seguridad</p>
        <input type="password" id="admin-pass" class="admin-input" placeholder="••••••••" onkeydown="if(event.key==='Enter') checkPass()">
        <button class="btn-admin" onclick="checkPass()">VERIFICAR</button>
        <button class="w3-button w3-text-grey w3-margin-top" onclick="closeAdmin()">Cancelar</button>
    </div>

    <div class="admin-box" id="vista-editor" style="display:none;">
        <h2 id="editor-titulo">Publicación</h2>
        <input type="hidden" id="edit-id"> 
        
        <label class="admin-label">Tamaño en el Mosaico</label>
        <select id="edit-formato" class="admin-input" style="border-color: var(--accent-gold); font-weight: bold;">
            <option value="">Cuadrado Normal (1x1)</option>
            <option value="span-h-izq">Horizontal — Foto Izquierda</option>
            <option value="span-h-der">Horizontal — Foto Derecha</option>
            <option value="span-v">Vertical Largo (1x2)</option>
            <option value="span-big">Extra Grande Destacado (2x2)</option>
        </select>

        <label class="admin-label">Fotografía (Ruta o Subir desde tu PC)</label>
        <input type="text" id="edit-imagen" class="admin-input" placeholder="Ej: images/foto.jpg o https://..." oninput="actualizarVistaPrevia(this.value)">
        <div style="display:flex; gap:10px; align-items:center; margin-bottom:8px;">
            <label for="upload-foto-pc" style="background:#2a2a2a; color:var(--accent-gold); border:1px dashed var(--accent-gold); padding:10px; border-radius:6px; cursor:pointer; font-size:12px; font-weight:bold; width:100%; text-align:center;">
                📷 SUBIR FOTO DESDE TU PC (Se guarda en Hosting)
            </label>
            <input type="file" id="upload-foto-pc" accept="image/*" style="display:none;" onchange="procesarFotoDesdePC(event)">
        </div>
        <img id="edit-preview-img" class="preview-img-box" alt="Vista previa">

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
                <label class="admin-label">Fecha</label>
                <input type="text" id="edit-fecha" class="admin-input">
            </div>
            <div>
                <label class="admin-label">Categoría</label>
                <input type="text" id="edit-etiqueta" class="admin-input">
            </div>
        </div>

        <label class="admin-label">Título</label>
        <input type="text" id="edit-titulo" class="admin-input">
        <label class="admin-label">Fuente / Autor</label>
        <input type="text" id="edit-fuente" class="admin-input">
        <label class="admin-label">Resumen (Mosaico)</label>
        <textarea id="edit-resumen" class="admin-input" rows="3"></textarea>
        <label class="admin-label">Contenido Completo (Inmersión)</label>
        <textarea id="edit-contenido" class="admin-input" rows="7"></textarea>

        <button class="btn-admin" id="btn-guardar-cms" onclick="guardarNoticia()">💾 GUARDAR PERMANENTEMENTE</button>
        <button class="w3-button w3-text-grey w3-margin-top" onclick="closeAdmin()">Cerrar</button>
    </div>
</div>

<footer>
    <button class="btn-panel-secreto" onclick="abrirLogin()">Acceso Administrativo</button>
    <h2 style="letter-spacing: 2px; color: #555;">PORTAL AMAZONÍA</h2>
    <p>creado por: Avrora Soft - Vibola LLC - 2026</p>
</footer>

<script type="application/json" id="json-memoria">
__JSON_MEMORIA__
</script>



    <script>
    window.reproduciendoInmersivo = false;

    window.toggleAudioInmersivo = function() {
        const btn = document.getElementById('btn-audio-inmersivo');
        const sintesis = window.speechSynthesis;
        
        if (!sintesis) {
            alert("Tu navegador no soporta lectura por voz.");
            return;
        }

        if (window.reproduciendoInmersivo) {
            sintesis.cancel();
            window.reproduciendoInmersivo = false;
            if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
        } else {
            sintesis.cancel();
            const textoEl = document.getElementById('lectura-texto');
            const tituloEl = document.getElementById('lectura-titulo');
            const textoCompleto = (tituloEl ? tituloEl.innerText + ". " : "") + (textoEl ? textoEl.innerText : "");
            
            if (!textoCompleto.trim()) {
                alert("No hay texto para leer en este artículo.");
                return;
            }

            const mensaje = new SpeechSynthesisUtterance(textoCompleto);
            mensaje.lang = 'es-ES';
            
            mensaje.onstart = function() {
                window.reproduciendoInmersivo = true;
                if(btn) { btn.classList.add('reproduciendo'); btn.innerHTML = '⏸️ Detener Lectura'; }
            };
            
            mensaje.onend = function() {
                window.reproduciendoInmersivo = false;
                if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
            };
            
            mensaje.onerror = function() {
                window.reproduciendoInmersivo = false;
                if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
            };

            sintesis.speak(mensaje);
        }
    };

    window.ejecutarCompartirInmersivo = function() {
        const idArt = typeof articuloActivoId !== 'undefined' ? articuloActivoId : "";
        const urlActual = window.location.origin + window.location.pathname + (idArt ? "?leer=" + idArt : "");
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(urlActual).then(() => {
                alert("¡Enlace copiado al portapapeles! Ya puedes compartirlo.");
            }).catch(() => {
                prompt("Copia este enlace para compartir:", urlActual);
            });
        } else {
            prompt("Copia este enlace para compartir:", urlActual);
        }
    };

    // Asegurar limpieza de audio al cerrar modal
    const cerrarOriginal = window.cerrarLectura;
    window.cerrarLectura = function() {
        if(window.speechSynthesis) window.speechSynthesis.cancel();
        window.reproduciendoInmersivo = false;
        const btn = document.getElementById('btn-audio-inmersivo');
        if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
        if(typeof cerrarOriginal === 'function') cerrarOriginal();
        else {
            const modal = document.getElementById('modal-lectura');
            if(modal) modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    };
    </script>
    

    




<script>
// --- FUNCIÓN MAESTRA DE INMERSIÓN Y COMPARTIR ---
window.abrirLectura = function(idArt) {
    if (typeof articulosData !== 'undefined' && articulosData[idArt]) {
        var art = articulosData[idArt];
        window.idArticuloInmersivo = String(idArt);
        
        var imgEl = document.getElementById('lectura-img');
        if (imgEl) imgEl.src = art.imagen || art.img || 'images/default.jpg';
        
        var titEl = document.getElementById('lectura-titulo');
        if (titEl) titEl.innerText = art.titulo || art.title || '';
        
        var catEl = document.getElementById('lectura-categoria');
        if (catEl) catEl.innerText = art.categoria || art.tipo || 'Noticia';
        
        var fecEl = document.getElementById('lectura-fecha');
        if (fecEl) fecEl.innerText = art.fecha || '';
        
        var fueEl = document.getElementById('lectura-fuente');
        if (fueEl) fueEl.innerText = art.fuente ? ('Fuente: ' + art.fuente) : '';
        
        var txtEl = document.getElementById('lectura-texto');
        if (txtEl) {
            var cuerpo = art.contenido || art.texto || art.cuerpo || "";
            txtEl.innerHTML = cuerpo;
        }
        
        var modal = document.getElementById('modal-lectura');
        if (modal) modal.style.display = 'flex';
    }
};

window.compartirNativo = function(tituloArticulo, ev) {
    var idEncontrado = "1";
    try {
        var origen = (ev && ev.target) ? ev.target : (window.event && window.event.target ? window.event.target : null);
        var el = origen;
        while (el && el !== document.body) {
            var btnLeer = el.querySelector ? el.querySelector('[onclick*="abrirLectura"]') : null;
            if (!btnLeer && el.getAttribute && el.getAttribute('onclick')) {
                var attr = el.getAttribute('onclick');
                var matchId = attr.match(/abrirLectura\(['"]?([^'"]+)['"]?\)/);
                if (matchId && matchId[2]) {
                    idEncontrado = matchId[2];
                    break;
                }
            }
            el = el.parentElement;
        }
    } catch (err) {}

    if (typeof window.idArticuloInmersivo !== 'undefined' && window.idArticuloInmersivo) {
        idEncontrado = window.idArticuloInmersivo;
    }

    var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idEncontrado) + ".html";
    var titulo = tituloArticulo || "Portal Amazonía";
    var nl = String.fromCharCode(10);
    var textoCompleto = "📰 " + titulo + nl + nl + "👉 Lee la noticia completa en Portal Amazonía:" + nl + urlArt;

    try {
        var area = document.createElement('textarea');
        area.value = textoCompleto;
        area.style.position = 'fixed';
        area.style.left = '-9999px';
        area.style.top = '0';
        document.body.appendChild(area);
        area.focus();
        area.select();
        document.execCommand('copy');
        document.body.removeChild(area);
    } catch (e) {}

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textoCompleto).catch(function(){});
    }

    alert("📋 ¡Enlace y texto copiados al portapapeles!\n\nPégalo con Ctrl+V en tu página institucional de Canal 9.");
    window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
};

window.compartirNoticiaPortal = function(red, idForzado, tituloForzado) {
    if (red === 'whatsapp') {
        var idArt = String(idForzado || window.idArticuloInmersivo || "1").trim();
        var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
        var elTit = document.getElementById('lectura-titulo');
        var titulo = tituloForzado || (elTit && elTit.innerText ? elTit.innerText.trim() : "Portal Amazonía");
        var nl = String.fromCharCode(10);
        var msg = "📰 *" + titulo + "*" + nl + "👉 " + urlArt;
        window.open("https://api.whatsapp.com/send?text=" + encodeURIComponent(msg), '_blank');
    } else {
        compartirNativo(tituloForzado || "Portal Amazonía");
    }
};

window.compartirWhatsApp = function() { window.compartirNoticiaPortal('whatsapp'); };
window.compartirFacebook = function() { window.compartirNoticiaPortal('facebook'); };
window.compartirWhatsAppModal = function() { window.compartirNoticiaPortal('whatsapp'); };
window.compartirFacebookModal = function() { window.compartirNoticiaPortal('facebook'); };
window.copiarEnlaceModal = function() { window.compartirNoticiaPortal('copiar'); };
window.ejecutarCompartirInmersivo = function() { window.compartirNoticiaPortal('facebook'); };

window.addEventListener('load', function() {
    var params = new URLSearchParams(window.location.search);
    var idUrl = params.get('id') || params.get('articulo');
    if (idUrl && typeof abrirLectura === 'function') {
        setTimeout(function() {
            abrirLectura(idUrl);
        }, 150);
    }
});
</script>
</body>
</html>
"""
    
    html_completo = plantilla_html.replace("__TOTAL_ART__", total_art).replace("__TARJETAS_HTML__", tarjetas_html).replace("__JSON_MEMORIA__", json_memoria)

    index_path = os.path.join(base_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_completo)
    
    print(f"¡index.html generado con éxito con {total_art} artículos!")

if __name__ == "__main__":
    generar_index_estatico()


def limpiar_slug(texto):
    if not texto:
        return "articulos"
    texto = unicodedata.normalize('NFD', texto).encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^a-zA-Z0-9_-]', '_', texto.lower())
    return texto.strip('_') or 'articulos'

def generar_paginas_individuales(articulos):
    template_art = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITULO__ - Portal Amazonía</title>
    
    <!-- Open Graph para Redes Sociales (Facebook, WhatsApp, Instagram, TikTok) -->
    <meta property="og:title" content="__TITULO__" />
    <meta property="og:description" content="__TEXTO_CORTO__..." />
    <meta property="og:image" content="__IMAGEN_OG__" />
    <meta property="og:url" content="https://portal-ia-web.web.app/__CARPETA__/articulo___ID__.html" />
    <meta property="og:type" content="article" />
    
    <!-- Twitter Cards -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="__TITULO__">
    <meta name="twitter:description" content="__TEXTO_CORTO__...">
    <meta name="twitter:image" content="__IMAGEN_OG__">

    <link rel="stylesheet" href="../w3.css">
    <link rel="stylesheet" href="../amazonia.css">
    <style>
        body { background: #121212; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; }
        .header-nav { background: #1f1f1f; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #d4af37; }
        .header-nav a { color: #d4af37; text-decoration: none; font-weight: bold; font-size: 18px; }
        .container { max-width: 800px; margin: 40px auto; background: #1e1e1e; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: #d4af37; font-size: 28px; margin-bottom: 10px; }
        .meta { color: #888; font-size: 14px; margin-bottom: 20px; }
        img { width: 100%; max-height: 450px; object-fit: cover; border-radius: 6px; margin-bottom: 25px; }
        .texto-articulo { font-size: 18px; line-height: 1.7; color: #dcdcdc; white-space: pre-line; }
        .acciones { margin-top: 40px; display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
        .btn { padding: 12px 25px; font-weight: bold; border-radius: 4px; text-decoration: none; border: none; cursor: pointer; }
        .btn-ws { background: #25D366; color: white; }
        .btn-fb { background: #1877F2; color: white; }
        .btn-volver { background: #d4af37; color: black; }
    </style>
</head>
<body>
    <div class="header-nav">
        <a href="../index.html">⬅ Volver al Portal Amazonía</a>
        <a href="../index.html">Inicio</a>
    </div>

    <div class="container">
        <h1>__TITULO__</h1>
        <div class="meta">📅 __FECHA__ &nbsp;|&nbsp; ✍️ __FUENTE__</div>
        <img src="../__IMAGEN__" alt="__TITULO__">
        <div class="texto-articulo">__TEXTO_COMPLETO__</div>

        <div class="acciones">
            <a href="https://api.whatsapp.com/send?text=__TITULO_ENC__%20-%20https://portal-ia-web.web.app/__CARPETA__/articulo___ID__.html" target="_blank" class="btn btn-ws">💬 Compartir en WhatsApp</a>
            <a href="https://www.facebook.com/sharer/sharer.php?u=https://portal-ia-web.web.app/__CARPETA__/articulo___ID__.html" target="_blank" class="btn btn-fb">📘 Compartir en Facebook</a>
            <a href="../index.html" class="btn btn-volver">🏠 Ir al Inicio</a>
        </div>
    </div>

    <script>
    // Controladores infalibles con soporte para carpetas por tipo
    document.addEventListener('click', function(e) {
        const target = e.target.closest('button, a');
        if (!target) return;
        
        const text = target.innerText || target.textContent || "";
        const idArt = typeof articuloActivoId !== 'undefined' && articuloActivoId ? articuloActivoId : (window.currentArticleId || "");
        const carpeta = (window.articuloFolders && idArt && window.articuloFolders[idArt]) ? window.articuloFolders[idArt] : "articulos";
        
        if (text.includes("WhatsApp") && (target.closest('.modal') || target.closest('#modal-lectura') || target.closest('.acciones'))) {
            e.preventDefault();
            const titulo = document.getElementById('lectura-titulo') ? document.getElementById('lectura-titulo').innerText : "Portal Amazonía";
            const urlArt = idArt ? "https://portal-ia-web.web.app/" + carpeta + "/articulo_" + idArt + ".html" : window.location.href;
            window.open("https://api.whatsapp.com/send?text=" + encodeURIComponent("📰 " + titulo + "\n👉 " + urlArt), '_blank');
        }
        
        if ((text.includes("Facebook") || text.includes("compartir")) && !text.includes("WhatsApp") && !text.includes("Copiar") && (target.closest('.modal') || target.closest('#modal-lectura') || target.closest('.acciones'))) {
            e.preventDefault();
            const urlArt = idArt ? "https://portal-ia-web.web.app/" + carpeta + "/articulo_" + idArt + ".html" : window.location.href;
            window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), '_blank', 'width=600,height=500');
        }
        
        if ((text.includes("Copiar") || text.includes("Enlace")) && (target.closest('.modal') || target.closest('#modal-lectura') || target.closest('.acciones'))) {
            e.preventDefault();
            const urlArt = idArt ? "https://portal-ia-web.web.app/" + carpeta + "/articulo_" + idArt + ".html" : window.location.href;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(urlArt).then(() => {
                    alert("¡Enlace del artículo copiado al portapapeles!");
                }).catch(() => {
                    prompt("Copia este enlace:", urlArt);
                });
            } else {
                prompt("Copia este enlace:", urlArt);
            }
        }
    });
    </script>
    






<script>
// --- FUNCIÓN MAESTRA DE INMERSIÓN Y COMPARTIR ---
window.abrirLectura = function(idArt) {
    if (typeof articulosData !== 'undefined' && articulosData[idArt]) {
        var art = articulosData[idArt];
        window.idArticuloInmersivo = String(idArt);
        
        var imgEl = document.getElementById('lectura-img');
        if (imgEl) imgEl.src = art.imagen || art.img || 'images/default.jpg';
        
        var titEl = document.getElementById('lectura-titulo');
        if (titEl) titEl.innerText = art.titulo || art.title || '';
        
        var catEl = document.getElementById('lectura-categoria');
        if (catEl) catEl.innerText = art.categoria || art.tipo || 'Noticia';
        
        var fecEl = document.getElementById('lectura-fecha');
        if (fecEl) fecEl.innerText = art.fecha || '';
        
        var fueEl = document.getElementById('lectura-fuente');
        if (fueEl) fueEl.innerText = art.fuente ? ('Fuente: ' + art.fuente) : '';
        
        var txtEl = document.getElementById('lectura-texto');
        if (txtEl) {
            var cuerpo = art.contenido || art.texto || art.cuerpo || "";
            txtEl.innerHTML = cuerpo;
        }
        
        var modal = document.getElementById('modal-lectura');
        if (modal) modal.style.display = 'flex';
    }
};

window.compartirNativo = function(tituloArticulo, ev) {
    var idEncontrado = "1";
    try {
        var origen = (ev && ev.target) ? ev.target : (window.event && window.event.target ? window.event.target : null);
        var el = origen;
        while (el && el !== document.body) {
            var btnLeer = el.querySelector ? el.querySelector('[onclick*="abrirLectura"]') : null;
            if (!btnLeer && el.getAttribute && el.getAttribute('onclick')) {
                var attr = el.getAttribute('onclick');
                var matchId = attr.match(/abrirLectura\(['"]?([^'"]+)['"]?\)/);
                if (matchId && matchId[2]) {
                    idEncontrado = matchId[2];
                    break;
                }
            }
            el = el.parentElement;
        }
    } catch (err) {}

    if (typeof window.idArticuloInmersivo !== 'undefined' && window.idArticuloInmersivo) {
        idEncontrado = window.idArticuloInmersivo;
    }

    var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idEncontrado) + ".html";
    var titulo = tituloArticulo || "Portal Amazonía";
    var nl = String.fromCharCode(10);
    var textoCompleto = "📰 " + titulo + nl + nl + "👉 Lee la noticia completa en Portal Amazonía:" + nl + urlArt;

    try {
        var area = document.createElement('textarea');
        area.value = textoCompleto;
        area.style.position = 'fixed';
        area.style.left = '-9999px';
        area.style.top = '0';
        document.body.appendChild(area);
        area.focus();
        area.select();
        document.execCommand('copy');
        document.body.removeChild(area);
    } catch (e) {}

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textoCompleto).catch(function(){});
    }

    alert("📋 ¡Enlace y texto copiados al portapapeles!\n\nPégalo con Ctrl+V en tu página institucional de Canal 9.");
    window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
};

window.compartirNoticiaPortal = function(red, idForzado, tituloForzado) {
    if (red === 'whatsapp') {
        var idArt = String(idForzado || window.idArticuloInmersivo || "1").trim();
        var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
        var elTit = document.getElementById('lectura-titulo');
        var titulo = tituloForzado || (elTit && elTit.innerText ? elTit.innerText.trim() : "Portal Amazonía");
        var nl = String.fromCharCode(10);
        var msg = "📰 *" + titulo + "*" + nl + "👉 " + urlArt;
        window.open("https://api.whatsapp.com/send?text=" + encodeURIComponent(msg), '_blank');
    } else {
        compartirNativo(tituloForzado || "Portal Amazonía");
    }
};

window.compartirWhatsApp = function() { window.compartirNoticiaPortal('whatsapp'); };
window.compartirFacebook = function() { window.compartirNoticiaPortal('facebook'); };
window.compartirWhatsAppModal = function() { window.compartirNoticiaPortal('whatsapp'); };
window.compartirFacebookModal = function() { window.compartirNoticiaPortal('facebook'); };
window.copiarEnlaceModal = function() { window.compartirNoticiaPortal('copiar'); };
window.ejecutarCompartirInmersivo = function() { window.compartirNoticiaPortal('facebook'); };

window.addEventListener('load', function() {
    var params = new URLSearchParams(window.location.search);
    var idUrl = params.get('id') || params.get('articulo');
    if (idUrl && typeof abrirLectura === 'function') {
        setTimeout(function() {
            abrirLectura(idUrl);
        }, 150);
    }
});
</script>
</body>
</html>'''

    folders_map = {}
    contador = 0

    for art in articulos:
        art_id = str(art.get('id', '1'))
        tipo = art.get('tipo') or art.get('categoria') or 'articulos'
        carpeta = limpiar_slug(tipo)
        folders_map[art_id] = carpeta

        titulo = art.get('titulo', 'Portal Amazonía')
        texto = art.get('texto', '')
        imagen = art.get('imagen', 'images/logo.png')
        fuente = art.get('fuente', 'Redacción Amazonía')
        fecha = art.get('fecha', '')
        
        img_og = imagen if imagen.startswith('http') else "https://portal-ia-web.web.app/" + imagen
        titulo_enc = urllib.parse.quote(titulo + " - Lee esta noticia en Portal Amazonía:")
        texto_corto = texto[:150].replace('"', '').replace("'", "")
        
        # Crear la subcarpeta física si no existe
        sub_dir = os.path.join(base_dir, carpeta)
        os.makedirs(sub_dir, exist_ok=True)

        html_pagina = template_art.replace("__TITULO__", titulo) \
                                  .replace("__TEXTO_CORTO__", texto_corto) \
                                  .replace("__IMAGEN_OG__", img_og) \
                                  .replace("__CARPETA__", carpeta) \
                                  .replace("__ID__", art_id) \
                                  .replace("__FECHA__", fecha) \
                                  .replace("__FUENTE__", fuente) \
                                  .replace("__IMAGEN__", imagen) \
                                  .replace("__TEXTO_COMPLETO__", texto) \
                                  .replace("__TITULO_ENC__", titulo_enc)
        
        filepath = os.path.join(sub_dir, f"articulo_{art_id}.html")
        with open(filepath, "w", encoding="utf-8") as f_art:
            f_art.write(html_pagina)
        contador += 1

    # Guardar el mapa de carpetas para que index.html lo use en los botones de compartir
    map_js = f"\n<script>\nwindow.articuloFolders = {json.dumps(folders_map)};\n</script>\n"
    
    # Inyectar el diccionario en index.html o como script global
    print(f"¡{contador} páginas organizadas en carpetas por tipo con éxito!")
    return map_js