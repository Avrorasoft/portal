import os
import json

base_dir = r"C:\Portal"
print("=== AUDITORÍA DEL PORTAL AMAZONÍA ===")

# 1. Verificar archivos esenciales
archivos_esenciales = ["index.html", "amazonia.css", "w3.css", "articulos_portal.json"]
for archivo in archivos_esenciales:
    ruta = os.path.join(base_dir, archivo)
    existe = os.path.exists(ruta)
    print(f"[{'OK' if existe else 'ERROR'}] Archivo requerido: {archivo}")

# 2. Verificar integridad del JSON y cantidad de artículos
json_path = os.path.join(base_dir, "articulos_portal.json")
if os.path.exists(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            articulos = json.load(f)
        print(f"[OK] artículos_portal.json cargado correctamente con {len(articulos)} registros.")
    except Exception as e:
        print(f"[ERROR] El archivo JSON está corrupto: {e}")
else:
    print("[ERROR] No se encontró articulos_portal.json")

# 3. Inspeccionar index.html en busca de funciones críticas
index_path = os.path.join(base_dir, "index.html")
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    tiene_abrir = "abrirLectura" in html_content
    tiene_reaccionar = "reaccionar" in html_content
    tiene_compartir = "compartirNativo" in html_content
    
    print(f"[{'OK' if tiene_abrir else 'ALERTA'}] Función 'abrirLectura' presente en index.html")
    print(f"[{'OK' if tiene_reaccionar else 'ALERTA'}] Función 'reaccionar' presente en index.html")
    print(f"[{'OK' if tiene_compartir else 'ALERTA'}] Función 'compartirNativo' presente en index.html")
else:
    print("[ERROR] index.html no existe en la raíz.")

print("=== FIN DE LA AUDITORÍA ===")
