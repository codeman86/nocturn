"""Local web UI for XFCE Theme Forge (stdlib only)."""

from __future__ import annotations

import json
import mimetypes
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .builder import build_preview, build_theme, _repo_root
from .config import ThemeConfig, ThemeOptions, merge_colors
from .palette import PRESETS, REFERENCE_COLORS

WEB_DIR = Path(__file__).resolve().parents[1] / "web"


def _config_from_body(body: dict) -> ThemeConfig:
    name = str(body.get("name", "MyTheme")).strip()
    colors = merge_colors(REFERENCE_COLORS, body.get("colors") or {})
    opts_data = body.get("options") or {}
    opts = ThemeOptions(
        square_corners=bool(opts_data.get("square_corners", True)),
        whisker_menu=True,
        generate_menu_icon=bool(opts_data.get("generate_menu_icon", True)),
        menu_icon_ring=str(opts_data.get("menu_icon_ring", colors["fg"])),
        menu_icon_fill=str(opts_data.get("menu_icon_fill", colors["accent_bright"])),
        icon_theme_name=opts_data.get("icon_theme_name") or name,
    )
    return ThemeConfig(
        name=name,
        display_name=str(body.get("display_name", name)),
        comment=str(body.get("comment", f"{name} — generated with XFCE Theme Forge")),
        colors=colors,
        options=opts,
    )


class ForgeHandler(BaseHTTPRequestHandler):
    repo_root: Path = _repo_root()

    def log_message(self, fmt: str, *args) -> None:
        print(f"[theme-forge] {self.address_string()} - {fmt % args}")

    def _send_json(self, data: object, status: int = 200) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        path = urllib.parse.unquote(self.path.split("?", 1)[0])

        if path == "/" or path == "/index.html":
            return self._serve_file(WEB_DIR / "index.html")

        if path == "/api/presets":
            presets = [
                {"id": k, "accent_bright": v["accent_bright"], "bg": v["bg"]}
                for k, v in PRESETS.items()
            ]
            return self._send_json({"presets": presets})

        m = re.match(r"^/api/presets/([a-z0-9_-]+)$", path)
        if m:
            preset_id = m.group(1)
            if preset_id not in PRESETS:
                return self._send_json({"error": "Unknown preset"}, 404)
            return self._send_json(PRESETS[preset_id])

        m = re.match(r"^/preview/([^/]+)/(.+)$", path)
        if m:
            theme_name = m.group(1)
            rel = m.group(2)
            if ".." in rel:
                return self.send_error(403)
            theme_file = self.repo_root / "dist" / theme_name / rel
            return self._serve_file(theme_file)

        return self.send_error(404)

    def do_POST(self) -> None:
        if self.path != "/api/build":
            return self.send_error(404)
        try:
            body = self._read_json()
            config = _config_from_body(body)
            out = build_theme(config, self.repo_root)
            build_preview(config, self.repo_root)
            preview_url = f"/preview/{config.name}/preview.html"
            self._send_json({
                "ok": True,
                "message": f"Built {config.display_name}",
                "preview_url": preview_url,
                "paths": [
                    str(out),
                    str(self.repo_root / "dist" / "pixmaps" / f"{config.name}.svg"),
                ],
            })
        except Exception as exc:
            self._send_json({"error": str(exc)}, 500)

    def _serve_file(self, path: Path) -> None:
        if not path.is_file():
            return self.send_error(404)
        data = path.read_bytes()
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    ForgeHandler.repo_root = _repo_root()
    server = ThreadingHTTPServer((host, port), ForgeHandler)
    url = f"http://{host}:{port}/"
    print(f"XFCE Theme Forge web UI: {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()
