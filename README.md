# Web-Capture - Conversor de Sites para PDF

Uma aplicação web estática que converte páginas web em PDF e HTML, com suporte a autenticação, configurações avançadas de viewport e PDF, e substituição automática de vídeos por links.

## Características

- ✨ Conversão de páginas web em PDF
- 📄 Exportação de HTML processado
- 🔐 Suporte a autenticação (opcional)
- 🎥 Substituição automática de vídeos por links
- 📱 Interface responsiva com Bootstrap
- 🎨 Tema escuro
- ⚙️ Configurações avançadas de PDF (formato, margens, escala)
- 🚀 Aplicação puramente estática (sem backend)

## Requisitos

- Node.js 14+ (para desenvolvimento local)
- Um navegador moderno com suporte a ES6+

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/eduardocecilio/web-capture.git
cd web-capture
```

2. Instale as dependências:
```bash
npm install
```

## Desenvolvimento

Para iniciar o servidor local:

```bash
npm start
```

A aplicação estará disponível em `http://localhost:8080`

## Estrutura do Projeto

```
web-capture/
├── index.html           # Página principal
├── static/
│   ├── css/
│   │   └── style.css    # Estilos customizados
│   └── js/
│       └── app.js       # Lógica da aplicação
├── package.json         # Dependências do projeto
└── README.md           # Este arquivo
```

## Como Usar

1. Abra a aplicação no navegador
2. Insira a URL da página web que deseja converter
3. (Opcional) Configure as opções avançadas:
   - Autenticação (login, usuário, senha)
   - Aguardar carregamento de elementos
   - Configurações do PDF (formato, margens, escala)
   - Viewport (largura e altura)
4. Clique em "Converter Página"
5. Após a conversão, baixe o PDF ou HTML

## Limitações e Considerações

- **CORS**: A aplicação usa um proxy CORS para contornar restrições de origem. Algumas websites podem bloquear a requisição.
- **JavaScript**: Apenas websites que carregam conteúdo no carregamento inicial são suportados. Sites que usam JavaScript pesado podem não funcionar corretamente.
- **Autenticação**: A autenticação é experimental e pode não funcionar com todos os sites.
- **Performance**: Conversões de páginas grandes podem levar algum tempo.

## Deploy

### Vercel

1. Acesse [vercel.com](https://vercel.com)
2. Conecte seu repositório GitHub
3. Configure o diretório raiz como `.` (raiz do projeto)
4. Clique em "Deploy"

### Netlify

1. Acesse [netlify.com](https://netlify.com)
2. Conecte seu repositório GitHub
3. Configure o diretório publicado como `.` (raiz do projeto)
4. Clique em "Deploy"

### GitHub Pages

1. Faça push do repositório para GitHub
2. Acesse as configurações do repositório
3. Role para baixo até "GitHub Pages"
4. Selecione a branch `main` como fonte
5. Clique em "Save"

## Tecnologias Utilizadas

- **HTML5**: Estrutura da aplicação
- **CSS3**: Estilos (com Bootstrap 5)
- **JavaScript (Vanilla)**: Lógica da aplicação
- **Bootstrap 5**: Framework CSS
- **html2pdf.js**: Geração de PDF
- **Feather Icons**: Ícones
- **http-server**: Servidor de desenvolvimento

## Dependências

- `http-server`: Servidor HTTP simples para desenvolvimento local

## Licença

MIT

## Autor

Eduardo Cecilio

## Suporte

Se encontrar problemas, abra uma issue no repositório do GitHub.
