$ErrorActionPreference = "Stop"
Set-Location -Path "C:\Portal"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " 1. Sincronizando noticias (JSON + Firestore) y Open Graph " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
python "C:\Portal\sincronizar_noticias_og.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Fallo la sincronizacion en Python. Proceso detenido por seguridad." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " 2. Desplegando portal actualizado en Firebase Hosting     " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
firebase deploy --only hosting
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Fallo el despliegue en Firebase Hosting." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host " 3. Guardando respaldo en Git Local y Remoto (GitHub)      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
$cambios = git status --porcelain
if ($cambios) {
    $fecha = Get-Date -Format "yyyy-MM-dd HH:mm"
    git add -A
    git commit -m "Publicacion automatica CMS: Open Graph e inmersion 100% ($fecha)"
    git push origin main
    Write-Host "[OK] Respaldo subido exitosamente a Git local y remoto." -ForegroundColor Green
} else {
    Write-Host "[OK] No hubo archivos nuevos que registrar en Git." -ForegroundColor Yellow
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " PROCESO COMPLETADO AL 100%                               " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
