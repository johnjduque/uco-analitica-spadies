# Elimina archivos de la versión anterior que ya no se usan (código legado y artefactos).
# Ejecutar UNA vez desde la raíz del proyecto:  .\scripts\limpiar_archivos_obsoletos.ps1
$root = Split-Path -Parent $PSScriptRoot
$obsoletos = @(
  "backend\app\auth.py", "backend\app\seed.py", "backend\app\schemas.py", "backend\app\ingestion.py",
  "backend\app\database.py", "backend\app\analytics_engine.py", "backend\app\program_codes.py",
  "backend\app\services\load_service.py", "backend\app\services\analytics_service.py",
  "backend\app\routers\analytics.py",
  "frontend\src\assets\hero.png", "frontend\src\assets\react.svg", "frontend\src\assets\vite.svg",
  "frontend\README.md"
)
foreach ($f in $obsoletos) {
  $p = Join-Path $root $f
  if (Test-Path $p) { Remove-Item $p -Force; Write-Host "Eliminado: $f" }
}
# Artefactos de compilación antiguos (se regeneran con scripts\build_windows.ps1)
foreach ($d in @("build_temp", "dist", "backend\user_uploads")) {
  $p = Join-Path $root $d
  if (Test-Path $p) { Remove-Item $p -Recurse -Force; Write-Host "Eliminada carpeta: $d" }
}
Get-ChildItem -Path $root -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Write-Host "Limpieza completada." -ForegroundColor Green
