# 🏗️ Arquitetura da Aplicação

## Diagrama de Fluxo - Conversão de URL

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USUÁRIO                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Web Browser │
                    └──────┬──────┘
                           │
                    ┌──────▼──────────────────┐
                    │   Flask Application    │
                    │  (Vercel Serverless)   │
                    └──────┬──────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
    │   Routes   │  │   Models   │  │   Conversion│
    │  /convert  │  │ SQLAlchemy │  │    Engine  │
    │  /api/*    │  │            │  │  (httpx +  │
    │  /health   │  │            │  │ WeasyPrint)│
    └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
          │                │               │
          │                │               │
    ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────────┐
    │  Validação │  │   Database │  │  HTTP Client   │
    │    URL     │  │ (PostgreSQL)│  │   (httpx)      │
    └─────┬──────┘  └─────┬──────┘  └─────┬──────────┘
          │                │               │
          │         ┌──────┴───────────────┘
          │         │
    ┌─────▼─────────▼─────────┐
    │   Generate PDF         │
    │  (WeasyPrint)          │
    └─────┬───────────────────┘
          │
    ┌─────▼──────────────┐
    │  Return to User    │
    │  (Download/API)    │
    └────────────────────┘
```

## Stack por Camada

```
┌──────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT                                 │
│  Vercel (Serverless)                                         │
│  - Automatic scaling                                         │
│  - HTTPS, CDN                                                │
│  - Environment variables                                    │
└──────────────────────────────────────────────────────────────┘
                            │
┌──────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                           │
│  Flask 3.0                                                    │
│  - Routes (GET, POST)                                        │
│  - Jinja2 templates                                         │
│  - Error handlers                                           │
└──────────────────────────────────────────────────────────────┘
                            │
┌──────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC                              │
│  Conversion Engine                                            │
│  - WebPageConverter class                                    │
│  - HTML cleaning                                             │
│  - PDF generation                                            │
└──────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼─────┐
│ DATA ACCESS    │  │ HTTP CLIENT    │  │ PDF ENGINE │
│                │  │                │  │            │
│ SQLAlchemy ORM │  │ httpx          │  │ WeasyPrint │
│ PostgreSQL/    │  │ - GET requests │  │ - CSS      │
│   SQLite       │  │ - Redirects    │  │ - Styling  │
└────────────────┘  │ - Timeouts     │  │ - Fonts    │
                    └────────────────┘  └────────────┘
```

## Estrutura de Arquivos

```
web-capture/
│
├── 📝 Core Application
│   ├── app.py              ← Flask config + DB init
│   ├── main.py             ← Entry point
│   ├── routes.py           ← Rotas web
│   └── models.py           ← SQLAlchemy models
│
├── 🔧 Conversion Engine
│   └── conversion/
│       └── __init__.py     ← WebPageConverter class
│
├── 👁️ Templates (Jinja2)
│   └── templates/
│       ├── base.html       ← Layout base
│       └── index.html      ← Página principal
│
├── 🎨 Frontend
│   └── static/
│       ├── css/
│       │   └── style.css   ← Estilos
│       └── js/
│           └── app.js      ← JavaScript
│
├── ⚙️ Configuration
│   ├── vercel.json         ← Vercel config
│   ├── requirements.txt    ← Python deps
│   ├── .env.example        ← Variáveis template
│   └── .gitignore          ← Git patterns
│
└── 📚 Documentation
    ├── README.md           ← Documentação principal
    ├── QUICKSTART.md       ← 5 minutos setup
    ├── DEVELOPMENT.md      ← Setup local
    ├── DEPLOYMENT.md       ← Passo a passo deploy
    ├── MIGRATION.md        ← Detalhes refatoração
    └── SUMMARY.md          ← Resumo executivo
```

## Fluxo de Dados - Conversão

```
Usuário Insere URL
        │
        ▼
┌───────────────────────────────────────┐
│  POST /api/convert                    │
│  {"url": "https://example.com"}       │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  Validação                            │
│  - URL válida?                        │
│  - Formato correto?                   │
└───────────────────────────────────────┘
        │
        ├─── ERRO ──┐
        │           ▼
        │  Return 400
        │
        ├─── OK
        ▼
┌───────────────────────────────────────┐
│  WebPageConverter.run()               │
│                                       │
│  1. httpx.get(url)                   │
│  2. Clean HTML                       │
│  3. Extract title                    │
│  4. WeasyPrint PDF                   │
└───────────────────────────────────────┘
        │
        ├─── ERRO ──┐
        │           ▼
        │  Log erro
        │  Return 500
        │
        ├─── OK
        ▼
┌───────────────────────────────────────┐
│  Salvar em DB                         │
│  - url                                │
│  - title                              │
│  - status (completed)                 │
│  - timestamp                          │
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│  Retornar Resultado                   │
│  - PDF bytes (download)               │
│  - Ou JSON (API)                      │
└───────────────────────────────────────┘
        │
        ▼
    Usuário Download
```

## Integração - Banco de Dados

```
┌─────────────────────────┐
│   Aplicação Flask       │
│   (Vercel Serverless)   │
└────────┬────────────────┘
         │ SQLAlchemy ORM
         │
    ┌────▼────────────────────┐
    │                         │
    ├─ Ambiente Local?        │
    │  └─ SQLite (local.db)   │
    │     (arquivo local)     │
    │                         │
    ├─ Ambiente Vercel?       │
    │  └─ PostgreSQL          │
    │     (gerenciado)        │
    │                         │
┌───┴─────────────────────────┐
│  Vercel Postgres Store      │
│  - Backups automáticos      │
│  - Replicação               │
│  - Recovery point objective │
└─────────────────────────────┘
```

## Deploy - CI/CD (Opcional)

```
┌────────────────────────┐
│  GitHub Repository     │
│  (seu código)          │
└────────┬───────────────┘
         │ git push
         ▼
┌────────────────────────┐
│  Vercel CI/CD          │
│  - Auto detects Python │
│  - Build app           │
│  - Run migrations DB   │
└────────┬───────────────┘
         │ Deploy automático
         ▼
┌────────────────────────┐
│  Production            │
│  https://your-app.     │
│     vercel.app         │
└────────────────────────┘
```

## Performance - Antes vs Depois

### Antes (Com Playwright)
```
URL Request
    │ (5-10s)
    ├─ Start Chromium (~3s)
    ├─ Load page (~2-5s)
    ├─ Execute JS (~1s)
    ├─ Take screenshot (~1s)
    ├─ Generate PDF (~1s)
    └─ Save file (~1s)
        │ (Total: 5-10s)
        ▼
    Usuário receive
```

### Depois (Com httpx + WeasyPrint)
```
URL Request
    │ (0.5-2s)
    ├─ HTTP GET (~0.5s)
    ├─ Parse HTML (~0.1s)
    ├─ Clean HTML (~0.1s)
    ├─ Generate PDF (~0.2s)
    └─ Return (~0.1s)
        │ (Total: 0.5-2s)
        ▼
    Usuário receives
```

---

## Componentes-Chave

### 1. WebPageConverter
- **Arquivo:** `conversion/__init__.py`
- **Responsabilidade:** Converter URL → PDF
- **Métodos:**
  - `__init__(settings)` - Inicializa
  - `run()` - Executa conversão
  - `clean_html_for_offline()` - Limpa HTML

### 2. Flask Application
- **Arquivo:** `app.py`
- **Responsabilidade:** Config Flask, DB, middleware
- **Features:**
  - ProxyFix para Vercel
  - SQLAlchemy init
  - Auto-detect PostgreSQL

### 3. Routes Handler
- **Arquivo:** `routes.py`
- **Rotas:**
  - `POST /convert` - Conversão (download)
  - `POST /api/convert` - API JSON
  - `GET /api/conversions` - Listar
  - `GET /health` - Health check

### 4. Data Models
- **Arquivo:** `models.py`
- **Model:**
  - `Conversion` - Histórico conversões

---

**Arquitetura pronta para produção! 🎯**
