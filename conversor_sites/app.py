from __future__ import annotations
import base64, re, json, sys
from typing import Dict, Optional
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

VIDEO_IFRAME_HINTS = [
    "youtube.com","youtu.be","player.vimeo.com","vimeo.com",
    "loom.com","wistia","dailymotion.com","rumble.com",
    "facebook.com/plugins/video","jwplayer","tiktok.com","spotify.com/embed","soundcloud.com"
]

def _headers_from_list(items):
    headers: Dict[str,str] = {}
    for h in items or []:
        if ":" in h:
            k, v = h.split(":", 1)
            headers[k.strip()] = v.strip()
    return headers

def run_convert(
    url: str,
    output: str = "saida.pdf",
    login_url: str = "",
    username: str = "",
    password: str = "",
    user_field: str = "#username",
    pass_field: str = "#password",
    submit_selector: str = "",
    wait_selector: str = "",
    wait_ms: int = 0,
    extra_headers: Optional[Dict[str,str]] = None,
    viewport_w: int = 1366,
    viewport_h: int = 900,
    scale: float = 1.0,
    fmt: str = "A4",
    landscape: bool = False,
    margins: str = "12mm,12mm,12mm,12mm",
):
    output_path = Path(output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    margins_list = [m.strip() for m in margins.split(",")]
    if len(margins_list) != 4:
        raise ValueError("Margens inválidas. Use 'top,right,bottom,left' (ex.: 12mm,12mm,12mm,12mm).")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": viewport_w, "height": viewport_h})
        if extra_headers:
            context.set_extra_http_headers(extra_headers)
        page = context.new_page()

        # LOGIN opcional
        if login_url and username and password:
            page.goto(login_url, wait_until="domcontentloaded")
            try:
                page.wait_for_selector(user_field, timeout=10000)
                page.fill(user_field, username)
                page.wait_for_selector(pass_field, timeout=10000)
                page.fill(pass_field, password)
                if submit_selector:
                    page.click(submit_selector)
                else:
                    page.keyboard.press("Enter")
                page.wait_for_load_state("networkidle", timeout=20000)
            except PWTimeoutError:
                print("[!] Aviso: não foi possível concluir o login com os seletores informados.", file=sys.stderr)

        # Abrir URL alvo
        page.goto(url, wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except PWTimeoutError:
            pass
        if wait_selector:
            try:
                page.wait_for_selector(wait_selector, timeout=20000)
            except PWTimeoutError:
                print(f"[!] Aviso: seletor {wait_selector!r} não apareceu a tempo.", file=sys.stderr)
        if wait_ms and int(wait_ms) > 0:
            page.wait_for_timeout(int(wait_ms))

        # Estilo overlay de play
        page.evaluate("""() => {
            const id='___video_placeholder_style';
            if(!document.getElementById(id)){
                const st=document.createElement('style'); st.id=id;
                st.textContent = `
                .___vid_ph{ position:relative; display:inline-block; }
                .___vid_ph::after{
                  content:'▶'; position:absolute; top:50%; left:50%;
                  transform:translate(-50%,-50%); font-size:48px; line-height:1;
                  background: rgba(0,0,0,0.5); color:#fff; border-radius:50%;
                  padding:10px 14px;
                }`;
                document.head.appendChild(st);
            }
        }""")

        # Helper: substituir elemento por screenshot + link
        def replace_element_by_screenshot(selector, is_iframe=False):
            els = page.query_selector_all(selector)
            for el in els:
                try:
                    box = el.bounding_box()
                    if not box or box["width"] < 4 or box["height"] < 4:
                        continue
                    bpng = el.screenshot(type="png")
                    b64 = base64.b64encode(bpng).decode("ascii")

                    link = "#"
                    if is_iframe:
                        src = el.get_attribute("src") or ""
                        if src: link = src
                    else:
                        src = el.get_attribute("src") or el.get_attribute("poster") or ""
                        if not src:
                            inner_src = el.eval_on_selector("source","e=>e?e.getAttribute('src'):null")
                            if inner_src: src = inner_src
                        link = src or "#"

                    page.evaluate(
                        """([sel,dataUri,w,h,href])=>{
                            const t=document.querySelector(sel); if(!t) return;
                            const ph=document.createElement('a'); ph.href=href||'#'; ph.target='_blank'; ph.className='___vid_ph';
                            const img=document.createElement('img'); img.src='data:image/png;base64,'+dataUri;
                            img.style.width=Math.max(1,Math.floor(w))+'px';
                            img.style.height=Math.max(1,Math.floor(h))+'px';
                            img.style.display='block';
                            ph.appendChild(img); t.replaceWith(ph);
                        }""", [selector, b64, box["width"], box["height"], link]
                    )
                except Exception as e:
                    print(f"[!] Falha ao substituir elemento {selector}: {e}", file=sys.stderr)

        # Substituir <video>
        replace_element_by_screenshot("video", is_iframe=False)

        # Substituir iframes de players conhecidos
        all_ifr = page.query_selector_all("iframe")
        for i, ifr in enumerate(all_ifr):
            src = (ifr.get_attribute("src") or "").lower()
            if any(h in src for h in VIDEO_IFRAME_HINTS):
                ifr.evaluate("(e,i)=>e.dataset._tmpSel='ifrvid_'+i", i)
                sel = f"iframe[data-_tmp-sel='ifrvid_{i}']"
                replace_element_by_screenshot(sel, is_iframe=True)

        # Gerar PDF
        page.emulate_media(media="print")
        page.pdf(
            path=str(output_path),
            format=fmt,
            print_background=True,
            landscape=landscape,
            scale=scale,
            margin={"top":margins_list[0],"right":margins_list[1],"bottom":margins_list[2],"left":margins_list[3]},
        )

        # Snapshot HTML
        html_snapshot = output_path.with_suffix(".snapshot.html")
        html_snapshot.write_text(page.content(), encoding="utf-8")

        context.close()
        browser.close()
