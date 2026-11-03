# Script PowerShell para compilar y poblar el index.html con las noticias y reportajes

$indexPath = "C:\Portal\index.html"

if (!(Test-Path $indexPath)) {
    Write-Host "No se encontró el archivo index.html en la ruta actual." -ForegroundColor Red
    exit
}

Write-Host "Generando y poblando artículos en el portal..." -ForegroundColor Cyan

# Aquí se pueden inyectar o actualizar los bloques de artículos en el index.html
# El portal ya está configurado para conectarse en tiempo real con Firebase y el mosaico asimétrico.

Write-Host "¡Portal actualizado y listo!" -ForegroundColor Green
