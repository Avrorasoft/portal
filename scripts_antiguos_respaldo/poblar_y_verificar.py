import os
import json

def verificar_y_actualizar():
    if not os.path.exists("articulos_portal.json"):
        print("No se encontró el archivo articulos_portal.json")
        return

    with open("articulos_portal.json", "r", encoding="utf-8") as f:
        articulos = json.load(f)

    print(f"Analizando {len(articulos)} artículos en el sistema...")

    con_foto = 0
    sin_foto = 0

    for art in articulos:
        # Validar ruta de imagen o asignar respaldo por defecto si no existe
        img_path = art.get("imagen", "")
        if img_path and os.path.exists(os.path.join("C:\\Portal", img_path)):
            con_foto += 1
        else:
            sin_foto += 1
            art["imagen"] = "images/default.jpg" # Respaldo estricto para evitar roturas visuales

    print(f"Resultados de verificación visual:")
    print(f"- Artículos con imagen local verificada: {con_foto}")
    print(f"- Artículos con imagen por defecto asignada: {sin_foto}")

    # Guardar sincronizado
    with open("articulos_portal.json", "w", encoding="utf-8") as f:
        json.dump(articulos, f, ensure_ascii=False, indent=4)

    print("¡El archivo articulos_portal.json está optimizado y listo para el portal inmersivo!")

if __name__ == "__main__":
    verificar_y_actualizar()