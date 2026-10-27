import os
import json
import re
import shutil
import unicodedata

def normalizar_texto(texto):
    if not texto:
        return ""
    texto = str(texto).lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return re.sub(r'[^a-z0-9]+', '-', texto).strip('-')

def indexar_imagenes_proyecto(base_dir):
    extensiones = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')
    por_id_carpeta = {}
    por_id_archivo = {}
    todas_las_imagenes = []

    carpetas_ignorar = {'.git', '__pycache__', 'node_modules'}
    archivos_ignorar = {'logo1.png', 'default.jpg', 'favicon.ico'}

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in carpetas_ignorar]
        nombre_carpeta = os.path.basename(root)
        
        match_dir_id = re.match(r'^(\d+)(?:_|$)', nombre_carpeta)
        
        imgs_en_carpeta = [f for f in files if f.lower().endswith(extensiones)]
        if match_dir_id and imgs_en_carpeta:
            id_carp = match_dir_id.group(1)
            elegida = imgs_en_carpeta[0]
            for img in imgs_en_carpeta:
                if 'principal' in img.lower():
                    elegida = img
                    break
            rel = os.path.relpath(os.path.join(root, elegida), base_dir).replace("\\", "/")
            if id_carp not in por_id_carpeta or 'principal' in elegida.lower():
                por_id_carpeta[id_carp] = rel

        for f in files:
            if not f.lower().endswith(extensiones):
                continue
            if f.lower() in archivos_ignorar:
                continue
            rel = os.path.relpath(os.path.join(root, f), base_dir).replace("\\", "/")
            todas_las_imagenes.append((f, normalizar_texto(os.path.splitext(f)[0]), rel))
            
            match_file_id = re.match(r'^(\d+)(?:_|-|\.)', f)
            if match_file_id:
                id_arch = match_file_id.group(1)
                if id_arch not in por_id_archivo or 'principal' in f.lower():
                    por_id_archivo[id_arch] = rel

    return por_id_carpeta, por_id_archivo, todas_las_imagenes

def buscar_imagen_articulo(art, base_dir, por_id_carpeta, por_id_archivo, todas_las_imagenes):
    id_str = str(art.get("id", "")).strip()

    # 1. Si el JSON ya trae una ruta válida o DataURL/URL externa editada por el usuario
    img_json = str(art.get("imagen", "")).strip()
    if img_json.startswith(("http://", "https://", "data:image/")):
        return img_json, "url_externa"
    if img_json and img_json != "images/default.jpg":
        ruta_fisica = os.path.join(base_dir, img_json.replace("/", os.sep))
        if os.path.isfile(ruta_fisica):
            return img_json.replace("\\", "/"), "json_existente"

    # 2. Por carpeta con ID (ej: imagenes_articulos/675_imagenes_articulos/...)
    if id_str in por_id_carpeta:
        return por_id_carpeta[id_str], "id_carpeta"

    # 3. Por archivo con ID (ej: 675_imagen_principal.jpg)
    if id_str in por_id_archivo:
        return por_id_archivo[id_str], "id_archivo"

    # 4. Búsqueda por coincidencia de título / slug en los nombres de archivo
    titulo_slug = normalizar_texto(art.get("titulo", ""))
    palabras_clave = [p for p in titulo_slug.split('-') if len(p) >= 4]
    if palabras_clave:
        mejor_ruta = None
        mejor_puntaje = 0
        for nombre_arch, slug_arch, rel_path in todas_las_imagenes:
            prefijo_slug = "-".join(palabras_clave[:3])
            if len(prefijo_slug) >= 8 and prefijo_slug in slug_arch:
                return rel_path, "slug_exacto"
            coincidencias = sum(1 for p in palabras_clave if p in slug_arch)
            if coincidencias >= 2 and coincidencias > mejor_puntaje:
                mejor_puntaje = coincidencias
                mejor_ruta = rel_path
        if mejor_ruta and mejor_puntaje >= max(2, min(3, len(palabras_clave))):
            return mejor_ruta, "slug_palabras"

    return "images/default.jpg", "default"

def asegurar_imagen_default(base_dir, todas_las_imagenes):
    images_dir = os.path.join(base_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    default_path = os.path.join(images_dir, "default.jpg")
    if not os.path.isfile(default_path):
        portada = os.path.join(images_dir, "1003202605032026la-amazonia-al-bordeP.jpg")
        if os.path.isfile(portada):
            shutil.copyfile(portada, default_path)
            print("-> Se creó 'images/default.jpg' automáticamente para evitar cualquier error 404.")
        elif todas_las_imagenes:
            primera_ruta = os.path.join(base_dir, todas_las_imagenes[0][2].replace("/", os.sep))
            if os.path.isfile(primera_ruta):
                shutil.copyfile(primera_ruta, default_path)
                print("-> Se creó 'images/default.jpg' automáticamente para evitar cualquier error 404.")

def generar_index_estatico():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "articulos_portal.json")

    if not os.path.exists(json_path):
        print("ERROR: No existe articulos_portal.json. Ejecuta primero: python poblar_portal_completo.py")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        articulos = json.load(f)

    por_id_carpeta, por_id_archivo, todas_las_imagenes = indexar_imagenes_proyecto(base_dir)
    asegurar_imagen_default(base_dir, todas_las_imagenes)

    print(f"Archivos de imagen detectados en C:\\Portal: {len(todas_las_imagenes)} imágenes totales.")
    print(f"Carpetas de artículos con ID detectadas: {len(por_id_carpeta)}")

    conteo_origen = {
        "url_externa": 0,
        "json_existente": 0,
        "id_carpeta": 0,
        "id_archivo": 0,
        "slug_exacto": 0,
        "slug_palabras": 0,
        "default": 0
    }
    memoria_dict = {}
    tarjetas_lista = []

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

        imagen_real, metodo = buscar_imagen_articulo(art, base_dir, por_id_carpeta, por_id_archivo, todas_las_imagenes)
        conteo_origen[metodo] = conteo_origen.get(metodo, 0) + 1
        art["imagen"] = imagen_real

        memoria_dict[id_art] = art

        titulo_attr = titulo.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        titulo_js = titulo.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", " ").replace("\r", "")
        resumen_html = resumen.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        categoria_html = categoria.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        fecha_txt = f"{fecha} | Fuente: {fuente}" if fuente else fecha

        ocultar_etnia = 'style="display:none;"' if categoria.upper() == "ETNIA" else ""

        tarjeta = (
            f'<article class="articulo-mosaico {formato}" id="card-{id_art}" data-id="{id_art}" data-categoria="{categoria_html}" {ocultar_etnia}>\n'
            f'    <div class="admin-controls">\n'
            f'        <button class="btn-accion" onclick="abrirEditorExistente(\'{id_art}\')">✏️ Editar</button>\n'
            f'        <button class="btn-accion btn-eliminar" onclick="eliminarNoticia(\'{id_art}\')">🗑️ Borrar</button>\n'
            f'    </div>\n'
            f'    <div class="badge" id="badge-{id_art}">{categoria_html}</div>\n'
            f'    <div class="mosaico-img-container">\n'
            f'        <img src="{imagen_real}" id="img-{id_art}" class="mosaico-img" alt="{titulo_attr}" loading="lazy" onerror="this.onerror=null; this.src=\'images/default.jpg\';">\n'
            f'    </div>\n'
            f'    <div class="texto-container">\n'
            f'        <span class="fecha-tarjeta" id="fecha-{id_art}">{fecha_txt}</span>\n'
            f'        <h3 id="titulo-{id_art}">{titulo_attr}</h3>\n'
            f'        <p id="resumen-{id_art}">{resumen_html}</p>\n'
            f'    </div>\n'
            f'    <div class="tarjeta-footer">\n'
            f'        <div class="botones-principales-tarjeta">\n'
            f'            <button class="btn-leer" onclick="abrirLectura(\'{id_art}\')">Leer Artículo</button>\n'
            f'            <button class="btn-compartir-tarjeta" id="share-{id_art}" onclick="compartirNativo(\'{titulo_js}\')" title="Compartir">🔗</button>\n'
            f'        </div>\n'
            f'        <div class="reacciones-bar">\n'
            f'            <button id="btn-card-likes-{id_art}" onclick="reaccionar(\'{id_art}\', \'likes\')" class="btn-reaccion" title="Me gusta">👍 <span id="likes-{id_art}">{likes}</span></button>\n'
            f'            <button id="btn-card-sads-{id_art}" onclick="reaccionar(\'{id_art}\', \'sads\')" class="btn-reaccion" title="Qué tristeza">😢 <span id="sads-{id_art}">{sads}</span></button>\n'
            f'        </div>\n'
            f'    </div>\n'
            f'</article>'
        )
        tarjetas_lista.append(tarjeta)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(articulos, f, ensure_ascii=False, indent=4)

    tarjetas_html = "\n".join(tarjetas_lista)
    json_memoria = json.dumps(memoria_dict, ensure_ascii=False)
    total_art = str(len(tarjetas_lista))

    plantilla_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Portal Amazonía Hoy | Vanguardia y Territorio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <link rel="stylesheet" href="w3.css">
    <link rel="stylesheet" href="amazonia.css">
    <link rel="stylesheet" href="font-awesome.min.css">

    <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-firestore.js"></script>

    <style>
        /* PORTAL AMAZONÍA HOY: MODO OSCURO MODERNO */
        :root { 
            --deep-green: #0A3D0A;
            --vibrant-green: #1D9A4C;
            --accent-gold: #FFB81C;
            --dark-bg: #121212; 
            --panel-bg: #1e1e1e; 
            --text-main: #E0E0E0; 
            --glass: rgba(25, 25, 25, 0.95);
        }

        body { 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            background-color: var(--dark-bg); 
            color: var(--text-main); 
            margin: 0;
            scroll-behavior: smooth;
            overflow-x: hidden;
        }

        /* NAVEGACIÓN COMPACTA Y DESLIZABLE */
        nav {
            position: sticky;
            top: 0;
            background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(10px);
            z-index: 2000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 20px;
            flex-wrap: wrap;
        }

        .nav-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            color: white;
            text-decoration: none;
            font-weight: 900;
            font-size: 16px;
            letter-spacing: 1px;
            white-space: nowrap;
        }

        .nav-brand img {
            height: 35px;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
        }

        .nav-links-container {
            display: flex;
            flex-grow: 1;
            justify-content: flex-end;
            gap: 10px;
            overflow-x: auto;
            white-space: nowrap;
            -webkit-overflow-scrolling: touch;
            padding: 5px 0;
            scrollbar-width: none;
        }
        
        .nav-links-container::-webkit-scrollbar { display: none; }

        .nav-links-container a {
            color: #ddd;
            text-decoration: none;
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 8px 12px;
            border-radius: 4px;
            transition: all 0.3s;
        }

        .nav-links-container a:hover { color: var(--accent-gold); background: rgba(255,255,255,0.1); }

        /* PORTADA INMERSIVA */
        .hero {
            height: 80vh;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
            background: #000;
            margin-bottom: 5px;
        }

        .hero-img {
            position: absolute;
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0.5;
        }

        .hero-content {
            position: relative;
            z-index: 10;
            max-width: 900px;
            padding: 20px;
        }

        .hero-content h1 {
            font-size: clamp(35px, 7vw, 75px);
            font-weight: 900;
            line-height: 1;
            margin: 0;
            text-shadow: 0 5px 30px rgba(0,0,0,0.9);
            text-transform: uppercase;
        }

        .hero-resumen {
            font-size: clamp(16px, 3vw, 20px);
            line-height: 1.6;
            margin-top: 25px;
            font-weight: 300;
            color: #eee;
            text-shadow: 0 2px 10px rgba(0,0,0,0.9);
        }

        /* MOSAICO ASIMÉTRICO TOTALMENTE DINÁMICO */
        .mosaico-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
            grid-auto-rows: auto; 
            grid-auto-flow: dense;
            gap: 25px;
            max-width: 1400px;
            margin: 40px auto;
            padding: 0 20px;
        }

        /* TARJETA DEL ARTÍCULO BASE */
        .articulo-mosaico {
            position: relative;
            border-radius: 6px;
            background: #111111;
            border: 1px solid #FFFFFF; 
            box-shadow: 0 6px 20px rgba(255,255,255,0.12), 0 10px 25px rgba(0,0,0,0.9); 
            padding: 20px; 
            display: flex;
            flex-direction: column; 
            justify-content: flex-start; 
            gap: 15px;
            box-sizing: border-box;
            transition: all 0.4s ease;
            height: 100%;
        }

        .articulo-mosaico:hover {
            transform: translateY(-6px);
            box-shadow: 0 8px 30px rgba(255,255,255,0.18), 0 15px 40px rgba(0,0,0,1);
            border-color: var(--accent-gold);
            z-index: 50;
        }

        /* CONTENEDOR DE FOTOGRAFÍA */
        .mosaico-img-container {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #080808; 
            border-radius: 4px;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.9);
            padding: 8px; 
            position: relative;
            box-sizing: border-box;
            flex-shrink: 0;
        }

        .mosaico-img {
            width: 100%;
            height: auto; 
            max-height: 400px; 
            object-fit: contain; 
            box-shadow: 0 4px 15px rgba(255,255,255,0.08), 0 8px 25px rgba(0,0,0,0.8); 
            transition: transform 0.5s ease;
        }

        .articulo-mosaico:hover .mosaico-img { 
            transform: scale(1.03); 
        }

        /* CONTENEDOR DE TEXTO AGRUPADO */
        .texto-container {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            flex-grow: 0; 
        }

        .texto-container h3 {
            margin: 0 0 10px 0;
            font-size: 20px;
            font-weight: 800;
            color: white;
            line-height: 1.2;
            text-shadow: 0 2px 4px rgba(0,0,0,0.8);
        }

        .fecha-tarjeta {
            font-size: 11px;
            color: #888;
            margin-bottom: 8px;
            display: block;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .texto-container p {
            margin: 0;
            font-size: 14px;
            line-height: 1.6;
            color: #ccc;
            display: -webkit-box;
            -webkit-line-clamp: 5;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        /* FOOTER DE LA TARJETA */
        .tarjeta-footer {
            margin-top: auto; 
            display: flex;
            flex-direction: column;
            gap: 15px;
            padding-top: 15px;
        }

        .botones-principales-tarjeta {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .btn-leer {
            padding: 10px 20px;
            background: var(--accent-gold);
            color: black;
            border: none;
            font-weight: 900;
            font-size: 11px;
            cursor: pointer;
            border-radius: 4px;
            text-transform: uppercase;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            transition: background 0.3s;
            flex-grow: 1;
            text-align: center;
        }

        .btn-leer:hover {
            background: white;
        }

        .btn-compartir-tarjeta {
            background: #222;
            color: white;
            border: 1px solid #444;
            padding: 9px 15px;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }

        .btn-compartir-tarjeta:hover {
            background: var(--accent-gold);
            color: black;
            border-color: var(--accent-gold);
        }

        .badge {
            position: absolute;
            top: 25px;
            left: 25px;
            background: var(--accent-gold);
            color: black;
            font-weight: 900;
            font-size: 10px;
            padding: 6px 12px;
            border-radius: 4px;
            text-transform: uppercase;
            z-index: 10;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }

        /* REACCIONES GRANDES Y VISIBLES */
        .reacciones-bar {
            display: flex;
            gap: 10px;
            border-top: 1px solid #333;
            padding-top: 15px;
        }

        .btn-reaccion {
            background: transparent;
            border: 1px solid #444;
            color: #ccc;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-size: 18px; 
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            min-height: 48px;
            padding: 8px 10px; 
            flex-grow: 1;
        }

        .btn-reaccion:hover {
            background: rgba(255,255,255,0.1);
            border-color: var(--accent-gold);
            color: white;
        }

        .btn-reaccion.activo {
            background: rgba(255,184,28,0.2);
            border-color: var(--accent-gold);
            color: var(--accent-gold);
        }

        /* SISTEMA DE CUADRÍCULA PC (GRID AVANZADO) */
        @media (min-width: 851px) {
            .span-big { 
                grid-column: span 2; 
                grid-row: span 2; 
            }
            .span-big .mosaico-img-container {
                flex-grow: 1; 
                min-height: 350px;
            }
            .span-big .mosaico-img {
                max-height: 100%;
                height: 100%;
                object-fit: cover; 
            }

            .span-v { 
                grid-row: span 2; 
            }

            .span-h-izq, .span-h-der {
                display: grid;
                grid-template-columns: 1fr 1fr;
                grid-template-rows: 1fr auto;
                gap: 15px 25px; 
                height: 100%;
            }

            .span-h-izq .mosaico-img-container { grid-column: 1 / 2; grid-row: 1 / 3; height: 100%; }
            .span-h-izq .texto-container { grid-column: 2 / 3; grid-row: 1 / 2; padding: 0; }
            .span-h-izq .tarjeta-footer { grid-column: 2 / 3; grid-row: 2 / 3; padding-top: 15px; margin-top: auto; }

            .span-h-der .mosaico-img-container { grid-column: 2 / 3; grid-row: 1 / 3; height: 100%; }
            .span-h-der .texto-container { grid-column: 1 / 2; grid-row: 1 / 2; padding: 0; }
            .span-h-der .tarjeta-footer { grid-column: 1 / 2; grid-row: 2 / 3; padding-top: 15px; margin-top: auto; }
        }

        /* CONTROLES DE EDICIÓN DEL ADMINISTRADOR */
        .admin-controls {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 20;
            display: none;
            gap: 8px;
        }

        body.modo-admin .admin-controls {
            display: flex;
        }

        .btn-accion { background: rgba(0,0,0,0.85); color: white; border: 1px solid rgba(255,255,255,0.4); padding: 6px 10px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 11px; transition: all 0.3s; }
        .btn-accion:hover { background: var(--accent-gold); color: black; }
        .btn-eliminar:hover { background: #ff4444; color: white; border-color: transparent; }

        /* BARRA SUPERIOR DE HERRAMIENTAS ADMIN */
        .admin-toolbar {
            display: none;
            justify-content: center;
            align-items: center;
            gap: 15px;
            flex-wrap: wrap;
            margin: 20px auto;
            padding: 15px 20px;
            max-width: 1100px;
            background: rgba(29, 154, 76, 0.12);
            border: 1px solid var(--vibrant-green);
            border-radius: 8px;
        }

        body.modo-admin .admin-toolbar {
            display: flex;
        }

        .btn-toolbar {
            background: var(--vibrant-green);
            color: white;
            border: none;
            padding: 12px 22px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 13px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            transition: all 0.3s;
        }

        .btn-toolbar:hover {
            background: var(--accent-gold);
            color: black;
        }

        /* VENTANA DE LECTURA INMERSIVA SELLADA */
        .modal-inmersivo {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: #000000; 
            z-index: 4000;
            align-items: flex-start;
            justify-content: center;
            overflow-y: auto;
            overflow-x: hidden;
            box-sizing: border-box;
        }

        .lectura-box {
            background: #111111; 
            color: var(--text-main);
            width: 100%;
            max-width: 900px; 
            min-height: 100%; 
            position: relative;
            box-shadow: 0 0 50px rgba(0,0,0,1);
            display: flex;
            flex-direction: column;
            border-left: 1px solid #222;
            border-right: 1px solid #222;
            box-sizing: border-box;
        }
        
        /* ALINEACIÓN SIMÉTRICA Y TRANSPARENCIA (CRISTAL OSCURO) */
        .btn-cerrar-lectura, .btn-pin {
            position: fixed;
            top: 20px; 
            background: rgba(0, 0, 0, 0.4); 
            color: rgba(255, 255, 255, 0.8);
            border: none;
            border-radius: 50%;
            width: 45px; height: 45px; 
            font-size: 22px;
            font-weight: bold;
            cursor: pointer;
            z-index: 4100;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            backdrop-filter: blur(5px);
        }

        .btn-cerrar-lectura { right: 20px; }
        .btn-cerrar-lectura:hover { background: rgba(0,0,0,0.8); color: white; transform: scale(1.1); }

        .btn-pin { left: 20px; }
        .btn-pin:hover { background: rgba(0,0,0,0.8); color: white; }
        .btn-pin.activo { background: rgba(0,0,0,0.7); color: var(--accent-gold); }

        /* FOTO Y SELLADO CON CHINCHE */
        .lectura-hero-container {
            padding: 30px 40px 10px 40px;
            background: #111111;
            position: relative;
            display: flex;
            justify-content: center;
        }

        .foto-clavada {
            position: sticky;
            top: 0; 
            z-index: 100;
        }

        .lectura-hero {
            width: 100%;
            height: auto;
            max-height: 65vh; 
            object-fit: contain; 
            display: block;
            box-shadow: 0 8px 30px rgba(255,255,255,0.12), 0 15px 40px rgba(0,0,0,0.9);
            border-radius: 6px;
            background-color: #080808;
            border: 1px solid rgba(255,255,255,0.15);
            transition: all 0.3s ease;
        }

        .lectura-body { 
            padding: 20px 60px 60px 60px; 
            flex-grow: 1;
            position: relative;
            z-index: 10;
            background: #111111; 
        }

        .lectura-body h1 {
            color: white;
            font-weight: 900;
            margin-top: 15px;
            margin-bottom: 10px;
            font-size: clamp(26px, 4vw, 40px);
            line-height: 1.15;
        }
        
        .lectura-fuente { font-size: 13px; color: var(--accent-gold); font-weight: bold; margin-bottom: 30px; display: block; text-transform: uppercase; letter-spacing: 1px; }
        .lectura-texto { font-size: 21px; line-height: 1.8; color: #E5E5E5; text-align: justify; }

        /* SECCIÓN COMENTARIOS */
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

        /* BOTÓN FLOTANTE REGRESO ARRIBA */
        .btn-volver-arriba {
            display: none;
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: rgba(0, 0, 0, 0.4);
            color: rgba(255, 255, 255, 0.6);
            border: none;
            border-radius: 50%;
            width: 45px;
            height: 45px;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            z-index: 4200; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            opacity: 0;
            backdrop-filter: blur(5px);
        }
        
        .btn-volver-arriba:hover { background: rgba(0,0,0,0.8); color: white; transform: scale(1.1); }

        /* ADMIN MODAL (CMS) */
        .modal-base { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); backdrop-filter: blur(8px); z-index: 5000; align-items: center; justify-content: center; padding: 20px; box-sizing: border-box; }
        .admin-box { background: var(--glass); padding: 35px; border-radius: 12px; width: 100%; max-width: 680px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.9); border: 1px solid #333; max-height: 92vh; overflow-y: auto; }
        .admin-box h2 { color: var(--accent-gold); font-weight: 900; margin-bottom: 15px; margin-top: 0; }
        .admin-label { display: block; text-align: left; font-size: 11px; color: var(--accent-gold); font-weight: bold; text-transform: uppercase; margin-top: 10px; margin-bottom: 2px; letter-spacing: 0.5px; }
        .admin-input { width: 100%; padding: 12px; margin: 4px 0 8px 0; border: 1px solid #444; background: var(--panel-bg); color: var(--text-main); border-radius: 6px; font-size: 14px; font-family: inherit; box-sizing: border-box; }
        .btn-admin { background: var(--vibrant-green); color: white; border: none; padding: 15px 30px; border-radius: 6px; font-weight: bold; cursor: pointer; width: 100%; margin-top: 15px; font-size: 15px; transition: all 0.3s; }
        .btn-admin:hover { background: var(--accent-gold); color: black; }
        .preview-img-box { width: 100%; max-height: 180px; object-fit: contain; background: #080808; border: 1px solid #333; border-radius: 6px; margin-top: 6px; display: none; }
        footer { background: #080808; color: #666; text-align: center; padding: 50px 20px; margin-top: 40px; border-top: 1px solid #1a1a1a; }
        .btn-panel-secreto { background: transparent; border: 1px solid #333; color: #555; padding: 8px 15px; font-size: 11px; cursor: pointer; margin-bottom: 20px; border-radius: 4px; }

        /* NOTIFICACIÓN TOAST DE GUARDADO */
        .cms-toast {
            position: fixed;
            bottom: 30px;
            left: 30px;
            background: var(--vibrant-green);
            color: white;
            padding: 12px 22px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
            z-index: 6000;
            box-shadow: 0 6px 20px rgba(0,0,0,0.8);
            display: none;
        }

        /* RESPONSIVE MÓVIL */
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
        PORTAL AMAZONÍA HOY
    </a>
    <div class="nav-links-container">
        <a href="#hero">Inicio</a>
        <a href="#mosaico" id="nav-contador-noticias">Noticias (__TOTAL_ART__)</a>
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

<!-- BARRA DE HERRAMIENTAS DEL CMS EN HOSTING -->
<div class="admin-toolbar" id="barra-admin-cms">
    <button class="btn-toolbar" onclick="abrirEditorNuevo()">+ CREAR NUEVA NOTICIA</button>
    <button class="btn-toolbar" style="background:#FFB81C; color:black;" onclick="exportarBaseDatosJSON()">💾 DESCARGAR RESPALDO (.JSON)</button>
    <button class="btn-toolbar" style="background:#333; border:1px solid #666;" onclick="cerrarSesionAdmin()">🔒 SALIR DE MODO ADMIN</button>
</div>

<div class="mosaico-container" id="mosaico">
__TARJETAS_HTML__
</div>

<div id="cms-toast" class="cms-toast">Cambios guardados permanentemente</div>

<button class="btn-volver-arriba" id="btn-volver-arriba" onclick="scrollToTop()">↑</button>

<div id="modal-lectura" class="modal-inmersivo">
    <button class="btn-cerrar-lectura" onclick="cerrarLectura()">×</button>
    <button class="btn-pin" id="btn-fijar-foto" onclick="togglePinFoto()" title="Fijar Fotografía">📌</button>
    
    <div class="lectura-box">
        <div class="lectura-hero-container" id="contenedor-foto-inmersiva">
            <img id="lectura-img" src="" class="lectura-hero" alt="Imagen del Artículo" onerror="this.onerror=null; this.src='images/default.jpg';">
        </div>
        <div class="lectura-body">
            <span id="lectura-categoria" class="badge" style="position:relative; top:0; left:0; margin-bottom: 15px; display:inline-block;">CATEGORÍA</span>
            <span id="lectura-fecha" class="fecha-tarjeta" style="margin-bottom:15px;">Fecha</span>
            <h1 id="lectura-titulo">Título del Artículo</h1>
            <span id="lectura-fuente" class="lectura-fuente">Fuente</span>
            
            <div id="lectura-texto" class="lectura-texto"></div>

            <div style="margin-top: 30px; text-align: center;">
                <button class="btn-compartir-tarjeta" style="width: 100%; max-width: 300px; padding: 15px; font-size: 18px; background: var(--accent-gold); color: black; font-weight: bold;" onclick="ejecutarCompartirInmersivo()">🔗 Compartir Artículo</button>
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
        <input type="hidden" id="edit-orden-original"> 
        
        <label class="admin-label">Tamaño y Formato de Tarjeta en el Mosaico</label>
        <select id="edit-formato" class="admin-input" style="border-color: var(--accent-gold); font-weight: bold;">
            <option value="">Cuadrado Normal (1x1)</option>
            <option value="span-h-izq">Horizontal — Foto a la Izquierda</option>
            <option value="span-h-der">Horizontal — Foto a la Derecha</option>
            <option value="span-v">Vertical Largo (1x2)</option>
            <option value="span-big">Extra Grande Destacado (2x2)</option>
        </select>

        <label class="admin-label">Fotografía (Ruta del Hosting, URL o Subir desde tu PC)</label>
        <input type="text" id="edit-imagen" class="admin-input" placeholder="Ej: imagenes_articulos/... o https://..." oninput="actualizarVistaPrevia(this.value)">
        <div style="display:flex; gap:10px; align-items:center; margin-bottom:8px;">
            <label for="upload-foto-pc" style="background:#2a2a2a; color:var(--accent-gold); border:1px dashed var(--accent-gold); padding:10px 14px; border-radius:6px; cursor:pointer; font-size:12px; font-weight:bold; width:100%; text-align:center;">
                📷 SUBIR / CAMBIAR FOTO DESDE TU PC (SE GUARDA EN EL HOSTING/FIREBASE)
            </label>
            <input type="file" id="upload-foto-pc" accept="image/*" style="display:none;" onchange="procesarFotoDesdePC(event)">
        </div>
        <img id="edit-preview-img" class="preview-img-box" alt="Vista previa">

        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div>
                <label class="admin-label">Fecha</label>
                <input type="text" id="edit-fecha" class="admin-input" placeholder="Ej: 2026-05-12">
            </div>
            <div>
                <label class="admin-label">Categoría</label>
                <input type="text" id="edit-etiqueta" class="admin-input" placeholder="Ej: NOTICIA / REPORTAJE">
            </div>
        </div>

        <label class="admin-label">Título del Artículo</label>
        <input type="text" id="edit-titulo" class="admin-input" placeholder="Título de la noticia">

        <label class="admin-label">Fuente o Autor</label>
        <input type="text" id="edit-fuente" class="admin-input" placeholder="Fuente o Autor">

        <label class="admin-label">Resumen Corto (Mosaico)</label>
        <textarea id="edit-resumen" class="admin-input" rows="3" placeholder="Resumen corto..."></textarea>

        <label class="admin-label">Contenido Completo (Lectura Inmersiva)</label>
        <textarea id="edit-contenido" class="admin-input" rows="7" placeholder="Contenido completo para la ventana inmersiva..."></textarea>

        <button class="btn-admin" id="btn-guardar-cms" onclick="guardarNoticia()">💾 GUARDAR CAMBIOS PERMANENTEMENTE</button>
        
        <div style="margin-top: 25px; padding: 15px; border: 1px dashed var(--vibrant-green); border-radius: 8px; background: rgba(0,0,0,0.3);">
            <h4 style="color: var(--vibrant-green); margin-top: 0; font-size: 14px;">Carga Masiva Recursiva (.json)</h4>
            <input type="file" id="bulkFileInput" accept=".json" onchange="ejecutarImportacionMasiva(event)" class="admin-input" style="background: #111;">
            <p style="font-size: 11px; color: #888; margin-bottom: 0;">Equipado con Memoria de ID: Sobrescribe para evitar duplicados.</p>
        </div>

        <button class="w3-button w3-text-grey w3-margin-top" onclick="closeAdmin()">Cerrar</button>
    </div>
</div>

<footer>
    <button class="btn-panel-secreto" onclick="abrirLogin()">Acceso Administrativo</button>
    <h2 style="letter-spacing: 2px; color: #555;">PORTAL AMAZONÍA HOY</h2>
    <p>creado por: Avrora Soft - Vibola LLC - 2026</p>
</footer>

<script>
    try {
        if (screen.orientation && screen.orientation.lock) {
            screen.orientation.lock("portrait-primary").catch(function(error) {});
        }
    } catch(e) {}

    function mostrarToast(mensaje, esError) {
        const toast = document.getElementById("cms-toast");
        if (!toast) return;
        toast.innerText = mensaje;
        toast.style.background = esError ? "#c0392b" : "#1D9A4C";
        toast.style.display = "block";
        setTimeout(function() {
            toast.style.display = "none";
        }, 3500);
    }

    function ajustarTeclado(elemento) {
        setTimeout(function() {
            elemento.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
    }

    function checkScroll() {
        const btn = document.getElementById("btn-volver-arriba");
        const modal = document.getElementById('modal-lectura');
        let currentScroll = 0;
        
        if (modal.style.display === 'flex') {
            currentScroll = modal.scrollTop;
        } else {
            currentScroll = document.body.scrollTop || document.documentElement.scrollTop;
        }

        if (currentScroll > 400) {
            btn.style.display = "flex";
            setTimeout(function() { btn.style.opacity = "1"; }, 50);
        } else {
            btn.style.opacity = "0";
            setTimeout(function() { 
                if (currentScroll <= 400) btn.style.display = "none"; 
            }, 300);
        }
    }

    window.onscroll = checkScroll;
    document.getElementById('modal-lectura').onscroll = checkScroll;

    function scrollToTop() {
        const modal = document.getElementById('modal-lectura');
        if (modal.style.display === 'flex') {
            modal.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    }

    function compartirNativo(titulo) {
        if (navigator.share) {
            navigator.share({
                title: titulo,
                text: 'Te comparto este artículo de Amazonía Hoy:',
                url: window.location.href
            }).catch(console.error);
        } else {
            alert("Enlace copiado al portapapeles. ¡Listo para pegar y compartir!");
        }
    }

    function ejecutarCompartirInmersivo() {
        const titulo = document.getElementById('lectura-titulo').innerText;
        compartirNativo(titulo);
    }

    const firebaseConfig = {
        apiKey: "AIzaSyBOwGbgEqRzFysi3mMnJUHolxNtyp0cMsI",
        authDomain: "portal-ia-web.firebaseapp.com",
        projectId: "portal-ia-web",
        storageBucket: "portal-ia-web.firebasestorage.app",
        messagingSenderId: "936426810042",
        appId: "1:936426810042:web:6945cec92108c4aed03083",
        measurementId: "G-6CFNPR19HG"
    };

    if (!firebase.apps.length) {
        firebase.initializeApp(firebaseConfig);
    }
    const db = firebase.firestore();
    try {
        db.enablePersistence({ synchronizeTabs: true }).catch(function(err) {});
    } catch(e) {}

    let isAdmin = false;
    let memoriaArticulos = __JSON_MEMORIA__;
    let articuloActivoId = null;
    const CLAVE_CACHE_CMS = "cms_ediciones_portal_v1";

    function obtenerCacheEdicionesLocal() {
        try {
            const raw = localStorage.getItem(CLAVE_CACHE_CMS);
            return raw ? JSON.parse(raw) : {};
        } catch(e) {
            return {};
        }
    }

    function guardarEnCacheEdicionesLocal(id, datos) {
        try {
            const cache = obtenerCacheEdicionesLocal();
            cache[String(id)] = Object.assign({}, cache[String(id)] || {}, datos);
            localStorage.setItem(CLAVE_CACHE_CMS, JSON.stringify(cache));
        } catch(e) {
            console.warn("Aviso de caché local:", e);
        }
    }

    function actualizarContadorNoticias() {
        const navCont = document.getElementById("nav-contador-noticias");
        if (!navCont) return;
        const totalVisibles = document.querySelectorAll("#mosaico .articulo-mosaico").length;
        navCont.innerText = "Noticias (" + totalVisibles + ")";
    }

    function crearTarjetaDOM(id, art) {
        const article = document.createElement("article");
        article.id = "card-" + id;
        article.setAttribute("data-id", id);
        article.setAttribute("data-categoria", art.categoria || "NOTICIA");
        article.className = "articulo-mosaico " + (art.formato || "");
        if ((art.categoria || "").toUpperCase() === "ETNIA" && !isAdmin) {
            article.style.display = "none";
        }

        const fechaTxt = art.fuente ? ((art.fecha || "") + " | Fuente: " + art.fuente) : (art.fecha || "");
        const imgSrc = art.imagen || "images/default.jpg";
        const likesCount = art.likes || 0;
        const sadsCount = art.sads || 0;
        const reaccionUsuario = localStorage.getItem("reaccion_" + id);
        const classLike = reaccionUsuario === 'likes' ? 'activo' : '';
        const classSad = reaccionUsuario === 'sads' ? 'activo' : '';

        article.innerHTML =
            '<div class="admin-controls">' +
                '<button class="btn-accion" onclick="abrirEditorExistente(\'' + id + '\')">✏️ Editar</button>' +
                '<button class="btn-accion btn-eliminar" onclick="eliminarNoticia(\'' + id + '\')">🗑️ Borrar</button>' +
            '</div>' +
            '<div class="badge" id="badge-' + id + '"></div>' +
            '<div class="mosaico-img-container">' +
                '<img src="' + imgSrc + '" id="img-' + id + '" class="mosaico-img" loading="lazy" onerror="this.onerror=null; this.src=\'images/default.jpg\';">' +
            '</div>' +
            '<div class="texto-container">' +
                '<span class="fecha-tarjeta" id="fecha-' + id + '"></span>' +
                '<h3 id="titulo-' + id + '"></h3>' +
                '<p id="resumen-' + id + '"></p>' +
            '</div>' +
            '<div class="tarjeta-footer">' +
                '<div class="botones-principales-tarjeta">' +
                    '<button class="btn-leer" onclick="abrirLectura(\'' + id + '\')">Leer Artículo</button>' +
                    '<button class="btn-compartir-tarjeta" id="share-' + id + '" title="Compartir">🔗</button>' +
                '</div>' +
                '<div class="reacciones-bar">' +
                    '<button id="btn-card-likes-' + id + '" onclick="reaccionar(\'' + id + '\', \'likes\')" class="btn-reaccion ' + classLike + '" title="Me gusta">👍 <span id="likes-' + id + '">' + likesCount + '</span></button>' +
                    '<button id="btn-card-sads-' + id + '" onclick="reaccionar(\'' + id + '\', \'sads\')" class="btn-reaccion ' + classSad + '" title="Qué tristeza">😢 <span id="sads-' + id + '">' + sadsCount + '</span></button>' +
                '</div>' +
            '</div>';

        const contenedor = document.getElementById("mosaico");
        if (contenedor) {
            contenedor.insertBefore(article, contenedor.firstChild);
        }
        return article;
    }

    // FUNCIÓN CENTRAL QUE APLICA TAMAÑO (FORMATO), FOTO, TEXTO Y BORRADO EN EL DOM
    function sincronizarTarjetaDOM(id, art, esNuevoDesdeCMS) {
        id = String(id);
        let card = document.getElementById("card-" + id);

        if (art.eliminado === true) {
            if (card) card.remove();
            delete memoriaArticulos[id];
            actualizarContadorNoticias();
            return;
        }

        if (!card) {
            if (!art.titulo) return;
            card = crearTarjetaDOM(id, art);
            actualizarContadorNoticias();
        }

        // 1. APLICAR TAMAÑO Y FORMATO DE LA TARJETA (span-big, span-v, span-h-izq, span-h-der o normal)
        const formatoLimpio = art.formato !== undefined ? art.formato : "";
        card.className = ("articulo-mosaico " + formatoLimpio).trim();

        // 2. APLICAR CATEGORÍA Y FILTRO ETNIA
        const cat = art.categoria || "NOTICIA";
        card.setAttribute("data-categoria", cat);
        if (cat.toUpperCase() === "ETNIA" && !isAdmin) {
            card.style.display = "none";
        } else {
            card.style.display = "";
        }

        const elBadge = document.getElementById("badge-" + id);
        if (elBadge) elBadge.innerText = cat;

        // 3. APLICAR FOTOGRAFÍA
        const elImg = document.getElementById("img-" + id);
        if (elImg && art.imagen) {
            if (elImg.getAttribute("src") !== art.imagen) {
                elImg.src = art.imagen;
            }
        }

        // 4. APLICAR FECHA, FUENTE, TÍTULO Y RESUMEN
        const elFecha = document.getElementById("fecha-" + id);
        if (elFecha) {
            const fechaStr = art.fecha || "";
            const fuenteStr = art.fuente || "";
            elFecha.innerText = fuenteStr ? (fechaStr + " | Fuente: " + fuenteStr) : fechaStr;
        }

        const elTitulo = document.getElementById("titulo-" + id);
        if (elTitulo && art.titulo !== undefined) elTitulo.innerText = art.titulo;

        const elResumen = document.getElementById("resumen-" + id);
        if (elResumen && art.resumen !== undefined) elResumen.innerText = art.resumen;

        const elShare = document.getElementById("share-" + id);
        if (elShare && art.titulo) {
            elShare.onclick = function() { compartirNativo(art.titulo); };
        }

        // 5. APLICAR REACCIONES
        const spanLikes = document.getElementById("likes-" + id);
        const spanSads = document.getElementById("sads-" + id);
        if (spanLikes && art.likes !== undefined) spanLikes.innerText = art.likes || 0;
        if (spanSads && art.sads !== undefined) spanSads.innerText = art.sads || 0;
    }

    if(sessionStorage.getItem("adminLogueado") === "true") {
        isAdmin = true;
        document.body.classList.add("modo-admin");
        document.querySelectorAll('[data-categoria="ETNIA"]').forEach(function(el) {
            el.style.display = '';
        });
    }

    // PASO 1 AL CARGAR: Aplicar instantáneamente (0ms) cualquier cambio guardado en caché local
    (function aplicarCacheInmediatoAlCargar() {
        const cacheLocal = obtenerCacheEdicionesLocal();
        Object.keys(cacheLocal).forEach(function(id) {
            const cambios = cacheLocal[id];
            if (cambios.eliminado === true) {
                sincronizarTarjetaDOM(id, { eliminado: true });
                return;
            }
            memoriaArticulos[id] = Object.assign({}, memoriaArticulos[id] || { id: id }, cambios);
            sincronizarTarjetaDOM(id, memoriaArticulos[id]);
        });
    })();

    // Marcar reacciones activas guardadas en el navegador
    Object.keys(memoriaArticulos).forEach(function(id) {
        const reaccionUsuario = localStorage.getItem("reaccion_" + id);
        if (reaccionUsuario === 'likes') {
            const b = document.getElementById("btn-card-likes-" + id);
            if (b) b.classList.add("activo");
        } else if (reaccionUsuario === 'sads') {
            const b = document.getElementById("btn-card-sads-" + id);
            if (b) b.classList.add("activo");
        }
    });

    // PASO 2 AL CARGAR: Sincronización en tiempo real con Firebase Firestore (Nube / Hosting)
    db.collection("articulos").onSnapshot(function(snapshot) {
        snapshot.docChanges().forEach(function(change) {
            const id = String(change.doc.id);
            const data = change.doc.data();

            if (change.type === "removed" || data.eliminado === true) {
                guardarEnCacheEdicionesLocal(id, { eliminado: true });
                sincronizarTarjetaDOM(id, { eliminado: true });
                return;
            }

            const baseExistente = memoriaArticulos[id] || { id: id };
            const imgPrevia = baseExistente.imagen;

            // Combinar datos de la nube sobre la memoria local
            const fusionado = Object.assign({}, baseExistente, data);

            // Si el documento en Firebase NO fue editado por CMS y traía default.jpg, conservar la foto local real
            if (!data.editado_cms && (!data.imagen || data.imagen === "images/default.jpg") && imgPrevia && imgPrevia !== "images/default.jpg") {
                fusionado.imagen = imgPrevia;
            }

            memoriaArticulos[id] = fusionado;

            if (data.editado_cms) {
                guardarEnCacheEdicionesLocal(id, fusionado);
            }

            sincronizarTarjetaDOM(id, fusionado);

            if (articuloActivoId === id) {
                actualizarBotonesInmersivos(id);
                renderizarComentarios(fusionado.comentarios || []);
            }
        });
    });

    function abrirLectura(id) {
        articuloActivoId = String(id);
        const art = memoriaArticulos[articuloActivoId];
        if(!art) return;

        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen().catch(function(err) {});
        }

        document.getElementById('lectura-img').src = art.imagen || "images/default.jpg";
        document.getElementById('lectura-categoria').innerText = art.categoria || "Noticia";
        document.getElementById('lectura-fecha').innerText = art.fecha || "";
        document.getElementById('lectura-titulo').innerText = art.titulo || "Sin título";
        document.getElementById('lectura-fuente').innerText = art.fuente ? "Fuente: " + art.fuente : "";
        
        let contenidoRaw = art.contenido_completo ? art.contenido_completo : (art.resumen ? art.resumen : "Contenido extenso no disponible.");
        
        let htmlContent = contenidoRaw
            .split(/\\r?\\n+/) 
            .map(function(p) { return p.trim(); })
            .filter(function(p) { return p.length > 0; })
            .map(function(p) { return '<p style="margin-bottom: 25px; margin-top: 0;">' + p + '</p>'; }) 
            .join('');
            
        document.getElementById('lectura-texto').innerHTML = htmlContent;

        actualizarBotonesInmersivos(articuloActivoId);

        document.getElementById('contenedor-foto-inmersiva').classList.remove('foto-clavada');
        document.getElementById('btn-fijar-foto').classList.remove('activo');

        renderizarComentarios(art.comentarios || []);

        document.getElementById('modal-lectura').style.display = 'flex';
        document.body.style.overflow = 'hidden'; 
        
        document.getElementById('modal-lectura').scrollTop = 0;
        checkScroll();
    }

    function cerrarLectura() {
        if (document.fullscreenElement && document.exitFullscreen) {
            document.exitFullscreen().catch(function(err) {});
        }

        document.getElementById('modal-lectura').style.display = 'none';
        document.body.style.overflow = 'auto'; 
        articuloActivoId = null;
        checkScroll();
    }

    function actualizarBotonesInmersivos(id) {
        const art = memoriaArticulos[id];
        if(!art) return;

        const btnLike = document.getElementById('btn-like-inmersivo');
        const btnSad = document.getElementById('btn-sad-inmersivo');
        
        const storageKey = "reaccion_" + id;
        const reaccionUsuario = localStorage.getItem(storageKey);

        btnLike.innerHTML = "👍 Me Gusta (" + (art.likes || 0) + ")";
        btnLike.className = "btn-reaccion " + (reaccionUsuario === 'likes' ? 'activo' : '');
        btnLike.onclick = function() { reaccionar(id, 'likes'); };
        
        btnSad.innerHTML = "😢 Qué Tristeza (" + (art.sads || 0) + ")";
        btnSad.className = "btn-reaccion " + (reaccionUsuario === 'sads' ? 'activo' : '');
        btnSad.onclick = function() { reaccionar(id, 'sads'); };
    }

    function togglePinFoto() {
        const contenedor = document.getElementById('contenedor-foto-inmersiva');
        const btn = document.getElementById('btn-fijar-foto');
        contenedor.classList.toggle('foto-clavada');
        btn.classList.toggle('activo');
    }

    function reaccionar(id, tipoSeleccionado) {
        id = String(id);
        const art = memoriaArticulos[id];
        if(!art) return;
        
        const storageKey = "reaccion_" + id;
        const reaccionActual = localStorage.getItem(storageKey);
        
        let updateData = {};
        
        if (reaccionActual === tipoSeleccionado) {
            art[tipoSeleccionado] = Math.max(0, (art[tipoSeleccionado] || 0) - 1);
            updateData[tipoSeleccionado] = art[tipoSeleccionado];
            localStorage.removeItem(storageKey);
        } else {
            art[tipoSeleccionado] = (art[tipoSeleccionado] || 0) + 1;
            updateData[tipoSeleccionado] = art[tipoSeleccionado];
            if (reaccionActual) {
                art[reaccionActual] = Math.max(0, (art[reaccionActual] || 0) - 1);
                updateData[reaccionActual] = art[reaccionActual];
            }
            localStorage.setItem(storageKey, tipoSeleccionado);
        }

        const spanLikes = document.getElementById("likes-" + id);
        const spanSads = document.getElementById("sads-" + id);
        if (spanLikes) spanLikes.innerText = art.likes || 0;
        if (spanSads) spanSads.innerText = art.sads || 0;

        const btnCardLike = document.getElementById("btn-card-likes-" + id);
        const btnCardSad = document.getElementById("btn-card-sads-" + id);
        const nuevaReaccion = localStorage.getItem(storageKey);
        if (btnCardLike) btnCardLike.className = "btn-reaccion " + (nuevaReaccion === 'likes' ? 'activo' : '');
        if (btnCardSad) btnCardSad.className = "btn-reaccion " + (nuevaReaccion === 'sads' ? 'activo' : '');

        if (articuloActivoId === id) {
            actualizarBotonesInmersivos(id);
        }
        
        guardarEnCacheEdicionesLocal(id, updateData);
        db.collection("articulos").doc(id).set(updateData, { merge: true });
    }

    function publicarComentario() {
        if(!articuloActivoId) return;
        const nombreInput = document.getElementById('comentario-nombre');
        const textoInput = document.getElementById('comentario-texto');
        
        const nombre = nombreInput.value.trim() || 'Anónimo';
        const texto = textoInput.value.trim();
        
        if(texto === "") {
            alert("Escribe un comentario antes de publicar.");
            return;
        }

        const art = memoriaArticulos[articuloActivoId];
        const nuevosComentarios = art.comentarios ? art.comentarios.slice() : [];
        
        const hoy = new Date();
        const fechaStr = hoy.toLocaleDateString() + ' ' + hoy.toLocaleTimeString();

        nuevosComentarios.push({
            nombre: nombre,
            texto: texto,
            fecha: fechaStr
        });

        art.comentarios = nuevosComentarios;
        nombreInput.value = "";
        textoInput.value = "";
        renderizarComentarios(nuevosComentarios);

        guardarEnCacheEdicionesLocal(articuloActivoId, { comentarios: nuevosComentarios });
        db.collection("articulos").doc(articuloActivoId).set({
            comentarios: nuevosComentarios
        }, { merge: true });
    }

    function renderizarComentarios(comentarios) {
        const contenedor = document.getElementById('lista-comentarios');
        contenedor.innerHTML = '';
        
        if(!comentarios || comentarios.length === 0) {
            contenedor.innerHTML = '<p style="color:#888; font-size:16px;">Sé el primero en comentar.</p>';
            return;
        }

        const reverseComments = comentarios.slice().reverse();
        
        reverseComments.forEach(function(c) {
            contenedor.innerHTML += 
                '<div class="comentario-item">' +
                    '<div class="comentario-autor">' + c.nombre + '</div>' +
                    '<div class="comentario-fecha">' + c.fecha + '</div>' +
                    '<p class="comentario-texto">' + c.texto + '</p>' +
                '</div>';
        });
    }

    /* ====================================================================
       LÓGICA DEL PANEL DE ADMINISTRACIÓN (CMS EN HOSTING Y LOCAL)
       ==================================================================== */
    function actualizarVistaPrevia(src) {
        const imgPrev = document.getElementById("edit-preview-img");
        if (!imgPrev) return;
        if (src && src.trim() !== "") {
            imgPrev.src = src.trim();
            imgPrev.style.display = "block";
        } else {
            imgPrev.style.display = "none";
        }
    }

    // Permite seleccionar una foto desde la PC, la comprime automáticamente y la guarda en el artículo (y en Firebase)
    function procesarFotoDesdePC(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                const canvas = document.createElement("canvas");
                const maxWidth = 1000;
                const maxHeight = 1000;
                let width = img.width;
                let height = img.height;

                if (width > height) {
                    if (width > maxWidth) {
                        height = Math.round(height * (maxWidth / width));
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width = Math.round(width * (maxHeight / height));
                        height = maxHeight;
                    }
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext("2d");
                ctx.drawImage(img, 0, 0, width, height);

                const dataUrlComprimida = canvas.toDataURL("image/jpeg", 0.80);
                document.getElementById("edit-imagen").value = dataUrlComprimida;
                actualizarVistaPrevia(dataUrlComprimida);
                mostrarToast("Fotografía optimizada y lista para guardar", false);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    function abrirLogin() {
        if(isAdmin) {
            abrirEditorNuevo();
            return;
        }
        document.getElementById('modal-admin').style.display = 'flex';
        document.getElementById('vista-login').style.display = 'block';
        document.getElementById('vista-editor').style.display = 'none';
        document.getElementById('admin-pass').value = '';
    }

    function checkPass() {
        const pass = document.getElementById('admin-pass').value;
        if(pass === "2026") {
            sessionStorage.setItem("adminLogueado", "true");
            isAdmin = true;
            document.body.classList.add("modo-admin");
            document.querySelectorAll('[data-categoria="ETNIA"]').forEach(function(el) {
                el.style.display = '';
            });
            closeAdmin();
            mostrarToast("Modo Administrador activado", false);
        } else {
            alert("Clave denegada.");
        }
    }

    function cerrarSesionAdmin() {
        sessionStorage.removeItem("adminLogueado");
        isAdmin = false;
        document.body.classList.remove("modo-admin");
        mostrarToast("Sesión de administrador cerrada", false);
    }

    function abrirEditorNuevo() {
        document.getElementById('edit-id').value = "";
        document.getElementById('edit-orden-original').value = "";
        document.getElementById('edit-fecha').value = new Date().toISOString().slice(0, 10);
        document.getElementById('edit-titulo').value = "";
        document.getElementById('edit-etiqueta').value = "NOTICIA";
        document.getElementById('edit-resumen').value = "";
        document.getElementById('edit-contenido').value = "";
        document.getElementById('edit-fuente').value = "REDACCIÓN CENTRAL";
        document.getElementById('edit-imagen').value = "";
        document.getElementById('edit-formato').value = "";
        document.getElementById('upload-foto-pc').value = "";
        actualizarVistaPrevia("");
        document.getElementById('editor-titulo').innerText = "Crear Nueva Noticia";
        
        document.getElementById('modal-admin').style.display = 'flex';
        document.getElementById('vista-login').style.display = 'none';
        document.getElementById('vista-editor').style.display = 'block';
    }

    function abrirEditorExistente(id) {
        id = String(id);
        const art = memoriaArticulos[id];
        if(!art) return;

        document.getElementById('edit-id').value = id;
        document.getElementById('edit-orden-original').value = art.orden || "";
        document.getElementById('edit-fecha').value = art.fecha || "";
        document.getElementById('edit-titulo').value = art.titulo || "";
        document.getElementById('edit-etiqueta').value = art.categoria || "NOTICIA";
        document.getElementById('edit-resumen').value = art.resumen || "";
        document.getElementById('edit-contenido').value = art.contenido_completo || "";
        document.getElementById('edit-fuente').value = art.fuente || "";
        document.getElementById('edit-imagen').value = art.imagen || "";
        document.getElementById('edit-formato').value = art.formato || "";
        document.getElementById('upload-foto-pc').value = "";
        actualizarVistaPrevia(art.imagen || "");
        document.getElementById('editor-titulo').innerText = "Editar Artículo (ID: " + id + ")";
        
        document.getElementById('modal-admin').style.display = 'flex';
        document.getElementById('vista-login').style.display = 'none';
        document.getElementById('vista-editor').style.display = 'block';
    }

    function guardarNoticia() {
        const id = document.getElementById('edit-id').value.trim();
        const ordenOriginal = document.getElementById('edit-orden-original').value;
        const docId = id === "" ? String(Date.now()) : String(id);
        const artPrevio = memoriaArticulos[docId] || {};

        const data = {
            id: isNaN(Number(docId)) ? docId : Number(docId),
            fecha: document.getElementById('edit-fecha').value.trim(),
            titulo: document.getElementById('edit-titulo').value.trim(),
            categoria: document.getElementById('edit-etiqueta').value.trim() || "NOTICIA",
            resumen: document.getElementById('edit-resumen').value.trim(),
            contenido_completo: document.getElementById('edit-contenido').value.trim(),
            fuente: document.getElementById('edit-fuente').value.trim(),
            imagen: document.getElementById('edit-imagen').value.trim() || "images/default.jpg",
            formato: document.getElementById('edit-formato').value,
            orden: ordenOriginal ? parseInt(ordenOriginal) : (artPrevio.orden || Date.now()),
            likes: artPrevio.likes || 0,
            sads: artPrevio.sads || 0,
            comentarios: artPrevio.comentarios || [],
            eliminado: false,
            editado_cms: true,
            ultima_edicion: Date.now()
        };

        if(!data.titulo) {
            alert("El título es obligatorio.");
            return;
        }

        const btnGuardar = document.getElementById("btn-guardar-cms");
        if (btnGuardar) {
            btnGuardar.innerText = "⏳ GUARDANDO...";
            btnGuardar.disabled = true;
        }

        // 1. Actualizar en memoria y aplicar a la tarjeta en el DOM de inmediato
        memoriaArticulos[docId] = Object.assign({}, artPrevio, data);
        guardarEnCacheEdicionesLocal(docId, data);
        sincronizarTarjetaDOM(docId, memoriaArticulos[docId], id === "");

        // 2. Guardar permanentemente en Firebase Firestore para que persista al actualizar y en el hosting
        db.collection("articulos").doc(docId).set(data, { merge: true }).then(function() {
            if (btnGuardar) {
                btnGuardar.innerText = "💾 GUARDAR CAMBIOS PERMANENTEMENTE";
                btnGuardar.disabled = false;
            }
            closeAdmin();
            mostrarToast("¡Cambios de tamaño, foto y texto guardados permanentemente!", false);
        }).catch(function(err) {
            if (btnGuardar) {
                btnGuardar.innerText = "💾 GUARDAR CAMBIOS PERMANENTEMENTE";
                btnGuardar.disabled = false;
            }
            closeAdmin();
            console.error("Aviso Firebase:", err);
            mostrarToast("Guardado en memoria local (Revisar conexión/reglas de Firebase)", false);
        });
    }

    function eliminarNoticia(id) {
        id = String(id);
        if(confirm("¿Estás completamente seguro de borrar este artículo? Desaparecerá de forma permanente.")) {
            guardarEnCacheEdicionesLocal(id, { eliminado: true });
            sincronizarTarjetaDOM(id, { eliminado: true });

            // Marcar como eliminado: true en Firebase para que al recargar el HTML estático no vuelva a aparecer
            db.collection("articulos").doc(id).set({
                eliminado: true,
                editado_cms: true,
                ultima_edicion: Date.now()
            }, { merge: true }).then(function() {
                mostrarToast("Artículo eliminado permanentemente", false);
            });
        }
    }

    function exportarBaseDatosJSON() {
        const listaExportar = Object.keys(memoriaArticulos)
            .map(function(k) { return memoriaArticulos[k]; })
            .filter(function(art) { return art && art.eliminado !== true; });

        const jsonStr = JSON.stringify(listaExportar, null, 4);
        const blob = new Blob([jsonStr], { type: "application/json;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "articulos_portal.json";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        mostrarToast("Archivo articulos_portal.json descargado", false);
    }

    function ejecutarImportacionMasiva(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async function(e) {
            try {
                const lista = JSON.parse(e.target.result);
                const baseDatos = firebase.firestore();
                let contador = 0;
                
                for (const art of lista) {
                    const articleId = art.id ? String(art.id) : String(Date.now() + contador);
                    const payload = {
                        id: art.id || articleId,
                        fecha: art.fecha || "",
                        titulo: (art.titulo || "Sin Título").toUpperCase(),
                        categoria: art.categoria || "GENERAL",
                        resumen: art.resumen || "",
                        contenido_completo: art.contenido_completo || "", 
                        fuente: art.fuente || "",
                        formato: art.formato || "",
                        imagen: art.imagen || ("imagenes_articulos/" + articleId + "_imagenes_articulos/" + articleId + "_imagen_principal.jpg"),
                        orden: art.orden || (Date.now() + contador),
                        likes: art.likes || 0,
                        sads: art.sads || 0,
                        comentarios: art.comentarios || [],
                        eliminado: false,
                        editado_cms: true
                    };
                    memoriaArticulos[articleId] = payload;
                    guardarEnCacheEdicionesLocal(articleId, payload);
                    sincronizarTarjetaDOM(articleId, payload);
                    await baseDatos.collection("articulos").doc(articleId).set(payload, { merge: true }); 
                    contador++;
                }
                alert("¡Éxito! Se han procesado " + contador + " artículos.\\nLa memoria de ID impidió la duplicidad de los materiales ya existentes.");
                event.target.value = ""; 
                closeAdmin();
            } catch (error) {
                alert("Error al procesar el archivo JSON: " + error.message);
            }
        };
        reader.readAsText(file);
    }

    function closeAdmin() {
        document.getElementById('modal-admin').style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == document.getElementById('modal-admin')) closeAdmin();
    }
</script>

</body>
</html>
"""

    html_completo = (
        plantilla_html
        .replace("__TOTAL_ART__", total_art)
        .replace("__TARJETAS_HTML__", tarjetas_html)
        .replace("__JSON_MEMORIA__", json_memoria)
    )

    index_path = os.path.join(base_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_completo)

    fotos_especificas = len(tarjetas_lista) - conteo_origen.get("default", 0)
    print("=================================================================")
    print(f"¡index.html generado con éxito con {len(tarjetas_lista)} artículos!")
    print(f"- Fotografías propias vinculadas: {fotos_especificas}")
    print(f"  * Por carpeta ID: {conteo_origen['id_carpeta']}")
    print(f"  * Por archivo ID: {conteo_origen['id_archivo']}")
    print(f"  * Por ruta previa/URL: {conteo_origen['json_existente'] + conteo_origen['url_externa']}")
    print(f"  * Por coincidencia de título en images/: {conteo_origen['slug_exacto'] + conteo_origen['slug_palabras']}")
    print(f"- Artículos con imagen de respaldo (images/default.jpg): {conteo_origen['default']}")
    print("- CMS Persistente para Hosting (Tamaño, Fotos, Creación y Borrado): ACTIVO")
    print("=================================================================")

if __name__ == "__main__":
    generar_index_estatico()
