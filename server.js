const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const app = express();

// Configuração do Limite
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 10,
    // Remova o keyGenerator manual e use a validação padrão do express-rate-limit
    validate: { xForwardedForHeader: false }, 
    handler: (req, res) => {
        console.warn(`⚠️ BLOQUEADO: IP ${req.ip} atingiu o limite.`);
        res.status(429).send('Muitas requisições, tente novamente em 15 minutos.');
    },
    standardHeaders: true,
    legacyHeaders: false,
    skip: (req, res) => process.env.NODE_ENV === 'development'
});

// Higiene de Rede e Segurança
app.set('trust proxy', 1);
app.disable('x-powered-by');
app.use(cors({
    origin: '*',
    exposedHeaders: ['X-Page-Title']
}));

// Servir arquivos estáticos (index.html, app.js, style.css)
app.use(express.static(__dirname));

// --- ROTAS COM RATE LIMIT ---

// 1. Rota de PDF (Puppeteer)
app.get('/api/capture', limiter, async (req, res) => {
    const url = req.query.url;
    console.log(`📡 Requisição de PDF: ${req.ip} para: ${url}`);
    
    if (!url) return res.status(400).send('URL necessária');

    let browser;
    try {
        browser = await puppeteer.launch({
            headless: true,
            executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || null,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        });

        const page = await browser.newPage();
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36');
        await page.setViewport({ width: 1280, height: 800 });
        await page.goto(url, { waitUntil: 'networkidle0', timeout: 90000 });

        const rawTitle = await page.title();
        const safeTitle = (rawTitle || 'pagina_capturada')
            .normalize('NFD').replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-z0-9]/gi, '_')
            .replace(/_+/g, '_')
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

// 2. Rota de HTML (Fetch interno)
app.get('/api/capture-html', limiter, async (req, res) => {
    const url = req.query.url;
    console.log(`📡 Requisição de HTML: ${req.ip} para: ${url}`);
    
    if (!url) return res.status(400).send('URL necessária');

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        const html = await response.text();
        res.send(html);
    } catch (e) {
        console.error("❌ Erro ao buscar HTML:", e.message);
        res.status(500).send(`Erro ao buscar HTML: ${e.message}`);
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 SERVIDOR RODANDO EM: http://localhost:${PORT}`);
});