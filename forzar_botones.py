import os
import json
import urllib.parse
import re

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Inyección directa de la función onclick para asegurar respuesta inmediata
    js_onclick_directo = """
<script>
// --- FUNCIÓN DIRECTA DE COMPARTIR PARA LOS BOTONES ---
window.compartirPortalDirecto = function(red) {
    var idArt = String((typeof window.idArticuloInmersivo !== 'undefined' && window.idArticuloInmersivo) ? window.idArticuloInmersivo : "1").trim();
    var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
    var elTit = document.getElementById('lectura-titulo');
    var titulo = (elTit && elTit.innerText) ? elTit.innerText.trim() : "Portal Amazonía";
    var nl = String.fromCharCode(10);

    if (red === 'whatsapp') {
        var msg = "📰 *" + titulo + "*" + nl + "👉 " + urlArt;
        window.open("https://api.whatsapp.com/send?text=" + encodeURIComponent(msg), '_blank');
    } else {
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
        } catch (err) {}

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(textoCompleto).catch(function(){});
        }

        alert("📋 ¡Enlace copiado al portapapeles!\\n\\nPégalo con Ctrl+V en tu página institucional de Canal 9.");
        window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
    }
};

// Forzar la conexión de los botones en el modal dinámicamente al abrirse
document.addEventListener('DOMContentLoaded', function() {
    setInterval(function() {
        var botones = document.querySelectorAll('button, a');
        botones.forEach(function(btn) {
            var txt = (btn.innerText || btn.textContent || "").toLowerCase();
            if ((txt.includes("facebook") || txt.includes("whatsapp") || txt.includes("compartir")) && !btn.getAttribute('data-conectado')) {
                btn.setAttribute('data-conectado', 'true');
                btn.style.cursor = 'pointer';
                btn.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    if (txt.includes("whatsapp")) {
                        window.compartirPortalDirecto('whatsapp');
                    } else {
                        window.compartirPortalDirecto('facebook');
                    }
                };
            }
        });
    }, 1000);
});
</script>
</body>"""

    # Limpiar scripts anteriores y agregar el nuevo
    code = re.sub(r'<script>\s*// --- (INTERCEPTOR|SISTEMA).*?</body>', '</body>', code, flags=re.DOTALL)
    if "</body>" in code:
        code = code.replace("</body>", js_onclick_directo)

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ generar_html_estatico.py actualizado con vinculación directa de botones.")

os.system(f"python {gen_path}")
os.system("python C:\\Portal\\crear_carpetas_noticias.py")
os.system("firebase deploy --only hosting")
