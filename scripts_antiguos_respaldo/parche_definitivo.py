import os

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # 1. Asegurar que los botones existan juntos en el HTML del modal de lectura inmersiva
    old_btn_share = '<button class="btn-compartir-tarjeta" style="width: 100%; max-width: 300px; padding: 15px; font-size: 18px; background: var(--accent-gold); color: black; font-weight: bold;" onclick="ejecutarCompartirInmersivo()">🔗 Compartir Artículo</button>'
    
    new_btns_container = '''<div style="margin-top: 30px; display: flex; gap: 15px; justify-content: center; flex-wrap: wrap;">
                    <button class="btn-compartir-tarjeta" style="padding: 12px 25px; font-size: 16px; background: var(--accent-gold); color: black; font-weight: bold; border-radius: 4px; border: none; cursor: pointer;" onclick="ejecutarCompartirInmersivo()">🔗 Compartir Artículo</button>
                    <button id="btn-audio-inmersivo" class="btn-audio" style="padding: 12px 25px; font-size: 16px; background: transparent; color: var(--accent-gold); border: 1px solid var(--accent-gold); font-weight: bold; border-radius: 4px; cursor: pointer;" onclick="toggleAudioInmersivo()">🔊 Escuchar Artículo</button>
                </div>'''

    if old_btn_share in code:
        code = code.replace(old_btn_share, new_btns_container)

    # 2. Agregar las funciones de JavaScript de forma robusta al final del script
    js_funcionalidades = """
    let reproduciendoInmersivo = false;

    function toggleAudioInmersivo() {
        const btn = document.getElementById('btn-audio-inmersivo');
        const sintesis = window.speechSynthesis;
        
        if (!sintesis) {
            alert("Tu navegador no soporta lectura por voz.");
            return;
        }

        if (reproduciendoInmersivo) {
            sintesis.cancel();
            reproduciendoInmersivo = false;
            if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
        } else {
            sintesis.cancel();
            const textoEl = document.getElementById('lectura-texto');
            const tituloEl = document.getElementById('lectura-titulo');
            const textoCompleto = (tituloEl ? tituloEl.innerText + ". " : "") + (textoEl ? textoEl.innerText : "");
            
            const mensaje = new SpeechSynthesisUtterance(textoCompleto);
            mensaje.lang = 'es-ES';
            
            mensaje.onstart = function() {
                reproduciendoInmersivo = true;
                if(btn) { btn.classList.add('reproduciendo'); btn.innerHTML = '⏸️ Detener Lectura'; }
            };
            
            mensaje.onend = function() {
                reproduciendoInmersivo = false;
                if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
            };
            
            mensaje.onerror = function() {
                reproduciendoInmersivo = false;
                if(btn) { btn.classList.remove('reproduciendo'); btn.innerHTML = '🔊 Escuchar Artículo'; }
            };

            sintesis.speak(mensaje);
        }
    }

    function ejecutarCompartirInmersivo() {
        const urlActual = window.location.origin + window.location.pathname + "?leer=" + articuloActivoId;
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(urlActual).then(() => {
                alert("¡Enlace copiado al portapapeles! Ya puedes compartirlo.");
            }).catch(() => {
                prompt("Copia este enlace para compartir:", urlActual);
            });
        } else {
            prompt("Copia este enlace para compartir:", urlActual);
        }
    }

    // Detener la voz si se cierra el modal
    const cerrarLecturaOriginal = window.cerrarLectura;
    window.cerrarLectura = function() {
        if(window.speechSynthesis) window.speechSynthesis.cancel();
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

    if "toggleAudioInmersivo" not in code:
        code = code.replace("</script>\n</body>", js_funcionalidades + "\n</script>\n</body>")

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)

print("¡generar_html_estatico.py reparado exitosamente!")
