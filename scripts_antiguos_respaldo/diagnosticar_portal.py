import os
import hashlib
import json

base_dir = r"C:\Portal"
public_dir = os.path.join(base_dir, "public")

print("=== DIAGNÓSTICO TÉCNICO DEL PORTAL ===")

# 1. Verificar existencia de archivos críticos
archivos_criticos = ["index.html", "amazonia.css", "w3.css", "articulos_portal.json"]
for archivo in archivos_criticos:
    ruta_raiz = os.path.join(base_dir, archivo)
    ruta_public = os.path.join(public_dir, archivo)
    
    existe_raiz = os.path.exists(ruta_raiz)
    existe_public = os.path.exists(ruta_public)
    
    print(f"\n[Archivo: {archivo}]")
    print(f"  - En raíz ({base_dir}): {'✅ Existe' if existe_raiz else '❌ FALTA'} (Tamaño: {os.path.getsize(ruta_raiz) if existe_raiz else 0} bytes)")
    print(f"  - En public ({public_dir}): {'✅ Existe' if existe_public else '❌ FALTA'} (Tamaño: {os.path.getsize(ruta_public) if existe_public else 0} bytes)")
    
    if existe_raiz and existe_public:
        with open(ruta_raiz, "rb") as f1, open(ruta_public, "rb") as f2:
            h1 = hashlib.md5(f1.read()).hexdigest()
            h2 = hashlib.md5(f2.read()).hexdigest()
        if h1 == h2:
            print("  -> Estado: 🟢 Raíz y Public son IDÉNTICOS.")
        else:
            print("  -> Estado: 🔴 ¡DIVERGENCIA! Raíz y Public tienen CONTENIDOS DISTINTOS.")

# 2. Verificar firebase.json
firebase_path = os.path.join(base_dir, "firebase.json")
if os.path.exists(firebase_path):
    with open(firebase_path, "r", encoding="utf-8") as f:
        try:
            fb_data = json.load(f)
            public_cfg = fb_data.get("hosting", {}).get("public", "NO DEFINIDO")
            print(f"\n[Configuración Firebase]")
            print(f"  - Carpeta pública configurada en firebase.json: '{public_cfg}'")
            if public_cfg != "public":
                print(f"  -> ADVERTENCIA: Firebase está apuntando a '{public_cfg}', pero tus archivos clave están en otra parte.")
        except Exception as e:
            print(f"\n[Configuración Firebase] ❌ Error leyendo firebase.json: {e}")
else:
    print("\n[Configuración Firebase] ❌ No se encontró firebase.json en la raíz.")

print("\n=== FIN DEL DIAGNÓSTICO ===")
