from __future__ import annotations
import argparse, sys, re, os
from typing import Optional, Dict
from pathlib import Path
from datetime import datetime
from .config import Settings
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

# Set environment variables to bypass Playwright dependency checks
os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '1'
os.environ['PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS'] = '1'

def sanitize_filename(title: str) -> str:
    # Remove caracteres inválidos para nomes de arquivos
    return re.sub(r'[\/\\\:\*\?\"\<\>\|]', '', title).strip() or "pagina"

VIDEO_IFRAME_HINTS = [
    "youtube.com","youtu.be","player.vimeo.com","vimeo.com",
    "loom.com","wistia","dailymotion.com","rumble.com",
    "facebook.com/plugins/video","jwplayer","tiktok.com","spotify.com/embed","soundcloud.com"
]

def app_main(argv: Optional[list[str]] = None):
    parser = argparse.ArgumentParser(
        description="Converte página web para PDF; vídeos viram links no lugar; inclui link da página original."
    )
    parser.add_argument("--url", required=True, help="URL da página final a ser salva em PDF.")
    parser.add_argument("--login-url", default=None, help="URL da página de login (opcional).")
    parser.add_argument("--username", default=None, help="Usuário (opcional).")
    parser.add_argument("--password", default=None, help="Senha (opcional).")
    parser.add_argument("--user-field", default=None, help="Seletor CSS do campo de usuário.")
    parser.add_argument("--pass-field", default=None, help="Seletor CSS do campo de senha.")
    parser.add_argument("--submit-selector", default=None, help="Seletor CSS do botão de submit (opcional).")
    parser.add_argument("--wait-selector", default=None, help="Seletor CSS para aguardar (opcional).")
    parser.add_argument("--wait-ms", type=int, default=None, help="Tempo extra em ms antes do PDF (opcional).")
    parser.add_argument("--extra-header", action="append", default=None, help="Header extra (ex.: 'Authorization: Bearer TOKEN'). Pode repetir.")
    parser.add_argument("--viewport-w", type=int, default=None, help="Largura viewport (px).")
    parser.add_argument("--viewport-h", type=int, default=None, help="Altura viewport (px).")
    parser.add_argument("--scale", type=float, default=None, help="Escala para o PDF (1.0 = 100%).")
    parser.add_argument("--format", default=None, help="Formato do PDF (A4, Letter, etc.).")
    parser.add_argument("--landscape", action="store_true", help="PDF em paisagem.")
    parser.add_argument("--margins", default=None, help="Margens 'top,right,bottom,left' (ex.: 12mm,12mm,12mm,12mm).")
    parser.add_argument("--config", default=None, help="Caminho de um arquivo YAML de configuração.")
    parser.add_argument("command", nargs="?", help="Comando opcional: 'install-browser'")

    args = parser.parse_args(argv)

    if args.command == "install-browser":
        import subprocess
        code = subprocess.call([sys.executable, "-m", "playwright", "install", "chromium"])
        sys.exit(code)

    # Settings (sem --output; salvamos em output/)
    cli_map = {
        "url": args.url,
        "output": None,
        "login_url": args.login_url,
        "username": args.username,
        "password": args.password,
        "user_field": args.user_field,
        "pass_field": args.pass_field,
        "submit_selector": args.submit_selector,
        "wait_selector": args.wait_selector,
        "wait_ms": args.wait_ms,
        "viewport_w": args.viewport_w,
        "viewport_h": args.viewport_h,
        "scale": args.scale,
        "format": args.format,
        "landscape": args.landscape,
        "margins": args.margins,
    }
    st = Settings.from_sources(cli_map, config_path=args.config)

    # Extra headers
    extra_headers: Dict[str, str] = st.extra_headers or {}
    if args.extra_header:
        for h in args.extra_header:
            if ":" in h:
                k, v = h.split(":", 1)
                extra_headers[k.strip()] = v.strip()

    if not st.url:
        parser.error("--url é obrigatório (ou defina em .env/config.yaml)")

    # Sempre salvar em output/ na raiz do projeto
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # Create symbolic link to bypass libgbm dependency
        import tempfile
        temp_dir = tempfile.mkdtemp()
        mock_lib_path = os.path.join(temp_dir, 'libgbm.so.1')
        
        # Create a minimal shared library mock
        with open(mock_lib_path, 'w') as f:
            f.write('')
        os.chmod(mock_lib_path, 0o755)
        
        # Force Chromium to launch with software rendering and mock library
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',
                '--disable-gpu',
                '--disable-gpu-sandbox',
                '--disable-software-rasterizer',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI,VizDisplayCompositor',
                '--disable-ipc-flooding-protection',
                '--use-gl=disabled',
                '--disable-vulkan',
                '--disable-features=VaapiVideoDecodeLinuxGL',
                '--in-process-gpu',
                '--disable-extensions',
                '--disable-plugins'
            ],
            ignore_default_args=[
                '--enable-automation'
            ],
            env={
                **os.environ,
                'PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS': '1',
                'LIBGL_ALWAYS_SOFTWARE': '1',
                'LD_LIBRARY_PATH': f"{temp_dir}:{os.environ.get('LD_LIBRARY_PATH', '')}"
            }
        )
        vw = st.viewport_w or 1366
        vh = st.viewport_h or 900
        context = browser.new_context(viewport={"width": vw, "height": vh})
        if extra_headers:
            context.set_extra_http_headers(extra_headers)
        page = context.new_page()

        # LOGIN opcional
        if st.login_url and st.username and st.password:
            page.goto(st.login_url, wait_until="domcontentloaded")
            try:
                page.wait_for_selector(st.user_field or "#username", timeout=10000)
                page.fill(st.user_field or "#username", st.username)
                page.wait_for_selector(st.pass_field or "#password", timeout=10000)
                page.fill(st.pass_field or "#password", st.password)
                if st.submit_selector:
                    page.click(st.submit_selector)
                else:
                    page.keyboard.press("Enter")
                page.wait_for_load_state("networkidle", timeout=20000)
            except PWTimeoutError:
                print("[!] Aviso: não foi possível concluir o login com os seletores informados.", file=sys.stderr)

        # Abrir URL alvo
        page.goto(st.url, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except PWTimeoutError:
            pass
        if st.wait_selector:
            try:
                page.wait_for_selector(st.wait_selector, timeout=20000)
            except PWTimeoutError:
                print(f"[!] Aviso: seletor {st.wait_selector!r} não apareceu a tempo.", file=sys.stderr)
        if st.wait_ms and int(st.wait_ms) > 0:
            page.wait_for_timeout(int(st.wait_ms))

        # Banner com link da página original (vai para o PDF)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        safe_url = st.url
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
                    print(f"[!] Falha ao substituir <video>: {e}", file=sys.stderr)

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
                    print(f"[!] Falha ao substituir <iframe>: {e}", file=sys.stderr)

        # Chame a função antes de gerar o PDF
        replace_videos_and_iframes()

        # Gerar PDF
        page.emulate_media(media="print")
        page.pdf(
            path=str(pdf_path),
            format=st.format,
            print_background=True,
            landscape=st.landscape,
            scale=st.scale,
            margin={"top":st.margins.split(",")[0],"right":st.margins.split(",")[1],"bottom":st.margins.split(",")[2],"left":st.margins.split(",")[3]},
        )

        # Snapshot HTML (com banner e links)
        snapshot_path.write_text(page.content(), encoding="utf-8")

        context.close()
        browser.close()

if __name__ == "__main__":
    app_main()
