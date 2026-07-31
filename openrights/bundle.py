from __future__ import annotations

from pathlib import Path

from .web import index_script, load_index_payload


def build(root: Path) -> tuple[Path, int]:
    """Inline the app into one HTML file that runs from disk with no server."""
    app = root / "app"
    html = (app / "index.html").read_text(encoding="utf-8")
    styles = (app / "styles.css").read_text(encoding="utf-8")
    script = (app / "app.js").read_text(encoding="utf-8")
    data = index_script(load_index_payload(root))

    html = html.replace('<link rel="stylesheet" href="./styles.css">', f"<style>\n{styles}\n</style>")
    html = html.replace('<link rel="manifest" href="./manifest.webmanifest">', "")
    html = html.replace('<script src="./data/index.js"></script>', f"<script>\n{data}</script>")
    html = html.replace('<script src="./app.js"></script>', f"<script>\n{script}</script>")

    target = root / "dist/openrights-demo.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target, len(html.encode("utf-8"))
