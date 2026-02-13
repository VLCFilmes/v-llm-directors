"""
🎨 Visual Layout Director 1

Director tático que GERA CÓDIGO HTML/CSS para motion graphics visuais.
Substitui o MotionGraphicsDirector0 (Manim) por layouts programáticos.

NÍVEL: 0 (Tactical/Core)

DIFERENÇA vs Director0:
- Director0: seleciona de catálogo fixo (arrow, circle, underline)
- Director1: GERA código HTML/CSS livre para layouts visuais completos

OUTPUT:
- Scenes com layers (cada layer = HTML/CSS → PNG transparente)
- Animações definidas por layer (entrance, exit, loop)
- Strokes com SVG path para reveal animation

MODELO:
- Fase 1: OpenAI GPT-4o (já integrado)
- Fase 2: Anthropic Claude Sonnet (plug-and-play)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class VisualLayoutDirector1:
    """
    Director Tático de Visual Layout — gera código HTML/CSS para motion graphics.
    
    Cada cena do vídeo é decomposta em layers visuais (PNG transparentes)
    que são renderizadas via Playwright e animadas no v-editor-python.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = self._load_system_prompt()
        self.examples = self._load_examples()
        logger.info(f"🎨 VisualLayoutDirector1 inicializado (model: {model})")

    def _load_system_prompt(self) -> str:
        """Carrega system prompt do arquivo."""
        prompt_path = (
            Path(__file__).parent.parent.parent
            / "prompts" / "level_0" / "visual_layout_director_1" / "system_prompt.txt"
        )
        if not prompt_path.exists():
            logger.warning(f"⚠️ System prompt não encontrado: {prompt_path}")
            return "You are a Visual Layout Director that generates HTML/CSS for video motion graphics."
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_examples(self) -> Dict:
        """Carrega exemplos few-shot do arquivo."""
        examples_path = (
            Path(__file__).parent.parent.parent
            / "prompts" / "level_0" / "visual_layout_director_1" / "examples.json"
        )
        if not examples_path.exists():
            logger.warning(f"⚠️ Examples não encontrados: {examples_path}")
            return {"examples": []}
        with open(examples_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ─────────────────────────────────────────────
    # PUBLIC API
    # ─────────────────────────────────────────────

    async def generate(
        self,
        user_prompt: str,
        context: Dict,
        max_tokens: int = 16000,
        reference_image_url: Optional[str] = None,
    ) -> Dict:
        """
        Gera layout visual completo com HTML/CSS por layer.

        Args:
            user_prompt: Descrição do visual desejado
            context: Contexto do vídeo (canvas, style, text, timestamps, etc.)
            max_tokens: Máximo de tokens para resposta
            reference_image_url: URL/base64 de imagem de referência (opcional)

        Returns:
            {
                "status": "success",
                "level": 0,
                "director": "VisualLayoutDirector1",
                "result": {
                    "scenes": [...],
                    "google_fonts_needed": [...],
                    "reasoning": "..."
                },
                "llm_usage": { ... }
            }
        """
        logger.info("🎨 [DIRECTOR1] Gerando layout visual...")
        logger.info(f"   Prompt: {user_prompt[:120]}...")
        logger.info(f"   Model: {self.model}")

        try:
            # Montar mensagens
            messages = self._build_messages(
                user_prompt, context, reference_image_url
            )

            # Chamar LLM
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                response_format={"type": "json_object"},
                messages=messages,
            )

            # Parse resposta
            response_text = response.choices[0].message.content
            result = self._parse_json_response(response_text)

            # Validar resultado
            self._validate_result(result)

            logger.info(
                f"✅ [DIRECTOR1] Layout gerado: "
                f"{len(result.get('scenes', []))} cenas, "
                f"{sum(len(s.get('layers', [])) for s in result.get('scenes', []))} layers total"
            )

            usage = response.usage
            return {
                "status": "success",
                "level": 0,
                "director": "VisualLayoutDirector1",
                "result": result,
                "llm_usage": {
                    "model": self.model,
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
            }

        except Exception as e:
            logger.error(f"❌ [DIRECTOR1] Erro ao gerar layout: {e}", exc_info=True)
            return {
                "status": "error",
                "level": 0,
                "director": "VisualLayoutDirector1",
                "error": str(e),
                "details": type(e).__name__,
            }

    async def edit_layer(
        self,
        layer_id: str,
        current_html: str,
        edit_instruction: str,
        context: Dict,
        max_tokens: int = 4000,
    ) -> Dict:
        """
        Edita uma layer específica baseado em instrução do usuário.

        Args:
            layer_id: ID da layer a editar
            current_html: HTML/CSS atual da layer
            edit_instruction: "mude a cor para azul", "aumente a fonte", etc.
            context: Contexto mínimo (canvas size, style)

        Returns:
            {
                "status": "success",
                "layer": { "id", "html", "description", ... },
                "llm_usage": { ... }
            }
        """
        logger.info(f"🎨 [DIRECTOR1] Editando layer {layer_id}: {edit_instruction[:80]}...")

        try:
            canvas = context.get("canvas", {"width": 720, "height": 1280})

            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": (
                        f"## EDIT REQUEST\n\n"
                        f"Edit the following layer based on the instruction.\n\n"
                        f"**Layer ID:** {layer_id}\n"
                        f"**Canvas:** {canvas['width']}x{canvas['height']}\n"
                        f"**Instruction:** {edit_instruction}\n\n"
                        f"**Current HTML:**\n```html\n{current_html}\n```\n\n"
                        f"Return JSON with the updated layer object (same format as in scenes.layers). "
                        f"Only return the single layer, not a full scenes array."
                    ),
                },
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.5,
                response_format={"type": "json_object"},
                messages=messages,
            )

            response_text = response.choices[0].message.content
            result = self._parse_json_response(response_text)

            usage = response.usage
            return {
                "status": "success",
                "layer": result,
                "llm_usage": {
                    "model": self.model,
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
            }

        except Exception as e:
            logger.error(f"❌ [DIRECTOR1] Erro ao editar layer: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "details": type(e).__name__,
            }

    # ─────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────

    def _build_messages(
        self,
        user_prompt: str,
        context: Dict,
        reference_image_url: Optional[str] = None,
    ) -> List[Dict]:
        """Monta a lista de messages para a chamada LLM."""
        messages = [{"role": "system", "content": self.system_prompt}]

        # Few-shot examples (completos para melhor qualidade)
        examples = self.examples.get("examples", [])
        if examples:
            # Enviar 1º exemplo completo como par user/assistant
            ex1 = examples[0]
            ex1_prompt = (
                f"## FEW-SHOT EXAMPLE\n\n"
                f"### {ex1['name']}\n"
                f"**Prompt:** {ex1['user_prompt']}\n"
                f"**Canvas:** {ex1['canvas']['width']}x{ex1['canvas']['height']}\n"
            )
            messages.append({"role": "user", "content": ex1_prompt})
            messages.append({
                "role": "assistant",
                "content": json.dumps(ex1["expected_output"], ensure_ascii=False),
            })

            # Enviar 2º exemplo completo se disponível (melhora diversidade)
            if len(examples) > 1:
                ex2 = examples[1]
                ex2_prompt = (
                    f"## ANOTHER EXAMPLE\n\n"
                    f"### {ex2['name']}\n"
                    f"**Prompt:** {ex2['user_prompt']}\n"
                    f"**Canvas:** {ex2['canvas']['width']}x{ex2['canvas']['height']}\n"
                )
                messages.append({"role": "user", "content": ex2_prompt})
                messages.append({
                    "role": "assistant",
                    "content": json.dumps(ex2["expected_output"], ensure_ascii=False),
                })

        # User message com contexto
        user_message = self._build_user_message(user_prompt, context)

        # Se tem imagem de referência, usar content multimodal
        if reference_image_url:
            content = [
                {"type": "text", "text": user_message},
                {
                    "type": "image_url",
                    "image_url": {"url": reference_image_url, "detail": "high"},
                },
            ]
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": user_message})

        return messages

    def _build_user_message(self, user_prompt: str, context: Dict) -> str:
        """Monta mensagem do usuário com contexto estruturado."""
        canvas = context.get("canvas", {"width": 720, "height": 1280})
        template_style = context.get("template_style", {})
        script_text = context.get("script_text", "")
        timestamps = context.get("timestamps", [])
        occupied_areas = context.get("occupied_areas", [])
        scene_descriptions = context.get("scene_descriptions", [])
        component_library = context.get("component_library", [])

        message = f"""## VISUAL LAYOUT REQUEST

### User Prompt
{user_prompt}

### Canvas
- Width: {canvas['width']}px
- Height: {canvas['height']}px
- Orientation: {"vertical" if canvas['height'] > canvas['width'] else "horizontal"}

### Template Style
- Colors: {json.dumps(template_style.get('colors', {}), ensure_ascii=False)}
- Fonts: {json.dumps(template_style.get('fonts', {}), ensure_ascii=False)}
- Mood: {template_style.get('mood', 'modern, clean')}
"""

        if script_text:
            message += f"""
### Script Text
{script_text[:1000]}
"""

        if scene_descriptions:
            message += f"""
### Scene Descriptions (from script)
{json.dumps(scene_descriptions[:6], indent=2, ensure_ascii=False)}
"""

        if timestamps:
            message += f"""
### Timestamps (first 10)
{json.dumps(timestamps[:10], indent=2, ensure_ascii=False)}
"""

        if occupied_areas:
            message += f"""
### Occupied Areas (subtitle positions — DO NOT OVERLAP)
{json.dumps(occupied_areas[:5], indent=2, ensure_ascii=False)}
"""

        if component_library:
            message += f"""
### Component Library (available building blocks)
{json.dumps(component_library, indent=2, ensure_ascii=False)}
"""

        message += """
### ⚠️ CRITICAL Instructions

Generate the visual layout following ALL rules:
1. **Generate ALL scenes** — One scene object for EACH scene_description. Do NOT skip any.
2. **Minimum 6 layers per scene** — background + 2-3 shapes/particles + title (word-by-word) + subtitle + decoration/CTA.
3. **Rich backgrounds** — Multi-stop gradients (3+ stops) with radial gradient mesh overlays. NEVER flat solid colors.
4. **EVERY title MUST use word-by-word animation** — Wrap each word in `<span data-w="N" style="display:inline-block;">` and use `word_stagger_up`, `word_stagger_fade`, or `word_stagger_scale` with `stagger_ms: 100-200`.
5. **Short labels/brand names: use letter-by-letter** — Wrap each letter in `<span data-l="N" style="display:inline-block;">` and use `letter_stagger_up` or `letter_stagger_fade` with `stagger_ms: 30-80`.
6. **Add decorative layers generously** — Glow orbs (pulse), geometric rings (spin), floating particles (float), corner brackets (fade_in), divider lines, diagonal accent lines. Fill the FULL canvas.
7. **Animate 70%+ of layers** — At least 70% should be `is_static: false`. Use staggered delays.
8. **Use ambient motion** — Add `loop` animations (pulse, float, spin) to shapes/glows for life.
9. **Use text from the script** — Title/subtitle text comes from scene_descriptions, not invented.
10. **Every scene equally rich** — Scene 5 should have the same visual density as Scene 1. No lazy scenes.
11. Return valid JSON matching the output schema.
"""

        return message

    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON da resposta da LLM, com fallback."""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Tentar extrair JSON de dentro do texto
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response_text[start:end])
            raise ValueError("Resposta não contém JSON válido")

    def _validate_result(self, result: Dict) -> None:
        """Valida estrutura do resultado."""
        scenes = result.get("scenes")
        if not isinstance(scenes, list):
            raise ValueError("Campo 'scenes' deve ser uma lista")

        for i, scene in enumerate(scenes):
            layers = scene.get("layers")
            if not isinstance(layers, list):
                raise ValueError(f"Scene {i}: campo 'layers' deve ser uma lista")

            if len(layers) > 15:
                logger.warning(
                    f"⚠️ Scene {i} tem {len(layers)} layers (recomendado: máx 8). "
                    f"Truncando para 15."
                )
                scene["layers"] = layers[:15]

            for j, layer in enumerate(layers):
                if "html" not in layer and layer.get("type") != "stroke_reveal":
                    raise ValueError(
                        f"Scene {i}, Layer {j}: campo 'html' obrigatório "
                        f"(exceto para stroke_reveal)"
                    )
                if "z_index" not in layer:
                    layer["z_index"] = 100 + j * 50  # auto z-index
                if "id" not in layer:
                    layer["id"] = f"layer_{i}_{j}"


# ─────────────────────────────────────────────
# SINGLETON
# ─────────────────────────────────────────────

_director: Optional[VisualLayoutDirector1] = None


def get_visual_layout_director_1(
    api_key: str, model: str = None
) -> VisualLayoutDirector1:
    """Retorna instância singleton (ou cria nova se necessário)."""
    global _director
    if _director is None:
        _director = VisualLayoutDirector1(api_key, model or "gpt-4o")
    return _director
