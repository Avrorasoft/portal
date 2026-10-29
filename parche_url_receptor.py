import os

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Script para leer el parámetro ?leer=ID en la URL y abrir el artículo automáticamente
    script_auto_abrir = """
    <script>
    window.addEventListener('DOMContentLoaded', function() {
        const urlParams = new URLSearchParams(window.location.search);
        const articuloId = urlParams.get('leer');
        if (articuloId && typeof abrirLectura === 'function') {
            // Dar un pequeño respiro para que cargue la estructura de artículos
            setTimeout(function() {
                abrirLectura(articuloId);
            }, 500);
        }
    });
    </script>
    """

    # Evitar duplicados limpiando versiones anteriores si existen
    import re
    code = re.sub(r'<script>\s*window\.addEventListener\(\'DOMContentLoaded\', function\(\) \{\s*const urlParams = new URLSearchParams\(window\.location\.search\);.*?</script>', '', code, flags=re.DOTALL)

    if "</body>" in code:
        code = code.replace("</body>", script_auto_abrir + "\n</body>")

    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(code)

print("¡Receptor de parámetros URL integrado en generar_html_estatico.py!")
