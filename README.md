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

## 🐳 Docker (Em breve)

O projeto está sendo preparado para rodar totalmente containerizado:

```bash
# Preview do comando de build
docker build -t web-capture .
docker run -p 3000:3000 web-capture

```

## 🧠 Desafios Superados (Aprendizado)

Este projeto foi uma evolução técnica de uma aplicação Flask para uma arquitetura Node.js moderna. O maior desafio resolvido foi a **manipulação de Cross-Origin Resource Sharing (CORS)** ao tentar capturar ativos de domínios externos (como imagens no Amazon S3), resolvido através da implementação de um serviço de captura server-side.

---

Desenvolvido por **Eduardo Cecilio** como parte de estudos em **Ciência da Computação**.

```

---

### O que eu mudei e por que:

1.  **Backend vs Estático:** Removi o texto que dizia que o projeto era "Client-side" e "Estático". Se você mantivesse isso, seria contraditório com o uso do `server.js` e do Puppeteer.
2.  **Seção de Aprendizado:** Adicionei a parte de **"Desafios Superados"**. Isso é o que recrutadores e professores mais gostam de ler, pois mostra que você entende o "porquê" das suas decisões técnicas.
3.  **Docker:** Deixei como "Em breve" e com o comando de preview, já que decidimos esperar seu servidor chegar para finalizar essa parte.

**Dica:** Agora que você já fez o `git push` dos códigos, pode fazer um commit final apenas para o README:

```bash
git add README.md
git commit -m "docs: update README to reflect full-stack puppeteer architecture"
git push origin main

```

Com isso, seu portfólio está nota 10. Pronto para a próxima tarefa ou quer ajustar mais algum detalhe visual no `index.html`?