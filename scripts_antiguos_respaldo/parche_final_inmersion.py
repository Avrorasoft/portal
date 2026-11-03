import os

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Nuevas funciones robustas para audio y compartir
    nuevas_funciones = """
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
        const titulo = document.getElementById('lectura-titulo').innerText;
        const urlActual = window.location.origin + window.location.pathname + (window.location.search ? window.location.search : "");
        
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(urlActual).then(() => {
                alert("¡Enlace copiado al portapapeles para compartir!");
            }).catch(() => {
                prompt("Copia este enlace:", urlActual);
            });
        } else {
            prompt("Copia este enlace:", urlActual);
        }
    }
    
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

    # Reemplazar las funciones viejas de inmersión si ya existen, o agregarlas
    if "toggleAudioInmersivo" in content:
        # Limpiar bloque anterior para actualizarlo
        import re
        content = re.sub(r'let reproduciendoInmersivo =.*?(?=function abrirLectura|\n\s*\n\s*</script>)', nuevas_funciones.strip() + "\n\n", content, flags=re.DOTALL)
    else:
        content = content.replace("</script>\n</body>", nuevas_funciones + "\n</script>\n</body>")

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(content)

print("¡Parche aplicado con éxito en generar_html_estatico.py!")
