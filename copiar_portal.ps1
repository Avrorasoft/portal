$origen = "F:\AMAZONIA-PORTAL"
$destino = "C:\amazoniahoy.org"

if (Test-Path $origen) {
    Write-Host "Copiando archivos y carpetas desde $origen a $destino..." -ForegroundColor Cyan
    Copy-Item -Path "$origen\*" -Destination $destino -Recurse -Force
    Write-Host "¡Copia completada con éxito!" -ForegroundColor Green
} else {
    Write-Host "No se encuentra la ruta de origen: $origen. Verifica que el disco o carpeta estén accesibles." -ForegroundColor Red
}
