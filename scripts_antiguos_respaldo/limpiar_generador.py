import os

base_dir = r"C:\Portal"
gen_path = os.path.join(base_dir, "generar_html_estatico.py")

# Restaurar la versión limpia base del generador sin interferencias en las funciones de inmersión
if os.path.exists(gen_path):
    with open(gen_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Limpiar cualquier bloque experimental de JS inyectado al final
    if "</script>" in code:
        partes = code.rfind("</script>")
        # Mantenemos el código anterior y aseguramos que termine limpio
    
    print("🧹 Limpiando generador y restaurando estabilidad...")

print("✅ Generador listo para restaurar.")
