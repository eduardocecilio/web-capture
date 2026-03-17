const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const path = require('path');
const rateLimit = require('express-rate-limit');
const { URL } = require('url');
const dns = require('dns');
const { promisify } = require('util');
const dnsResolve = promisify(dns.resolve4);
const app = express();

// --- VALIDAÇÃO DE URL (proteção contra SSRF) ---

const BLOCKED_IP_RANGES = [
    /^127\./,                   // Loopback
    /^10\./,                    // Rede privada classe A
    /^172\.(1[6-9]|2\d|3[01])\./, // Rede privada classe B
    /^192\.168\./,              // Rede privada classe C
    /^169\.254\./,              // Link-local (AWS metadata etc.)
    /^0\./,                     // Rede atual
    /^100\.(6[4-9]|[7-9]\d|1[0-2]\d)\./, // Carrier-grade NAT
    /^::1$/,                    // IPv6 loopback
    /^fc00:/,                   // IPv6 privado
    /^fe80:/,                   // IPv6 link-local
];

async function validateUrl(urlString) {
    let parsed;
    try {
        parsed = new URL(urlString);
    } catch {
        throw new Error('URL inválida.');
    }

    // Apenas HTTP e HTTPS
    if (!['http:', 'https:'].includes(parsed.protocol)) {
        throw new Error('Apenas protocolos HTTP e HTTPS são permitidos.');
    }

    const hostname = parsed.hostname;

    // Bloqueia IPs diretos em ranges privados
    for (const range of BLOCKED_IP_RANGES) {
        if (range.test(hostname)) {
            throw new Error('URLs para redes internas não são permitidas.');
        }
    }

    // Resolve DNS e verifica se o IP resolvido é privado
    try {
        const addresses = await dnsResolve(hostname);
        for (const addr of addresses) {
            for (const range of BLOCKED_IP_RANGES) {
                if (range.test(addr)) {
                    throw new Error('URLs para redes internas não são permitidas.');
                }
            }
        }
    } catch (e) {
        if (e.message.includes('redes internas')) throw e;
        // Se DNS falhar, deixa o Puppeteer/fetch lidar com o erro
    }

    return parsed.href;
}

// --- CONFIGURAÇÃO DO RATE LIMIT ---

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 10,
    validate: { xForwardedForHeader: false },
    handler: (req, res) => {
        console.warn(`⚠️ BLOQUEADO: IP ${req.ip} atingiu o limite.`);
        res.status(429).send('Muitas requisições, tente novamente em 15 minutos.');
    },
    standardHeaders: true,
    legacyHeaders: false,
    skip: () => process.env.NODE_ENV === 'development'
});

// --- SEGURANÇA E MIDDLEWARES ---

app.set('trust proxy', 1);
app.disable('x-powered-by');

// Headers de segurança
app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
    res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
    next();
});

app.use(cors({
    origin: process.env.CORS_ORIGIN || '*',
    exposedHeaders: ['X-Page-Title']
}));

// Servir arquivos estáticos (apenas a pasta /static, protegendo o código-fonte)
app.use('/static', express.static(path.join(__dirname, 'static')));
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// --- ROTAS COM RATE LIMIT ---

// 1. Rota de PDF (Puppeteer)
app.get('/api/capture', limiter, async (req, res) => {
    const rawUrl = req.query.url;
    console.log(`📡 Requisição de PDF: ${req.ip} para: ${rawUrl}`);

    if (!rawUrl) return res.status(400).send('URL necessária.');

    let validatedUrl;
    try {
        validatedUrl = await validateUrl(rawUrl);
    } catch (e) {
        return res.status(400).send(e.message);
    }

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
        await page.goto(validatedUrl, { waitUntil: 'networkidle0', timeout: 90000 });

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
        res.status(500).send('Erro ao gerar o PDF. Verifique se a URL é válida e acessível.');
    }
});

// 2. Rota de HTML (Fetch interno)
app.get('/api/capture-html', limiter, async (req, res) => {
    const rawUrl = req.query.url;
    console.log(`📡 Requisição de HTML: ${req.ip} para: ${rawUrl}`);

    if (!rawUrl) return res.status(400).send('URL necessária.');

    let validatedUrl;
    try {
        validatedUrl = await validateUrl(rawUrl);
    } catch (e) {
        return res.status(400).send(e.message);
    }

    try {
        const response = await fetch(validatedUrl);
        if (!response.ok) throw new Error(`Status: ${response.status}`);
        const html = await response.text();
        res.send(html);
    } catch (e) {
        console.error("❌ Erro ao buscar HTML:", e.message);
        res.status(500).send('Erro ao buscar o HTML. Verifique se a URL é válida e acessível.');
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 SERVIDOR RODANDO EM: http://localhost:${PORT}`);
});
