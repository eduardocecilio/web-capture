# 🌐 Web-Capture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Node.js](https://img.shields.io/badge/node.js-%23339933.svg?style=flat&logo=node.js&logoColor=white)
![Puppeteer](https://img.shields.io/badge/puppeteer-%2340b5a4.svg?style=flat&logo=puppeteer&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)

O **Web-Capture** é uma solução Full-Stack robusta para converter páginas web em documentos PDF de alta fidelidade e arquivos HTML. Diferente de conversores estáticos simples, este projeto utiliza um motor de navegação real para garantir que layouts complexos e recursos protegidos sejam capturados com precisão.

## 🚀 Diferenciais Técnicos

- **Motor de Renderização Backend:** Utiliza o **Puppeteer** para instanciar um navegador Chromium no servidor, contornando restrições de CORS e renderizando conteúdo dinâmico (JavaScript) que conversores comuns ignoram.
- **Arquitetura Full-Stack:** Separação clara entre uma interface reativa no Frontend e um serviço de captura dedicado no Backend.
- **Fidelidade Visual:** Opções de renderização configuradas para emular dispositivos desktop, garantindo que o PDF gerado mantenha o layout original.
- **Pronto para Homelab:** Estrutura otimizada para rodar em containers Docker, ideal para infraestruturas locais como Mac Mini ou servidores Linux.

## 🛠️ Stack Tecnológica

- **Backend:** Node.js, Express.js
- **Engine de Captura:** Puppeteer (Headless Chromium)
- **Frontend:** HTML5, CSS3 (Bootstrap Dark Theme), JavaScript Assíncrono
- **Ícones:** Feather Icons

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
```bash
npm start

```


4. **Acesse a aplicação:**
Abra seu navegador em `http://localhost:3000`