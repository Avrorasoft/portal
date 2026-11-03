import os
import re

base_dir = r"C:\Portal"

# 1. CORREGIR EL GENERADOR DE INDEX.HTML (NOMBRE "AMAZONÍA" Y 5 LINKS LIMPIOS)
gen_path = os.path.join(base_dir, "generar_html_estatico.py")
if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    content = content.replace("PORTAL AMAZONÍA HOY", "PORTAL AMAZONÍA")
    content = content.replace("Portal Amazonía Hoy", "Portal Amazonía")
    
    # Nav limpio de 5 enlaces
    nav_index = """<nav>
    <a href="#" class="nav-brand">
        <img src="images/logo1.png" alt="Logo" onerror="this.style.display='none'">
        AMAZONÍA
    </a>
    <div class="nav-links-container">
        <a href="#hero">Inicio</a>
        <a href="#mosaico">Noticias</a>
        <a href="indigenas.html">Mapa Indígena</a>
        <a href="#turismo">Turismo</a>
        <a href="#economia">Economía</a>
    </div>
</nav>"""
    content = re.sub(r'(?s)<nav>.*?</nav>', nav_index, content)
    
    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(content)

# 2. CORREGIR INDIGENAS.HTML (ELIMINAR DUPLICACIÓN Y DEJAR 5 LINKS)
mapa_path = os.path.join(base_dir, "indigenas.html")
if os.path.exists(mapa_path):
    with open(mapa_path, "r", encoding="utf-8") as f:
        m_content = f.read()
    
    nav_mapa = """    <nav>
        <a href="index.html" class="nav-brand">
            <img src="images/logo1.png" alt="Logo" style="height: 35px;" onerror="this.style.display='none'">
            AMAZONÍA
        </a>
        <div class="nav-links-container">
            <a href="index.html">Inicio</a>
            <a href="index.html#mosaico">Noticias</a>
            <a href="indigenas.html" style="color: var(--accent-gold);">Mapa Indígena</a>
            <a href="index.html#turismo">Turismo</a>
            <a href="index.html#economia">Economía</a>
        </div>
    </nav>"""
    
    # Reemplazar cualquier <nav> existente por este limpio
    m_content = re.sub(r'(?s)<nav>.*?</nav>', nav_mapa, m_content)
    
    # Asegurar diseño CSS estables para el mapa
    if "height: 100vh;" not in m_content:
        m_content = m_content.replace("height: 100vh;", "height: calc(100vh - 60px);")

    with open(mapa_path, "w", encoding="utf-8") as f:
        f.write(m_content)

print("¡Estructuras de navegación y títulos corregidos sin tocar las 36 páginas!")
