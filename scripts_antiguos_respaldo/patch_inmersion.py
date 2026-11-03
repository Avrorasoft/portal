import os
import re

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Asegurar que el botón de audio esté en el HTML del modal inmersivo
    old_modal_header = '<h1 id="lectura-titulo"></h1>\n            <span id="lectura-fuente" class="lectura-fuente"></span>'
    new_modal_header = '<h1 id="lectura-titulo"></h1>\n            <span id="lectura-fuente" class="lectura-fuente"></span>\n            <button id="btn-audio-inmersivo" class="btn-audio" onclick="toggleAudioInmersivo()">🔊 Escuchar Artículo</button>'
    
    if old_modal_header in content and "btn-audio-inmersivo" not in content:
        content = content.replace(old_modal_header, new_modal_header, 1)

    # 2. Agregar las funciones de JavaScript para el audio inmersivo y compartir robusto
    js_funciones_nuevas = """
    let reproduciendoInmersivo = false;
    const sintesisInmersivo = window.speechSynthesis;
    let mensajeInmersivo = null;

    function toggleAudioInmersivo() {
        const btn = document.getElementById('btn-audio-inmersivo');
        if (reproduciendoInmersivo) {
            sintesisInmersivo.cancel();
            reproduciendoInmersivo = false;
            if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
        } else {
            const textoEl = document.getElementById('lectura-texto');
            const tituloEl = document.getElementById('lectura-titulo');
            const textoCompleto = (tituloEl ? tituloEl.innerText + ". " : "") + (textoEl ? textoEl.innerText : "");
            
            mensajeInmersivo = new SpeechSynthesisUtterance(textoCompleto);
            mensajeInmersivo.lang = 'es-ES';
            mensajeInmersivo.onend = function() {
                reproduciendoInmersivo = false;
                if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
            };
            sintesisInmersivo.speak(mensajeInmersivo);
            reproduciendoInmersivo = true;
            if(btn) { btn.classList.add('reproduciendo'); btn.innerHTML = '⏸️ Detener Lectura'; }
        }
    }

    function ejecutarCompartirInmersivo() {
        const titulo = document.getElementById('lectura-titulo').innerText;
        const urlActual = window.location.origin + window.location.pathname + "?leer=" + articuloActivoId;
        if (navigator.share) {
            navigator.share({ title: titulo, url: urlActual }).catch(() => {});
        } else {
            navigator.clipboard.writeText(urlActual).then(() => {
                alert("¡Enlace del artículo copiado al portapapeles!");
            }).catch(() => {
                alert("Enlace: " + urlActual);
            });
        }
    }
    
    // Detener audio al cerrar o salir
    const cerrarLecturaOriginal = window.cerrarLectura;
    window.cerrarLectura = function() {
        if(sintesisInmersivo) sintesisInmersivo.cancel();
        reproduciendoInmersivo = false;
        const btn = document.getElementById('btn-audio-inmersivo');
        if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
        if(typeof cerrarLecturaOriginal === 'function') cerrarLecturaOriginal();
        else {
            document.getElementById('modal-lectura').style.display = 'none';
            document.body.style.overflow = 'auto';
            articuloActivoId = null;
        }
    };
    """

    if "toggleAudioInmersivo" not in content:
        # Insertar antes del cierre del script principal
        content = content.replace("</script>\n</body>", js_funciones_nuevas + "\n</script>\n</body>")

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(content)

print("¡generar_html_estatico.py actualizado con éxito!")
