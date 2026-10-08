@echo off
chcp 65001 >nul
title JobPilot - Inicializador
color 0A

echo ======================================================
echo           INICIANDO JOBPILOT - 1 CLIQUE
echo ======================================================
echo.

set PROJECT_DIR=C:\Users\guilherme\.gemini\antigravity\scratch\jobpilot

echo [1/3] Iniciando Backend FastAPI (Porta 8001)...
start "JobPilot Backend (Porta 8001)" cmd /k "cd /d %PROJECT_DIR%\backend && uvicorn app.main:app --port 8001 --loop asyncio"

echo [2/3] Iniciando Frontend Next.js (Porta 3000)...
start "JobPilot Frontend (Porta 3000)" cmd /k "cd /d %PROJECT_DIR%\frontend && npm run dev"

echo [3/3] Aguardando servidores iniciarem...
timeout /t 5 /nobreak >nul

echo Abrindo aplicacao no navegador...
start http://localhost:3000

echo.
echo ======================================================
echo   JobPilot pronto e aberto em http://localhost:3000!
echo ======================================================
echo Pressione qualquer tecla para fechar este assistente.
pause >nul
