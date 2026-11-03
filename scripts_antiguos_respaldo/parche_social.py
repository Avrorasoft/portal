import os

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # HTML actualizado para los botones de compartir (WhatsApp, Facebook y Copiar)
    new_btns_container = '''<div style="margin-top: 30px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                    <button class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: #25D366; color: white; font-weight: bold; border-radius: 4px; border: none; cursor: pointer;" onclick="compartirWhatsApp()">💬 WhatsApp</button>
                    <button class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: #1877F2; color: white; font-weight: bold; border-radius: 4px; border: none; cursor: pointer;" onclick="compartirFacebook()">📘 Facebook</button>
                    <button class="btn-compartir-tarjeta" style="padding: 12px 20px; font-size: 15px; background: var(--accent-gold); color: black; font-weight: bold; border-radius: 4px; border: none; cursor: pointer;" onclick="ejecutarCompartirInmersivo()">🔗 Copiar Enlace</button>
                    <button id="btn-audio-inmersivo" class="btn-audio" style="padding: 12px 20px; font-size: 15px; background: transparent; color: var(--accent-gold); border: 1px solid var(--accent-gold); font-weight: bold; border-radius: 4px; cursor: pointer;" onclick="toggleAudioInmersivo()">🔊 Escuchar Artículo</button>
                </div>'''

    # Reemplazar el contenedor viejo de botones de compartir por este nuevo con redes sociales
    import re
    code = re.sub(r'<div style="margin-top: 30px; display: flex;.*?<\/div>', new_btns_container, code, flags=re.DOTALL)

    # Funciones JavaScript para WhatsApp, Facebook y Copiar
    script_social = """
    <script>
    window.compartirWhatsApp = function() {
        const titulo = document.getElementById('lectura-titulo') ? document.getElementById('lectura-titulo').innerText : "Portal Amazonía";
        const idArt = typeof articuloActivoId !== 'undefined' && articuloActivoId ? articuloActivoId : "";
        const urlActual = window.location.origin + window.location.pathname + (idArt ? "?leer=" + idArt : "");
        const texto = encodeURIComponent(titulo + " - " + urlActual);
        window.open("https://api.whatsapp.com/send?text=" + texto, "_blank");
    };

    window.compartirFacebook = function() {
        const idArt = typeof articuloActivoId !== 'undefined' && articuloActivoId ? articuloActivoId : "";
        const urlActual = window.location.origin + window.location.pathname + (idArt ? "?leer=" + idArt : "");
        const urlEnc = encodeURIComponent(urlActual);
        window.open("https://www.facebook.com/sharer/sharer.php?u=" + urlEnc, "_blank");
    };

    window.ejecutarCompartirInmersivo = function() {
        const idArt = typeof articuloActivoId !== 'undefined' ? articuloActivoId : "";
        const urlActual = window.location.origin + window.location.pathname + (idArt ? "?leer=" + idArt : "");
        
        if (navigator.share) {
            navigator.share({ title: 'Portal Amazonía', url: urlActual }).catch(() => {});
        } else if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(urlActual).then(() => {
                alert("¡Enlace copiado al portapapeles!");
            });
        } else {
            prompt("Copia este enlace:", urlActual);
        }
    };
    </script>
    """

    # Limpiar scripts sociales anteriores si existen
    code = re.sub(r'<script>\s*window\.compartirWhatsApp =.*?</script>', '', code, flags=re.DOTALL)

    if "</body>" in code:
        code = code.replace("</body>", script_social + "\n</body>")

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)

print("¡Generador actualizado con botones directos de WhatsApp y Facebook!")
