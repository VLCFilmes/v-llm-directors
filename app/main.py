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

from directors.level_0.motion_graphics_director_0 import get_motion_graphics_director_0
from orchestrator.context_builder import get_context_builder

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
        "model": OPENAI_MODEL
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
                "description": "Planeja motion graphics baseado em contexto completo"
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
# STARTUP
# ═══════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup_event():
    """Evento de startup"""
    logger.info("🎬 V-LLM Directors iniciando...")
    logger.info(f"   OpenAI API: {'✅ Configurada' if OPENAI_API_KEY else '❌ Não configurada'}")
    logger.info(f"   Model: {OPENAI_MODEL}")
    logger.info("✅ V-LLM Directors pronto!")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', 5025))
    host = os.getenv('HOST', '0.0.0.0')
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True
    )
