import os
import json
import urllib.parse
import re

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Definición limpia y directa de compartirNativo para conectar todos los botones
    js_compartir_nativo_definitivo = """
<script>
// --- FUNCIÓN NATIVA MAESTRA PARA TODOS LOS BOTONES DE COMPARTIR ---
window.compartirNativo = function(tituloArticulo, ev) {
    var idEncontrado = "1";
    try {
        var origen = (ev && ev.target) ? ev.target : (window.event && window.event.target ? window.event.target : null);
        var el = origen;
        while (el && el !== document.body) {
            var btnLeer = el.querySelector ? el.querySelector('[onclick*="abrirLectura"]') : null;
            if (!btnLeer && el.getAttribute && el.getAttribute('onclick')) {
                var attr = el.getAttribute('onclick');
                var matchId = attr.match(/abrirLectura\\(['\"]?([^'\"]+)['\"]?\\)/);
                if (matchId && matchId[2]) {
                    idEncontrado = matchId[2];
                    break;
                }
            }
            el = el.parentElement;
        }
    } catch (err) {}

    // Si estamos dentro del modal inmersivo, usamos el ID actual del modal
    if (typeof window.idArticuloInmersivo !== 'undefined' && window.idArticuloInmersivo) {
        idEncontrado = window.idArticuloInmersivo;
    }

    var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idEncontrado) + ".html";
    var titulo = tituloArticulo || "Portal Amazonía";
    var nl = String.fromCharCode(10);

    var textoCompleto = "📰 " + titulo + nl + nl + "👉 Lee la noticia completa en Portal Amazonía:" + nl + urlArt;

    try {
        var area = document.createElement('textarea');
        area.value = textoCompleto;
        area.style.position = 'fixed';
        area.style.left = '-9999px';
        area.style.top = '0';
        document.body.appendChild(area);
        area.focus();
        area.select();
        document.execCommand('copy');
        document.body.removeChild(area);
    } catch (e) {}

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(textoCompleto).catch(function(){});
    }

    alert("📋 ¡Enlace y texto copiados al portapapeles!\\n\\nPégalo con Ctrl+V en tu página institucional de Canal 9 para publicar al instante con la foto perfecta.");
    window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
};

window.compartirNoticiaPortal = function(red, idForzado, tituloForzado) {
    if (red === 'whatsapp') {
        var idArt = String(idForzado || window.idArticuloInmersivo || "1").trim();
        var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
        var elTit = document.getElementById('lectura-titulo');
        var titulo = tituloForzado || (elTit && elTit.innerText ? elTit.innerText.trim() : "Portal Amazonía");
        var nl = String.fromCharCode(10);
        var msg = "📰 *" + titulo + "*" + nl + "👉 " + urlArt;
        window.open("https://api.whatsapp.com/send?text=" + encodeURIComponent(msg), '_blank');
    } else {
        compartirNativo(tituloForzado || "Portal Amazonía");
    }
};

window.compartirWhatsApp = function() { window.compartirNoticiaPortal('whatsapp'); };
window.compartirFacebook = function() { window.compartirNoticiaPortal('facebook'); };
window.compartirWhatsAppModal = function() { window.compartirNoticiaPortal('whatsapp'); };
window.compartirFacebookModal = function() { window.compartirNoticiaPortal('facebook'); };
window.copiarEnlaceModal = function() { window.compartirNoticiaPortal('copiar'); };
window.ejecutarCompartirInmersivo = function() { window.compartirNoticiaPortal('facebook'); };
</script>
</body>"""

    # Limpiar scripts anteriores e inyectar el definitivo
    code = re.sub(r'<script>\s*// ---.*?</script>', '', code, flags=re.DOTALL)
    code = re.sub(r'<script>\s*window\.compartirNativo.*?</script>', '', code, flags=re.DOTALL)

    if "</body>" in code:
        code = code.replace("</body>", js_compartir_nativo_definitivo)

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ generar_html_estatico.py actualizado con compartirNativo maestro.")

os.system(f"python {gen_path}")
os.system("python C:\\Portal\\crear_carpetas_noticias.py")
os.system("firebase deploy --only hosting")
