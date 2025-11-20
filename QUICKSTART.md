# ⚡ Quick Start - 5 Minutos

## Local (Desenvolvimento)

### 1. Setup
```bash
git clone https://github.com/seu-user/web-capture.git
cd web-capture
python -m venv venv
source venv/bin/activate  # ou: venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### 2. Run
```bash
python main.py
# Abra http://localhost:5000
```

### 3. Teste
```bash
# Via browser: Insira URL
# Via API:
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}' \
  http://localhost:5000/api/convert
```

---

## Deploy no Vercel (2 minutos)

### 1. Setup Vercel
```bash
npm i -g vercel
vercel login
```

### 2. Crie Banco de Dados
```bash
vercel postgres create
# Copie a POSTGRES_URL
```

### 3. Vá ao Dashboard
https://vercel.com/dashboard

### 4. Adicione Variáveis
```
SESSION_SECRET = <gere com: python -c "import secrets; print(secrets.token_hex(32))">
POSTGRES_URL = <Cole aqui>
FLASK_ENV = production
```

### 5. Deploy
```bash
vercel --prod
```

### 6. Pronto! 🎉
```
https://web-capture.vercel.app
```

---

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| "ModuleNotFoundError" | `pip install -r requirements.txt` |
| "Port 5000 in use" | `python main.py` (muda automaticamente) |
| "Conversão lenta" | Normal (primeira execução) |
| Deploy falha | `vercel logs` |
| Banco vazio | Configure POSTGRES_URL |

---

## Próximos Passos

1. Leia `README.md` - Documentação completa
2. Veja `DEVELOPMENT.md` - Setup mais detalhado
3. Siga `DEPLOY_CHECKLIST.md` - Deploy seguro
4. Verifique `MIGRATION.md` - Entenda as mudanças

---

**Pronto? Comece agora! 🚀**
