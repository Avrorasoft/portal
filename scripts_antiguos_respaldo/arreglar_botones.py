import os
import json
import urllib.parse
import re

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Bloque JS limpio que se inyectará siempre antes de </body> en el index.html
    js_definitivo = """
<script>
// --- INTERCEPTOR GLOBAL Y SEGURO DE COMPARTIR ---
document.addEventListener('click', function(e) {
    var btn = e.target.closest('button, a');
    if (!btn) return;
    
    var txt = (btn.innerText || btn.textContent || "").toLowerCase();
    var esModal = btn.closest('.modal') || btn.closest('#modal-lectura') || btn.closest('.modal-inmersivo') || btn.closest('.acciones');
    if (!esModal) return;

    if (txt.includes("whatsapp") || txt.includes("facebook") || txt.includes("compartir") || txt.includes("copiar")) {
        e.preventDefault();
        e.stopPropagation();
        
        var idArt = String((typeof window.idArticuloInmersivo !== 'undefined' && window.idArticuloInmersivo) ? window.idArticuloInmersivo : (window.currentArticleId || "1")).trim();
        var urlArt = "https://portal-ia-web.web.app/noticias/articulo_" + encodeURIComponent(idArt) + ".html";
        var elTit = document.getElementById('lectura-titulo');
        var titulo = (elTit && elTit.innerText) ? elTit.innerText.trim() : "Portal Amazonía";
        var nl = String.fromCharCode(10);

        if (txt.includes("whatsapp")) {
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

            alert("📋 ¡Enlace copiado al portapapeles!\\n\\nPégalo con Ctrl+V en tu página institucional de Canal 9 para publicar al instante con la foto perfecta.");
            window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
        }
    }
}, true);
</script>
</body>"""

    # Limpiar scripts de compartir viejos repetidos
    code = re.sub(r'<script>\s*// --- INTERCEPTOR GLOBAL.*?</body>', '</body>', code, flags=re.DOTALL)
    code = re.sub(r'<script>\s*// --- SISTEMA DE COMPARTIR.*?</body>', '</body>', code, flags=re.DOTALL)

    if "</body>" in code:
        code = code.replace("</body>", js_definitivo)

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ generar_html_estatico.py actualizado permanentemente.")

os.system(f"python {gen_path}")
os.system("python C:\\Portal\\crear_carpetas_noticias.py")
os.system("firebase deploy --only hosting")
