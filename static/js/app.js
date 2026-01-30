document.addEventListener('DOMContentLoaded', function () {
    const convertForm = document.getElementById('convertForm');
    const submitBtn = document.getElementById('submitBtn');

    let conversionData = {
        pdfBlob: null,
        htmlContent: null,
        pageTitle: 'pagina-capturada'
    };

    convertForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const url = document.getElementById('url').value.trim();
        const downloadPdf = document.getElementById('downloadPdfCheckbox').checked;
        const downloadHtml = document.getElementById('downloadHtmlCheckbox').checked;

        if (!url) return alert('Insira uma URL válida.');

        hideAllCards();
        document.getElementById('progressCard').style.display = 'block';
        updateProgress('Iniciando comunicação...', 10);
        submitBtn.disabled = true;

        try {
            // 1. Captura de HTML
            if (downloadHtml) {
                updateProgress('Capturando código HTML...', 30);
                const resp = await fetch(`https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`);
                const htmlText = await resp.text();
                conversionData.htmlContent = htmlText;

                const parser = new DOMParser();
                const doc = parser.parseFromString(htmlText, 'text/html');
                const parsedTitle = doc.querySelector('title')?.innerText;
                if (parsedTitle) {
                    // Mesma lógica de limpeza do servidor
                    conversionData.pageTitle = parsedTitle
                        .normalize('NFD').replace(/[\u0300-\u036f]/g, "")
                        .replace(/[^a-z0-9]/gi, '_')
                        .replace(/_+/g, '_')
                        .toLowerCase();
                }
            }

            // 2. Captura de PDF
            if (downloadPdf) {
                updateProgress('Puppeteer renderizando PDF...', 60);
                const response = await fetch(`/api/capture?url=${encodeURIComponent(url)}`);

                if (!response.ok) throw new Error('O servidor Puppeteer falhou.');

                const serverTitle = response.headers.get('X-Page-Title');
                if (serverTitle) {
                    conversionData.pageTitle = serverTitle;
                }

                conversionData.pdfBlob = await response.blob();
            }

            updateProgress('Tudo pronto!', 100);
            setTimeout(() => {
                document.getElementById('progressCard').style.display = 'none';
                showResultsCard(downloadPdf, downloadHtml);
                submitBtn.disabled = false;
            }, 800);

        } catch (error) {
            console.error(error);
            document.getElementById('progressCard').style.display = 'none';
            document.getElementById('errorCard').style.display = 'block';
            document.getElementById('errorMessage').innerText = error.message;
            submitBtn.disabled = false;
        }
    });

    function updateProgress(msg, pct) {
        document.getElementById('progressMessage').innerText = msg;
        document.getElementById('progressBar').style.width = pct + '%';
    }

    function showResultsCard(hasPdf, hasHtml) {
        document.getElementById('resultsCard').style.display = 'block';
        const container = document.getElementById('downloadButtonsContainer');
        container.innerHTML = '';

        if (hasPdf && conversionData.pdfBlob) {
            container.innerHTML += `<button onclick="downloadFile('pdf')" class="btn btn-success w-100 mb-2">Baixar PDF</button>`;
        }
        if (hasHtml && conversionData.htmlContent) {
            container.innerHTML += `<button onclick="downloadFile('html')" class="btn btn-info w-100">Baixar HTML</button>`;
        }
    }

    window.downloadFile = function (type) {
        const blob = type === 'pdf' ? conversionData.pdfBlob : new Blob([conversionData.htmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${conversionData.pageTitle}.${type}`;
        a.click();
        URL.revokeObjectURL(url);
    };

    function hideAllCards() {
        ['progressCard', 'resultsCard', 'errorCard'].forEach(id => {
            document.getElementById(id).style.display = 'none';
        });
    }
});