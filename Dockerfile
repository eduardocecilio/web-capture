# Usando uma imagem que já vem com as dependências de sistema para o Puppeteer
FROM ghcr.io/puppeteer/puppeteer:latest

USER root

WORKDIR /app

# Copia arquivos de dependência
COPY package*.json ./

# Instala as dependências do Node
RUN npm install

# Copia o restante do código
COPY . .

# Garante que as permissões de execução estão corretas
RUN chown -R pptruser:pptruser /app

USER pptruser

EXPOSE 3000

CMD ["node", "server.js"]