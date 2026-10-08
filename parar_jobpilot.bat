@echo off
chcp 65001 >nul
title JobPilot - Encerrador
color 0C

echo ======================================================
echo           ENCERRANDO SERVIDORES DO JOBPILOT
echo ======================================================
echo.

echo [1/2] Liberando porta 8001 (Backend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8001 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo [2/2] Liberando porta 3000 (Frontend)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ======================================================
echo   Todos os servidores do JobPilot foram desligados!
echo ======================================================
timeout /t 3 >nul
