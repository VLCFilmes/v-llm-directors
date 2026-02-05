"""
🎬 Motion Graphics Director 0

Director tático que planeja motion graphics baseado em contexto completo do vídeo.

NÍVEL: 0 (Tactical/Core)

CONHECE:
- Transcrição completa
- Timestamps de cada palavra
- Posições EXATAS de todos os textos (X, Y, width, height)
- Bounding boxes de frases
- Espaços vazios do canvas

DECIDE:
- Onde colocar motion graphics
- Quando aparecer (timing)
- Que tipo de MG usar
- Cores e estilos
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class MotionGraphicsDirector0:
    """
    Director Tático de Motion Graphics
    
    Planeja motion graphics estratégicos baseado em contexto completo.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = self._load_system_prompt()
        self.examples = self._load_examples()
        logger.info(f"🎬 MotionGraphicsDirector0 inicializado (model: {model})")
    
    def _load_system_prompt(self) -> str:
        """Carrega system prompt do arquivo"""
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "level_0" / "motion_graphics_director_0" / "system_prompt.txt"
        
        if not prompt_path.exists():
            logger.warning(f"⚠️ System prompt não encontrado: {prompt_path}")
            return "Você é um Motion Graphics Director."
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_examples(self) -> Dict:
        """Carrega exemplos do arquivo"""
        examples_path = Path(__file__).parent.parent.parent / "prompts" / "level_0" / "motion_graphics_director_0" / "examples.json"
        
        if not examples_path.exists():
            logger.warning(f"⚠️ Examples não encontrados: {examples_path}")
            return {"examples": []}
        
        with open(examples_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def plan(
        self,
        user_prompt: str,
        context: Dict,
        max_tokens: int = 4000
    ) -> Dict:
        """
        Planeja motion graphics baseado em contexto completo
        
        Args:
            user_prompt: Prompt do usuário (ex: "Crie setas e grifados")
            context: Contexto completo do vídeo (já construído pelo ContextBuilder)
            max_tokens: Máximo de tokens para resposta
        
        Returns:
            {
                "status": "success",
                "level": 0,
                "director": "MotionGraphicsDirector0",
                "plan": {
                    "motion_graphics": [...],
                    "total": 3,
                    "reasoning": "..."
                },
                "llm_usage": {
                    "model": "gpt-3.5-turbo",
                    "input_tokens": 1234,
                    "output_tokens": 567,
                    "total_tokens": 1801
                }
            }
        """
        logger.info(f"🎬 [DIRECTOR0] Planejando motion graphics...")
        logger.info(f"   Prompt: {user_prompt[:100]}...")
        logger.info(f"   Model: {self.model}")
        
        try:
            # Montar mensagem para LLM
            user_message = self._build_user_message(user_prompt, context)
            
            # Chamar OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,  # Criatividade moderada
                response_format={"type": "json_object"},  # Force JSON output
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            
            # Extrair resposta
            response_text = response.choices[0].message.content
            
            # Parse JSON
            try:
                plan = json.loads(response_text)
            except json.JSONDecodeError:
                # LLM pode ter retornado texto + JSON
                # Tentar extrair JSON
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start >= 0 and end > start:
                    plan = json.loads(response_text[start:end])
                else:
                    raise ValueError("Resposta não contém JSON válido")
            
            # Validar plano
            if not isinstance(plan.get('motion_graphics'), list):
                raise ValueError("Campo 'motion_graphics' deve ser uma lista")
            
            # Limitar a 5 MGs (regra de ouro)
            if len(plan['motion_graphics']) > 5:
                logger.warning(f"⚠️ LLM sugeriu {len(plan['motion_graphics'])} MGs, limitando a 5")
                plan['motion_graphics'] = plan['motion_graphics'][:5]
                plan['total'] = 5
            
            logger.info(f"✅ [DIRECTOR0] Plano criado: {len(plan['motion_graphics'])} MGs")
            
            # Extrair usage
            usage = response.usage
            
            return {
                "status": "success",
                "level": 0,
                "director": "MotionGraphicsDirector0",
                "plan": plan,
                "llm_usage": {
                    "model": self.model,
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
            }
        
        except Exception as e:
            logger.error(f"❌ [DIRECTOR0] Erro ao planejar: {e}")
            return {
                "status": "error",
                "level": 0,
                "director": "MotionGraphicsDirector0",
                "error": str(e),
                "details": str(type(e).__name__)
            }
    
    def _build_user_message(self, user_prompt: str, context: Dict) -> str:
        """
        Monta mensagem do usuário com contexto estruturado
        """
        # Extrair informações principais
        video_info = context.get('video', {})
        words_info = context.get('words', {})
        text_layout_info = context.get('text_layout', {})
        available_space = context.get('available_space', {})
        
        # Montar mensagem estruturada
        message = f"""
## PROMPT DO USUÁRIO

{user_prompt}

## CONTEXTO DO VÍDEO

**Duração:** {video_info.get('duration')}s
**Canvas:** {video_info.get('canvas', {}).get('width')}x{video_info.get('canvas', {}).get('height')}
**Estilo:** {video_info.get('style')}

**Transcrição:**
{video_info.get('transcription', '')[:500]}...

## PALAVRAS IMPORTANTES (Emphasis)

{json.dumps(words_info.get('emphasis', []), indent=2, ensure_ascii=False)}

## LAYOUT DE TEXTO (Posições Exatas)

Total de grupos de texto: {text_layout_info.get('total_groups', 0)}

Primeiros 3 grupos:
{json.dumps(text_layout_info.get('sentences', [])[:3], indent=2, ensure_ascii=False)}

## ESPAÇOS DISPONÍVEIS

{json.dumps(available_space.get('safe_zones', []), indent=2, ensure_ascii=False)}

## INSTRUÇÕES

Analise o contexto acima e crie um plano de motion graphics que:

1. Destaque os pontos mais importantes do vídeo
2. Use posições que NÃO sobreponham o texto existente
3. Apareçam em momentos estratégicos (0.2s antes da palavra-alvo)
4. Criem antecipação e retenção visual
5. Sejam balanceados ao longo do vídeo (máximo 5 MGs)

Retorne APENAS JSON válido com o plano, seguindo exatamente o formato especificado no system prompt.
"""
        
        return message


# Singleton instance
_director = None


def get_motion_graphics_director_0(api_key: str, model: str = None) -> MotionGraphicsDirector0:
    """Retorna instância singleton (ou cria nova se mudar API key)"""
    global _director
    if _director is None:
        _director = MotionGraphicsDirector0(api_key, model or "gpt-3.5-turbo")
    return _director
