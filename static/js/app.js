// Form handling and PDF/HTML conversion logic
document.addEventListener('DOMContentLoaded', function() {
    const convertForm = document.getElementById('convertForm');
    const submitBtn = document.getElementById('submitBtn');
    
    let conversionData = {
        pdfBlob: null,
        htmlContent: null,
        downloadPdf: false,
        downloadHtml: false
    };

    // Handle form submission
    convertForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Gather form data
        const url = document.getElementById('url').value.trim();
        const downloadPdf = document.getElementById('downloadPdfCheckbox').checked;
        const downloadHtml = document.getElementById('downloadHtmlCheckbox').checked;

        // Validate inputs
        if (!url) {
            showAlert('Por favor, insira uma URL válida.', 'error');
            return;
        }

        if (!downloadPdf && !downloadHtml) {
            showAlert('Selecione pelo menos um formato para download.', 'error');
            return;
        }

        // Store selections
        conversionData.downloadPdf = downloadPdf;
        conversionData.downloadHtml = downloadHtml;

        // Reset UI state
        hideAllCards();
        showProgressCard();
        submitBtn.disabled = true;

        try {
            // Fetch the webpage content
            updateProgress('Carregando página...', 20);
            const pageContent = await fetchPageContent(url);

            // Extrai título
            const parser = new DOMParser();
            const doc = parser.parseFromString(pageContent, 'text/html');
            let pageTitle = doc.querySelector('title')?.innerText || 'pagina-convertida';
            pageTitle = pageTitle.replace(/\s+/g, '_').replace(/[^\w\-]/g, '');

            // Renderiza conteúdo original visualmente para PDF
            let previewContainer = document.getElementById('previewContainer');
            if (previewContainer) previewContainer.remove();
            previewContainer = document.createElement('div');
            previewContainer.id = 'previewContainer';
            previewContainer.style.position = 'fixed';
            previewContainer.style.top = '-9999px';
            previewContainer.style.left = '-9999px';
            previewContainer.style.width = '800px';
            previewContainer.style.background = '#fff';
            previewContainer.style.zIndex = '9999';
            previewContainer.innerHTML = pageContent;
            document.body.appendChild(previewContainer);

            conversionData.htmlContent = pageContent;
            conversionData.pageTitle = pageTitle;

            // Generate PDF if selected
            if (downloadPdf) {
                updateProgress('Gerando PDF...', 75);
                const pdfBlob = await generatePDF(previewContainer, pageTitle);
                conversionData.pdfBlob = pdfBlob;
            }

            // Remove preview
            previewContainer.remove();

            // Success
            updateProgress('Conversão concluída!', 100);
            setTimeout(() => {
                hideProgressCard();
                showResultsCard();
                submitBtn.disabled = false;
            }, 500);

        } catch (error) {
            console.error('Error during conversion:', error);
            hideProgressCard();
            showErrorCard(error.message || 'Erro ao converter a página. Verifique a URL e tente novamente.');
            submitBtn.disabled = false;
        }
    });

    // Fetch page content with multiple CORS methods
    async function fetchPageContent(url) {
        // Validate URL format
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            throw new Error('URL deve começar com http:// ou https://');
        }

        const corsProxies = [
            `https://cors-anywhere.herokuapp.com/${url}`,
            `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`,
            url // Try without proxy last
        ];

        let lastError = null;

        for (const proxyUrl of corsProxies) {
            try {
                const response = await fetch(proxyUrl, {
                    method: 'GET',
                    headers: {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                });

                if (response.ok) {
                    return await response.text();
                }
            } catch (error) {
                lastError = error;
                console.log(`Proxy failed: ${proxyUrl}`);
                continue;
            }
        }

        throw new Error(
            'Não foi possível acessar a URL fornecida. Possíveis razões:\n' +
            '• O site pode estar bloqueando requisições externas\n' +
            '• Verifique se a URL está correta (ex: https://www.exemplo.com)\n' +
            '• O site pode estar temporariamente indisponível'
        );
    }

    // Process HTML: replace videos with links, sanitize content
    function processHTML(htmlContent) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');

        // Extrai o título da página
        let pageTitle = doc.querySelector('title')?.innerText || 'pagina-convertida';
        pageTitle = pageTitle.replace(/\s+/g, '_').replace(/[^\w\-]/g, '');

        // Remove script tags
        doc.querySelectorAll('script').forEach(script => script.remove());
        // Remove style tags (keep external stylesheets)
        doc.querySelectorAll('style').forEach(style => style.remove());
        // Remove noscript tags
        doc.querySelectorAll('noscript').forEach(noscript => noscript.remove());

        // Replace video elements with links
        doc.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"], iframe[src*="dailymotion"]').forEach(video => {
            const link = document.createElement('p');
            const videoSrc = video.src || video.getAttribute('data-src') || '#';
            link.innerHTML = `<strong>[VÍDEO]</strong> <a href="${videoSrc}" target="_blank">${videoSrc}</a>`;
            link.className = 'alert alert-info';
            video.parentNode.replaceChild(link, video);
        });

        // Limpa classes e ids desnecessários do body
        doc.body.removeAttribute('class');
        doc.body.removeAttribute('id');

        // Adiciona um cabeçalho simples
        const header = document.createElement('header');
        header.innerHTML = `<h1 style="text-align:center; margin: 24px 0;">${pageTitle.replace(/_/g, ' ')}</h1>`;
        doc.body.prepend(header);

        // Remove rodapés e menus laterais comuns
        doc.querySelectorAll('footer, aside, nav').forEach(el => el.remove());

        // Retorna HTML limpo e título
        return { processedHtml: doc.documentElement.outerHTML, pageTitle };
    }

    // Generate PDF from HTML using html2pdf
    async function generatePDF(htmlContent) {
        return new Promise((resolve, reject) => {
            try {
                const options = {
                    margin: 10,
                    filename: `${conversionData.pageTitle}.pdf`,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2, logging: false },
                    jsPDF: { 
                        orientation: 'p',
                        unit: 'mm',
                        format: 'a4'
                    }
                };

                html2pdf()
                    .set(options)
                    .from(htmlContent)
                    .outputPdf('blob')
                    .then(blob => {
                        resolve(blob);
                    })
                    .catch(error => {
                        reject(new Error('Erro ao gerar PDF: ' + error.message));
                    });
            } catch (error) {
                reject(error);
            }
        });
    }

    // UI Helper functions
    function updateProgress(message, percent) {
        document.getElementById('progressMessage').textContent = message;
        document.getElementById('progressPercent').textContent = percent + '%';
        document.getElementById('progressBar').style.width = percent + '%';
        document.getElementById('progressBar').setAttribute('aria-valuenow', percent);
    }

    function showProgressCard() {
        document.getElementById('progressCard').style.display = 'block';
        updateProgress('Iniciando...', 0);
    }

    function hideProgressCard() {
        document.getElementById('progressCard').style.display = 'none';
    }

    function showResultsCard() {
        const container = document.getElementById('downloadButtonsContainer');
        container.innerHTML = '';

        if (conversionData.downloadPdf && conversionData.pdfBlob) {
            const pdfBtn = document.createElement('button');
            pdfBtn.type = 'button';
            pdfBtn.className = 'btn btn-success btn-lg w-100 mb-2';
            pdfBtn.innerHTML = `<i data-feather="file-pdf" class="me-2"></i>Baixar PDF`;
            pdfBtn.onclick = () => downloadPDF();
            container.appendChild(pdfBtn);
            feather.replace();
        }

        if (conversionData.downloadHtml && conversionData.htmlContent) {
            const htmlBtn = document.createElement('button');
            htmlBtn.type = 'button';
            htmlBtn.className = 'btn btn-info btn-lg w-100';
            htmlBtn.innerHTML = `<i data-feather="file-text" class="me-2"></i>Baixar HTML`;
            htmlBtn.onclick = () => downloadHTML();
            container.appendChild(htmlBtn);
            feather.replace();
        }

        document.getElementById('resultsCard').style.display = 'block';
    }

    function hideResultsCard() {
        document.getElementById('resultsCard').style.display = 'none';
    }

    function showErrorCard(message) {
        document.getElementById('errorCard').style.display = 'block';
        document.getElementById('errorMessage').textContent = message;
    }

    function hideErrorCard() {
        document.getElementById('errorCard').style.display = 'none';
    }

    function hideAllCards() {
        hideProgressCard();
        hideResultsCard();
        hideErrorCard();
    }

    function showAlert(message, type) {
        const alertContainer = document.getElementById('alertContainer');
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'info'} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        alertContainer.appendChild(alertDiv);

        // Auto-remove alert after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Download functions
    function downloadPDF() {
        if (conversionData.pdfBlob) {
            const url = URL.createObjectURL(conversionData.pdfBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${conversionData.pageTitle}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    }

    function downloadHTML() {
        if (conversionData.htmlContent) {
            const blob = new Blob([conversionData.htmlContent], { type: 'text/html;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${conversionData.pageTitle}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    }

    // Make download functions global
    window.downloadPDF = downloadPDF;
    window.downloadHTML = downloadHTML;
});

// Global function for resetting form
function resetForm() {
    document.getElementById('convertForm').reset();
    document.getElementById('progressCard').style.display = 'none';
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('errorCard').style.display = 'none';
    document.getElementById('url').focus();
}
