"""
🔧 Context Builder

Monta contexto completo e otimizado para Directors
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ContextBuilder:
    """
    Constrói contexto rico para LLM Directors
    """
    
    def build_motion_graphics_context(
        self,
        raw_context: Dict
    ) -> Dict:
        """
        Constrói contexto otimizado para MotionGraphicsDirector0
        
        Args:
            raw_context: Contexto bruto do orquestrador
                {
                    "transcription": str,
                    "words": [{word, start, end, emphasis}, ...],
                    "text_layout": [{sentences com positions}, ...],
                    "canvas": {width, height},
                    "duration": float,
                    "style": str
                }
        
        Returns:
            Contexto otimizado e estruturado para LLM
        """
        logger.info("🔧 Construindo contexto para MotionGraphicsDirector0...")
        
        # Extrair dados
        transcription = raw_context.get('transcription', '')
        words = raw_context.get('words', [])
        text_layout = raw_context.get('text_layout', [])
        canvas = raw_context.get('canvas', {'width': 1080, 'height': 1920})
        duration = raw_context.get('duration', 0)
        style = raw_context.get('style', 'modern')
        
        # Identificar palavras emphasis
        emphasis_words = [
            {
                'word': w['word'],
                'start': w.get('start_time', w.get('start', 0)),
                'end': w.get('end_time', w.get('end', 0))
            }
            for w in words if w.get('emphasis', False)
        ]
        
        # Mapear palavras com posições
        words_with_positions = self._map_words_to_positions(
            words,
            text_layout
        )
        
        # Identificar espaços vazios
        empty_spaces = self._identify_empty_spaces(
            text_layout,
            canvas
        )
        
        # Montar contexto estruturado
        context = {
            "video": {
                "transcription": transcription,
                "duration": duration,
                "style": style,
                "canvas": canvas
            },
            
            "words": {
                "total": len(words),
                "emphasis": emphasis_words,
                "with_positions": words_with_positions[:20]  # Limitar para não sobrecarregar
            },
            
            "text_layout": {
                "sentences": text_layout,
                "total_groups": len(text_layout),
                "occupied_areas": self._calculate_occupied_areas(text_layout)
            },
            
            "available_space": {
                "empty_regions": empty_spaces,
                "safe_zones": self._calculate_safe_zones(text_layout, canvas)
            },
            
            "constraints": {
                "max_motion_graphics": 5,
                "min_spacing_between_mgs": 1.0,  # segundos
                "anticipation_time": 0.2  # aparecer 0.2s antes
            }
        }
        
        logger.info(f"✅ Contexto construído:")
        logger.info(f"   - Palavras: {len(words)}")
        logger.info(f"   - Emphasis: {len(emphasis_words)}")
        logger.info(f"   - Grupos de texto: {len(text_layout)}")
        logger.info(f"   - Espaços vazios: {len(empty_spaces)}")
        
        return context
    
    def _map_words_to_positions(
        self,
        words: List[Dict],
        text_layout: List[Dict]
    ) -> List[Dict]:
        """
        Mapeia palavras com suas posições no canvas
        """
        mapped = []
        
        for group in text_layout:
            group_words = group.get('words', [])
            group_position = group.get('position', {})
            
            for word_data in group_words:
                # word_data pode ser string ou dict
                if isinstance(word_data, str):
                    word_text = word_data
                    position = group_position  # usar posição do grupo
                    dimensions = {}
                else:
                    word_text = word_data.get('text', '')
                    position = word_data.get('canvas_position', group_position)
                    dimensions = word_data.get('dimensions', {})
                
                # Encontrar timing da palavra
                timing = next(
                    (w for w in words if w.get('word', '').lower() == word_text.lower()),
                    None
                )
                
                if timing:
                    mapped.append({
                        'word': word_text,
                        'position': position,
                        'dimensions': dimensions,
                        'start': timing.get('start_time', timing.get('start', 0)),
                        'end': timing.get('end_time', timing.get('end', 0)),
                        'emphasis': timing.get('emphasis', False)
                    })
        
        return mapped
    
    def _identify_empty_spaces(
        self,
        text_layout: List[Dict],
        canvas: Dict
    ) -> List[Dict]:
        """
        Identifica regiões vazias do canvas
        """
        canvas_width = canvas['width']
        canvas_height = canvas['height']
        
        # Calcular áreas ocupadas
        occupied = []
        for group in text_layout:
            layout = group.get('layout', {})
            if layout:
                occupied.append({
                    'x': layout.get('center_x', 0),
                    'y': layout.get('center_y', 0),
                    'width': layout.get('group_width', 0),
                    'height': layout.get('group_height', 0)
                })
        
        # Identificar espaços vazios (simplificado)
        # TODO: Implementar algoritmo mais sofisticado
        empty_spaces = []
        
        # Assumir que texto está no terço inferior (comum em shorts)
        # Espaço acima do texto é vazio
        if occupied:
            min_y = min(o['y'] - o['height']/2 for o in occupied)
            if min_y > 100:
                empty_spaces.append({
                    'region': 'top',
                    'x_range': [0, canvas_width],
                    'y_range': [0, min_y - 50],
                    'suitable_for': ['arrow_pointing', 'icon']
                })
        
        return empty_spaces
    
    def _calculate_occupied_areas(
        self,
        text_layout: List[Dict]
    ) -> List[Dict]:
        """
        Calcula áreas ocupadas por texto
        """
        areas = []
        
        for group in text_layout:
            layout = group.get('layout', {})
            if layout:
                cx = layout.get('center_x', 0)
                cy = layout.get('center_y', 0)
                w = layout.get('group_width', 0)
                h = layout.get('group_height', 0)
                
                areas.append({
                    'center': {'x': cx, 'y': cy},
                    'dimensions': {'width': w, 'height': h},
                    'bounding_box': {
                        'left': cx - w/2,
                        'right': cx + w/2,
                        'top': cy - h/2,
                        'bottom': cy + h/2
                    }
                })
        
        return areas
    
    # ═══════════════════════════════════════════════════════════
    # CONTEXTO PARA VISUAL LAYOUT DIRECTOR (v1)
    # ═══════════════════════════════════════════════════════════

    def build_visual_layout_context(self, raw_context: Dict) -> Dict:
        """
        Constrói contexto otimizado para VisualLayoutDirector1.

        Args:
            raw_context: {
                "canvas": {width, height},
                "template_style": {colors, fonts, mood},
                "script_text": str,
                "scene_descriptions": [{scene_id, text, visual_hint, start_time, duration}],
                "timestamps": [{text, start, end}],
                "occupied_areas": [{x, y, width, height}],  # subtitle positions
                "user_prompt": str,
                "reference_image_url": str (optional),
                "component_library": [...] (optional)
            }

        Returns:
            Contexto estruturado para o Director v1
        """
        logger.info("🔧 Construindo contexto para VisualLayoutDirector1...")

        canvas = raw_context.get("canvas", {"width": 720, "height": 1280})
        template_style = raw_context.get("template_style", {})
        script_text = raw_context.get("script_text", "")
        scene_descriptions = raw_context.get("scene_descriptions", [])
        timestamps = raw_context.get("timestamps", [])
        occupied_areas = raw_context.get("occupied_areas", [])
        component_library = raw_context.get("component_library", [])

        # Defaults para template_style
        if not template_style.get("colors"):
            template_style["colors"] = {
                "primary": "#00e5ff",
                "secondary": "#7c3aed",
                "accent": "#ff6b35",
                "background": "#0a0a2e",
                "text": "#ffffff",
            }
        if not template_style.get("fonts"):
            template_style["fonts"] = {
                "title": "Space Grotesk",
                "body": "Inter",
            }
        if not template_style.get("mood"):
            template_style["mood"] = "modern, clean, professional"

        context = {
            "canvas": canvas,
            "template_style": template_style,
            "script_text": script_text,
            "scene_descriptions": scene_descriptions,
            "timestamps": timestamps,
            "occupied_areas": occupied_areas,
            "component_library": component_library,
        }

        logger.info(f"✅ Contexto visual construído:")
        logger.info(f"   - Canvas: {canvas['width']}x{canvas['height']}")
        logger.info(f"   - Scenes: {len(scene_descriptions)}")
        logger.info(f"   - Timestamps: {len(timestamps)}")
        logger.info(f"   - Style: {template_style.get('mood', 'N/A')}")

        return context

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def _calculate_safe_zones(
        self,
        text_layout: List[Dict],
        canvas: Dict
    ) -> List[Dict]:
        """
        Calcula zonas seguras para posicionar MGs (sem sobrepor texto)
        """
        # TODO: Implementar cálculo de safe zones
        # Por ora, retornar zonas genéricas
        
        return [
            {
                'zone': 'above_text',
                'description': 'Acima do texto principal',
                'suitable_for': ['arrow_pointing', 'icon']
            },
            {
                'zone': 'around_word',
                'description': 'Ao redor de palavra específica',
                'suitable_for': ['oval_highlight', 'circle_attention']
            },
            {
                'zone': 'below_word',
                'description': 'Embaixo de palavra',
                'suitable_for': ['underline']
            }
        ]


# Singleton instance
_context_builder = None


def get_context_builder() -> ContextBuilder:
    """Retorna instância singleton"""
    global _context_builder
    if _context_builder is None:
        _context_builder = ContextBuilder()
    return _context_builder
