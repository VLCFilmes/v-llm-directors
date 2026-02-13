"""
🎬 V-LLM Directors - FastAPI Application

Sistema hierárquico de LLM Directors para produção de vídeo.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging
import os
from dotenv import load_dotenv

from app.directors.level_0.motion_graphics_director_0 import get_motion_graphics_director_0
from app.directors.level_0.visual_layout_director_1 import get_visual_layout_director_1
from app.orchestrator.context_builder import get_context_builder
from app.renderer.playwright_renderer import (
    render_layer_to_png,
    render_scene_layers,
    shutdown_browser,
)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar app FastAPI
app = FastAPI(
    title="V-LLM Directors",
    description="Sistema hierárquico de LLM Directors para produção de vídeo",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_MODEL_VISUAL = os.getenv('OPENAI_MODEL_VISUAL', 'gpt-4o')  # Modelo para Director v1

if not OPENAI_API_KEY:
    logger.warning("⚠️ OPENAI_API_KEY não configurada!")


# ═══════════════════════════════════════════════════════════
# MODELS (Pydantic)
# ═══════════════════════════════════════════════════════════

class VideoContext(BaseModel):
    """Contexto do vídeo"""
    transcription: str = Field(..., description="Transcrição completa")
    words: List[Dict] = Field(..., description="Lista de palavras com timestamps")
    text_layout: List[Dict] = Field(..., description="Layout de texto com posições")
    canvas: Dict = Field(..., description="Dimensões do canvas")
    duration: float = Field(..., description="Duração total em segundos")
    style: Optional[str] = Field("modern", description="Estilo visual")


class MotionGraphicsPlanRequest(BaseModel):
    """Request para planejar motion graphics"""
    user_prompt: str = Field(..., description="Prompt do usuário")
    context: VideoContext = Field(..., description="Contexto do vídeo")


class VisualLayoutRequest(BaseModel):
    """Request para gerar layout visual (Director v1)"""
    user_prompt: str = Field(..., description="Descrição do visual desejado")
    canvas: Dict = Field(default={"width": 720, "height": 1280}, description="Dimensões do canvas")
    template_style: Optional[Dict] = Field(default=None, description="Cores, fontes, mood")
    script_text: Optional[str] = Field(default=None, description="Texto do roteiro")
    scene_descriptions: Optional[List[Dict]] = Field(default=None, description="Cenas do roteiro")
    timestamps: Optional[List[Dict]] = Field(default=None, description="Timestamps de palavras")
    occupied_areas: Optional[List[Dict]] = Field(default=None, description="Áreas de legenda")
    reference_image_url: Optional[str] = Field(default=None, description="URL/base64 de imagem referência")
    component_library: Optional[List[Dict]] = Field(default=None, description="Componentes disponíveis")


class EditLayerRequest(BaseModel):
    """Request para editar uma layer específica"""
    layer_id: str = Field(..., description="ID da layer a editar")
    current_html: str = Field(..., description="HTML atual da layer")
    edit_instruction: str = Field(..., description="Instrução de edição")
    canvas: Dict = Field(default={"width": 720, "height": 1280}, description="Dimensões do canvas")


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "v-llm-directors",
        "version": "1.0.0",
        "levels": {
            "+2": "Meta/Executive (futuro)",
            "+1": "Strategic/Creative (futuro)",
            "0": "Tactical/Core (implementado)",
            "-1": "Operational (futuro)",
            "-2": "Micro/Validation (futuro)"
        },
        "directors_available": {
            "level_0": ["MotionGraphicsDirector0"]
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "v-llm-directors",
        "openai_configured": bool(OPENAI_API_KEY),
        "models": {
            "director_0": OPENAI_MODEL,
            "director_1_visual": OPENAI_MODEL_VISUAL,
        },
    }


@app.get("/directors")
async def list_directors():
    """Lista todos os directors disponíveis por nível"""
    return {
        "level_plus_2": [],
        "level_plus_1": [],
        "level_0": [
            {
                "name": "MotionGraphicsDirector0",
                "endpoint": "/directors/level-0/motion-graphics/plan",
                "description": "Planeja motion graphics (catálogo Manim)"
            },
            {
                "name": "VisualLayoutDirector1",
                "endpoint": "/directors/level-0/visual-layout/generate",
                "description": "Gera layouts visuais via HTML/CSS (LLM code-gen)",
                "model": OPENAI_MODEL_VISUAL
            }
        ],
        "level_minus_1": [],
        "level_minus_2": []
    }


@app.post("/directors/level-0/motion-graphics/plan")
async def plan_motion_graphics(request: MotionGraphicsPlanRequest):
    """
    Planeja motion graphics usando MotionGraphicsDirector0
    
    Este director recebe contexto COMPLETO (incluindo posições de texto)
    e planeja estrategicamente onde/quando colocar motion graphics.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY não configurada"
        )
    
    try:
        # Construir contexto otimizado
        context_builder = get_context_builder()
        optimized_context = context_builder.build_motion_graphics_context(
            request.context.model_dump()
        )
        
        # Chamar Director
        director = get_motion_graphics_director_0(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL
        )
        
        result = await director.plan(
            user_prompt=request.user_prompt,
            context=optimized_context
        )
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Erro no endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/directors/level-0/motion-graphics/plan-simple")
async def plan_motion_graphics_simple(request: Dict):
    """
    Versão simplificada do endpoint de planejamento
    
    Aceita contexto raw sem validação estrita.
    Útil para testes e integrações rápidas.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY não configurada"
        )
    
    try:
        user_prompt = request.get('user_prompt')
        raw_context = request.get('context', {})
        
        if not user_prompt:
            raise HTTPException(
                status_code=400,
                detail="Campo 'user_prompt' é obrigatório"
            )
        
        # Construir contexto
        context_builder = get_context_builder()
        optimized_context = context_builder.build_motion_graphics_context(raw_context)
        
        # Chamar Director
        director = get_motion_graphics_director_0(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL
        )
        
        result = await director.plan(
            user_prompt=user_prompt,
            context=optimized_context
        )
        
        return result
    
    except Exception as e:
        logger.error(f"❌ Erro no endpoint simplificado: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ═══════════════════════════════════════════════════════════
# VISUAL LAYOUT DIRECTOR v1 ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.post("/directors/level-0/visual-layout/generate")
async def generate_visual_layout(request: VisualLayoutRequest):
    """
    Gera layout visual completo via LLM (HTML/CSS por layer).

    Cada cena retorna layers com HTML inline + metadados de animação.
    Use o render service para converter layers em PNGs transparentes.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada")

    try:
        # Construir contexto
        context_builder = get_context_builder()
        context = context_builder.build_visual_layout_context({
            "canvas": request.canvas,
            "template_style": request.template_style or {},
            "script_text": request.script_text or "",
            "scene_descriptions": request.scene_descriptions or [],
            "timestamps": request.timestamps or [],
            "occupied_areas": request.occupied_areas or [],
            "component_library": request.component_library or [],
        })

        # Chamar Director v1
        director = get_visual_layout_director_1(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL_VISUAL,
        )

        result = await director.generate(
            user_prompt=request.user_prompt,
            context=context,
            reference_image_url=request.reference_image_url,
        )

        return result

    except Exception as e:
        logger.error(f"❌ Erro no visual-layout/generate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/directors/level-0/visual-layout/edit-layer")
async def edit_visual_layer(request: EditLayerRequest):
    """
    Edita uma layer específica via instrução em texto natural.

    Ex: "mude a cor do título para azul", "aumente a fonte em 20%"
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada")

    try:
        director = get_visual_layout_director_1(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL_VISUAL,
        )

        result = await director.edit_layer(
            layer_id=request.layer_id,
            current_html=request.current_html,
            edit_instruction=request.edit_instruction,
            context={"canvas": request.canvas},
        )

        return result

    except Exception as e:
        logger.error(f"❌ Erro no visual-layout/edit-layer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/directors/level-0/visual-layout/generate-simple")
async def generate_visual_layout_simple(request: Dict):
    """
    Versão simplificada — aceita JSON arbitrário.
    Útil para testes e integrações rápidas.
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada")

    try:
        user_prompt = request.get("user_prompt")
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Campo 'user_prompt' é obrigatório")

        context_builder = get_context_builder()
        context = context_builder.build_visual_layout_context(request)

        director = get_visual_layout_director_1(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL_VISUAL,
        )

        result = await director.generate(
            user_prompt=user_prompt,
            context=context,
            reference_image_url=request.get("reference_image_url"),
        )

        return result

    except Exception as e:
        logger.error(f"❌ Erro no visual-layout/generate-simple: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# RENDER ENDPOINTS (Playwright HTML → PNG)
# ═══════════════════════════════════════════════════════════

class RenderLayerRequest(BaseModel):
    """Request para renderizar uma layer HTML em PNG"""
    html: str = Field(..., description="HTML inline da layer")
    canvas_width: int = Field(default=720)
    canvas_height: int = Field(default=1280)
    crop_to_content: bool = Field(default=False, description="Recortar ao bounding box")
    google_fonts: Optional[List[str]] = Field(default=None, description="Fontes Google")


class RenderSceneRequest(BaseModel):
    """Request para renderizar todas layers de uma cena"""
    scene: Dict = Field(..., description="Objeto scene do Director v1")
    canvas_width: int = Field(default=720)
    canvas_height: int = Field(default=1280)
    google_fonts: Optional[List[str]] = Field(default=None)
    output_dir: Optional[str] = Field(default=None, description="Se informado, salva PNGs em disco")


@app.post("/render/layer")
async def api_render_layer(request: RenderLayerRequest):
    """
    Renderiza uma layer HTML → PNG transparente.

    Retorna PNG como base64 + metadata de posição/dimensão.
    """
    try:
        result = await render_layer_to_png(
            html=request.html,
            canvas_width=request.canvas_width,
            canvas_height=request.canvas_height,
            crop_to_content=request.crop_to_content,
            google_fonts=request.google_fonts,
        )
        return {"status": "success", **result}
    except Exception as e:
        logger.error(f"❌ Erro no render/layer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/render/scene")
async def api_render_scene(request: RenderSceneRequest):
    """
    Renderiza todas as layers de uma cena → PNGs + metadata.

    Se output_dir for informado, salva PNGs em disco (mais eficiente para pipeline).
    Caso contrário, retorna base64 no JSON.
    """
    try:
        result = await render_scene_layers(
            scene=request.scene,
            canvas_width=request.canvas_width,
            canvas_height=request.canvas_height,
            google_fonts=request.google_fonts,
            output_dir=request.output_dir,
        )
        return {"status": "success", **result}
    except Exception as e:
        logger.error(f"❌ Erro no render/scene: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/render/full-pipeline")
async def api_render_full_pipeline(request: Dict):
    """
    Pipeline completo: prompt → LLM → layers HTML → render PNGs.

    Combina Director v1 + Renderer em um único endpoint.
    Entrada mínima: { "user_prompt": "..." }
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY não configurada")

    try:
        user_prompt = request.get("user_prompt")
        if not user_prompt:
            raise HTTPException(status_code=400, detail="Campo 'user_prompt' é obrigatório")

        canvas = request.get("canvas", {"width": 720, "height": 1280})
        output_dir = request.get("output_dir")

        # 1) Gerar layout via LLM
        context_builder = get_context_builder()
        context = context_builder.build_visual_layout_context(request)

        director = get_visual_layout_director_1(
            api_key=OPENAI_API_KEY,
            model=OPENAI_MODEL_VISUAL,
        )

        llm_result = await director.generate(
            user_prompt=user_prompt,
            context=context,
            reference_image_url=request.get("reference_image_url"),
        )

        if llm_result.get("status") != "success":
            return llm_result

        # 2) Renderizar cada cena
        scenes = llm_result["result"].get("scenes", [])
        google_fonts = llm_result["result"].get("google_fonts_needed", [])

        rendered_scenes = []
        for scene in scenes:
            scene_out_dir = None
            if output_dir:
                scene_out_dir = str(Path(output_dir) / scene.get("scene_id", "scene"))

            rendered = await render_scene_layers(
                scene=scene,
                canvas_width=canvas.get("width", 720),
                canvas_height=canvas.get("height", 1280),
                google_fonts=google_fonts,
                output_dir=scene_out_dir,
            )
            rendered_scenes.append(rendered)

        return {
            "status": "success",
            "llm_result": llm_result["result"],
            "rendered_scenes": rendered_scenes,
            "llm_usage": llm_result.get("llm_usage"),
        }

    except Exception as e:
        logger.error(f"❌ Erro no render/full-pipeline: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# STARTUP / SHUTDOWN
# ═══════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Evento de startup"""
    logger.info("🎬 V-LLM Directors iniciando...")
    logger.info(f"   OpenAI API: {'✅ Configurada' if OPENAI_API_KEY else '❌ Não configurada'}")
    logger.info(f"   Director 0 (Manim): {OPENAI_MODEL}")
    logger.info(f"   Director 1 (Visual Layout): {OPENAI_MODEL_VISUAL}")
    logger.info("✅ V-LLM Directors pronto!")


@app.on_event("shutdown")
async def shutdown_event():
    """Encerra browser Playwright."""
    logger.info("🛑 Encerrando Playwright browser...")
    await shutdown_browser()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 5025))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
    )
