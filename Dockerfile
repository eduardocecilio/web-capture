FROM node:20-slim

# Instala Chromium e dependências (funciona em amd64 e arm64)
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m pptruser
WORKDIR /home/pptruser/app

# Muda o dono da pasta para o usuário novo
RUN chown -R pptruser:pptruser /home/pptruser/app

USER pptruser

# Variáveis de ambiente
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Copia os arquivos
COPY --chown=pptruser:pptruser package*.json ./
RUN npm install
COPY --chown=pptruser:pptruser . .

EXPOSE 3000
CMD ["node", "server.js"]