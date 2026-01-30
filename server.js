const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const path = require('path');
const app = express();

app.use(cors({
    origin: '*',
    exposedHeaders: ['X-Page-Title']
}));

app.use(express.static(__dirname));

app.get('/api/capture', async (req, res) => {
    const url = req.query.url;
    if (!url) return res.status(400).send('URL necessária');

    console.log(`📸 Capturando: ${url}`);

    let browser;
    try {
        browser = await puppeteer.launch({ 
            headless: "new",
            args: ['--no-sandbox', '--disable-setuid-sandbox'] 
        });
        
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 800 });
        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
        
        const rawTitle = await page.title();
        
        // Ajuste CC: Normalize remove acentos e a regex limpa múltiplos sublinhados
        const safeTitle = (rawTitle || 'pagina_capturada')
            .normalize('NFD').replace(/[\u0300-\u036f]/g, "") // Remove acentos
            .replace(/[^a-z0-9]/gi, '_')                     // Troca especial por _
            .replace(/_+/g, '_')                             // Troca ___ por _
            .toLowerCase()
            .trim();

        const pdf = await page.pdf({
            format: 'A4',
            printBackground: true,
            margin: { top: '1cm', right: '1cm', bottom: '1cm', left: '1cm' }
        });

        await browser.close();

        res.setHeader('X-Page-Title', safeTitle);
        res.setHeader('Access-Control-Expose-Headers', 'X-Page-Title');
        res.contentType("application/pdf");
        
        console.log(`✅ PDF gerado: ${safeTitle}.pdf`);
        res.send(pdf);

    } catch (e) {
        if (browser) await browser.close();
        console.error("❌ Erro no Puppeteer:", e.message);
        res.status(500).send(`Erro na geração: ${e.message}`);
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 SERVIDOR RODANDO EM: http://localhost:${PORT}`);
});