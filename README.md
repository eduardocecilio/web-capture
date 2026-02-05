# 🌐 Web-Capture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Node.js](https://img.shields.io/badge/node.js-%23339933.svg?style=flat&logo=node.js&logoColor=white)
![Puppeteer](https://img.shields.io/badge/puppeteer-%2340b5a4.svg?style=flat&logo=puppeteer&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)

O **Web-Capture** é uma solução Full-Stack robusta para converter páginas web em documentos PDF de alta fidelidade e arquivos HTML. Diferente de conversores estáticos simples, este projeto utiliza um motor de navegação real para garantir que layouts complexos e recursos protegidos sejam capturados com precisão.

## 🚀 Diferenciais Técnicos

- **Motor de Renderização Backend:** Utiliza o **Puppeteer** com Google Chrome estável para instanciar um navegador real no servidor, renderizando conteúdo dinâmico (SPA/JavaScript) com fidelidade.
- **Segurança de Camada:** Implementação de **Rate Limiting** para proteção contra abuso de recursos e execução via **usuário não-privilegiado** dentro do container.
- **Proxy Trust:** Configurado para identificar IPs reais através de túneis (Cloudflare) e proxies reversos.
- **Pronto para Homelab:** Estrutura otimizada para infraestruturas locais de baixo consumo, com limites de memória e gerenciamento de cache de imagem.

## 🛠️ Stack Tecnológica

- **Backend:** Node.js, Express.js
- **Segurança:** Express Rate Limit
- **Engine de Captura:** Puppeteer (Google Chrome Stable)
- **Frontend:** HTML5, CSS3 (Bootstrap Dark Theme), Vanilla JS
- **Infra:** Docker & Docker Compose

## 📦 Instalação e Execução Local

1. **Clone o repositório:**
```bash
git clone [https://github.com/eduardocecilio/web-capture.git](https://github.com/eduardocecilio/web-capture.git)
cd web-capture

```

2. **Instale as dependências:**

```bash
npm install

```

3. **Inicie o servidor:**

* **Modo Produção (Com Rate Limit):**
```bash
npm start

```


* **Modo Desenvolvimento (Sem Rate Limit):**
```bash
npm run dev

```



4. **Acesse a aplicação:**
Abra seu navegador em `http://localhost:3000`

## 🐳 Docker & Homelab

O deploy em servidores Linux (como o Mini-150) é feito via Docker:

```bash
# Otimização de limpeza (Higiene de disco)
sudo docker image prune -f

```

O container roda sob a porta interna `3000`. No Homelab, recomenda-se o mapeamento para `3001` e uso de Cloudflare Tunnel para exposição segura.

---

Desenvolvido por **Eduardo Cecilio** 🚀

```

---

### 🛠️ O que fazer agora:

1.  **No Mac:** Salve esse conteúdo no seu `README.md`.
2.  **No Mac:** Verifique se o seu `package.json` já tem o `"dev": "NODE_ENV=development node server.js"` na parte de scripts.
3.  **Git Push Final:**
    ```bash
    git add .
    git commit -m "docs: update readme with security features and dev workflow"
    git push origin main
    ```

Com isso, o ciclo de desenvolvimento deste problema está fechado com **higiene total**. O servidor está seguro, o local está fácil de usar e o código está documentado.

**Gostaria que eu gerasse agora o arquivo `docs/GUIA.md` com os comandos de manutenção do seu Mini-150 para você guardar de consulta?**

```