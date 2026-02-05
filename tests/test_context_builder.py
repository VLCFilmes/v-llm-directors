"""
Testes unitários para ContextBuilder
"""

import pytest
from app.orchestrator.context_builder import ContextBuilder


@pytest.fixture
def context_builder():
    """Fixture para ContextBuilder"""
    return ContextBuilder()


@pytest.fixture
def sample_context():
    """Contexto de exemplo para testes"""
    return {
        "transcription": "Bem-vindo ao tutorial. Passo 1: Abra o aplicativo.",
        "words": [
            {"word": "Bem-vindo", "start_time": 0.0, "end_time": 0.5, "confidence": 0.98},
            {"word": "tutorial", "start_time": 0.6, "end_time": 1.0, "confidence": 0.95, "emphasis": True},
            {"word": "Passo", "start_time": 1.5, "end_time": 1.8, "confidence": 0.99, "emphasis": True},
            {"word": "1", "start_time": 1.9, "end_time": 2.0, "confidence": 0.99, "emphasis": True},
            {"word": "Abra", "start_time": 2.1, "end_time": 2.4, "confidence": 0.97, "emphasis": True},
            {"word": "aplicativo", "start_time": 2.5, "end_time": 3.0, "confidence": 0.96, "emphasis": True},
        ],
        "text_layout": [
            {
                "id": "sentence_001",
                "text": "Bem-vindo ao tutorial",
                "position": {"x": 100, "y": 200, "width": 880, "height": 100},
                "timing": {"start_time": 0.0, "end_time": 2.0},
                "words": ["Bem-vindo", "ao", "tutorial"]
            },
            {
                "id": "sentence_002",
                "text": "Passo 1: Abra o aplicativo",
                "position": {"x": 100, "y": 500, "width": 880, "height": 120},
                "timing": {"start_time": 1.5, "end_time": 4.0},
                "words": ["Passo", "1", "Abra", "o", "aplicativo"]
            }
        ],
        "canvas": {"width": 1080, "height": 1920},
        "duration": 5.0,
        "style": {
            "primary_color": "#FF6B35",
            "accent_color": "#F7931E",
            "theme": "tutorial"
        }
    }


def test_build_motion_graphics_context(context_builder, sample_context):
    """Testa construção de contexto para motion graphics"""
    result = context_builder.build_motion_graphics_context(sample_context)
    
    # Verificar estrutura básica
    assert "transcription" in result
    assert "words_with_positions" in result
    assert "text_layout" in result
    assert "canvas" in result
    assert "duration" in result
    assert "style" in result
    assert "emphasis_words" in result
    
    # Verificar transcription
    assert result["transcription"] == sample_context["transcription"]
    
    # Verificar canvas
    assert result["canvas"] == sample_context["canvas"]
    
    # Verificar duration
    assert result["duration"] == sample_context["duration"]
    
    # Verificar emphasis words
    assert len(result["emphasis_words"]) > 0
    assert "tutorial" in result["emphasis_words"]
    assert "Passo" in result["emphasis_words"]


def test_map_words_to_positions(context_builder, sample_context):
    """Testa mapeamento de palavras para posições"""
    words = sample_context["words"]
    text_layout = sample_context["text_layout"]
    
    mapped_words = context_builder._map_words_to_positions(words, text_layout)
    
    # Verificar que palavras foram mapeadas
    assert len(mapped_words) > 0
    
    # Verificar estrutura de palavra mapeada
    for word_data in mapped_words:
        assert "word" in word_data
        assert "timing" in word_data
        assert "position" in word_data or word_data["position"] is None


def test_identify_empty_spaces(context_builder, sample_context):
    """Testa identificação de espaços vazios"""
    text_layout = sample_context["text_layout"]
    canvas = sample_context["canvas"]
    
    empty_spaces = context_builder._identify_empty_spaces(text_layout, canvas)
    
    # Verificar que espaços foram identificados
    assert isinstance(empty_spaces, list)
    
    # Verificar estrutura de espaço vazio
    for space in empty_spaces:
        assert "region" in space
        assert "position" in space
        assert "x" in space["position"]
        assert "y" in space["position"]


def test_calculate_occupied_areas(context_builder, sample_context):
    """Testa cálculo de áreas ocupadas"""
    text_layout = sample_context["text_layout"]
    
    occupied_areas = context_builder._calculate_occupied_areas(text_layout)
    
    # Verificar que áreas foram calculadas
    assert isinstance(occupied_areas, list)
    assert len(occupied_areas) == len(text_layout)
    
    # Verificar estrutura de área ocupada
    for area in occupied_areas:
        assert "element_id" in area
        assert "bbox" in area
        assert "x" in area["bbox"]
        assert "y" in area["bbox"]
        assert "width" in area["bbox"]
        assert "height" in area["bbox"]


def test_calculate_safe_zones(context_builder, sample_context):
    """Testa cálculo de zonas seguras"""
    text_layout = sample_context["text_layout"]
    canvas = sample_context["canvas"]
    
    safe_zones = context_builder._calculate_safe_zones(text_layout, canvas)
    
    # Verificar que zonas foram calculadas
    assert isinstance(safe_zones, list)


def test_empty_context(context_builder):
    """Testa contexto vazio"""
    empty_context = {
        "transcription": "",
        "words": [],
        "text_layout": [],
        "canvas": {"width": 1080, "height": 1920},
        "duration": 0.0
    }
    
    result = context_builder.build_motion_graphics_context(empty_context)
    
    # Deve funcionar sem erros
    assert result["transcription"] == ""
    assert len(result["emphasis_words"]) == 0
    assert len(result["words_with_positions"]) == 0


def test_context_without_emphasis(context_builder):
    """Testa contexto sem palavras de ênfase"""
    context = {
        "transcription": "Texto simples sem ênfase",
        "words": [
            {"word": "Texto", "start_time": 0.0, "end_time": 0.5, "confidence": 0.98},
            {"word": "simples", "start_time": 0.6, "end_time": 1.0, "confidence": 0.95},
        ],
        "text_layout": [],
        "canvas": {"width": 1080, "height": 1920},
        "duration": 2.0
    }
    
    result = context_builder.build_motion_graphics_context(context)
    
    # Deve funcionar sem palavras de ênfase
    assert len(result["emphasis_words"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
