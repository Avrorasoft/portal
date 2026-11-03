import os

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    script_nuevo = """
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
    """

    if "toggleAudioInmersivo" not in code:
        if "</script>\n</body>" in code:
            code = code.replace("</script>\n</body>", script_nuevo + "\n</script>\n</body>")
        elif "</script>" in code:
            parts = code.rsplit("</script>", 1)
            code = parts[0] + script_nuevo + "\n</script>" + parts[1]

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)

print("¡Funciones inyectadas con éxito!")
