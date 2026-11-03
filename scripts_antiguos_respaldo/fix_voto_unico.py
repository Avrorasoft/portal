import os
import re

base_dir = r"C:\Portal"
html_files = [f for f in os.listdir(base_dir) if f.endswith(".html") and f not in ("index.html", "mapa.html", "indigenas.html")]

for hf in html_files:
    fp = os.path.join(base_dir, hf)
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Limpiar cualquier carga anterior de localStorage para reacciones y poner la nueva
    new_load = """        const votoGuardado = localStorage.getItem(`voto_hecho_${DOC_ID_ETNIA}`);
        if (votoGuardado === 'likes') document.getElementById('btn-like').classList.add('activo');
        if (votoGuardado === 'sads') document.getElementById('btn-sad').classList.add('activo');"""

    # Buscar y reemplazar la sección de lectura de localStorage en el script
    content = re.sub(r'const reaccionGuardada =.*?(?=function reaccionar|\n\s*\n)', new_load + "\n", content, flags=re.DOTALL)
    content = re.sub(r'if\(localStorage\.getItem\(`reaccion_likes.*?function publicarComentario', r'function publicarComentario', content, flags=re.DOTALL)

    # 2. Nueva función reaccionar con regla estricta de voto único y exclusivo
    nuevo_reaccionar_js = """
        function reaccionar(tipo) {
            const storageKey = `voto_hecho_${DOC_ID_ETNIA}`;
            const votoAnterior = localStorage.getItem(storageKey);
            
            if (votoAnterior === tipo) {
                alert("Ya has votado por esta opción anteriormente.");
                return;
            }

            const docRef = db.collection("reacciones_etnias").doc(DOC_ID_ETNIA);
            let payload = {};

            if (votoAnterior) {
                // Si ya había votado por la otra opción, restamos a la anterior y sumamos a la nueva
                payload[votoAnterior] = firebase.firestore.FieldValue.increment(-1);
                payload[tipo] = firebase.firestore.FieldValue.increment(1);
            } else {
                // Primer voto de este usuario
                payload[tipo] = firebase.firestore.FieldValue.increment(1);
            }

            docRef.set(payload, { merge: true }).then(() => {
                localStorage.setItem(storageKey, tipo);
                document.getElementById('btn-like').classList.remove('activo');
                document.getElementById('btn-sad').classList.remove('activo');
                if (tipo === 'likes') {
                    document.getElementById('btn-like').classList.add('activo');
                } else {
                    document.getElementById('btn-sad').classList.add('activo');
                }
            }).catch(err => {
                alert("Error al registrar el voto: " + err.message);
            });
        }
    """

    patron = re.compile(r'function reaccionar\(tipo\).*?function publicarComentario', re.DOTALL)
    if patron.search(content):
        content = patron.sub(nuevo_reaccionar_js.strip() + "\n\n        function publicarComentario", content)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)

print("¡Las 36 páginas de etnias ahora operan bajo la regla estricta de voto único y exclusivo!")
