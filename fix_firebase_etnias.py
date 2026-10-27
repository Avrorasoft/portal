import os
import re

base_dir = r"C:\Portal"
html_files = [f for f in os.listdir(base_dir) if f.endswith(".html") and f not in ("index.html", "mapa.html", "indigenas.html")]

for hf in html_files:
    fp = os.path.join(base_dir, hf)
    with open(fp, "r", encoding="utf-8") as f:
        content = f.read()

    # Nuevo bloque robusto para reaccionar y publicar comentarios usando .set con { merge: true }
    nuevo_bloque_js = """
        function reaccionar(tipo) {
            const reaccionActual = localStorage.getItem(`reaccion_${DOC_ID_ETNIA}`);
            const docRef = db.collection("reacciones_etnias").doc(DOC_ID_ETNIA);
            let payload = {};
            
            if (reaccionActual === tipo) {
                payload[tipo] = firebase.firestore.FieldValue.increment(-1);
                docRef.set(payload, { merge: true }).then(() => {
                    localStorage.removeItem(`reaccion_${DOC_ID_ETNIA}`);
                    const btn = document.getElementById(`btn-${tipo === 'likes' ? 'like' : 'sad'}`);
                    if (btn) btn.classList.remove('activo');
                });
            } else {
                payload[tipo] = firebase.firestore.FieldValue.increment(1);
                const btn = document.getElementById(`btn-${tipo === 'likes' ? 'like' : 'sad'}`);
                if (btn) btn.classList.add('activo');
                
                if (reaccionActual) {
                    payload[reaccionActual] = firebase.firestore.FieldValue.increment(-1);
                    const oldBtn = document.getElementById(`btn-${reaccionActual === 'likes' ? 'like' : 'sad'}`);
                    if (oldBtn) oldBtn.classList.remove('activo');
                }
                docRef.set(payload, { merge: true }).then(() => {
                    localStorage.setItem(`reaccion_${DOC_ID_ETNIA}`, tipo);
                });
            }
        }

        function publicarComentario() {
            const nomEl = document.getElementById('comentario-nombre');
            const texEl = document.getElementById('comentario-texto');
            if(!nomEl || !texEl) return;

            const nombre = nomEl.value.trim() || 'Anónimo';
            const texto = texEl.value.trim();
            if(texto === "") { alert("Por favor, escribe un comentario antes de publicar."); return; }

            const fechaStr = new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString();
            const nuevoComentario = { nombre: nombre, texto: texto, fecha: fechaStr };

            db.collection("reacciones_etnias").doc(DOC_ID_ETNIA).set({
                comentarios: firebase.firestore.FieldValue.arrayUnion(nuevoComentario)
            }, { merge: true }).then(() => {
                nomEl.value = "";
                texEl.value = "";
            }).catch(err => {
                alert("Error al enviar el comentario: " + err.message);
            });
        }
    """

    # Reemplazar las funciones viejas en el archivo HTML de la etnia
    # Buscamos desde function reaccionar hasta el final de publicarComentario
    patron = re.compile(r'function reaccionar\(tipo\).*?function renderizarComentarios', re.DOTALL)
    
    if patron.search(content):
        content = patron.sub(nuevo_bloque_js.strip() + "\n\n        function renderizarComentarios", content)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)

print("¡Las 36 páginas de etnias han sido actualizadas con el sistema de Firebase blindado!")
