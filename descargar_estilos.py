import urllib.request
import os

base_dir = r"C:\Portal"
base_url = "https://portal-ia-web.web.app/"

archivos = ["amazonia.css", "w3.css"]

for archivo in archivos:
    url = base_url + archivo
    destino = os.path.join(base_dir, archivo)
    try:
        print(f"Descargando {archivo} desde la web...")
        urllib.request.urlretrieve(url, destino)
        print(f"[OK] {archivo} guardado correctamente en {destino}")
    except Exception as e:
        print(f"[ERROR] No se pudo descargar {archivo}: {e}")

# Volver a correr la auditoría para verificar
print("\nVerificando auditoría local...")
import subprocess
subprocess.run(["python", "auditar_portal.py"])
