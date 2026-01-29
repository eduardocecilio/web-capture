const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const path = require('path');
const app = express();

app.use(cors());
// Isso faz o servidor na porta 3000 entregar o seu index.html e a pasta static
app.use(express.static(__dirname));

// Rota para capturar o PDF usando Puppeteer
app.get('/api/capture', async (req, res) => {
    const url = req.query.url;
    if (!url) return res.status(400).send('URL necessária');

    console.log(`📸 Puppeteer iniciando captura de: ${url}`);

    try {
        const browser = await puppeteer.launch({ headless: "new" });
        const page = await browser.newPage();
        
        // Define um viewport de desktop
        await page.setViewport({ width: 1280, height: 800 });
        
        // O pulo do gato: networkidle2 espera o site carregar quase tudo
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
        
        const pdf = await page.pdf({
            format: 'A4',
            printBackground: true,
            margin: { top: '1cm', right: '1cm', bottom: '1cm', left: '1cm' }
        });

        await browser.close();
        console.log("✅ PDF gerado com sucesso pelo Puppeteer");
        res.contentType("application/pdf");
        res.send(pdf);
    } catch (e) {
        console.error("❌ Erro no Puppeteer:", e.message);
        res.status(500).send(e.message);
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`
    🚀 PROJETO ORGANIZADO!
    Link de acesso: http://localhost:${PORT}
    (Pode fechar o terminal que estiver rodando na porta 8080)
    `);
});