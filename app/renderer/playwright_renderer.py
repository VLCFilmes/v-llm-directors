"""
🎨 Playwright Renderer

Converte layers HTML/CSS em PNGs transparentes usando Playwright (Chromium headless).

Responsabilidades:
- Renderizar layer HTML → PNG transparente (full canvas OU cropped)
- Renderizar stroke_reveal → PNG estática HQ + luma masks (PNG sequence)
- Renderizar animações → PNG sequence por frame
- Fornecer metadata de cada layer (posição, dimensão, anchor point)

Saídas:
- Layers estáticas: 1 PNG por layer
- Layers animadas: N PNGs por layer (frame sequence)
- Stroke reveals: 1 PNG HQ + N mask PNGs

Essas saídas são consumidas pelo v-editor-python para composição final.
"""

import asyncio
import base64
import hashlib
import io
import json
import logging
import math
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Importação lazy do playwright para não quebrar se não estiver instalado
_playwright = None
_browser = None


async def _get_browser():
    """Inicializa browser Chromium singleton."""
    global _playwright, _browser
    if _browser is None:
        from playwright.async_api import async_playwright

        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        logger.info("🌐 Playwright browser inicializado (Chromium headless)")
    return _browser


async def shutdown_browser():
    """Desliga o browser (chamar no shutdown do app)."""
    global _playwright, _browser
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
    logger.info("🌐 Playwright browser encerrado")


# ═══════════════════════════════════════════════════════════
# RENDER LAYER (STATIC)
# ═══════════════════════════════════════════════════════════


async def render_layer_to_png(
    html: str,
    canvas_width: int = 720,
    canvas_height: int = 1280,
    crop_to_content: bool = False,
    google_fonts: Optional[List[str]] = None,
) -> Dict:
    """
    Renderiza HTML de uma layer em PNG transparente.

    Args:
        html: HTML inline da layer (com estilos inline)
        canvas_width: Largura do canvas
        canvas_height: Altura do canvas
        crop_to_content: Se True, recorta ao bounding box do conteúdo
        google_fonts: Lista de fontes Google para carregar

    Returns:
        {
            "png_base64": str,
            "width": int,
            "height": int,
            "position": {"x": int, "y": int},       # posição no canvas original
            "anchor_point": {"x": float, "y": float} # centro do conteúdo no canvas
        }
    """
    browser = await _get_browser()
    page = await browser.new_page(viewport={"width": canvas_width, "height": canvas_height})

    try:
        # Construir HTML completo
        fonts_import = ""
        if google_fonts:
            families = "|".join(f.replace(" ", "+") for f in google_fonts)
            fonts_import = (
                f'<link href="https://fonts.googleapis.com/css2?'
                f'{"&".join("family=" + f.replace(" ", "+") for f in google_fonts)}'
                f'&display=swap" rel="stylesheet">'
            )

        full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
{fonts_import}
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: {canvas_width}px; height: {canvas_height}px; overflow: hidden; background: transparent; }}
</style>
</head>
<body>
{html}
</body>
</html>"""

        await page.set_content(full_html, wait_until="networkidle")

        # Aguardar fontes carregarem
        if google_fonts:
            await page.wait_for_timeout(500)

        if crop_to_content:
            # Encontrar bounding box do conteúdo
            bbox = await page.evaluate("""() => {
                const el = document.body.firstElementChild;
                if (!el) return null;
                const rect = el.getBoundingClientRect();
                return {
                    x: Math.floor(rect.x),
                    y: Math.floor(rect.y),
                    width: Math.ceil(rect.width),
                    height: Math.ceil(rect.height)
                };
            }""")

            if bbox and bbox["width"] > 0 and bbox["height"] > 0:
                padding = 4
                clip = {
                    "x": max(0, bbox["x"] - padding),
                    "y": max(0, bbox["y"] - padding),
                    "width": min(bbox["width"] + padding * 2, canvas_width - max(0, bbox["x"] - padding)),
                    "height": min(bbox["height"] + padding * 2, canvas_height - max(0, bbox["y"] - padding)),
                }

                png_bytes = await page.screenshot(
                    type="png",
                    omit_background=True,
                    clip=clip,
                )

                center_x = bbox["x"] + bbox["width"] / 2
                center_y = bbox["y"] + bbox["height"] / 2

                return {
                    "png_base64": base64.b64encode(png_bytes).decode(),
                    "width": int(clip["width"]),
                    "height": int(clip["height"]),
                    "position": {"x": int(clip["x"]), "y": int(clip["y"])},
                    "anchor_point": {"x": center_x, "y": center_y},
                }

        # Full canvas screenshot
        png_bytes = await page.screenshot(
            type="png",
            omit_background=True,
            clip={"x": 0, "y": 0, "width": canvas_width, "height": canvas_height},
        )

        return {
            "png_base64": base64.b64encode(png_bytes).decode(),
            "width": canvas_width,
            "height": canvas_height,
            "position": {"x": 0, "y": 0},
            "anchor_point": {"x": canvas_width / 2, "y": canvas_height / 2},
        }

    finally:
        await page.close()


# ═══════════════════════════════════════════════════════════
# RENDER SCENE (ALL LAYERS)
# ═══════════════════════════════════════════════════════════


async def render_scene_layers(
    scene: Dict,
    canvas_width: int = 720,
    canvas_height: int = 1280,
    google_fonts: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
) -> Dict:
    """
    Renderiza todas as layers de uma cena.

    Args:
        scene: Objeto scene do Director v1 output
        canvas_width: Largura do canvas
        canvas_height: Altura do canvas
        google_fonts: Fontes Google para carregar
        output_dir: Diretório para salvar PNGs (se None, retorna base64)

    Returns:
        {
            "scene_id": str,
            "layers": [
                {
                    "id": str,
                    "type": str,
                    "png_base64": str (ou "png_path" se output_dir),
                    "width": int,
                    "height": int,
                    "position": {"x", "y"},
                    "anchor_point": {"x", "y"},
                    "z_index": int,
                    "animation": {...} | null,
                    "is_static": bool,
                }
            ],
            "stroke_reveals": [
                {
                    "id": str,
                    "hq_png_base64": str,
                    "masks": [{"frame": int, "png_base64": str}, ...],
                    "reveal": {...}
                }
            ]
        }
    """
    scene_id = scene.get("scene_id", "scene_unknown")
    layers = scene.get("layers", [])
    logger.info(f"🎨 Renderizando cena {scene_id}: {len(layers)} layers")

    out_dir = Path(output_dir) if output_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    rendered_layers = []
    stroke_reveals = []

    for layer in layers:
        layer_id = layer.get("id", "unknown")
        layer_type = layer.get("type", "unknown")
        html = layer.get("html", "")

        if layer_type == "stroke_reveal":
            # Renderizar stroke com masks
            stroke_result = await _render_stroke_reveal(
                layer, canvas_width, canvas_height, google_fonts
            )
            stroke_reveals.append(stroke_result)
            continue

        if not html:
            logger.warning(f"⚠️ Layer {layer_id} sem HTML, pulando")
            continue

        # Renderizar layer
        result = await render_layer_to_png(
            html=html,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            crop_to_content=False,  # full canvas for compositing
            google_fonts=google_fonts,
        )

        rendered = {
            "id": layer_id,
            "type": layer_type,
            "description": layer.get("description", ""),
            "z_index": layer.get("z_index", 100),
            "is_static": layer.get("is_static", True),
            "animation": layer.get("animation"),
            "width": result["width"],
            "height": result["height"],
            "position": result["position"],
            "anchor_point": result["anchor_point"],
        }

        if out_dir:
            png_path = out_dir / f"{layer_id}.png"
            png_bytes = base64.b64decode(result["png_base64"])
            png_path.write_bytes(png_bytes)
            rendered["png_path"] = str(png_path)
        else:
            rendered["png_base64"] = result["png_base64"]

        rendered_layers.append(rendered)
        logger.info(f"   ✅ {layer_id} ({layer_type}): {result['width']}x{result['height']}")

    return {
        "scene_id": scene_id,
        "layers": rendered_layers,
        "stroke_reveals": stroke_reveals,
    }


# ═══════════════════════════════════════════════════════════
# STROKE REVEAL (ANIMATED MASK SEQUENCE)
# ═══════════════════════════════════════════════════════════


async def _render_stroke_reveal(
    layer: Dict,
    canvas_width: int,
    canvas_height: int,
    google_fonts: Optional[List[str]] = None,
    fps: int = 30,
) -> Dict:
    """
    Renderiza stroke reveal como PNG HQ + sequência de luma masks.

    Usa abordagem path-following (PoC #3, approach C).
    """
    layer_id = layer.get("id", "stroke")
    svg_path = layer.get("svg_path", "")
    svg_style = layer.get("svg_style", {})
    reveal_config = layer.get("reveal", {})

    duration_ms = reveal_config.get("duration_ms", 1200)
    total_frames = int((duration_ms / 1000) * fps)

    logger.info(f"🖊️ Renderizando stroke reveal {layer_id}: {total_frames} frames")

    browser = await _get_browser()

    # 1) Render HQ static stroke
    stroke_color = svg_style.get("stroke", "#00e5ff")
    stroke_width = svg_style.get("stroke_width", 4)
    glow = svg_style.get("glow", False)
    glow_color = svg_style.get("glow_color", "rgba(0,229,255,0.3)")
    glow_blur = svg_style.get("glow_blur", 12)

    filter_def = ""
    filter_attr = ""
    if glow:
        filter_def = f"""<defs><filter id="glow">
            <feGaussianBlur stdDeviation="{glow_blur}" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter></defs>"""
        filter_attr = 'filter="url(#glow)"'

    hq_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>* {{ margin:0; padding:0; }} body {{ width:{canvas_width}px; height:{canvas_height}px; background:transparent; }}</style>
</head><body>
<svg width="{canvas_width}" height="{canvas_height}" xmlns="http://www.w3.org/2000/svg">
  {filter_def}
  <path d="{svg_path}" fill="none" stroke="{stroke_color}"
        stroke-width="{stroke_width}" stroke-linecap="round"
        {filter_attr} />
</svg>
</body></html>"""

    page = await browser.new_page(viewport={"width": canvas_width, "height": canvas_height})
    try:
        await page.set_content(hq_html, wait_until="load")
        hq_bytes = await page.screenshot(type="png", omit_background=True,
                                          clip={"x": 0, "y": 0, "width": canvas_width, "height": canvas_height})
    finally:
        await page.close()

    # 2) Generate luma masks (path-following approach)
    masks = []
    page = await browser.new_page(viewport={"width": canvas_width, "height": canvas_height})
    try:
        for frame in range(total_frames):
            progress = frame / max(total_frames - 1, 1)
            # Ease-out-cubic
            eased = 1 - (1 - progress) ** 3

            # Gerar mask com círculos acumulados ao longo do path
            mask_html = _generate_path_mask_html(
                svg_path, eased, canvas_width, canvas_height
            )

            await page.set_content(mask_html, wait_until="load")
            mask_bytes = await page.screenshot(
                type="png",
                omit_background=False,
                clip={"x": 0, "y": 0, "width": canvas_width, "height": canvas_height},
            )

            masks.append({
                "frame": frame,
                "png_base64": base64.b64encode(mask_bytes).decode(),
            })
    finally:
        await page.close()

    logger.info(f"   ✅ {layer_id}: 1 HQ + {len(masks)} masks")

    return {
        "id": layer_id,
        "type": "stroke_reveal",
        "hq_png_base64": base64.b64encode(hq_bytes).decode(),
        "masks": masks,
        "reveal": reveal_config,
        "total_frames": total_frames,
        "fps": fps,
    }


def _generate_path_mask_html(
    svg_path: str,
    progress: float,
    canvas_width: int,
    canvas_height: int,
    num_points: int = 60,
    blur_radius: int = 30,
) -> str:
    """
    Gera HTML de máscara luma com círculos acumulados ao longo de um SVG path.
    Fundo preto, círculos brancos com blur = reveal.
    """
    # Simplificação: extrair pontos do path movendo linearmente
    # Para paths complexos, usaria biblioteca de parsing SVG
    # Por enquanto, interpolar linearmente entre coordenadas do path
    points = _extract_path_points(svg_path, num_points)

    # Quantos pontos revelar
    reveal_count = max(1, int(progress * len(points)))
    visible_points = points[:reveal_count]

    circles_html = ""
    for px, py in visible_points:
        circles_html += (
            f'<div style="position:absolute;'
            f"left:{px - blur_radius}px;top:{py - blur_radius}px;"
            f"width:{blur_radius * 2}px;height:{blur_radius * 2}px;"
            f"border-radius:50%;background:white;"
            f'filter:blur({blur_radius // 2}px);"></div>'
        )

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>* {{ margin:0; padding:0; }} body {{ width:{canvas_width}px; height:{canvas_height}px; background:black; overflow:hidden; }}</style>
</head><body>
{circles_html}
</body></html>"""


def _extract_path_points(svg_path: str, num_points: int) -> List[Tuple[float, float]]:
    """
    Extrai pontos uniformemente espaçados de um SVG path simplificado.
    Suporta M, L, Q, C commands (simplificado).
    """
    import re

    # Parse coordenadas numéricas do path
    numbers = [float(n) for n in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)", svg_path)]

    if len(numbers) < 4:
        # Fallback: linha horizontal no centro
        return [(i * 720 / num_points, 640) for i in range(num_points)]

    # Extrair pares (x, y) — simplificado
    raw_points = []
    for i in range(0, len(numbers) - 1, 2):
        raw_points.append((numbers[i], numbers[i + 1]))

    if len(raw_points) < 2:
        return [(i * 720 / num_points, 640) for i in range(num_points)]

    # Interpolar linearmente entre pontos brutos
    result = []
    total_segments = len(raw_points) - 1
    for i in range(num_points):
        t = i / max(num_points - 1, 1)
        seg = min(int(t * total_segments), total_segments - 1)
        seg_t = (t * total_segments) - seg

        x0, y0 = raw_points[seg]
        x1, y1 = raw_points[min(seg + 1, len(raw_points) - 1)]

        x = x0 + (x1 - x0) * seg_t
        y = y0 + (y1 - y0) * seg_t
        result.append((x, y))

    return result
