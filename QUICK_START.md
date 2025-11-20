# Quick Start - Web-Capture

## Para Começar Rápido

### 1. **Instalação Local**

```bash
# Instale as dependências
npm install

# Inicie o servidor
npm start
```

A aplicação estará disponível em **http://localhost:8080**

### 2. **Como Usar**

1. Abra o navegador em `http://localhost:8080`
2. Cole a URL de uma página web
3. Clique em "Converter Página"
4. Baixe o PDF ou HTML gerado

### 3. **Deploy no Vercel**

```bash
# Login no Vercel
npm install -g vercel
vercel login

# Deploy
vercel deploy
```

### 4. **Deploy no Netlify**

```bash
# Instale Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

### 5. **Deploy no GitHub Pages**

1. Faça push para o GitHub
2. Vá para Settings > Pages
3. Selecione branch `main` e salve

## Estrutura Mínima

```
web-capture/
├── index.html          # Página principal
├── static/
│   ├── css/
│   │   └── style.css   # Estilos
│   └── js/
│       └── app.js      # Lógica
├── package.json        # Dependências
└── server.js          # Servidor dev
```

## Tecnologias

- **HTML5** - Estrutura
- **CSS3** - Estilos (Bootstrap 5)
- **JavaScript Vanilla** - Lógica
- **html2pdf.js** - Geração de PDF
- **Node.js** - Servidor de desenvolvimento

## Limitações Conhecidas

⚠️ Alguns sites podem não funcionar por:
- Restrições CORS
- Conteúdo gerado por JavaScript
- JavaScript Heavy (SPAs)

## Suporte

Problemas? Veja `CONVERSION_GUIDE.md` para mais detalhes.

---

**Versão**: 1.0.0  
**Autor**: Eduardo Cecilio  
**Licença**: MIT
