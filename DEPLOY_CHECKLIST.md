# 🚀 Checklist de Deploy - Vercel

## ✅ Pré-Deploy (Local)

### Código
- [ ] Todas as imports funcionam sem erro
- [ ] Nenhum arquivo `.pyc` commitado
- [ ] Nenhum `__pycache__` commitado
- [ ] `.env` local não commitado (apenas `.env.example`)
- [ ] Nenhum hardcode de secrets

### Testes
- [ ] Rodou `python main.py` com sucesso
- [ ] Interface carrega em http://localhost:5000
- [ ] Conseguiu converter um site estático (ex: Wikipedia)
- [ ] API `/health` responde 200 OK
- [ ] Erros são capturados e reportados

### Git
- [ ] Fez commit com mensagem clara: `refactor: vercel migration`
- [ ] Fez push para main branch
- [ ] Nenhuma mudança não-commitada

### Arquivos Críticos
- [ ] ✅ `vercel.json` existe
- [ ] ✅ `requirements.txt` existe
- [ ] ✅ `main.py` exporta `app`
- [ ] ✅ `.env.example` existe
- [ ] ✅ `.gitignore` está completo

## 🔐 Segurança

- [ ] `SESSION_SECRET` não está em `.env` commitado
- [ ] Nenhuma URL privada no código
- [ ] Nenhuma credencial nos comments
- [ ] Error handlers não expõem detalhes de sistema

## 📦 Dependências

```bash
# Verificar tamanho
pip list --format=freeze | wc -l  # Deve ser ~7

# Verificar sem Playwright
pip list | grep -i playwright  # Não deve aparecer

# Verificar WeasyPrint está presente
pip show weasyprint  # Version 60.1
```

## 🔗 Links Importantes

- Vercel Dashboard: https://vercel.com/dashboard
- Project Settings: https://vercel.com/project/web-capture/settings
- Environment Variables: https://vercel.com/project/web-capture/settings/environment-variables
- Domains: https://vercel.com/project/web-capture/settings/domains

## 📝 Passo a Passo Deploy

### 1. Login Vercel
```bash
vercel login
# Escolha GitHub/GitLab/Gitlab (onde seu repo está)
```

### 2. Link Projeto
```bash
# Se primeira vez
cd /caminho/para/web-capture
vercel
# Escolha: Create new project
# Name: web-capture
# Selecione: web-capture no GitHub

# Se já vinculado
vercel
```

### 3. Configurar Banco de Dados (Postgres)

#### Opção A: Via Dashboard
1. Vá a https://vercel.com/project/web-capture/settings/stores
2. Clique "Create Postgres Database"
3. Escolha region (defina mais próxima de você)
4. Crie banco vazio
5. Copie `POSTGRES_URL`

#### Opção B: Via CLI
```bash
vercel postgres create
# Siga instruções
# Copie DATABASE_URL que será exibida
```

### 4. Configurar Variáveis de Ambiente

```bash
# Gere SESSION_SECRET
python -c "import secrets; print('SESSION_SECRET=' + secrets.token_hex(32))"

# Adicione no Vercel Dashboard:
# Settings > Environment Variables

# Variáveis a adicionar:
SESSION_SECRET=<seu-token>
POSTGRES_URL=<seu-banco-postgres>
FLASK_ENV=production
DEBUG=False
```

### 5. Deploy Staging
```bash
# Testa sem publicar (gera preview URL)
vercel

# Teste a preview URL
# Verifique logs
vercel logs
```

### 6. Verificar Logs
```bash
# Ver logs de erro
vercel logs --follow

# Buscar por erro específico
vercel logs | grep ERROR
```

### 7. Testar Endpoints
```bash
# Health check
curl https://web-capture.vercel.app/health

# Conversão (teste com site estático)
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}' \
  https://web-capture.vercel.app/api/convert
```

### 8. Deploy Produção
```bash
# Após confirmar funciona
vercel --prod

# Isso atualizará:
# - web-capture.vercel.app (main)
# - Todas as preview URLs
```

## ⚠️ Troubleshooting Deploy

### Erro: "MODULE NOT FOUND"
- Verifique: `pip install -r requirements.txt`
- Verifique: Todos os imports estão em requirements.txt

### Erro: "CONNECTION REFUSED"
- PostgreSQL não configurada
- Solução: Crie PostgreSQL via Vercel Dashboard

### Erro: "TIMEOUT"
- Site demora muito pra responder
- Solução: Tente com site diferente (alguns bloqueiam)

### Erro: "403 FORBIDDEN"
- Site bloqueia requests automated
- Solução: Tente com site que não bloqueia bots

### Erro: "502 BAD GATEWAY"
- Função serverless crashou
- Solução: Verifique logs com `vercel logs`

## 📊 Monitoramento Pós-Deploy

### Verificar Saúde
```bash
# Health check
curl https://web-capture.vercel.app/health

# Deve retornar:
{"status": "ok", "timestamp": "2024-01-15T..."}
```

### Verificar Banco de Dados
```bash
# Via Vercel Dashboard
# Settings > Stores > Postgres > Query Editor

# Ou via psql
psql $POSTGRES_URL

# Verifique tables criadas
\dt

# Verifique conversions
SELECT COUNT(*) FROM conversions;
```

### Verificar Performance
```bash
# Via Vercel Analytics Dashboard
# https://vercel.com/project/web-capture/analytics

# Métricas importantes:
# - Response time: < 2s para conversão
# - Error rate: < 1%
# - Uptime: > 99.9%
```

### Logs em Tempo Real
```bash
vercel logs --follow

# Filtrar por erro
vercel logs --follow 2>&1 | grep ERROR

# Ver últimas 10 linhas
vercel logs | tail -10
```

## 🔄 Rollback (Se necessário)

```bash
# Voltar para última versão estável
git revert HEAD
git push
vercel --prod
```

## 📋 Após Deploy

- [ ] Documentar URL de produção
- [ ] Testar todos endpoints
- [ ] Configurar monitoramento
- [ ] Adicionar analytics
- [ ] Comunicar ao time

## 🎉 Done!

Se chegou aqui sem erros, você está pronto! 

Sua aplicação está rodando em:
**https://web-capture.vercel.app**

---

**Tempo estimado de deploy:** 5-10 minutos
**Custo:** Grátis (até 100 funções serverless/mês)
