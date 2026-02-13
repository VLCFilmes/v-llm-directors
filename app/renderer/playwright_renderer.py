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
# EASING FUNCTIONS
# ═══════════════════════════════════════════════════════════

def _ease(t: float, easing: str = "ease-out") -> float:
    """Calcula valor eased para progresso t (0..1)."""
    t = max(0.0, min(1.0, t))
    if easing == "linear":
        return t
    elif easing == "ease-in":
        return t * t
    elif easing == "ease-out":
        return 1 - (1 - t) ** 2
    elif easing == "ease-in-out":
        return 3 * t * t - 2 * t * t * t
    elif easing == "ease-out-cubic":
        return 1 - (1 - t) ** 3
    elif easing == "ease-out-back":
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
    else:
        return 1 - (1 - t) ** 2  # default ease-out


def _get_frame_css(effect: str, progress: float) -> str:
    """Retorna CSS transform+opacity para um frame de animação."""
    p = progress  # 0..1 (já eased)

    if effect == "fade_in":
        return f"opacity:{p:.3f};"

    elif effect == "scale_up":
        s = 0.3 + 0.7 * p
        return f"transform:scale({s:.3f});opacity:{p:.3f};transform-origin:center center;"

    elif effect == "scale_down":
        s = 1.5 - 0.5 * p
        return f"transform:scale({s:.3f});opacity:{p:.3f};transform-origin:center center;"

    elif effect == "slide_up":
        y = 120 * (1 - p)
        return f"transform:translateY({y:.1f}px);opacity:{p:.3f};"

    elif effect == "slide_down":
        y = -120 * (1 - p)
        return f"transform:translateY({y:.1f}px);opacity:{p:.3f};"

    elif effect == "slide_left":
        x = 120 * (1 - p)
        return f"transform:translateX({x:.1f}px);opacity:{p:.3f};"

    elif effect == "slide_right":
        x = -120 * (1 - p)
        return f"transform:translateX({x:.1f}px);opacity:{p:.3f};"

    elif effect == "bounce_in":
        # Scale 0 → 1.15 → 0.95 → 1.0
        if p < 0.6:
            s = (p / 0.6) * 1.15
        elif p < 0.8:
            s = 1.15 - ((p - 0.6) / 0.2) * 0.20
        else:
            s = 0.95 + ((p - 0.8) / 0.2) * 0.05
        return f"transform:scale({s:.3f});opacity:{min(p * 2, 1.0):.3f};transform-origin:center center;"

    elif effect == "fade_out":
        return f"opacity:{1.0 - p:.3f};"

    elif effect == "scale_out":
        s = 1.0 + 0.5 * p
        return f"transform:scale({s:.3f});opacity:{1.0 - p:.3f};transform-origin:center center;"

    else:
        # Default: fade_in
        return f"opacity:{p:.3f};"


# ═══════════════════════════════════════════════════════════
# RENDER ANIMATED LAYER (PNG SEQUENCE)
# ═══════════════════════════════════════════════════════════


async def render_animated_layer(
    html: str,
    animation: Dict,
    canvas_width: int = 720,
    canvas_height: int = 1280,
    fps: int = 30,
    google_fonts: Optional[List[str]] = None,
) -> Dict:
    """
    Renderiza uma layer animada como sequência de PNGs.

    O HTML da layer é envolvido em um container, e para cada frame
    aplicamos CSS transform/opacity correspondente ao progresso da animação.

    Args:
        html: HTML inline da layer
        animation: {effect, duration_ms, delay_ms, easing, type}
        canvas_width/canvas_height: Dimensões do canvas
        fps: Frames por segundo
        google_fonts: Fontes Google

    Returns:
        {
            "frames": [{"frame": 0, "png_base64": str}, ...],
            "total_frames": int,
            "delay_frames": int,   # frames de espera (transparente) antes da animação
            "anim_frames": int,    # frames da animação propriamente
            "hold_frames": int,    # frames parados no estado final
            "fps": int,
            "duration_ms": int,
            "effect": str,
        }
    """
    effect = animation.get("effect", "fade_in")
    duration_ms = animation.get("duration_ms", 500)
    delay_ms = animation.get("delay_ms", 0)
    easing = animation.get("easing", "ease-out")

    delay_frames = int((delay_ms / 1000) * fps)
    anim_frames = max(1, int((duration_ms / 1000) * fps))
    # Hold final state for a few frames to allow smooth composition
    hold_frames = 2
    total_frames = delay_frames + anim_frames + hold_frames

    logger.info(
        f"🎬 Renderizando animação: effect={effect} "
        f"delay={delay_frames}f + anim={anim_frames}f + hold={hold_frames}f "
        f"= {total_frames}f total ({fps}fps)"
    )

    browser = await _get_browser()
    page = await browser.new_page(viewport={"width": canvas_width, "height": canvas_height})

    try:
        # Construir HTML com container animável
        fonts_import = ""
        if google_fonts:
            fonts_import = (
                '<link href="https://fonts.googleapis.com/css2?'
                + "&".join("family=" + f.replace(" ", "+") for f in google_fonts)
                + '&display=swap" rel="stylesheet">'
            )

        wrapped_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
{fonts_import}
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ width: {canvas_width}px; height: {canvas_height}px; overflow: hidden; background: transparent; }}
  #anim-container {{
    width: {canvas_width}px;
    height: {canvas_height}px;
    position: relative;
  }}
</style>
</head>
<body>
<div id="anim-container">
{html}
</div>
</body>
</html>"""

        await page.set_content(wrapped_html, wait_until="networkidle")
        if google_fonts:
            await page.wait_for_timeout(500)

        clip = {"x": 0, "y": 0, "width": canvas_width, "height": canvas_height}
        frames = []

        for frame_idx in range(total_frames):
            if frame_idx < delay_frames:
                # Delay phase: invisible (transparent PNG)
                css = "opacity:0;"
            elif frame_idx >= delay_frames + anim_frames:
                # Hold phase: final state (fully visible)
                css = _get_frame_css(effect, 1.0)
            else:
                # Animation phase
                t = (frame_idx - delay_frames) / max(anim_frames - 1, 1)
                eased_t = _ease(t, easing)
                css = _get_frame_css(effect, eased_t)

            # Apply CSS via JavaScript (fast, no page reload)
            await page.evaluate(
                f'document.getElementById("anim-container").style.cssText = "{css}";'
            )

            png_bytes = await page.screenshot(
                type="png",
                omit_background=True,
                clip=clip,
            )

            frames.append({
                "frame": frame_idx,
                "png_base64": base64.b64encode(png_bytes).decode(),
            })

        logger.info(f"   ✅ {total_frames} frames renderizados")

        return {
            "frames": frames,
            "total_frames": total_frames,
            "delay_frames": delay_frames,
            "anim_frames": anim_frames,
            "hold_frames": hold_frames,
            "fps": fps,
            "duration_ms": delay_ms + duration_ms,
            "effect": effect,
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
    render_animations: bool = False,
    fps: int = 30,
) -> Dict:
    """
    Renderiza todas as layers de uma cena.

    Args:
        scene: Objeto scene do Director v1 output
        canvas_width: Largura do canvas
        canvas_height: Altura do canvas
        google_fonts: Fontes Google para carregar
        output_dir: Diretório para salvar PNGs (se None, retorna base64)
        render_animations: Se True, layers com animation são renderizadas como PNG sequences
        fps: Frames por segundo para animações

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
                    "animation_sequence": {...} | null   # presente se render_animations=True
                }
            ],
            "stroke_reveals": [...]
        }
    """
    scene_id = scene.get("scene_id", "scene_unknown")
    layers = scene.get("layers", [])
    logger.info(f"🎨 Renderizando cena {scene_id}: {len(layers)} layers (animations={render_animations})")

    out_dir = Path(output_dir) if output_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    rendered_layers = []
    stroke_reveals = []

    for layer in layers:
        layer_id = layer.get("id", "unknown")
        layer_type = layer.get("type", "unknown")
        html = layer.get("html", "")
        animation = layer.get("animation")
        is_static = layer.get("is_static", True)

        if layer_type == "stroke_reveal":
            # Renderizar stroke com masks (salva no disco se out_dir disponível)
            stroke_result = await _render_stroke_reveal(
                layer, canvas_width, canvas_height, google_fonts,
                fps=fps, output_dir=out_dir,
            )
            stroke_reveals.append(stroke_result)
            continue

        if not html:
            logger.warning(f"⚠️ Layer {layer_id} sem HTML, pulando")
            continue

        # 1) Sempre renderizar versão estática
        result = await render_layer_to_png(
            html=html,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            crop_to_content=False,
            google_fonts=google_fonts,
        )

        rendered = {
            "id": layer_id,
            "type": layer_type,
            "description": layer.get("description", ""),
            "z_index": layer.get("z_index", 100),
            "is_static": is_static,
            "animation": animation,
            "width": result["width"],
            "height": result["height"],
            "position": result["position"],
            "anchor_point": result["anchor_point"],
            "animation_sequence": None,
        }

        if out_dir:
            png_path = out_dir / f"{layer_id}.png"
            png_bytes = base64.b64decode(result["png_base64"])
            png_path.write_bytes(png_bytes)
            rendered["png_path"] = str(png_path)
        else:
            rendered["png_base64"] = result["png_base64"]

        # 2) Se tem animação E render_animations=True, gerar sequência
        if render_animations and animation and not is_static:
            logger.info(f"   🎬 Gerando sequência para {layer_id} (effect={animation.get('effect', '?')})")
            anim_result = await render_animated_layer(
                html=html,
                animation=animation,
                canvas_width=canvas_width,
                canvas_height=canvas_height,
                fps=fps,
                google_fonts=google_fonts,
            )

            if out_dir:
                # Salvar frames em subdiretório
                frames_dir = out_dir / f"{layer_id}_frames"
                frames_dir.mkdir(parents=True, exist_ok=True)
                for f_data in anim_result["frames"]:
                    f_path = frames_dir / f"frame_{f_data['frame']:04d}.png"
                    f_path.write_bytes(base64.b64decode(f_data["png_base64"]))
                anim_result["frames_dir"] = str(frames_dir)
                # Não retornar base64 dos frames quando salvou em disco
                anim_result["frames"] = [
                    {"frame": f["frame"], "png_path": str(frames_dir / f"frame_{f['frame']:04d}.png")}
                    for f in anim_result["frames"]
                ]

            rendered["animation_sequence"] = anim_result

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
    output_dir: Optional[Path] = None,
) -> Dict:
    """
    Renderiza stroke reveal como PNG HQ + sequência de luma masks.

    Usa abordagem path-following (PoC #3, approach C).
    Se output_dir fornecido, salva HQ + masks em disco (mesmo padrão de layers normais).
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
    mask_frames_dir = None

    # Preparar diretório de saída se disponível
    if output_dir:
        mask_frames_dir = output_dir / f"{layer_id}_masks"
        mask_frames_dir.mkdir(parents=True, exist_ok=True)
        # Salvar HQ PNG em disco
        hq_path = output_dir / f"{layer_id}_hq.png"
        hq_path.write_bytes(hq_bytes)

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

            if mask_frames_dir:
                # Salvar mask em disco
                mask_path = mask_frames_dir / f"mask_{frame:04d}.png"
                mask_path.write_bytes(mask_bytes)
                masks.append({
                    "frame": frame,
                    "png_path": str(mask_path),
                })
            else:
                masks.append({
                    "frame": frame,
                    "png_base64": base64.b64encode(mask_bytes).decode(),
                })
    finally:
        await page.close()

    logger.info(f"   ✅ {layer_id}: 1 HQ + {len(masks)} masks"
                f"{' (saved to disk)' if output_dir else ''}")

    result = {
        "id": layer_id,
        "type": "stroke_reveal",
        "masks": masks,
        "reveal": reveal_config,
        "total_frames": total_frames,
        "fps": fps,
    }

    if output_dir:
        result["hq_png_path"] = str(hq_path)
        result["masks_dir"] = str(mask_frames_dir)
    else:
        result["hq_png_base64"] = base64.b64encode(hq_bytes).decode()

    return result


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
