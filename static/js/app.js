let currentTaskId = null;
let pollInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('convertForm');
    const submitBtn = document.getElementById('submitBtn');
    const progressCard = document.getElementById('progressCard');
    const resultsCard = document.getElementById('resultsCard');
    const errorCard = document.getElementById('errorCard');
    
    form.addEventListener('submit', handleFormSubmit);
});

async function handleFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitBtn = document.getElementById('submitBtn');
    const url = form.url.value.trim();
    
    // Validate URL
    if (!isValidUrl(url)) {
        showError('Por favor, insira uma URL válida (incluindo http:// ou https://)');
        return;
    }
    
    // Reset UI
    resetUI();
    
    // Show loading state
    setButtonLoading(submitBtn, true);
    
    try {
        const formData = new FormData(form);
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.task_id) {
            currentTaskId = data.task_id;
            showProgressCard();
            startPolling();
        } else {
            throw new Error('ID da tarefa não retornado');
        }
        
    } catch (error) {
        console.error('Erro na conversão:', error);
        showError('Erro ao iniciar conversão: ' + error.message);
        setButtonLoading(submitBtn, false);
    }
}

function startPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    pollInterval = setInterval(checkStatus, 1000);
    checkStatus(); // Check immediately
}

async function checkStatus() {
    if (!currentTaskId) return;
    
    try {
        const response = await fetch(`/status/${currentTaskId}`);
        
        if (!response.ok) {
            throw new Error(`Erro ao verificar status: ${response.status}`);
        }
        
        const data = await response.json();
        
        updateProgress(data);
        
        if (data.status === 'completed') {
            clearInterval(pollInterval);
            showResults(data);
        } else if (data.status === 'error') {
            clearInterval(pollInterval);
            showError(data.message || 'Erro desconhecido na conversão');
        }
        
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        clearInterval(pollInterval);
        showError('Erro ao verificar progresso: ' + error.message);
    }
}

function updateProgress(data) {
    const progressBar = document.getElementById('progressBar');
    const progressMessage = document.getElementById('progressMessage');
    const progressPercent = document.getElementById('progressPercent');
    
    const progress = data.progress || 0;
    
    progressBar.style.width = progress + '%';
    progressBar.setAttribute('aria-valuenow', progress);
    
    progressMessage.textContent = data.message || 'Processando...';
    progressPercent.textContent = Math.round(progress) + '%';
}

function showProgressCard() {
    document.getElementById('progressCard').style.display = 'block';
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('errorCard').style.display = 'none';
}

function showResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const downloadPdf = document.getElementById('downloadPdf');
    const downloadHtml = document.getElementById('downloadHtml');
    const submitBtn = document.getElementById('submitBtn');
    
    // Update download links
    downloadPdf.href = `/download/${data.pdf_file}`;
    downloadHtml.href = `/download/${data.html_file}`;
    
    // Show results card
    resultsCard.style.display = 'block';
    document.getElementById('progressCard').style.display = 'none';
    
    // Reset button
    setButtonLoading(submitBtn, false);
    
    // Re-initialize feather icons
    feather.replace();
}

function showError(message) {
    const errorCard = document.getElementById('errorCard');
    const errorMessage = document.getElementById('errorMessage');
    const submitBtn = document.getElementById('submitBtn');
    
    errorMessage.textContent = message;
    errorCard.style.display = 'block';
    
    document.getElementById('progressCard').style.display = 'none';
    document.getElementById('resultsCard').style.display = 'none';
    
    setButtonLoading(submitBtn, false);
    
    // Re-initialize feather icons
    feather.replace();
}

function resetForm() {
    // Stop polling
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
    
    currentTaskId = null;
    
    // Reset UI
    resetUI();
    
    // Reset form
    document.getElementById('convertForm').reset();
    
    // Reset advanced options
    const advancedOptions = document.getElementById('advancedOptions');
    if (advancedOptions.classList.contains('show')) {
        bootstrap.Collapse.getInstance(advancedOptions).hide();
    }
    
    // Reset button
    const submitBtn = document.getElementById('submitBtn');
    setButtonLoading(submitBtn, false);
    
    // Scroll to top
    window.scrollTo(0, 0);
}

function resetUI() {
    document.getElementById('progressCard').style.display = 'none';
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('errorCard').style.display = 'none';
}

function setButtonLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.classList.add('btn-loading');
        const icon = button.querySelector('i');
        if (icon) icon.style.display = 'none';
        const textSpan = button.querySelector('.btn-text') || button;
        if (textSpan !== button) {
            textSpan.textContent = 'Convertendo...';
        } else {
            button.innerHTML = '<span class="btn-text">Convertendo...</span>';
        }
    } else {
        button.disabled = false;
        button.classList.remove('btn-loading');
        button.innerHTML = '<i data-feather="download" class="me-2"></i>Converter Página';
        feather.replace();
    }
}

function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Auto-cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});
