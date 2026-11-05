import os
import re
import json
import base64
import urllib.request
import html

PROJECT_ID = "portal-ia-web"
HOSTING_URL = "https://portal-ia-web.web.app"
BASE_DIR = r"C:\Portal"
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
NOTICIAS_DIR = os.path.join(PUBLIC_DIR, "noticias")
IMG_ART_DIR = os.path.join(PUBLIC_DIR, "imagenes_articulos")
JSON_LOCAL_PUBLIC = os.path.join(PUBLIC_DIR, "articulos_portal.json")
JSON_LOCAL_ROOT = os.path.join(BASE_DIR, "articulos_portal.json")
INDEX_HTML_PATH = os.path.join(PUBLIC_DIR, "index.html")


def decodificar_valor_firestore(val_dict):
    if not isinstance(val_dict, dict):
        return None
    if "stringValue" in val_dict:
        return val_dict["stringValue"]
    if "integerValue" in val_dict:
        try:
            return int(val_dict["integerValue"])
        except Exception:
            return val_dict["integerValue"]
    if "doubleValue" in val_dict:
        return float(val_dict["doubleValue"])
    if "booleanValue" in val_dict:
        return bool(val_dict["booleanValue"])
    if "nullValue" in val_dict:
        return None
    if "arrayValue" in val_dict:
        valores = val_dict["arrayValue"].get("values", [])
        return [decodificar_valor_firestore(v) for v in valores]
    if "mapValue" in val_dict:
        campos = val_dict["mapValue"].get("fields", {})
        return {k: decodificar_valor_firestore(v) for k, v in campos.items()}
    return None


def descargar_articulos_firestore():
    articulos_remotos = {}
    base_url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/articulos?pageSize=300"
    page_token = None

    while True:
        url = base_url + (f"&pageToken={page_token}" if page_token else "")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[AVISO] No se pudo consultar Firestore en esta pagina: {e}")
            break

        for doc in data.get("documents", []):
            doc_name = doc.get("name", "")
            doc_id = doc_name.split("/")[-1].strip()
            fields = doc.get("fields", {})
            art = {k: decodificar_valor_firestore(v) for k, v in fields.items()}
            art["id"] = doc_id
            articulos_remotos[str(doc_id)] = art

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return articulos_remotos


def cargar_articulos_locales():
    articulos_locales = {}
    ruta_usar = JSON_LOCAL_PUBLIC if os.path.exists(JSON_LOCAL_PUBLIC) else JSON_LOCAL_ROOT
    if os.path.exists(ruta_usar):
        try:
            with open(ruta_usar, "r", encoding="utf-8") as f:
                lista = json.load(f)
            if isinstance(lista, list):
                for idx, item in enumerate(lista):
                    if isinstance(item, dict):
                        id_str = str(item.get("id", idx)).strip()
                        articulos_locales[id_str] = item
            elif isinstance(lista, dict):
                for k, item in lista.items():
                    articulos_locales[str(k).strip()] = item
        except Exception as e:
            print(f"[AVISO] Error leyendo JSON local: {e}")
    return articulos_locales


def resolver_imagen_og(id_art, art):
    os.makedirs(IMG_ART_DIR, exist_ok=True)
    img_raw = str(art.get("imagen", "") or "").strip()

    # 1. Si es una imagen subida desde la PC en Base64 (data:image/...), guardarla como archivo fisico .jpg
    if img_raw.startswith("data:image/"):
        try:
            encabezado, b64_data = img_raw.split(",", 1)
            ext = "jpg"
            if "png" in encabezado.lower():
                ext = "png"
            elif "webp" in encabezado.lower():
                ext = "webp"
            nombre_archivo = f"{id_art}_imagen_principal.{ext}"
            ruta_relativa = f"imagenes_articulos/{nombre_archivo}"
            ruta_fisica = os.path.join(PUBLIC_DIR, "imagenes_articulos", nombre_archivo)
            with open(ruta_fisica, "wb") as img_f:
                img_f.write(base64.b64decode(b64_data))
            return f"{HOSTING_URL}/{ruta_relativa}", f"/{ruta_relativa}"
        except Exception as e:
            print(f"[AVISO] No se pudo decodificar Base64 para ID {id_art}: {e}")

    # 2. Si ya es una URL absoluta http/https
    if img_raw.startswith(("http://", "https://")):
        return img_raw, img_raw

    # 3. Si es una ruta relativa existente dentro de public/
    if img_raw and img_raw != "images/default.jpg":
        ruta_limpia = img_raw.lstrip("/").replace("\\", "/")
        ruta_fisica = os.path.join(PUBLIC_DIR, ruta_limpia.replace("/", os.sep))
        if os.path.isfile(ruta_fisica):
            return f"{HOSTING_URL}/{ruta_limpia}", f"/{ruta_limpia}"

    # 4. Buscar en public/imagenes_articulos/<id>_imagenes_articulos/
    carpeta_id = os.path.join(IMG_ART_DIR, f"{id_art}_imagenes_articulos")
    if os.path.isdir(carpeta_id):
        archivos = [
            f for f in os.listdir(carpeta_id)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        ]
        if archivos:
            elegida = archivos[0]
            for a in archivos:
                if "principal" in a.lower():
                    elegida = a
                    break
            ruta_rel = f"imagenes_articulos/{id_art}_imagenes_articulos/{elegida}"
            return f"{HOSTING_URL}/{ruta_rel}", f"/{ruta_rel}"

    # 5. Respaldo seguro por defecto
    return f"{HOSTING_URL}/images/default.jpg", "/images/default.jpg"


def construir_html_articulo(id_art, art, url_img_og, url_img_local):
    titulo = str(art.get("titulo") or "Portal Amazonía").strip()
    resumen = str(art.get("resumen") or art.get("contenido_completo") or "Noticia de Portal Amazonía Hoy.").strip()
    resumen_corto = re.sub(r"\s+", " ", resumen)[:220]
    categoria = str(art.get("categoria") or "NOTICIA").strip()
    fecha = str(art.get("fecha") or "").strip()
    fuente = str(art.get("fuente") or "Redacción Central").strip()
    contenido = str(art.get("contenido_completo") or resumen).strip()

    titulo_esc = html.escape(titulo, quote=True)
    resumen_esc = html.escape(resumen_corto, quote=True)
    categoria_esc = html.escape(categoria, quote=True)
    meta_linea = f"{html.escape(fecha)} | Fuente: {html.escape(fuente)}" if fecha else f"Fuente: {html.escape(fuente)}"
    contenido_esc = html.escape(contenido)

    url_canonica = f"{HOSTING_URL}/noticias/articulo_{id_art}.html"
    url_inmersion = f"/?id={id_art}"

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo_esc} | Portal Amazonía</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{titulo_esc}">
    <meta property="og:description" content="{resumen_esc}">
    <meta property="og:image" content="{url_img_og}">
    <meta property="og:image:secure_url" content="{url_img_og}">
    <meta property="og:image:width" content="1000">
    <meta property="og:image:height" content="630">
    <meta property="og:url" content="{url_canonica}">
    <meta property="og:site_name" content="Portal Amazonía">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{titulo_esc}">
    <meta name="twitter:description" content="{resumen_esc}">
    <meta name="twitter:image" content="{url_img_og}">
    <link rel="stylesheet" href="/w3.css">
    <link rel="stylesheet" href="/amazonia.css">
    <script>window.location.replace("{url_inmersion}");</script>
</head>
<body style="background:#0a0a0a; color:#e0e0e0; font-family:Arial, sans-serif; padding:20px;">
    <div style="max-width:800px; margin:40px auto; background:#121212; padding:30px; border-radius:8px; border:1px solid #333;">
        <a href="{url_inmersion}" style="color:#ffb81c; text-decoration:none; font-weight:bold; display:inline-block; margin-bottom:20px;">← Abrir en Inmersión Total</a>
        <div style="margin-bottom:20px; text-align:center;">
            <img src="{url_img_og}" style="width:100%; max-height:450px; object-fit:contain; background:#000; border-radius:4px;" alt="{titulo_esc}">
        </div>
        <span style="background:#ffb81c; color:black; font-weight:bold; font-size:10px; padding:4px 8px; border-radius:3px; text-transform:uppercase;">{categoria_esc}</span>
        <p style="color:#888; font-size:12px; margin:10px 0;">{meta_linea}</p>
        <h1 style="color:white; font-size:26px; font-weight:800; line-height:1.3; margin-bottom:20px;">{titulo_esc}</h1>
        <div style="font-size:16px; line-height:1.7; color:#ddd; white-space:pre-wrap;">{contenido_esc}</div>
    </div>
</body>
</html>
"""


def inyectar_redireccion_en_huérfanos(ids_procesados):
    os.makedirs(NOTICIAS_DIR, exist_ok=True)
    patron = re.compile(r"^articulo_([A-Za-z0-9_\-]+)\.html$")
    actualizados_extra = 0

    for nombre in os.listdir(NOTICIAS_DIR):
        m = patron.match(nombre)
        if not m:
            continue
        id_art = m.group(1)
        if id_art in ids_procesados:
            continue

        ruta = os.path.join(NOTICIAS_DIR, nombre)
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            linea_script = f'    <script>window.location.replace("/?id={id_art}");</script>'
            if 'window.location.replace("/?id=' in contenido:
                nuevo = re.sub(
                    r'\s*<script>window\.location\.replace\("/\?id=[^"]+"\);</script>',
                    "\n" + linea_script,
                    contenido
                )
            else:
                nuevo = contenido.replace("</head>", f"{linea_script}\n</head>", 1)
            if nuevo != contenido:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(nuevo)
                actualizados_extra += 1
        except Exception as e:
            print(f"[AVISO] No se pudo actualizar archivo existente {nombre}: {e}")

    return actualizados_extra


def actualizar_index_html():
    if not os.path.exists(INDEX_HTML_PATH):
        print(f"[ERROR] No se encontró {INDEX_HTML_PATH}")
        return

    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html_index = f.read()

    original = html_index

    # 1. Asegurar que urlArt en compartirNoticiaPortal apunte siempre al archivo estatico con Open Graph
    html_index = re.sub(
        r'var\s+urlArt\s*=\s*"https://portal-ia-web\.web\.app/\?id="\s*\+\s*encodeURIComponent\(idArt\);',
        'var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";',
        html_index
    )

    # 2. Asegurar que cuando un articulo nuevo viene de Firestore (como PBQRUApRwVth7WKZEcPG),
    # si el usuario entro con ?id=PBQRUApRwVth7WKZEcPG se abra la inmersion 100% apenas cargue el documento
    marcador_snapshot = "sincronizarTarjetaDOM(id, fusionado);"
    hook_inmersion_firestore = (
        "sincronizarTarjetaDOM(id, fusionado);\n"
        "            var _pUrl = new URLSearchParams(window.location.search);\n"
        "            var _idSolicitado = _pUrl.get('id') || _pUrl.get('articulo');\n"
        "            if (_idSolicitado && String(_idSolicitado) === String(id) && !articuloActivoId && typeof abrirLectura === 'function') {\n"
        "                setTimeout(function() { if (!articuloActivoId) abrirLectura(id); }, 100);\n"
        "            }"
    )

    if "_idSolicitado" not in html_index and marcador_snapshot in html_index:
        html_index = html_index.replace(marcador_snapshot, hook_inmersion_firestore, 1)

    if html_index != original:
        with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(html_index)
        print("[OK] index.html actualizado quirurgicamente (enlace Open Graph + apertura automatica de IDs Firestore).")
    else:
        print("[OK] index.html ya contaba con la configuracion correcta.")


def main():
    os.makedirs(NOTICIAS_DIR, exist_ok=True)
    os.makedirs(IMG_ART_DIR, exist_ok=True)

    print("1. Cargando articulos locales desde articulos_portal.json...")
    locales = cargar_articulos_locales()
    print(f"   -> {len(locales)} articulos locales cargados.")

    print("2. Descargando articulos en vivo desde Firebase Firestore...")
    remotos = descargar_articulos_firestore()
    print(f"   -> {len(remotos)} documentos descargados de Firestore.")

    # Combinar locales + Firestore (Firestore tiene prioridad si fue editado o es nuevo)
    todos = dict(locales)
    for id_doc, datos_remotos in remotos.items():
        base = dict(todos.get(id_doc, {}))
        img_previa = base.get("imagen")
        base.update(datos_remotos)
        if not datos_remotos.get("editado_cms") and (not base.get("imagen") or base.get("imagen") == "images/default.jpg") and img_previa:
            base["imagen"] = img_previa
        todos[id_doc] = base

    generados = 0
    fotos_b64_extraidas = 0
    ids_procesados = set()

    for id_art, art in todos.items():
        if not isinstance(art, dict):
            continue
        if art.get("eliminado") is True:
            continue

        img_antes = str(art.get("imagen", "") or "")
        url_img_og, url_img_local = resolver_imagen_og(id_art, art)
        if img_antes.startswith("data:image/"):
            fotos_b64_extraidas += 1

        html_art = construir_html_articulo(id_art, art, url_img_og, url_img_local)
        ruta_salida = os.path.join(NOTICIAS_DIR, f"articulo_{id_art}.html")
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(html_art)

        ids_procesados.add(id_art)
        generados += 1

    extra = inyectar_redireccion_en_huérfanos(ids_procesados)
    actualizar_index_html()

    print("=================================================================")
    print(f"PROCESO COMPLETADO CON EXITO:")
    print(f"- Paginas estaticas generadas/actualizadas en public/noticias/: {generados}")
    print(f"- Fotografias Base64 convertidas a .jpg reales para WhatsApp/FB: {fotos_b64_extraidas}")
    print(f"- Archivos previos adicionales con redireccion asegurada: {extra}")
    if "PBQRUApRwVth7WKZEcPG" in ids_procesados:
        print("- Verificado: articulo_PBQRUApRwVth7WKZEcPG.html creado con su foto y redireccion.")
    print("=================================================================")


if __name__ == "__main__":
    main()
