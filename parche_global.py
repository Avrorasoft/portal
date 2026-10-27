import os

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Bloque definitivo de JavaScript y control global para el modal inmersivo
    script_definitivo = """
    <script>
    window.reproduciendoInmersivo = false;

    window.toggleAudioInmersivo = function() {
        const btn = document.getElementById('btn-audio-inmersivo');
        const sintesis = window.speechSynthesis;
        
        if (!sintesis) {
            alert("Tu navegador no soporta lectura por voz.");
            return;
        }

        if (window.reproduciendoInmersivo) {
            sintesis.cancel();
            window.reproduciendoInmersivo = false;
            if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
        } else {
            sintesis.cancel();
            const textoEl = document.getElementById('lectura-texto');
            const tituloEl = document.getElementById('lectura-titulo');
            const textoCompleto = (tituloEl ? tituloEl.innerText + ". " : "") + (textoEl ? textoEl.innerText : "");
            
            if (!textoCompleto.trim()) {
                alert("No hay texto para leer en este artículo.");
                return;
            }

            const mensaje = new SpeechSynthesisUtterance(textoCompleto);
            mensaje.lang = 'es-ES';
            
            mensaje.onstart = function() {
                window.reproduciendoInmersivo = true;
                if(btn) { btn.classList.add('reproduciendo'); btn.innerHTML = '⏸️ Detener Lectura'; }
            };
            
            mensaje.onend = function() {
                window.reproduciendoInmersivo = false;
                if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
            };
            
            mensaje.onerror = function() {
                window.reproduciendoInmersivo = false;
                if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
            };

            sintesis.speak(mensaje);
        }
    };

    window.ejecutarCompartirInmersivo = function() {
        const idArt = typeof articuloActivoId !== 'undefined' ? articuloActivoId : "";
        const urlActual = window.location.origin + window.location.pathname + (idArt ? "?leer=" + idArt : "");
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(urlActual).then(() => {
                alert("¡Enlace copiado al portapapeles! Ya puedes compartirlo.");
            }).catch(() => {
                prompt("Copia este enlace para compartir:", urlActual);
            });
        } else {
            prompt("Copia este enlace para compartir:", urlActual);
        }
    };

    // Asegurar limpieza de audio al cerrar modal
    const cerrarOriginal = window.cerrarLectura;
    window.cerrarLectura = function() {
        if(window.speechSynthesis) window.speechSynthesis.cancel();
        window.reproduciendoInmersivo = false;
        const btn = document.getElementById('btn-audio-inmersivo');
        if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
        if(typeof cerrarOriginal === 'function') cerrarOriginal();
        else {
            const modal = document.getElementById('modal-lectura');
            if(modal) modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    };
    </script>
    """

    # Limpiar cualquier bloque previo idéntico para evitar duplicaciones
    if "<script>" in code and "window.toggleAudioInmersivo" in code:
        import re
        code = re.sub(r'<script>\s*window\.reproduciendoInmersivo =.*?</script>', '', code, flags=re.DOTALL)

    # Inyectar las funciones antes del cierre del body
    if "</body>" in code:
        code = code.replace("</body>", script_definitivo + "\n</body>")

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)

print("¡Generador actualizado con funciones globales definitivas!")
