import os
import json
import urllib.parse
import re

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Sistema de copiado inteligente y apertura directa para la página institucional
    js_copiado_inteligente = """// --- SISTEMA DE COPIADO INTELIGENTE PARA CANAL 9 ---
window.compartirNoticiaPortal = function(red, idForzado, tituloForzado) {
    var idArt = String(idForzado || window.idArticuloInmersivo || "1").trim();
    var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
    var elTit = document.getElementById('lectura-titulo');
    var titulo = tituloForzado || (elTit && elTit.innerText ? elTit.innerText.trim() : "Portal Amazonía");
    var nl = String.fromCharCode(10);

    if (red === 'whatsapp') {
        var msg = "📰 *" + titulo + "*" + nl + "👉 " + urlArt;
        window.open("https://api.whatsapp.com/send?text=" + encodeURIComponent(msg), '_blank');
    } else {
        // Paquete completo de texto + enlace para que al pegar en Facebook salga perfecto
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

        if (typeof mostrarToast === 'function') {
            mostrarToast("📋 ¡Enlace copiado! Haz clic en tu página institucional y presiona Ctrl+V.");
        } else {
            alert("📋 ¡Contenido copiado al portapapeles!\n\nSe abrió tu página institucional: haz clic en '¿Qué estás pensando?' y presiona Ctrl+V para publicar.");
        }

        // Abrir la página de la institución o el creador de publicaciones directamente
        window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
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
        code = re.sub(patron_limpieza, js_copiado_inteligente, code, flags=re.DOTALL)
    else:
        code = code.replace("</body>", "<script>\n" + js_copiado_inteligente)

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ generar_html_estatico.py optimizado con copiado inteligente.")

os.system(f"python {gen_path}")
os.system("python C:\\Portal\\crear_carpetas_noticias.py")
os.system("firebase deploy --only hosting")
