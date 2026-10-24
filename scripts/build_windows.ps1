# ===================================================================
# Genera el ejecutable y el instalador de Windows de UCO Analytics.
# Uso: doble clic en scripts\generar_instalador.bat
#      (o en PowerShell, desde la raíz:  powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1)
# Requisitos: Python 3.11+, Node.js 20+ e Inno Setup 6 (si falta, se intenta instalar con winget).
# Registro completo: installer\build_log.txt
# ===================================================================
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Start-Transcript -Path "$root\installer\build_log.txt" -Force | Out-Null

function Step($msg) { Write-Host ""; Write-Host "=== $msg ===" -ForegroundColor Green }
function Fail($msg) { Write-Host "ERROR: $msg" -ForegroundColor Red; Stop-Transcript | Out-Null; exit 1 }
function Run($exe, [string[]]$argList) {
  & $exe @argList
  if ($LASTEXITCODE -ne 0) { Fail "Falló: $exe $($argList -join ' ') (código $LASTEXITCODE)" }
}

try {
  Step "0/6 Verificando herramientas"
  $py = $null
  foreach ($c in @("py", "python")) { if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break } }
  if (-not $py) { Fail "No se encontró Python. Instálelo desde https://www.python.org (marque 'Add to PATH')." }
  if ($py -eq "py") { & py -3 --version } else { & python --version }
  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { Fail "No se encontró Node.js/npm. Instálelo desde https://nodejs.org (versión LTS)." }
  node --version

  Step "1/6 Entorno virtual de Python"
  $venv = if (Test-Path "$root\.venv\Scripts\python.exe") { "$root\.venv" } else { "$root\backend\.venv" }
  if (-not (Test-Path "$venv\Scripts\python.exe")) {
    if ($py -eq "py") { Run "py" @("-3", "-m", "venv", $venv) } else { Run "python" @("-m", "venv", $venv) }
  }
  $vpy = "$venv\Scripts\python.exe"
  Write-Host "Usando $vpy"
  Run $vpy @("-m", "pip", "install", "--upgrade", "pip")
  Run $vpy @("-m", "pip", "install", "-r", "$root\backend\requirements-dev.txt")

  Step "2/6 Compilando el frontend"
  Push-Location "$root\frontend"
  Run "npm.cmd" @("ci", "--no-audit", "--no-fund")
  Run "npm.cmd" @("run", "build")
  Pop-Location

  Step "3/6 Ejecutando pruebas automáticas"
  Push-Location "$root\backend"
  if (Test-Path "$root\Datos_UCO\Indicadores") { $env:UCO_DATOS_DIR = "$root\Datos_UCO"; Write-Host "Incluye validación contra SPADIES con Datos_UCO" }
  Run $vpy @("-m", "unittest", "discover", "-s", "tests", "-v")
  Remove-Item Env:\UCO_DATOS_DIR -ErrorAction SilentlyContinue
  Pop-Location

  Step "4/6 Empaquetando el ejecutable (PyInstaller)"
  Push-Location "$root\installer"
  Run $vpy @("-m", "PyInstaller", "main.spec", "--noconfirm", "--clean")
  if (-not (Test-Path "$root\installer\dist\UcoAnalytics.exe")) { Fail "No se generó installer\dist\UcoAnalytics.exe" }
  Pop-Location

  Step "5/6 Buscando Inno Setup"
  $iscc = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
  ) | Where-Object { Test-Path $_ } | Select-Object -First 1
  if (-not $iscc -and (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "Inno Setup no está instalado. Instalando con winget..."
    & winget install --id JRSoftware.InnoSetup -e --silent --accept-package-agreements --accept-source-agreements
    $iscc = @(
      "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
      "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
      "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
  }
  if (-not $iscc) { Fail "No se encontró Inno Setup 6. Instálelo desde https://jrsoftware.org/isdl.php y ejecute de nuevo." }
  Write-Host "Usando $iscc"

  Step "6/6 Generando el instalador"
  Push-Location "$root\installer"
  Run $iscc @("setup_installer.iss")
  Pop-Location

  $out = Get-ChildItem "$root\installer\Output\Setup_UCO_Analytics_*.exe" | Select-Object -First 1
  Write-Host ""
  Write-Host "LISTO: $($out.FullName)  ($([math]::Round($out.Length/1MB,1)) MB)" -ForegroundColor Green
  Write-Host "Ejecutable portable: $root\installer\dist\UcoAnalytics.exe"
}
catch {
  Fail $_.Exception.Message
}
Stop-Transcript | Out-Null
exit 0
