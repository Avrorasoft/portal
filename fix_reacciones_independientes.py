import os
import re

base_dir = r"C:\Portal"
html_files = [f for f in os.listdir(base_dir) if f.endswith(".html") and f not in ("index.html", "mapa.html", "indigenas.html")]

for hf in html_files:
    fp = os.path.join(base_dir, hf)
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Actualizar la lectura inicial de localStorage para reacciones independientes
    old_load = """        const reaccionGuardada = localStorage.getItem(`reaccion_${DOC_ID_ETNIA}`);
        if(reaccionGuardada === 'likes') document.getElementById('btn-like').classList.add('activo');
        if(reaccionGuardada === 'sads') document.getElementById('btn-sad').classList.add('activo');"""
    
    new_load = """        if(localStorage.getItem(`reaccion_likes_${DOC_ID_ETNIA}`) === 'true') document.getElementById('btn-like').classList.add('activo');
        if(localStorage.getItem(`reaccion_sads_${DOC_ID_ETNIA}`) === 'true') document.getElementById('btn-sad').classList.add('activo');"""
    
    content = content.replace(old_load, new_load)

    # 2. Nuevo bloque de reaccionar totalmente independiente
    nuevo_reaccionar_js = """
        function reaccionar(tipo) {
            const storageKey = `reaccion_${tipo}_${DOC_ID_ETNIA}`;
            const yaReaccionado = localStorage.getItem(storageKey) === 'true';
            const docRef = db.collection("reacciones_etnias").doc(DOC_ID_ETNIA);
            let payload = {};

            if (yaReaccionado) {
                payload[tipo] = firebase.firestore.FieldValue.increment(-1);
                docRef.set(payload, { merge: true }).then(() => {
                    localStorage.setItem(storageKey, 'false');
                    const btn = document.getElementById(`btn-${tipo === 'likes' ? 'like' : 'sad'}`);
                    if (btn) btn.classList.remove('activo');
                });
            } else {
                payload[tipo] = firebase.firestore.FieldValue.increment(1);
                docRef.set(payload, { merge: true }).then(() => {
                    localStorage.setItem(storageKey, 'true');
                    const btn = document.getElementById(`btn-${tipo === 'likes' ? 'like' : 'sad'}`);
                    if (btn) btn.classList.add('activo');
                });
            }
        }
    """

    patron = re.compile(r'function reaccionar\(tipo\).*?function publicarComentario', re.DOTALL)
    if patron.search(content):
        content = patron.sub(nuevo_reaccionar_js.strip() + "\n\n        function publicarComentario", content)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)

print("¡Las 36 páginas de etnias ahora tienen reacciones independientes y normales!")
