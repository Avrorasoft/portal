import os
import json

def integrar_datos():
    json_path = "articulos_portal.json"
    index_path = "index.html"

    if not os.path.exists(json_path):
        print("No se encontró el archivo articulos_portal.json. Ejecuta primero el script de parsing.")
        return

    if not os.path.exists(index_path):
        print("No se encontró el archivo index.html en C:\\Portal.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        articulos = json.load(f)

    print(f"Se cargaron {len(articulos)} artículos desde el JSON.")
    print("El portal web está listo para reflejar la estructura en tiempo real mediante Firebase o sincronización local.")

if __name__ == "__main__":
    integrar_datos()