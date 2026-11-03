import os

path = r"C:\Portal\index.html"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    script_interactivo = """
    <script>
    let articuloActivoId = null;

    function abrirLectura(id) {
        const card = document.getElementById('card-' + id);
        if (!card) return;
        articuloActivoId = id;
        
        const titulo = document.getElementById('titulo-' + id) ? document.getElementById('titulo-' + id).innerText : '';
        const resumen = document.getElementById('resumen-' + id) ? document.getElementById('resumen-' + id).innerText : '';
        const img = document.getElementById('img-' + id) ? document.getElementById('img-' + id).src : 'images/default.jpg';
        const fecha = document.getElementById('fecha-' + id) ? document.getElementById('fecha-' + id).innerText : '';
        const badge = document.getElementById('badge-' + id) ? document.getElementById('badge-' + id).innerText : 'NOTICIA';

        let modal = document.getElementById('modal-lectura');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'modal-lectura';
            modal.style.cssText = 'display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.95); z-index:1000; overflow-y:auto; padding:40px 20px;';
            modal.innerHTML = `
                <div class="lectura-box" style="max-width:900px; margin:0 auto; background:#121212; padding:40px; border-radius:8px; border:1px solid #333; position:relative;">
                    <button onclick="cerrarLectura()" style="position:absolute; top:20px; right:20px; background:#222; color:white; border:none; padding:10px 15px; border-radius:4px; cursor:pointer; font-weight:bold;">✕ Cerrar</button>
                    <div style="margin-bottom:25px;"><img id="lectura-img" src="" style="width:100%; max-height:450px; object-fit:contain; background:#000; border-radius:6px;"></div>
                    <span id="lectura-categoria" class="badge"></span>
                    <span id="lectura-fecha" class="fecha-tarjeta"></span>
                    <h1 id="lectura-titulo" style="font-size:30px; font-weight:800; color:white; margin-bottom:15px; line-height:1.3;"></h1>
                    <div id="lectura-texto" style="font-size:17px; line-height:1.8; color:#ddd; margin-bottom:30px; white-space:pre-wrap;"></div>
                    <div style="display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
                        <button class="btn-compartir-tarjeta" style="background:#25D366; color:white; padding:12px 20px; border:none; border-radius:4px; cursor:pointer; font-weight:bold;" onclick="compartirWhatsApp()">💬 WhatsApp</button>
                        <button class="btn-compartir-tarjeta" style="background:#1877F2; color:white; padding:12px 20px; border:none; border-radius:4px; cursor:pointer; font-weight:bold;" onclick="compartirFacebook()">📘 Facebook</button>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        document.getElementById('lectura-img').src = img;
        document.getElementById('lectura-categoria').innerText = badge;
        document.getElementById('lectura-fecha').innerText = fecha;
        document.getElementById('lectura-titulo').innerText = titulo;
        document.getElementById('lectura-texto').innerText = resumen;

        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function cerrarLectura() {
        const modal = document.getElementById('modal-lectura');
        if (modal) modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        articuloActivoId = null;
    }

    window.compartirNativo = function(t, ev) {
        let idArt = '1';
        try {
            if (ev && ev.target) {
                let btn = ev.target.closest('button');
                if (btn && btn.id && btn.id.startsWith('share-')) {
                    idArt = btn.id.replace('share-', '');
                }
            }
        } catch(err) {}
        const urlArt = 'https://portal-ia-web.web.app/noticias/articulo_' + encodeURIComponent(idArt) + '.html';
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(urlArt).catch(() => {});
        }
        const fbWin = window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
        if (!fbWin || fbWin.closed || typeof fbWin.closed == 'undefined') {
            alert('Enlace copiado al portapapeles. Pégalo directamente en tu página de Facebook.');
        }
    };

    window.compartirWhatsApp = function() {
        const titulo = document.getElementById('lectura-titulo') ? document.getElementById('lectura-titulo').innerText : 'Portal Amazonía';
        const idArt = articuloActivoId || '1';
        const urlArt = 'https://portal-ia-web.web.app/noticias/articulo_' + encodeURIComponent(idArt) + '.html';
        const texto = encodeURIComponent('📰 *' + titulo + '*\n\n👉 ' + urlArt);
        window.open('https://api.whatsapp.com/send?text=' + texto, '_blank');
    };

    window.compartirFacebook = function() {
        const idArt = articuloActivoId || '1';
        const urlArt = 'https://portal-ia-web.web.app/noticias/articulo_' + encodeURIComponent(idArt) + '.html';
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(urlArt).catch(() => {});
        }
        window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(urlArt), '_blank', 'width=650,height=600');
    };

    function reaccionar(id, tipo) {
        const span = document.getElementById(tipo + '-' + id);
        if (span) {
            let actual = parseInt(span.innerText) || 0;
            span.innerText = actual + 1;
            localStorage.setItem('reaccion_' + id, tipo);
        }
    }

    function scrollToFooter() {
        const footer = document.getElementById('portal-footer') || document.querySelector('footer');
        if (footer) footer.scrollIntoView({ behavior: 'smooth' });
    }
    </script>
    """

    if "function abrirLectura" not in html:
        html = html.replace("</body>", script_interactivo + "\n</body>")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print("¡Script interactivo inyectado con éxito en el index.html!")
    else:
        print("El script ya estaba presente en index.html.")
else:
    print("No se encontró index.html")
