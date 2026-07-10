# Web-Capture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Node.js](https://img.shields.io/badge/node.js-%23339933.svg?style=flat&logo=node.js&logoColor=white)
![Puppeteer](https://img.shields.io/badge/puppeteer-%2340b5a4.svg?style=flat&logo=puppeteer&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)

Solucao Full-Stack para converter paginas web em documentos PDF e arquivos HTML. Utiliza Puppeteer com Google Chrome para renderizar conteudo dinamico (SPA/JavaScript) com alta fidelidade.

## Stack

- **Backend:** Node.js, Express.js 5
- **Engine de Captura:** Puppeteer (Chromium)
- **Frontend:** HTML5, Bootstrap 5.3 (Dark Theme), Vanilla JS
- **Infra:** Docker, Docker Compose, Cloudflare Tunnel

## Seguranca

- **Protecao contra SSRF:** Validacao de URL com bloqueio de IPs privados, loopback, link-local e metadata endpoints. Resolucao DNS para verificar IPs reais.
- **Rate Limiting:** 10 requisicoes por 15 minutos por IP (desabilitado em desenvolvimento).
- **Security Headers:** X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy.
- **Container isolado:** Execucao como usuario nao-privilegiado (`pptruser`) dentro do Docker.
- **Trust Proxy:** Configurado para identificar IPs reais atraves de Cloudflare Tunnel.
- **Erros sanitizados:** Mensagens de erro genericas para o cliente, detalhes apenas no log do servidor.

## Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| `GET` | `/` | Interface web |
| `GET` | `/api/capture?url=` | Gera PDF da pagina via Puppeteer |
| `GET` | `/api/capture-html?url=` | Retorna o HTML da pagina |

## Instalacao Local

```bash
git clone https://github.com/eduardocecilio/web-capture.git
cd web-capture
npm install
```

**Producao (com rate limit):**
```bash
npm start
```

**Desenvolvimento (sem rate limit):**
```bash
npm run dev
```

Acesse em `http://localhost:3000`

## Docker

```bash
docker compose up -d --build
```

O Dockerfile usa Chromium, compativel com `amd64` e `arm64` (Apple Silicon). O container roda na porta `3000`, mapeada via variavel `HOST_PORT`.

## Variaveis de Ambiente

| Variavel | Descricao | Padrao |
|----------|-----------|--------|
| `NODE_ENV` | `development` desabilita rate limit | `production` |
| `CORS_ORIGIN` | Origem permitida para CORS; aceita lista separada por virgula | `https://capture.cernevia.com` |
| `PUPPETEER_EXECUTABLE_PATH` | Caminho do Chromium no container | `/usr/bin/chromium` |
| `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD` | Pula download do Chromium no Docker | `true` |

---

Desenvolvido por **Eduardo Cecilio**
