"""
Rotas Flask para conversão de URLs em PDF/HTML.
Versão segura para Vercel: sem Playwright e sem execução de código pesado no import.
"""
import logging
import re
from io import BytesIO
from datetime import datetime
from urllib.parse import urlparse
import os

from flask import render_template, request, jsonify, send_file
from app import app, db
from models import Conversion
from conversion import WebPageConverter, ConversionSettings

logger = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_filename(title: str) -> str:
    if not title:
        return "webpage"
    title = re.sub(r'[<>:"/\\|?*&%=+\[\]{}()#@!$^`~,;]', '_', title)
    title = re.sub(r'\s+', '_', title.strip())
    return (title[:50] or "webpage")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert():
    try:
        url = request.form.get('url', '').strip()
        if not url:
            return jsonify({'error': 'URL é obrigatória'}), 400
        if not is_valid_url(url):
            return jsonify({'error': 'URL inválida. Certifique-se de incluir http:// ou https://'}), 400

        logger.info(f"Iniciando conversão: {url}")
        settings = ConversionSettings(url=url)
        converter = WebPageConverter(settings)
        result = converter.run()

        if not result.success:
            logger.error(f"Erro na conversão: {result.error}")
            # Se WeasyPrint não está disponível, retornamos o HTML para inspeção
            return jsonify({'error': result.error, 'html': result.html_content}), 500

        conversion = Conversion(url=url, title=result.title, status='completed')
        db.session.add(conversion)
        db.session.commit()

        return send_file(
            BytesIO(result.pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{sanitize_filename(result.title)}.pdf'
        )
    except Exception as e:
        logger.error(f"Erro na conversão: {str(e)}", exc_info=True)
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


@app.route('/api/convert', methods=['POST'])
def api_convert():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Body JSON é obrigatório'}), 400
        url = data.get('url', '').strip()
        if not url:
            return jsonify({'error': 'URL é obrigatória'}), 400
        if not is_valid_url(url):
            return jsonify({'error': 'URL inválida'}), 400

        logger.info(f"API: Iniciando conversão: {url}")
        settings = ConversionSettings(url=url)
        converter = WebPageConverter(settings)
        result = converter.run()

        if not result.success:
            logger.error(f"Erro na conversão: {result.error}")
            return jsonify({'success': False, 'error': result.error}), 500

        conversion = Conversion(url=url, title=result.title, status='completed')
        db.session.add(conversion)
        db.session.commit()

        return jsonify({
            'success': True,
            'title': result.title,
            'conversion_id': conversion.id,
            'url': url,
            'created_at': conversion.created_at.isoformat(),
            'message': 'Conversão realizada com sucesso'
        })
    except Exception as e:
        logger.error(f"Erro na API de conversão: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500


@app.route('/api/conversions', methods=['GET'])
def api_conversions():
    try:
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        limit = min(limit, 100)
        total = Conversion.query.count()
        conversions = Conversion.query.order_by(Conversion.created_at.desc()).limit(limit).offset(offset).all()
        return jsonify({'conversions': [c.to_dict() for c in conversions], 'total': total, 'limit': limit, 'offset': offset})
    except Exception as e:
        logger.error(f"Erro ao listar conversões: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversions/<int:conversion_id>', methods=['GET'])
def api_conversion_detail(conversion_id):
    try:
        conversion = Conversion.query.get_or_404(conversion_id)
        return jsonify(conversion.to_dict())
    except Exception as e:
        logger.error(f"Erro ao buscar conversão {conversion_id}: {str(e)}")
        return jsonify({'error': 'Conversão não encontrada'}), 404


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {str(error)}", exc_info=True)
    return jsonify({'error': 'Erro interno do servidor'}), 500
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
