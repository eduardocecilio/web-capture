@echo off
REM Script de limpeza para Windows
REM Remove arquivos não necessários para Vercel

echo Limpando arquivos nao necessarios para Vercel...

REM Remover Replit
if exist .replit del .replit
if exist .config rmdir /s /q .config
if exist replit.md del replit.md

REM Remover scheduler (nao funciona em Vercel)
if exist scheduler.py del scheduler.py

REM Remover CLI (nao funciona em Vercel)
if exist conversor_sites rmdir /s /q conversor_sites

REM Limpar cache Python
if exist __pycache__ rmdir /s /q __pycache__
if exist instance rmdir /s /q instance
for /r . %%f in (*.pyc) do del %%f

REM Limpar output local
if exist output rmdir /s /q output

echo.
echo Limpeza concluida!
echo.
echo Estrutura final:
dir /b

echo.
echo Seu projeto agora esta pronto para Vercel!
pause
