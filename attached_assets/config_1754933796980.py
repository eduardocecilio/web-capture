from __future__ import annotations
import os, json, yaml
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from dotenv import load_dotenv

@dataclass
class Settings:
    url: str = ""
    output: str = "saida.pdf"
    login_url: str = ""
    username: str = ""
    password: str = ""
    user_field: str = "#username"
    pass_field: str = "#password"
    submit_selector: str = ""
    wait_selector: str = ""
    wait_ms: int = 0
    extra_headers: Dict[str, str] | None = None
    viewport_w: int = 1366
    viewport_h: int = 900
    scale: float = 1.0
    format: str = "A4"
    landscape: bool = False
    margins: str = "12mm,12mm,12mm,12mm"

    @classmethod
    def from_sources(cls, args: dict, config_path: Optional[str] = None) -> "Settings":
        # Load .env first (lowest priority)
        load_dotenv(override=False)

        # Start with env
        env = {k: os.getenv(k) for k in [
            "LOGIN_URL","USERNAME","PASSWORD","USER_FIELD","PASS_FIELD","SUBMIT_SELECTOR",
            "WAIT_SELECTOR","WAIT_MS","EXTRA_HEADERS","VIEWPORT_W","VIEWPORT_H","SCALE",
            "FORMAT","LANDSCAPE","MARGINS","URL","OUTPUT"
        ]}
        st = cls()
        if env.get("URL"): st.url = env["URL"]
        if env.get("OUTPUT"): st.output = env["OUTPUT"]
        if env.get("LOGIN_URL"): st.login_url = env["LOGIN_URL"]
        if env.get("USERNAME"): st.username = env["USERNAME"]
        if env.get("PASSWORD"): st.password = env["PASSWORD"]
        if env.get("USER_FIELD"): st.user_field = env["USER_FIELD"]
        if env.get("PASS_FIELD"): st.pass_field = env["PASS_FIELD"]
        if env.get("SUBMIT_SELECTOR"): st.submit_selector = env["SUBMIT_SELECTOR"]
        if env.get("WAIT_SELECTOR"): st.wait_selector = env["WAIT_SELECTOR"]
        if env.get("WAIT_MS"): st.wait_ms = int(env["WAIT_MS"] or 0)
        if env.get("VIEWPORT_W"): st.viewport_w = int(env["VIEWPORT_W"] or 1366)
        if env.get("VIEWPORT_H"): st.viewport_h = int(env["VIEWPORT_H"] or 900)
        if env.get("SCALE"): st.scale = float(env["SCALE"] or 1.0)
        if env.get("FORMAT"): st.format = env["FORMAT"]
        if env.get("LANDSCAPE"): st.landscape = str(env["LANDSCAPE"]).strip() in ("1","true","True","yes","on")
        if env.get("MARGINS"): st.margins = env["MARGINS"]
        if env.get("EXTRA_HEADERS"):
            try:
                st.extra_headers = json.loads(env["EXTRA_HEADERS"])
            except Exception:
                st.extra_headers = None

        # Load YAML (medium priority)
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            for k, v in data.items():
                if hasattr(st, k) and v is not None:
                    setattr(st, k, v)

        # Finally, overlay CLI args (highest priority)
        for k, v in args.items():
            if v is not None and hasattr(st, k):
                setattr(st, k, v)

        return st
