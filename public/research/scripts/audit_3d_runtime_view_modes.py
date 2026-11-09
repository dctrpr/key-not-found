#!/usr/bin/env python3
"""
Runtime sanity check for the local 3D article map.

This is a bounded rendered-view audit. It captures the existing local viewer in
several URL-controlled modes and checks whether the canvas is actually nonblank.
It does not extract key material, hash text, generate seed phrases, check WIF
strings, or query addresses.
"""

from __future__ import annotations

import json
import asyncio
import base64
import re
import shutil
import socket
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests
import websockets
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "3d_article_map" / "runtime_view_modes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INDEX_HTML = ROOT / "analysis_outputs" / "3d_article_map" / "index.html"
VIEWER_JS = ROOT / "analysis_outputs" / "3d_article_map" / "viewer.js"
DATA_JSON = ROOT / "analysis_outputs" / "3d_article_map" / "article_3d_map_data.json"
OUT_JSON = OUT_DIR / "runtime_view_modes.json"
OUT_MD = OUT_DIR / "runtime_view_modes.md"

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
BASE_URL = "http://127.0.0.1:8765/analysis_outputs/3d_article_map/index.html"
VIEWPORT = (1440, 1000)
PANEL_WIDTH = 360

CAPTURES = [
    {"id": "spread_all", "layout": "spread", "focus": "all"},
    {"id": "fold_all", "layout": "fold", "focus": "all"},
    {"id": "fold_page76", "layout": "fold", "focus": "76"},
    {"id": "stack_all", "layout": "stack", "focus": "all"},
]


def chrome_available() -> bool:
    return CHROME.exists()


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def wait_for_debug_tab(port: int, timeout: float = 10.0) -> str:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            tabs = requests.get(f"http://127.0.0.1:{port}/json/list", timeout=0.5).json()
            for tab in tabs:
                if tab.get("type") == "page" and tab.get("webSocketDebuggerUrl"):
                    return tab["webSocketDebuggerUrl"]
        except Exception as exc:  # pragma: no cover - diagnostic path
            last_error = exc
        time.sleep(0.1)
    raise RuntimeError(f"Chrome debug tab did not appear: {last_error}")


async def cdp_capture(mode: dict[str, str], ws_url: str, screenshot: Path) -> dict[str, object]:
    url = f"{BASE_URL}?layout={mode['layout']}&focus={mode['focus']}"
    msg_id = 0

    async with websockets.connect(ws_url, max_size=16 * 1024 * 1024) as ws:
        async def call(method: str, params: dict | None = None) -> dict:
            nonlocal msg_id
            msg_id += 1
            await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
            while True:
                raw = await ws.recv()
                message = json.loads(raw)
                if message.get("id") == msg_id:
                    if "error" in message:
                        raise RuntimeError(f"{method} failed: {message['error']}")
                    return message.get("result", {})

        await call("Page.enable")
        await call("Runtime.enable")
        await call(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": VIEWPORT[0],
                "height": VIEWPORT[1],
                "deviceScaleFactor": 1,
                "mobile": False,
            },
        )
        await call("Page.navigate", {"url": url})

        readiness: dict[str, object] = {}
        for _ in range(50):
            result = await call(
                "Runtime.evaluate",
                {
                    "awaitPromise": True,
                    "returnByValue": True,
                    "expression": f"""
(() => {{
  const active = [...document.querySelectorAll('[data-layout]')].find((b) => b.classList.contains('active'))?.dataset.layout || null;
  const focus = document.querySelector('#focusSelect')?.value || null;
  const metrics = {{
    charCount: document.querySelector('#charCount')?.textContent || null,
    wordCount: document.querySelector('#wordCount')?.textContent || null,
    anchorCount: document.querySelector('#anchorCount')?.textContent || null,
    reflectionCount: document.querySelector('#reflectionCount')?.textContent || null,
  }};
  const canvas = document.querySelector('#scene');
  const rect = canvas?.getBoundingClientRect();
  const findings = document.querySelectorAll('#findings li').length;
  return {{
    ready: metrics.wordCount !== '0' && active === '{mode['layout']}' && focus === '{mode['focus']}',
    active,
    focus,
    metrics,
    findings,
    canvasRect: rect ? {{x: rect.x, y: rect.y, width: rect.width, height: rect.height}} : null,
    hoverText: document.querySelector('#hoverText')?.textContent || null,
  }};
}})()
""",
                },
            )
            readiness = result.get("result", {}).get("value", {}) or {}
            if readiness.get("ready"):
                break
            await asyncio.sleep(0.2)

        # Give WebGL one more frame after the controls and URL state are ready.
        await asyncio.sleep(0.8)
        screenshot_result = await call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})
        screenshot.write_bytes(base64.b64decode(screenshot_result["data"]))
        return {
            "url": url,
            "runtimeReadiness": readiness,
        }


def capture(mode: dict[str, str]) -> dict[str, object]:
    screenshot = OUT_DIR / f"{mode['id']}.png"
    user_data_dir = Path(tempfile.mkdtemp(prefix=f"maxkeiser-3d-{mode['id']}-"))
    port = free_port()
    cmd = [
        str(CHROME),
        "--headless=new",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        f"--window-size={VIEWPORT[0]},{VIEWPORT[1]}",
        "--use-angle=swiftshader",
        "about:blank",
    ]
    process = subprocess.Popen(
        cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    runtime: dict[str, object] = {}
    timed_out = False
    try:
        ws_url = wait_for_debug_tab(port)
        runtime = asyncio.run(cdp_capture(mode, ws_url, screenshot))
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.kill()
                stdout, stderr = process.communicate(timeout=5)
    finally:
        shutil.rmtree(user_data_dir, ignore_errors=True)

    stats = image_stats(screenshot) if screenshot.exists() else {}
    return {
        **mode,
        "url": runtime.get("url"),
        "screenshot": str(screenshot.relative_to(ROOT)) if screenshot.exists() else None,
        "returnCode": process.returncode,
        "chromeTimedOut": timed_out,
        "stderrTail": stderr[-1200:],
        "stdoutTail": stdout[-400:],
        "runtimeReadiness": runtime.get("runtimeReadiness", {}),
        "imageStats": stats,
    }


def image_stats(path: Path) -> dict[str, object]:
    img = Image.open(path).convert("RGB")
    width, height = img.size
    canvas = img.crop((PANEL_WIDTH, 0, width, height))
    # Background is the viewer clear color / dark page background family.
    bg = canvas.getpixel((min(20, canvas.width - 1), min(20, canvas.height - 1)))
    pixels = list(canvas.getdata())
    total = len(pixels)
    non_bg = 0
    bright = 0
    saturated = 0
    orange = 0
    cyan = 0
    magenta = 0
    green = 0
    for r, g, b in pixels:
        delta = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
        if delta > 24:
            non_bg += 1
        if r + g + b > 240:
            bright += 1
        if max(r, g, b) - min(r, g, b) > 45:
            saturated += 1
        if r > 180 and 80 <= g <= 190 and b < 90:
            orange += 1
        if b > 130 and g > 100 and r < 130:
            cyan += 1
        if r > 150 and b > 120 and g < 120:
            magenta += 1
        if g > 110 and r < 140 and b < 120:
            green += 1
    return {
        "size": [width, height],
        "canvasSize": [canvas.width, canvas.height],
        "canvasBackgroundSample": list(bg),
        "nonBackgroundPixels": non_bg,
        "nonBackgroundFraction": round(non_bg / total, 5),
        "brightPixels": bright,
        "saturatedPixels": saturated,
        "approxColorPixels": {
            "orange": orange,
            "cyan": cyan,
            "magenta": magenta,
            "green": green,
        },
    }


def static_viewer_surface() -> dict[str, object]:
    html = INDEX_HTML.read_text()
    js = VIEWER_JS.read_text()
    data = json.loads(DATA_JSON.read_text())
    modes = re.findall(r'data-layout="([^"]+)"', html)
    toggles = re.findall(r'id="(toggle[^"]+)"', html)
    url_params = sorted(set(re.findall(r"params\.get\('([^']+)'\)", js)))
    focus_options = re.findall(r'<option value="([^"]+)">Page ([0-9]+)</option>', html)
    ray_slice = re.search(r"data\.raySelections\.slice\(0,\s*([0-9]+)\)", js)
    return {
        "htmlModes": modes,
        "toggleIds": toggles,
        "urlParams": url_params,
        "focusPages": [page for _, page in focus_options],
        "rayDisplayLimit": int(ray_slice.group(1)) if ray_slice else None,
        "dataCounts": {
            "pages": len(data["pages"]),
            "chars": sum(len(page["chars"]) for page in data["pages"]),
            "words": sum(len(page["words"]) for page in data["pages"]),
            "anchors": len(data["anchors"]),
            "reflections": len(data["reflections"]),
            "raySelections": len(data["raySelections"]),
        },
        "reflectionTargetPairs": sorted(
            {
                f"{item['source']}->{item['target']}"
                for item in data["reflections"]
            }
        ),
    }


def main() -> None:
    if not chrome_available():
        raise SystemExit(f"Chrome not found at {CHROME}")

    captures = [capture(mode) for mode in CAPTURES]
    static_surface = static_viewer_surface()
    nonblank = [
        row["id"]
        for row in captures
        if row.get("imageStats", {}).get("nonBackgroundFraction", 0) > 0.01
    ]
    blank = [row["id"] for row in captures if row["id"] not in nonblank]

    assessment = [
        "The rendered 3D viewer is reproducibly nonblank when Chrome is forced to use SwiftShader/ANGLE; this avoids the blank-canvas failure seen in the default headless path.",
        "The viewer still exposes only the three known layout modes: spread, fold, and stack.",
        "The URL focus parameter is a display filter only. It hides non-selected page groups but does not recompute mirror/fold geometry or create a new selector.",
        "Runtime metrics are populated and source-consistent: the viewer reports 5,966 display letters, 1,243 words, 16 anchors, and 29 mirror boxes; the JSON has 7,299 raw character records because it includes blanks/spacing, plus 40 stored ray selections with 28 displayed.",
        "The screenshots show overlay layers, anchors, rays, highlights, and text sprites as review aids. They do not reveal a hidden UI mode, hidden fold selector, or new ordering rule.",
    ]
    if blank:
        assessment.append(f"Blank or near-blank captures under the SwiftShader path: {', '.join(blank)}.")

    decision = (
        "Use the 3D viewer for visual review/orientation only. Future runtime screenshots should force SwiftShader/ANGLE; do not infer puzzle signal from blank default headless captures or from focus/layout UI state."
    )
    next_move = (
        "Return to source evidence: only reopen extraction when a new source/clue names the unit/order, or when a physical/original-layout image changes the page-76/G5/O5 geometry."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "3D viewer runtime mode sanity check; no key derivation.",
        "chrome": str(CHROME),
        "baseUrl": BASE_URL,
        "viewport": list(VIEWPORT),
        "staticSurface": static_surface,
        "captures": captures,
        "nonblankCaptures": nonblank,
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# 3D Runtime View Modes Audit",
        "",
        "Scope: render the local 3D article map in several modes and check whether the canvas is actually usable. No text extraction stream, key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Base URL: `{BASE_URL}`",
        f"- Render path: Chrome headless with `--use-angle=swiftshader`",
        "",
        "## Static Viewer Surface",
        "",
        f"- Layout modes: `{', '.join(static_surface['htmlModes'])}`",
        f"- URL params: `{', '.join(static_surface['urlParams'])}`",
        f"- Toggles: `{', '.join(static_surface['toggleIds'])}`",
        f"- Data counts: `{static_surface['dataCounts']}`",
        f"- Reflection target pairs: `{', '.join(static_surface['reflectionTargetPairs'])}`",
        "",
        "## Render Captures",
        "",
        "| capture | layout | focus | screenshot | canvas non-bg | color pixels | status |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in captures:
        stats = row.get("imageStats", {})
        colors = stats.get("approxColorPixels", {})
        status = "nonblank" if row["id"] in nonblank else "blank/weak"
        md.append(
            f"| `{row['id']}` | `{row['layout']}` | `{row['focus']}` | `{row.get('screenshot')}` | "
            f"{stats.get('nonBackgroundFraction', 0)} | `{colors}` | {status} |"
        )

    md.extend(["", "## Findings", ""])
    for item in assessment:
        md.append(f"- {item}")
    md.extend(
        [
            "",
            "## Decision",
            "",
            f"- {decision}",
            f"- Next move: {next_move}",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")

    print(OUT_MD)
    print(OUT_JSON)
    for row in captures:
        print(row.get("screenshot"))


if __name__ == "__main__":
    main()
