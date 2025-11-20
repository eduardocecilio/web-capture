# Web to PDF Converter

Aplicativo Flask que converte páginas web em PDF, otimizado para Vercel (serverless).

## Features

- Conversão de URLs em PDF com um clique
- Preservação de HTML com estilos para uso offline
- Interface web intuitiva com Bootstrap 5
- Histórico de conversões em banco de dados
- API REST para integração
- Otimizado para Vercel (serverless)

## Limitações

Este aplicativo funciona apenas com sites estáticos (sem execução de JavaScript).

- Não executa JavaScript (apenas requisições HTTP para recuperar HTML)
- Não faz login em sites protegidos
- Não captura conteúdo gerado dinamicamente por vídeos
- Não suporta SPAs (React, Vue, Angular, etc.)
- Funciona offline sem dependências externas
- Conversão rápida e uso mínimo de CPU/RAM

## Stack Tecnológica

- Backend: Flask + SQLAlchemy  
- HTTP Client: httpx  
- Gerador de PDF: WeasyPrint  
- Banco de dados: PostgreSQL (Vercel Postgres) ou SQLite (local)  
- Frontend: Bootstrap 5 + Feather Icons  
- Deploy: Vercel (serverless)

## Requisitos

Desenvolvimento local:
- Python 3.11+
- pip
- Git

Produção (Vercel):
- Conta Vercel
- Vercel Postgres (opcional)
- Vercel Blob (opcional)

## Quick Start — Desenvolvimento Local

```bash
# 1. Clone o repositório
git clone https://github.com/seu-user/web-capture.git
cd web-capture

# 2. Crie virtualenv
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
copy .env.example .env  # Windows
# Edite .env conforme necessário

# 5. Rode a aplicação
python main.py

# Acesse: http://localhost:5000
```

## Deploy no Vercel

Pré-requisitos:
```bash
# Instale Vercel CLI
npm i -g vercel
vercel login
```

Configurar Postgres:
```bash
vercel postgres create
# copie a URL do banco (POSTGRES_URL)
```

Deploy:
```bash
# Deploy preview
vercel

# Deploy produção
vercel --prod
```

Variáveis de ambiente no Vercel:
- SESSION_SECRET — chave secreta para Flask (gere com: `python -c "import secrets; print(secrets.token_hex(32))"`)
- POSTGRES_URL — URL do banco Postgres
- BLOB_READ_WRITE_TOKEN — token do Vercel Blob (se usar blob)

## API

POST /convert
- Converte página para PDF e retorna download direto:
```bash
curl -X POST -F "url=https://example.com" http://localhost:5000/convert
```

POST /api/convert
- Converte página e retorna JSON com resultado:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}' \
  http://localhost:5000/api/convert
```

GET /api/conversions
- Lista conversões recentes

GET /api/conversions/<id>
- Detalhes de uma conversão

GET /health
- Health check

## Estrutura do Projeto

```
web-capture/
├── app.py
├── main.py
├── routes.py
├── models.py
├── conversion/
│   └── __init__.py
├── templates/
├── static/
├── vercel.json
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Desenvolvimento

- Adicione novas rotas em `routes.py`
- Teste localmente com `python main.py`
- Use `black` e `pylint` para formatar/lint

## Troubleshooting

- httpx.ConnectError: verifique URL e conexão
- WeasyPrint: fontes podem não ser encontradas — fontes padrão serão usadas
- POSTGRES_URL não setado: usa SQLite local em desenvolvimento

## Licença

MIT License — veja LICENSE.md
