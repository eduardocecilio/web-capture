# Configuração de Desenvolvimento Local

Para desenvolver localmente sem precisar Vercel, use este guia.

## 🛠 Setup Inicial

### 1. Clone e entre na pasta
```bash
git clone <repo>
cd web-capture
```

### 2. Crie virtual environment
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
```

### 4. Configure .env
```bash
cp .env.example .env

# Edite .env para:
SESSION_SECRET=dev-secret-just-for-testing
FLASK_ENV=development
DEBUG=True

# Banco de dados: deixe em branco para usar SQLite local
# POSTGRES_URL não precisa ser configurada em dev
```

### 5. Rode aplicação
```bash
python main.py

# Deve mostrar:
# WARNING in app.run() is not intended for production
# http://127.0.0.1:5000/
```

### 6. Acesse
```
http://localhost:5000
```

## 📝 Estrutura de Desenvolvimento

### Arquivos que você pode editar
- `templates/` - HTML/Jinja2
- `static/` - CSS/JavaScript
- `routes.py` - Rotas Flask
- `models.py` - Models SQLAlchemy
- `conversion/__init__.py` - Motor de conversão

### Arquivos que não devem mexer sem entender
- `app.py` - Configuração core
- `main.py` - Entry point
- `requirements.txt` - Dependências

## 🔄 Workflow de Desenvolvimento

### 1. Criar branch
```bash
git checkout -b feature/minha-feature
```

### 2. Fazer mudanças
```bash
# Edite seus arquivos
# Teste localmente em http://localhost:5000
```

### 3. Commit
```bash
git add .
git commit -m "feat: descição da mudança"
```

### 4. Push
```bash
git push origin feature/minha-feature
```

### 5. Pull Request
- Vá ao GitHub
- Abra PR da sua branch para `main`

## 🧪 Testes Locais

### Testar conversão básica
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}' \
  http://localhost:5000/api/convert
```

### Testar health check
```bash
curl http://localhost:5000/health
```

### Testar listar conversões
```bash
curl http://localhost:5000/api/conversions
```

### Testar com site real
```bash
# Wikipedia é bom para testar
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://en.wikipedia.org/wiki/Python_(programming_language)"}' \
  http://localhost:5000/api/convert
```

## 🐛 Debug

### Ver logs detalhados
```bash
# Já rodando, adicione ao final de .env
DEBUG=True
```

### Usar debugger do Flask
```python
# No routes.py, adicione:
from flask import current_app

@app.route('/debug')
def debug():
    return jsonify({'debug': current_app.debug})
```

### Inspecionar BD local
```bash
# Database é SQLite em local.db
sqlite3 local.db

# Ver tables
.tables

# Ver schema de conversions
.schema conversions

# Listar conversões
SELECT * FROM conversions;
```

### Resetar BD
```bash
rm local.db
python main.py
# BD será recriada vazia
```

## 📦 Adicionar Dependências

Se precisar adicionar nova biblioteca:

```bash
# 1. Instale localmente
pip install nova-lib

# 2. Atualize requirements.txt
pip freeze > requirements.txt

# 3. Teste localmente
python main.py

# 4. Commit
git add requirements.txt
git commit -m "deps: add nova-lib"
```

## 🎨 Formatação de Código

### Formatador Python (Black)
```bash
# Instale
pip install black pylint

# Formate todos arquivos
black *.py routes.py models.py conversion/

# Lint
pylint routes.py models.py
```

### Style Guide
- PEP 8 (Python)
- 4 spaces indentation
- Max 100 caracteres por linha

## 🚀 Performance Local

### Medir tempo de conversão
```python
import time

# Em routes.py, no /api/convert
start = time.time()
result = converter.run()
elapsed = time.time() - start
print(f"Tempo: {elapsed:.2f}s")
```

### Memory profiling
```bash
# Instale
pip install memory-profiler

# Execute
python -m memory_profiler main.py
```

## 🔒 Secrets e Segurança

### Never commit:
- ❌ `.env` (use `.env.example`)
- ❌ Chaves de API
- ❌ Senhas
- ❌ Tokens
- ❌ `local.db` com dados sensíveis

### Always use:
- ✅ `.env.example` como template
- ✅ `SESSION_SECRET` gerado
- ✅ Variáveis de ambiente para secrets

## 🆘 Problemas Comuns

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### "Port 5000 already in use"
```bash
# Mude porta em main.py
app.run(port=5001)
```

### "Cannot write to local.db"
```bash
# Verifique permissões
chmod 755 .
```

### WeasyPrint errors
```bash
# WeasyPrint precisa de algumas deps do sistema
# Ubuntu/Debian:
sudo apt-get install libpango-1.0-0 libpango-gobject-0 libgobject-2.0-0

# macOS:
brew install pango
```

## 📚 Referências Locais

- Flask docs: http://localhost:5000/docs (se implementado)
- SQLAlchemy: Ver `models.py`
- WeasyPrint: Ver `conversion/__init__.py`

## 🎯 Próximos Passos

Após fazer mudanças:

1. Teste localmente
2. Rode linter/formatter
3. Faça commit
4. Teste em staging (Vercel)
5. Merge para main
6. Deploy em produção

---

**Happy developing! 🎉**
