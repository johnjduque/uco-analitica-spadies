@echo off
cd /d "%~dp0dist"
echo Iniciando prueba %date% %time% > "%~dp0prueba_exe_log.txt"
UcoAnalytics.exe >> "%~dp0prueba_exe_log.txt" 2>&1
echo Codigo de salida: %errorlevel% >> "%~dp0prueba_exe_log.txt"
