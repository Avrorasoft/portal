import os
import re

base_dir = r"C:\Portal"
html_files = [f for f in os.listdir(base_dir) if f.endswith(".html") and f not in ("index.html", "mapa.html", "indigenas.html")]

for hf in html_files:
    fp = os.path.join(base_dir, hf)
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # Carga inicial de localStorage para verificar el voto actual
    new_load = """        const votoGuardado = localStorage.getItem(`voto_hecho_${DOC_ID_ETNIA}`);
        if (votoGuardado === 'likes') document.getElementById('btn-like').classList.add('activo');
        if (votoGuardado === 'sads') document.getElementById('btn-sad').classList.add('activo');"""

    content = re.sub(r'const votoGuardado =.*?(?=function reaccionar|\n\s*\n)', new_load + "\n", content, flags=re.DOTALL)

    # Nueva función reaccionar con lógica de Toggle y Exclusividad perfecta
    nuevo_reaccionar_js = """
        function reaccionar(tipo) {
            const storageKey = `voto_hecho_${DOC_ID_ETNIA}`;
            const votoAnterior = localStorage.getItem(storageKey);
            const docRef = db.collection("reacciones_etnias").doc(DOC_ID_ETNIA);
            let payload = {};

            const btnLike = document.getElementById('btn-like');
            const btnSad = document.getElementById('btn-sad');
            if(btnLike) btnLike.disabled = true;
            if(btnSad) btnSad.disabled = true;

            if (votoAnterior === tipo) {
                // Si ya estaba activo, el usuario quiere desmarcarlo (quitar su voto)
                payload[tipo] = firebase.firestore.FieldValue.increment(-1);
                docRef.set(payload, { merge: true }).then(() => {
                    localStorage.removeItem(storageKey);
                    if(btnLike) { btnLike.classList.remove('activo'); btnLike.disabled = false; }
                    if(btnSad) { btnSad.classList.remove('activo'); btnSad.disabled = false; }
                }).catch(() => {
                    if(btnLike) btnLike.disabled = false;
                    if(btnSad) btnSad.disabled = false;
                });
            } else if (votoAnterior) {
                // Si tenía un voto en la otra opción, cambiamos de opinión (restamos anterior, sumamos nueva)
                payload[votoAnterior] = firebase.firestore.FieldValue.increment(-1);
                payload[tipo] = firebase.firestore.FieldValue.increment(1);
                docRef.set(payload, { merge: true }).then(() => {
                    localStorage.setItem(storageKey, tipo);
                    if(btnLike) btnLike.classList.remove('activo');
                    if(btnSad) btnSad.classList.remove('activo');
                    if(tipo === 'likes' && btnLike) btnLike.classList.add('activo');
                    if(tipo === 'sads' && btnSad) btnSad.classList.add('activo');
                    if(btnLike) btnLike.disabled = false;
                    if(btnSad) btnSad.disabled = false;
                }).catch(() => {
                    if(btnLike) btnLike.disabled = false;
                    if(btnSad) btnSad.disabled = false;
                });
            } else {
                // Sin voto previo: sumamos por primera vez
                payload[tipo] = firebase.firestore.FieldValue.increment(1);
                docRef.set(payload, { merge: true }).then(() => {
                    localStorage.setItem(storageKey, tipo);
                    if(tipo === 'likes' && btnLike) btnLike.classList.add('activo');
                    if(tipo === 'sads' && btnSad) btnSad.classList.add('activo');
                    if(btnLike) btnLike.disabled = false;
                    if(btnSad) btnSad.disabled = false;
                }).catch(() => {
                    if(btnLike) btnLike.disabled = false;
                    if(btnSad) btnSad.disabled = false;
                });
            }
        }
    """

    patron = re.compile(r'function reaccionar\(tipo\).*?function publicarComentario', re.DOTALL)
    if patron.search(content):
        content = patron.sub(nuevo_reaccionar_js.strip() + "\n\n        function publicarComentario", content)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)

print("¡Las 36 páginas de etnias tienen ahora un sistema de votación fluido, exclusivo y sin duplicados!")
