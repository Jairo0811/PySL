$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$ExecutablePath = Join-Path $ProjectRoot "dist\PySL\PySL.exe"

Set-Location $ProjectRoot

if (-not (Test-Path $PythonPath)) {
    throw "No se encontró .venv. Créalo con: py -3.13 -m venv .venv"
}

Write-Host "Preparando PySL con $(& $PythonPath --version)..."

& $PythonPath -m pip install -e ".[dev,build]"
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron instalar las dependencias."
}

Write-Host "Ejecutando pruebas automatizadas..."
& $PythonPath -m pytest
if ($LASTEXITCODE -ne 0) {
    throw "Las pruebas fallaron. Se canceló la compilación."
}

Write-Host "Validando el código fuente..."
& $PythonPath -m compileall -q src
if ($LASTEXITCODE -ne 0) {
    throw "Se detectaron errores de sintaxis."
}

Write-Host "Generando el ejecutable de Windows..."
& $PythonPath -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name "PySL" `
    --icon "assets\pysl-logo.ico" `
    --add-data "assets;assets" `
    --add-data "data;data" `
    --add-data "legacy;legacy" `
    "src\pysl\app.py"

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller no pudo generar el ejecutable."
}

if (-not (Test-Path $ExecutablePath)) {
    throw "La compilación terminó, pero no se encontró: $ExecutablePath"
}

Write-Host ""
Write-Host "Compilación completada correctamente." -ForegroundColor Green
Write-Host "Ejecutable: $ExecutablePath"
