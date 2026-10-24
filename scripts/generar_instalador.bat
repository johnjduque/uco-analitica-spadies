@echo off
chcp 65001 >nul
title UCO Analytics - Generar instalador
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_windows.ps1"
if errorlevel 1 (echo. & echo *** La generacion fallo. Revise installer\build_log.txt ***) else (echo. & echo *** Instalador generado en installer\Output ***)
echo.
pause
