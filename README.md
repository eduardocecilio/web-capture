# 🌐 Web-Capture

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=flat&logo=javascript&logoColor=%23F7DF1E)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)

O **Web-Capture** é uma ferramenta desenvolvida para converter páginas web complexas em documentos PDF e arquivos HTML prontos para uso. O projeto foca em portabilidade e eficiência, rodando inteiramente no lado do cliente (Client-side) ou via containerização.



## 🚀 Diferenciais Técnicos

- **Arquitetura Estática:** Processamento via DOMParser e Bibliotecas JS modernas, eliminando a necessidade de um backend pesado para tarefas simples.
- **Tratamento de Mídia:** Algoritmo customizado para identificação de vídeos (YouTube/Vimeo) e substituição automática por links navegáveis no PDF.
- **CORS Bypass:** Implementação de lógica multi-proxy para contornar restrições de Cross-Origin Resource Sharing.
- **Ready for Homelab:** Configurado para rodar via Docker em infraestruturas locais (Mac Mini/Linux).

## 🛠️ Stack Tecnológica

- **Frontend:** HTML5, CSS3 (Bootstrap Dark Theme)
- **Engine de PDF:** [html2pdf.js](https://rawgit.com/eKoopmans/html2pdf/master/dist/html2pdf.bundle.min.js)
- **Ícones:** Feather Icons
- **Servidor de Dev:** Node.js & http-server

## 📦 Instalação e Execução Local

1. Clone o repositório:
   ```bash
   git clone [https://github.com/eduardocecilio/web-capture.git](https://github.com/eduardocecilio/web-capture.git)