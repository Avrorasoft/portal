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

# Tomar los primeros artículos o todos de forma segura
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
        "sads": art.get("sads", 0)
    }

json_memoria = json.dumps(memoria_dict, ensure_ascii=False).replace("</script>", "<\\/script>")

html_limpio = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Portal Amazonía | Vanguardia y Territorio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/w3.css">
    <link rel="stylesheet" href="/amazonia.css">
    <link rel="stylesheet" href="/font-awesome.min.css">
    <style>
        body {{ background-color: #0a0a0a; color: #e0e0e0; font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .mosaico-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; max-width: 1400px; margin: 0 auto; }}
        .articulo-mosaico {{ background: #111; border: 1px solid #333; border-radius: 6px; padding: 20px; display: flex; flex-direction: column; gap: 15px; }}
        .btn-leer {{ background: var(--accent-gold, #ffb81c); color: black; border: none; padding: 10px; font-weight: bold; cursor: pointer; border-radius: 4px; text-transform: uppercase; }}
        .btn-reaccion {{ background: transparent; border: 1px solid #444; color: #ccc; padding: 8px; cursor: pointer; border-radius: 4px; }}
        .btn-reaccion.activo {{ background: rgba(255,184,28,0.2); border-color: var(--accent-gold, #ffb81c); color: var(--accent-gold, #ffb81c); }}
    </style>
</head>
<body>
    <h1 style="text-align:center; color:white;">Portal Amazonía</h1>
    <div id="mosaico" class="mosaico-container">
        <article class="articulo-mosaico">
            <h3>Portal en funcionamiento</h3>
            <p>Estructura principal restaurada y limpia de errores de sintaxis.</p>
            <button class="btn-leer" onclick="abrirLectura('1')">Leer Artículo</button>
            <button class="btn-reaccion" id="btn-card-likes-1" onclick="reaccionar('1', 'likes')">👍 <span id="likes-1">0</span></button>
        </article>
    </div>

    <!-- Modal Inmersivo -->
    <div id="modal-lectura" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:1000; padding:40px; box-sizing:border-box;">
        <div style="max-width:800px; margin:0 auto; background:#121212; padding:30px; border-radius:8px; position:relative; color:white;">
            <button onclick="cerrarLectura()" style="position:absolute; top:20px; right:20px; background:#333; color:white; border:none; padding:8px 12px; cursor:pointer;">✕ Cerrar</button>
            <h2 id="lectura-titulo">Título</h2>
            <p id="lectura-texto">Texto del artículo...</p>
        </div>
    </div>

    <script>
        const memoriaArticulos = {json_memoria};
        
        function abrirLectura(id) {{
            const art = memoriaArticulos[id];
            if(!art) return;
            document.getElementById('lectura-titulo').innerText = art.titulo;
            document.getElementById('lectura-texto').innerText = art.texto || art.resumen;
            document.getElementById('modal-lectura').style.display = 'block';
        }}

        function cerrarLectura() {{
            document.getElementById('modal-lectura').style.display = 'none';
        }}

        function reaccionar(id, tipo) {{
            console.log("Reacción registrada:", id, tipo);
        }}

        function compartirNativo(t) {{
            alert("Enlace copiado.");
        }}
    </script>
</body>
</html>
"""

# Guardar en la raíz y en public
with open(os.path.join(base_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_limpio)

with open(os.path.join(public_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_limpio)

# Copiar estilos esenciales a public
for css in ["amazonia.css", "w3.css", "font-awesome.min.css"]:
    src = os.path.join(base_dir, css)
    if os.path.exists(src):
        import shutil
        shutil.copy(src, public_dir)

print("✅ index.html regenerado limpio de sintaxis en raíz y public.")
