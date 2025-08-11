import os
import logging
import traceback
import threading
import time
import uuid
from urllib.parse import urlparse
from pathlib import Path
from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app, db
from models import ScheduledConversion
from conversor_sites.config import Settings
from conversor_sites.cli import VIDEO_IFRAME_HINTS
import re

def sanitize_filename(title):
    """Sanitize the page title to use as filename"""
    if not title:
        return "webpage"
    # Remove/replace invalid characters including URL special chars
    title = re.sub(r'[<>:"/\\|?*&%=+\[\]{}()#@!$^`~,;]', '_', title)
    # Remove extra whitespace and limit length severely for long URLs
    title = re.sub(r'\s+', '_', title.strip())
    # Limit to 30 characters max to avoid filesystem issues
    title = title[:30]
    return title or "webpage"
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from datetime import datetime, timedelta

# Set environment variables to bypass Playwright dependency checks
os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '1'
os.environ['PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS'] = '1'

# Global dictionary to store conversion statuses
conversion_status = {}

def is_valid_url(url):
    """Validate if the provided string is a valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def perform_conversion(task_id, url, settings):
    """Perform the actual conversion in a background thread"""
    try:
        conversion_status[task_id] = {
            'status': 'processing', 
            'progress': 10,
            'message': 'Inicializando navegador...'
        }
        
        output_dir = Path("output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Limpar arquivos antigos para economizar espaço (manter apenas os últimos 3)
        try:
            existing_files = list(output_dir.glob("*"))
            if len(existing_files) > 6:  # PDF + HTML = 2 arquivos por conversão, manter 3 conversões
                # Ordenar por data de modificação e remover os mais antigos
                existing_files.sort(key=lambda x: x.stat().st_mtime)
                for old_file in existing_files[:-6]:
                    old_file.unlink(missing_ok=True)
                    logging.info(f"Arquivo antigo removido: {old_file.name}")
        except Exception as e:
            logging.warning(f"Erro ao limpar arquivos antigos: {e}")

        with sync_playwright() as p:
            conversion_status[task_id].update({
                'progress': 20,
                'message': 'Abrindo navegador...'
            })
            
            # Try Firefox first since it doesn't have the libgbm dependency issue
            try:
                logging.info("Tentando usar Firefox...")
                browser = p.firefox.launch(headless=True)
                browser_type = 'firefox'
            except Exception as firefox_error:
                logging.warning(f"Firefox falhou: {firefox_error}")
                logging.info("Tentando usar WebKit...")
                try:
                    browser = p.webkit.launch(headless=True)
                    browser_type = 'webkit'
                except Exception as webkit_error:
                    logging.warning(f"WebKit falhou: {webkit_error}")
                    # Como último recurso, tentar Chromium com configuração mínima
                    logging.info("Tentando Chromium como último recurso...")
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-dev-shm-usage',
                            '--virtual-time-budget=10000'
                        ],
                        env={
                            **os.environ,
                            'PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS': '1'
                        }
                    )
                    browser_type = 'chromium'
            vw = settings.viewport_w or 1366
            vh = settings.viewport_h or 900
            context = browser.new_context(viewport={"width": vw, "height": vh})
            
            if settings.extra_headers:
                context.set_extra_http_headers(settings.extra_headers)
            page = context.new_page()

            conversion_status[task_id].update({
                'progress': 30,
                'message': 'Carregando página...'
            })

            # LOGIN opcional
            if settings.login_url and settings.username and settings.password:
                conversion_status[task_id].update({
                    'message': 'Realizando login...'
                })
                
                page.goto(settings.login_url, wait_until="domcontentloaded")
                try:
                    page.wait_for_selector(settings.user_field or "#username", timeout=10000)
                    page.fill(settings.user_field or "#username", settings.username)
                    page.wait_for_selector(settings.pass_field or "#password", timeout=10000)
                    page.fill(settings.pass_field or "#password", settings.password)
                    if settings.submit_selector:
                        page.click(settings.submit_selector)
                    else:
                        page.keyboard.press("Enter")
                    page.wait_for_load_state("networkidle", timeout=20000)
                except PWTimeoutError:
                    logging.warning("Não foi possível concluir o login com os seletores informados.")

            # Abrir URL alvo
            page.goto(url, wait_until="domcontentloaded")
            
            conversion_status[task_id].update({
                'progress': 50,
                'message': 'Aguardando carregamento completo...'
            })
            
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except PWTimeoutError:
                pass
                
            if settings.wait_selector:
                try:
                    page.wait_for_selector(settings.wait_selector, timeout=20000)
                except PWTimeoutError:
                    logging.warning(f"Seletor {settings.wait_selector!r} não apareceu a tempo.")
                    
            if settings.wait_ms and int(settings.wait_ms) > 0:
                page.wait_for_timeout(int(settings.wait_ms))

            conversion_status[task_id].update({
                'progress': 60,
                'message': 'Preparando conteúdo...'
            })

            # Banner com link da página original (vai para o PDF)
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            safe_url = url
            page.evaluate(f"""
                (function() {{
                  if (document.querySelector('.___src_banner')) return;
                  const b = document.createElement('div');
                  b.className = '___src_banner';
                  b.style.cssText = 'font:12px/1.4 -apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#f5f5f7;color:#111;padding:8px 12px;border:1px solid #e5e5e5;margin:8px auto;max-width:1000px;';
                  b.innerHTML = '<strong>Fonte:</strong> <a href="{safe_url}" target="_blank" rel="noopener">{safe_url}</a> &nbsp; · &nbsp; <strong>Gerado:</strong> {now}';
                  const holder = document.body || document.documentElement;
                  holder.insertBefore(b, holder.firstChild);
                }})();
            """)

            # Capturar título da página e limpar para nome de arquivo
            title = page.title()
            filename_base = sanitize_filename(title)
            pdf_path = output_dir / f"{filename_base}.pdf"
            snapshot_path = output_dir / f"{filename_base}.snapshot.html"

            conversion_status[task_id].update({
                'progress': 70,
                'message': 'Processando vídeos...'
            })

            # Estilo básico para caixa de link de vídeo
            page.evaluate("""() => {
                const id='___video_link_style';
                if(!document.getElementById(id)){
                    const st=document.createElement('style'); st.id=id;
                    st.textContent = `
                    .___vid_box{
                      border:1px dashed #bbb; padding:10px; text-align:center; margin:8px 0;
                      font: 13px/1.4 -apple-system,Segoe UI,Roboto,Arial,sans-serif; color:#222;
                      background:#fafafa;
                    }
                    .___vid_box a{ text-decoration:none; }
                    .___vid_box .play{ font-weight:600; margin-right:.35rem; }
                    `;
                    document.head.appendChild(st);
                }
            }""")

            # Substituir elementos de vídeo por uma caixa com link
            def replace_videos_and_iframes():
                # Substitui <video>
                videos = page.query_selector_all("video")
                for i, el in enumerate(videos):
                    try:
                        src = el.get_attribute("src") or el.get_attribute("poster") or ""
                        if not src:
                            inner_src = el.eval_on_selector("source","e=>e?e.getAttribute('src'):null")
                            if inner_src: src = inner_src
                        href = src or "#"
                        el.evaluate("(e,i)=>e.dataset._tmpSel='vid_'+i", i)
                        sel = f"[data-_tmp-sel='vid_{i}']"
                        page.evaluate(
                            """([selector, href])=>{
                                const t = document.querySelector(selector);
                                if(!t) return;
                                const box = document.createElement('div');
                                box.className = '___vid_box';
                                if(href && href !== '#'){
                                  box.innerHTML = '<span class="play">▶</span><a href="'+href+'" target="_blank" rel="noopener">'+href+'</a>';
                                } else {
                                  box.textContent = 'Vídeo (sem link detectado)';
                                }
                                t.replaceWith(box);
                            }""",
                            [sel, href]
                        )
                    except Exception as e:
                        logging.error(f"Falha ao substituir <video>: {e}")

                # Substitui iframes de players conhecidos
                iframes = page.query_selector_all("iframe")
                for i, el in enumerate(iframes):
                    try:
                        src = (el.get_attribute("src") or "").lower()
                        if any(h in src for h in VIDEO_IFRAME_HINTS):
                            href = el.get_attribute("src") or "#"
                            el.evaluate("(e,i)=>e.dataset._tmpSel='ifr_'+i", i)
                            sel = f"[data-_tmp-sel='ifr_{i}']"
                            page.evaluate(
                                """([selector, href])=>{
                                    const t = document.querySelector(selector);
                                    if(!t) return;
                                    const box = document.createElement('div');
                                    box.className = '___vid_box';
                                    if(href && href !== '#'){
                                      box.innerHTML = '<span class="play">▶</span><a href="'+href+'" target="_blank" rel="noopener">'+href+'</a>';
                                    } else {
                                      box.textContent = 'Vídeo (iframe sem link detectado)';
                                    }
                                    t.replaceWith(box);
                                }""",
                                [sel, href]
                            )
                    except Exception as e:
                        logging.error(f"Falha ao substituir <iframe>: {e}")

            # Chame a função antes de gerar o PDF
            replace_videos_and_iframes()

            conversion_status[task_id].update({
                'progress': 85,
                'message': 'Gerando PDF...'
            })

            # Gerar PDF (apenas funciona com Chromium)
            page.emulate_media(media="print")
            
            if browser_type == 'chromium':
                page.pdf(
                    path=str(pdf_path),
                    format=settings.format,
                    print_background=True,
                    landscape=settings.landscape,
                    scale=settings.scale,
                    margin={"top":settings.margins.split(",")[0],"right":settings.margins.split(",")[1],"bottom":settings.margins.split(",")[2],"left":settings.margins.split(",")[3]},
                )
                logging.info(f"PDF gerado com Chromium: {pdf_path}")
            else:
                # Para outros browsers, gerar PDF usando WeasyPrint do HTML processado
                logging.info(f"Gerando PDF a partir do HTML usando {browser_type}")
                
                try:
                    # Obter o conteúdo HTML da página processada
                    html_content = page.content()
                    
                    # Tentar usar WeasyPrint para HTML para PDF de alta qualidade
                    try:
                        from weasyprint import HTML, CSS
                        from weasyprint.text.fonts import FontConfiguration
                        
                        # CSS adicional para melhorar a renderização do PDF
                        pdf_css = CSS(string="""
                            @page {
                                margin: 2cm;
                                size: A4;
                            }
                            body {
                                font-family: Arial, sans-serif;
                                line-height: 1.6;
                                color: #333;
                            }
                            .___vid_box {
                                border: 2px solid #007bff;
                                padding: 15px;
                                margin: 10px 0;
                                background-color: #f8f9fa;
                                border-radius: 5px;
                            }
                            .___vid_box a {
                                color: #007bff;
                                text-decoration: none;
                                font-weight: bold;
                            }
                            .___src_banner {
                                background: #e9ecef !important;
                                border: 1px solid #dee2e6 !important;
                                padding: 10px !important;
                                margin: 10px 0 !important;
                                font-size: 12px !important;
                            }
                            img {
                                max-width: 100%;
                                height: auto;
                            }
                        """)
                        
                        # Gerar PDF usando WeasyPrint
                        font_config = FontConfiguration()
                        html_doc = HTML(string=html_content, base_url=url)
                        html_doc.write_pdf(str(pdf_path), stylesheets=[pdf_css], font_config=font_config)
                        
                        logging.info(f"PDF gerado com WeasyPrint: {pdf_path}")
                        
                    except ImportError:
                        logging.warning("WeasyPrint não disponível, tentando pdfkit")
                        
                        # Fallback para pdfkit
                        try:
                            import pdfkit
                            
                            # Configurações para pdfkit
                            options = {
                                'page-size': 'A4',
                                'margin-top': '0.75in',
                                'margin-right': '0.75in',
                                'margin-bottom': '0.75in',
                                'margin-left': '0.75in',
                                'encoding': "UTF-8",
                                'no-outline': None,
                                'enable-local-file-access': None
                            }
                            
                            pdfkit.from_string(html_content, str(pdf_path), options=options)
                            logging.info(f"PDF gerado com pdfkit: {pdf_path}")
                            
                        except ImportError:
                            logging.warning("pdfkit não disponível, usando fallback de screenshot otimizado")
                            
                            # Fallback melhorado com screenshot otimizado
                            from reportlab.pdfgen import canvas
                            from reportlab.lib.pagesizes import A4
                            from PIL import Image
                            import io
                            
                            # Configurar dimensões do PDF
                            page_width, page_height = A4
                            if settings.landscape:
                                page_width, page_height = page_height, page_width
                            
                            c = canvas.Canvas(str(pdf_path), pagesize=(page_width, page_height))
                            
                            # Capturar viewport por viewport para manter qualidade
                            viewport_height = page.evaluate("window.innerHeight")
                            page_height_px = page.evaluate("document.documentElement.scrollHeight")
                            
                            # Limitar para evitar problemas
                            max_height = min(page_height_px, 25000)
                            num_sections = max(1, int(max_height / min(viewport_height, 4000)))
                            section_height = max_height / num_sections
                            
                            current_y_pdf = page_height
                            
                            for section in range(num_sections):
                                scroll_top = section * section_height
                                
                                page.evaluate(f"window.scrollTo(0, {scroll_top})")
                                page.wait_for_timeout(300)
                                
                                try:
                                    # Capturar com viewport limitado
                                    screenshot = page.screenshot(
                                        clip={
                                            'x': 0, 'y': 0,
                                            'width': min(1200, page.evaluate("window.innerWidth")),
                                            'height': min(4000, viewport_height)
                                        }
                                    )
                                    
                                    img = Image.open(io.BytesIO(screenshot))
                                    img_width, img_height = img.size
                                    
                                    # Escalar para caber na página
                                    scale_factor = min(page_width / img_width, page_height / img_height) * 0.9
                                    scaled_width = img_width * scale_factor
                                    scaled_height = img_height * scale_factor
                                    
                                    if current_y_pdf - scaled_height < 0:
                                        c.showPage()
                                        current_y_pdf = page_height
                                    
                                    # Usar arquivo temporário mais seguro
                                    temp_img_path = output_dir / f"tmp_{section}.png"
                                    img.save(temp_img_path)
                                    
                                    c.drawImage(str(temp_img_path), 0, current_y_pdf - scaled_height, scaled_width, scaled_height)
                                    current_y_pdf -= scaled_height
                                    
                                    temp_img_path.unlink(missing_ok=True)
                                    logging.info(f"Seção {section + 1}/{num_sections} processada")
                                    
                                except Exception as section_error:
                                    logging.error(f"Erro na seção {section}: {section_error}")
                                    continue
                            
                            c.save()
                            logging.info(f"PDF gerado via screenshot otimizado: {pdf_path}")
                        
                except Exception as e:
                    logging.error(f"Erro ao gerar PDF: {e}")
                    # Último recurso: salvar apenas HTML
                    pdf_path = pdf_path.with_suffix('.html')
                    pdf_path.write_text(page.content(), encoding='utf-8')
                    logging.info(f"Salvando apenas HTML: {pdf_path}")

            conversion_status[task_id].update({
                'progress': 95,
                'message': 'Salvando snapshot HTML...'
            })

            # Preparar para salvar snapshot HTML
            
            # Obter HTML e limpar problemas comuns
            html_content = page.content()
            
            # Correções para HTML quebrado
            import re
            
            # Remover scripts duplicados do Replit
            html_content = re.sub(r'<script src="/__replco/.*?".*?></script>', '', html_content)
            
            # Corrigir DOCTYPE duplicado
            html_content = re.sub(r'<!DOCTYPE html>\s*<!DOCTYPE html>', '<!DOCTYPE html>', html_content)
            
            # Corrigir scripts malformados
            html_content = re.sub(r'<script[^>]*onerror="[^"]*"[^>]*></script>', '', html_content)
            
            # Adicionar meta viewport se não existir
            if 'viewport' not in html_content:
                html_content = html_content.replace('<head>', '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
            
            # Adicionar estilos para os vídeos renderizarem melhor
            video_styles = '''
            <style>
            .___vid_box {
                border: 2px solid #007bff;
                padding: 15px;
                margin: 15px 0;
                background-color: #f8f9fa;
                border-radius: 8px;
                text-align: center;
            }
            .___vid_box a {
                color: #007bff;
                text-decoration: none;
                font-weight: bold;
                font-size: 16px;
            }
            .___vid_box a:hover {
                text-decoration: underline;
            }
            .___vid_box .play {
                font-size: 20px;
                color: #28a745;
            }
            .___src_banner {
                background: #e9ecef !important;
                border: 1px solid #dee2e6 !important;
                padding: 12px !important;
                margin: 15px 0 !important;
                border-radius: 6px !important;
                font-size: 14px !important;
            }
            .___src_banner a {
                color: #007bff;
                text-decoration: none;
            }
            </style>
            '''
            
            # Inserir estilos antes do </head>
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', video_styles + '\n</head>')
            
            snapshot_path.write_text(html_content, encoding="utf-8")

            context.close()
            browser.close()

            conversion_status[task_id].update({
                'status': 'completed',
                'progress': 100,
                'message': 'Conversão concluída!',
                'pdf_file': str(pdf_path.name),
                'html_file': str(snapshot_path.name),
                'title': title
            })

    except Exception as e:
        logging.error(f"Erro na conversão: {str(e)}")
        logging.error(traceback.format_exc())
        conversion_status[task_id] = {
            'status': 'error',
            'progress': 0,
            'message': f'Erro na conversão: {str(e)}'
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url', '').strip()
    
    if not url:
        flash('Por favor, insira uma URL válida.', 'error')
        return redirect(url_for('index'))
    
    if not is_valid_url(url):
        flash('URL inválida. Certifique-se de incluir http:// ou https://', 'error')
        return redirect(url_for('index'))
    
    # Create settings from form data
    cli_map = {
        'url': url,
        'login_url': request.form.get('login_url', ''),
        'username': request.form.get('username', ''),
        'password': request.form.get('password', ''),
        'user_field': request.form.get('user_field', '#username'),
        'pass_field': request.form.get('pass_field', '#password'),
        'submit_selector': request.form.get('submit_selector', ''),
        'wait_selector': request.form.get('wait_selector', ''),
        'wait_ms': int(request.form.get('wait_ms', 0) or 0),
        'viewport_w': int(request.form.get('viewport_w', 1366) or 1366),
        'viewport_h': int(request.form.get('viewport_h', 900) or 900),
        'scale': float(request.form.get('scale', 1.0) or 1.0),
        'format': request.form.get('format', 'A4'),
        'landscape': request.form.get('landscape') == 'on',
        'margins': request.form.get('margins', '12mm,12mm,12mm,12mm'),
    }
    
    settings = Settings.from_sources(cli_map)
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Start conversion in background thread
    thread = threading.Thread(target=perform_conversion, args=(task_id, url, settings))
    thread.daemon = True
    thread.start()
    
    return jsonify({'task_id': task_id, 'status': 'started'})

@app.route('/status/<task_id>')
def status(task_id):
    if task_id not in conversion_status:
        return jsonify({'status': 'not_found'}), 404
    
    return jsonify(conversion_status[task_id])

@app.route('/download/<filename>')
def download(filename):
    try:
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            return "Arquivo não encontrado", 404
            
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logging.error(f"Erro no download: {str(e)}")
        return "Erro no download", 500

@app.route('/cleanup')
def cleanup():
    """Clean up old conversion statuses"""
    # Remove statuses older than 1 hour
    current_time = time.time()
    to_remove = []
    for task_id, status_data in conversion_status.items():
        # If status is more than 1 hour old, mark for removal
        if current_time - status_data.get('created', current_time) > 3600:
            to_remove.append(task_id)
    
    for task_id in to_remove:
        del conversion_status[task_id]
    
    return jsonify({'cleaned': len(to_remove)})

# ===== ROTAS DO SCHEDULER =====

@app.route('/scheduler')
def scheduler_index():
    """Página principal do scheduler"""
    conversions = ScheduledConversion.query.order_by(ScheduledConversion.created_at.desc()).all()
    return render_template('scheduler.html', conversions=conversions)

@app.route('/scheduler/new')
def scheduler_new():
    """Formulário para nova conversão agendada"""
    return render_template('scheduler_form.html')

@app.route('/scheduler/create', methods=['POST'])
def scheduler_create():
    """Cria uma nova conversão agendada"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        # Validação básica
        url = data.get('url', '').strip()
        name = data.get('name', '').strip()
        scheduled_time_str = data.get('scheduled_time', '').strip()
        frequency = data.get('frequency', 'once')
        
        if not all([url, name, scheduled_time_str]):
            return jsonify({'error': 'URL, nome e horário são obrigatórios'}), 400
        
        if not is_valid_url(url):
            return jsonify({'error': 'URL inválida'}), 400
        
        # Parse do datetime
        try:
            scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            # Converte para UTC se necessário (remove timezone info para usar datetime naive)
            if scheduled_time.tzinfo:
                scheduled_time = scheduled_time.replace(tzinfo=None)
            
            # Verifica se não é no passado (para execuções únicas)
            if frequency == 'once' and scheduled_time <= datetime.utcnow():
                return jsonify({'error': 'Horário agendado deve ser no futuro'}), 400
                
        except ValueError:
            return jsonify({'error': 'Formato de data/hora inválido'}), 400
        
        # Configurações da conversão
        settings = {
            'login_url': data.get('login_url', ''),
            'username': data.get('username', ''),
            'password': data.get('password', ''),
            'user_field': data.get('user_field', '#username'),
            'pass_field': data.get('pass_field', '#password'),
            'submit_selector': data.get('submit_selector', ''),
            'wait_selector': data.get('wait_selector', ''),
            'wait_ms': int(data.get('wait_ms', 0) or 0),
            'viewport_w': int(data.get('viewport_w', 1366) or 1366),
            'viewport_h': int(data.get('viewport_h', 900) or 900),
            'scale': float(data.get('scale', 1.0) or 1.0),
            'format': data.get('format', 'A4'),
            'landscape': data.get('landscape') in ['true', 'on', '1', True],
            'margins': data.get('margins', '12mm,12mm,12mm,12mm'),
        }
        
        # Cria conversão agendada
        conversion = ScheduledConversion(
            url=url,
            name=name,
            scheduled_time=scheduled_time,
            frequency=frequency,
            next_run=scheduled_time,
            status='scheduled'
        )
        conversion.set_settings_dict(settings)
        
        db.session.add(conversion)
        db.session.commit()
        
        logging.info(f"Conversão agendada criada: {conversion.id} - {name}")
        
        if request.is_json:
            return jsonify({'success': True, 'id': conversion.id, 'message': 'Conversão agendada com sucesso'})
        else:
            flash('Conversão agendada com sucesso!', 'success')
            return redirect(url_for('scheduler_index'))
            
    except Exception as e:
        logging.error(f"Erro ao criar conversão agendada: {e}")
        if request.is_json:
            return jsonify({'error': f'Erro interno: {str(e)}'}), 500
        else:
            flash(f'Erro ao agendar conversão: {str(e)}', 'error')
            return redirect(url_for('scheduler_new'))

@app.route('/scheduler/<int:conversion_id>')
def scheduler_detail(conversion_id):
    """Detalhes de uma conversão agendada"""
    conversion = ScheduledConversion.query.get_or_404(conversion_id)
    return render_template('scheduler_detail.html', conversion=conversion)

@app.route('/scheduler/<int:conversion_id>/delete', methods=['POST', 'DELETE'])
def scheduler_delete(conversion_id):
    """Remove uma conversão agendada"""
    try:
        conversion = ScheduledConversion.query.get_or_404(conversion_id)
        name = conversion.name
        
        db.session.delete(conversion)
        db.session.commit()
        
        logging.info(f"Conversão agendada removida: {conversion_id} - {name}")
        
        if request.is_json:
            return jsonify({'success': True, 'message': 'Conversão removida'})
        else:
            flash('Conversão removida com sucesso!', 'success')
            return redirect(url_for('scheduler_index'))
            
    except Exception as e:
        logging.error(f"Erro ao remover conversão agendada {conversion_id}: {e}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Erro ao remover conversão: {str(e)}', 'error')
            return redirect(url_for('scheduler_index'))

@app.route('/scheduler/<int:conversion_id>/run', methods=['POST'])
def scheduler_run_now(conversion_id):
    """Executa uma conversão agendada imediatamente"""
    try:
        conversion = ScheduledConversion.query.get_or_404(conversion_id)
        
        if conversion.status == 'running':
            return jsonify({'error': 'Conversão já está sendo executada'}), 400
        
        # Atualiza para executar agora
        conversion.next_run = datetime.utcnow()
        conversion.status = 'scheduled'
        conversion.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logging.info(f"Conversão {conversion_id} agendada para execução imediata")
        
        return jsonify({'success': True, 'message': 'Conversão iniciada'})
        
    except Exception as e:
        logging.error(f"Erro ao executar conversão {conversion_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/conversions')
def api_scheduler_list():
    """API para listar conversões agendadas"""
    conversions = ScheduledConversion.query.order_by(ScheduledConversion.created_at.desc()).all()
    return jsonify([conv.to_dict() for conv in conversions])

@app.route('/scheduler/download/<int:conversion_id>/<file_type>')
def scheduler_download(conversion_id, file_type):
    """Download de arquivos de conversões agendadas"""
    try:
        conversion = ScheduledConversion.query.get_or_404(conversion_id)
        
        if conversion.status != 'completed':
            return "Conversão não foi concluída com sucesso", 404
        
        if file_type == 'pdf':
            file_path = conversion.result_pdf_path
        elif file_type == 'html':
            file_path = conversion.result_html_path
        else:
            return "Tipo de arquivo inválido", 400
        
        if not file_path:
            return "Arquivo não disponível", 404
            
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        full_path = os.path.join(output_dir, file_path)
        
        if not os.path.exists(full_path):
            return "Arquivo não encontrado", 404
            
        return send_file(full_path, as_attachment=True)
        
    except Exception as e:
        logging.error(f"Erro no download do scheduler: {str(e)}")
        return "Erro no download", 500
