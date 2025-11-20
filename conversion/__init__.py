"""
Motor de conversão simplificado para Vercel (sem Playwright).
Usa httpx para buscar HTML e WeasyPrint para gerar PDF.
"""
from dataclasses import dataclass
from typing import Optional
import re
import logging
from io import BytesIO

import httpx
from weasyprint import HTML, CSS

logger = logging.getLogger(__name__)


@dataclass
class ConversionSettings:
    """Configurações de conversão"""
    url: str
    timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


@dataclass
class ConversionResult:
    """Resultado da conversão"""
    success: bool
    pdf_bytes: Optional[bytes] = None
    html_content: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None


class WebPageConverter:
    """Conversor de páginas web para PDF usando httpx + WeasyPrint"""
    
    def __init__(self, settings: ConversionSettings):
        self.settings = settings
    
    def run(self) -> ConversionResult:
        """Executa a conversão"""
        try:
            # Buscar HTML via HTTP
            logger.info(f"Buscando página: {self.settings.url}")
            headers = {"User-Agent": self.settings.user_agent}
            
            response = httpx.get(
                self.settings.url,
                headers=headers,
                follow_redirects=True,
                timeout=self.settings.timeout
            )
            response.raise_for_status()
            html = response.text
            
            logger.info("HTML buscado com sucesso")
            
            # Extrair título
            title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            title = title_match.group(1) if title_match else "Untitled"
            
            # Limpar HTML para uso offline
            clean_html = self.clean_html_for_offline(html, title)
            
            # Gerar PDF com WeasyPrint
            logger.info("Gerando PDF...")
            pdf_bytes = self._generate_pdf(clean_html)
            
            logger.info(f"PDF gerado com sucesso ({len(pdf_bytes)} bytes)")
            
            return ConversionResult(
                success=True,
                pdf_bytes=pdf_bytes,
                html_content=clean_html,
                title=title
            )
        except httpx.HTTPError as e:
            error_msg = f"Erro HTTP ao buscar página: {str(e)}"
            logger.error(error_msg)
            return ConversionResult(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"Erro na conversão: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return ConversionResult(success=False, error=error_msg)
    
    def _generate_pdf(self, html: str) -> bytes:
        """Gera PDF a partir do HTML"""
        pdf_file = BytesIO()
        HTML(string=html, base_url=self.settings.url).write_pdf(pdf_file)
        return pdf_file.getvalue()
    
    def clean_html_for_offline(self, html: str, title: str) -> str:
        """Remove scripts desnecessários e prepara HTML para uso offline"""
        
        # Fix DOCTYPE
        html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)
        html = '<!DOCTYPE html>\n' + html
        
        # Remover scripts Replit/tracking
        html = re.sub(
            r'<script[^>]*>.*?(__replit|gtag|analytics).*?</script>',
            '',
            html,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Remover scripts inline de tracking
        html = re.sub(
            r'<script[^>]*(src=["\']?.*?(__replit|google-analytics|analytics)[^"\']*["\']?)[^>]*></script>',
            '',
            html,
            flags=re.IGNORECASE
        )
        
        # Adicionar banner com informações da fonte (antes de </body>)
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        safe_url = self.settings.url.replace('"', '&quot;').replace("'", "&#39;")
        
        banner_html = f'''
<div style="font: 12px/1.4 -apple-system, Segoe UI, Roboto, Arial, sans-serif; 
            background: #f5f5f7; color: #111; padding: 8px 12px; border: 1px solid #e5e5e5; 
            margin: 16px auto; max-width: 1000px; border-radius: 4px;">
    <strong>Fonte:</strong> <a href="{safe_url}" target="_blank" rel="noopener noreferrer">{safe_url}</a> 
    &nbsp; · &nbsp; 
    <strong>Convertido:</strong> {now}
</div>
'''
        
        html = re.sub(
            r'</body>',
            banner_html + '</body>',
            html,
            flags=re.IGNORECASE,
            count=1
        )
        
        return html
