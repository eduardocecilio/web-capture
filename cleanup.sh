#!/bin/bash
# Script de limpeza - Remove arquivos não necessários para Vercel

echo "🧹 Limpando arquivos não necessários para Vercel..."

# Remover Replit
rm -f .replit
rm -rf .config/
rm -f replit.md

# Remover scheduler (não funciona em Vercel)
rm -f scheduler.py

# Remover CLI (não funciona em Vercel)
rm -rf conversor_sites/

# Limpar cache Python
rm -rf __pycache__/
rm -rf instance/
rm -f *.pyc

# Limpar output local
rm -rf output/

# Limpeza segura - só remover se vazio
rmdir instance 2>/dev/null || true
rmdir output 2>/dev/null || true

echo "✅ Limpeza concluída!"
echo ""
echo "📁 Estrutura final:"
ls -la | grep -E "^-" | awk '{print $9}'

echo ""
echo "✨ Seu projeto agora está pronto para Vercel!"
