import os
import json
import urllib.parse
import re

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Sistema de diálogo oficial de Facebook optimizado para evitar bloqueos institucionales
    js_dialogo_oficial = """// --- SISTEMA DE COMPARTIR OFICIAL PROFESIONAL ---
window.compartirNoticiaPortal = function(red, idForzado, tituloForzado) {
    var idArt = String(idForzado || window.idArticuloInmersivo || "1").trim();
    var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
    var nl = String.fromCharCode(10);

    if (red === 'whatsapp') {
        var elTit = document.getElementById('lectura-titulo');
        var titulo = tituloForzado || (elTit && elTit.innerText ? elTit.innerText.trim() : "Portal Amazonía");
        var msg = "📰 *" + titulo + "*" + nl + "👉 " + urlArt;
        window.open("https://api.whatsapp.com/send?text=" + encodeURIComponent(msg), '_blank');
    } else {
        // Uso del diálogo oficial de Meta para compartir URL directamente de forma nativa
        var fbUrl = "https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt) + "&display=popup";
        var w = 650, h = 600;
        var y = window.top.outerHeight / 2 + window.top.screenY - (h / 2);
        var x = window.top.outerWidth / 2 + window.top.screenX - (w / 2);
        window.open(fbUrl, 'Compartir en Facebook', 'toolbar=no, location=no, directories=no, status=no, menubar=no, scrollbars=yes, resizable=yes, copyhistory=no, width=' + w + ', height=' + h + ', top=' + y + ', left=' + x);
    }
};

window.compartirDesdeTarjetaIndex = function(t, ev) {
    var idEncontrado = "";
    try {
        var origen = (ev && ev.target) ? ev.target : (window.event && window.event.target ? window.event.target : null);
        var el = origen;
        while (el && el !== document.body) {
            var btnLeer = el.querySelector ? el.querySelector('[onclick*="abrirLectura"]') : null;
            if (btnLeer) {
                var attr = btnLeer.getAttribute('onclick') || "";
                var partes = attr.split("'");
                if (partes.length >= 2) {
                    idEncontrado = partes[1];
                    break;
                }
            }
            el = el.parentElement;
        }
    } catch (err) {}
    window.compartirNoticiaPortal('facebook', idEncontrado || "1", t || "");
};

window.compartirWhatsApp = function() { window.compartirNoticiaPortal('whatsapp'); };
window.compartirFacebook = function() { window.compartirNoticiaPortal('facebook'); };
window.compartirWhatsAppModal = function() { window.compartirNoticiaPortal('whatsapp'); };
window.compartirFacebookModal = function() { window.compartirNoticiaPortal('facebook'); };
window.copiarEnlaceModal = function() { window.compartirNoticiaPortal('copiar'); };
window.ejecutarCompartirInmersivo = function() { window.compartirNoticiaPortal('facebook'); };

window.addEventListener('load', function() {
    var params = new URLSearchParams(window.location.search);
    var idUrl = params.get('id') || params.get('articulo');
    if (idUrl && typeof abrirLectura === 'function') {
        setTimeout(function() {
            abrirLectura(idUrl);
        }, 150);
    }
});
</script>
</body>"""

    patron_limpieza = r'(?:window\.compartirNoticiaPortal\s*=\s*function|// --- SISTEMA DE COMPARTIR).*?</body>'
    if re.search(patron_limpieza, code, flags=re.DOTALL):
        code = re.sub(patron_limpieza, js_dialogo_oficial, code, flags=re.DOTALL)
    else:
        code = code.replace("</body>", "<script>\n" + js_dialogo_oficial)

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ generar_html_estatico.py restaurado con el diálogo web oficial.")

os.system(f"python {gen_path}")
os.system("python C:\\Portal\\crear_carpetas_noticias.py")
os.system("firebase deploy --only hosting")
