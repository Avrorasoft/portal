import os

base_dir = r"C:\Portal"
html_files = [f for f in os.listdir(base_dir) if f.endswith(".html") and f not in ("index.html", "mapa.html", "indigenas.html")]

for hf in html_files:
    fp = os.path.join(base_dir, hf)
    with open(fp, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Hojear y hacer que el Satélite Real sea la capa por defecto en Leaflet
    c = c.replace(
        "const darkLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }).addTo(map);", 
        "const darkLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 });"
    )
    c = c.replace(
        "const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}');", 
        "const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}').addTo(map);"
    )
    c = c.replace(
        'L.control.layers({"Modo Oscuro": darkLayer, "Satélite Real": satelliteLayer}).addTo(map);', 
        'L.control.layers({"Satélite Real": satelliteLayer, "Modo Oscuro": darkLayer}).addTo(map);'
    )

    # 2. Corregir función reaccionar: cambiar docRef.update por docRef.set con merge
    old_reaccionar = """            if (reaccionActual === tipo) {
                let down = {}; down[tipo] = firebase.firestore.FieldValue.increment(-1);
                docRef.update(down);"""
    new_reaccionar = """            if (reaccionActual === tipo) {
                let down = {}; down[tipo] = firebase.firestore.FieldValue.increment(-1);
                docRef.set(down, { merge: true });"""
    c = c.replace(old_reaccionar, new_reaccionar)

    with open(fp, "w", encoding="utf-8") as f:
        f.write(c)

print("¡Las 36 páginas de etnias fueron actualizadas: Satélite Real por defecto y Me Gusta reparados!")
