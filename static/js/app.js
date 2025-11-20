// Form handling and PDF conversion logic
document.addEventListener('DOMContentLoaded', function() {
    const convertForm = document.getElementById('convertForm');
    const submitBtn = document.getElementById('submitBtn');
    const progressCard = document.getElementById('progressCard');
    const resultsCard = document.getElementById('resultsCard');
    const errorCard = document.getElementById('errorCard');
    const downloadPdf = document.getElementById('downloadPdf');
    const downloadHtml = document.getElementById('downloadHtml');

    let conversionData = {
        pdfBlob: null,
        htmlContent: null
    };

    // Handle form submission
    convertForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Gather form data
        const formData = new FormData(convertForm);
        const url = formData.get('url');

        if (!url) {
            showAlert('Por favor, insira uma URL válida.', 'error');
            return;
        }

        // Reset UI state
        hideAllCards();
        showProgressCard();

        try {
            // Fetch the webpage content
            updateProgress('Carregando página...', 20);
            const pageContent = await fetchPageContent(url);

            // Process HTML (replace videos with links, clean up content)
            updateProgress('Processando conteúdo...', 50);
            const processedHtml = processHTML(pageContent);
            conversionData.htmlContent = processedHtml;

            // Generate PDF from HTML
            updateProgress('Gerando PDF...', 75);
            const pdfBlob = await generatePDF(processedHtml);
            conversionData.pdfBlob = pdfBlob;

            // Success
            updateProgress('Conversão concluída!', 100);
            setTimeout(() => {
                hideProgressCard();
                showResultsCard();
            }, 500);

        } catch (error) {
            console.error('Error during conversion:', error);
            hideProgressCard();
            showErrorCard(error.message || 'Erro ao converter a página. Tente novamente.');
        }
    });

    // Download PDF
    downloadPdf.addEventListener('click', function(e) {
        e.preventDefault();
        if (conversionData.pdfBlob) {
            const url = URL.createObjectURL(conversionData.pdfBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'pagina-convertida.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    });

    // Download HTML
    downloadHtml.addEventListener('click', function(e) {
        e.preventDefault();
        if (conversionData.htmlContent) {
            const blob = new Blob([conversionData.htmlContent], { type: 'text/html;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'pagina-convertida.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    });

    // Fetch page content using a CORS-enabled API or direct fetch
    async function fetchPageContent(url) {
        try {
            // Using a CORS proxy to fetch the page
            const corsProxy = 'https://cors-anywhere.herokuapp.com/';
            const response = await fetch(corsProxy + url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`Erro ao carregar a página: ${response.status}`);
            }

            return await response.text();
        } catch (error) {
            console.error('Fetch error:', error);
            throw new Error('Não foi possível acessar a URL fornecida. Verifique o endereço.');
        }
    }

    // Process HTML: replace videos with links, sanitize content
    function processHTML(htmlContent) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');

        // Remove script tags
        const scripts = doc.querySelectorAll('script');
        scripts.forEach(script => script.remove());

        // Remove style tags (keep external stylesheets)
        const styles = doc.querySelectorAll('style');
        styles.forEach(style => style.remove());

        // Replace video elements with links
        const videos = doc.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"]');
        videos.forEach(video => {
            const link = document.createElement('a');
            link.href = video.src || video.getAttribute('data-src') || '#';
            link.textContent = `[Vídeo: ${video.src || video.getAttribute('data-src') || 'Link do vídeo'}]`;
            link.style.display = 'block';
            link.style.marginBottom = '10px';
            video.parentNode.replaceChild(link, video);
        });

        return doc.documentElement.outerHTML;
    }

    // Generate PDF from HTML using html2pdf
    async function generatePDF(htmlContent) {
        return new Promise((resolve, reject) => {
            try {
                const element = document.createElement('div');
                element.innerHTML = htmlContent;

                const options = {
                    margin: 10,
                    filename: 'pagina-convertida.pdf',
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2 },
                    jsPDF: { 
                        orientation: document.getElementById('landscape').checked ? 'l' : 'p',
                        unit: 'mm',
                        format: document.getElementById('format').value
                    }
                };

                html2pdf()
                    .set(options)
                    .from(element)
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
    }

    function showProgressCard() {
        progressCard.style.display = 'block';
        updateProgress('Iniciando...', 0);
    }

    function hideProgressCard() {
        progressCard.style.display = 'none';
    }

    function showResultsCard() {
        resultsCard.style.display = 'block';
    }

    function hideResultsCard() {
        resultsCard.style.display = 'none';
    }

    function showErrorCard(message) {
        errorCard.style.display = 'block';
        document.getElementById('errorMessage').textContent = message;
    }

    function hideErrorCard() {
        errorCard.style.display = 'none';
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
});

// Global function for resetting form
function resetForm() {
    document.getElementById('convertForm').reset();
    document.getElementById('progressCard').style.display = 'none';
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('errorCard').style.display = 'none';
    document.getElementById('convertForm').scrollIntoView({ behavior: 'smooth' });
}
