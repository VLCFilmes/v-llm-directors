# 🧪 Tests - V-LLM Directors

Testes unitários e de integração para o sistema V-LLM Directors.

---

## 📦 Setup

### Instalar Dependências

```bash
pip install -r requirements.txt
```

---

## 🚀 Executar Testes

### Todos os Testes

```bash
# Rodar todos os testes
pytest

# Com mais verbosidade
pytest -v

# Com cobertura
pytest --cov=app --cov-report=html
```

### Testes Específicos

```bash
# Testar apenas ContextBuilder
pytest tests/test_context_builder.py

# Testar apenas um teste específico
pytest tests/test_context_builder.py::test_build_motion_graphics_context

# Testar por marcador (se configurado)
pytest -m unit
pytest -m integration
```

---

## 📋 Estrutura de Testes

```
tests/
├── __init__.py
├── test_context_builder.py        # Testes do ContextBuilder
├── test_motion_graphics_director.py  # (TODO) Testes dos Directors
├── test_api_endpoints.py          # (TODO) Testes de endpoints
└── README.md
```

---

## 🧩 Tipos de Testes

### Unit Tests

Testam componentes individuais isoladamente.

**Exemplos:**
- `test_context_builder.py` - Testa lógica do ContextBuilder
- `test_motion_graphics_director.py` - Testa lógica dos Directors

### Integration Tests

Testam integração entre componentes.

**Exemplos:**
- `test_api_endpoints.py` - Testa endpoints completos
- `test_llm_integration.py` - Testa integração com Anthropic API

---

## 📝 Escrevendo Novos Testes

### Template Básico

```python
import pytest

@pytest.fixture
def sample_data():
    """Fixture com dados de exemplo"""
    return {
        "key": "value"
    }

def test_something(sample_data):
    """Testa funcionalidade X"""
    # Arrange
    input_data = sample_data
    
    # Act
    result = some_function(input_data)
    
    # Assert
    assert result == expected_value
```

### Testes Assíncronos

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Testa função assíncrona"""
    result = await some_async_function()
    assert result is not None
```

### Mocking API Calls

```python
from unittest.mock import patch, MagicMock

@patch('anthropic.Anthropic')
def test_llm_call(mock_anthropic):
    """Testa chamada LLM sem fazer requisição real"""
    # Configure o mock
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    
    # Execute teste
    director = MotionGraphicsDirector0(api_key="test-key")
    # ...
```

---

## ✅ Testes Implementados

### test_context_builder.py

- ✅ `test_build_motion_graphics_context` - Constrói contexto completo
- ✅ `test_map_words_to_positions` - Mapeia palavras para posições
- ✅ `test_identify_empty_spaces` - Identifica espaços vazios
- ✅ `test_calculate_occupied_areas` - Calcula áreas ocupadas
- ✅ `test_calculate_safe_zones` - Calcula zonas seguras
- ✅ `test_empty_context` - Testa contexto vazio
- ✅ `test_context_without_emphasis` - Testa sem palavras de ênfase

---

## 📊 Cobertura de Código

```bash
# Instalar pytest-cov
pip install pytest-cov

# Gerar relatório de cobertura
pytest --cov=app --cov-report=html

# Abrir relatório
open htmlcov/index.html
```

**Meta de cobertura:** 80%+

---

## 🚨 Troubleshooting

### Erro: ModuleNotFoundError

```bash
# Certifique-se de estar no diretório raiz
cd /path/to/v-llm-directors

# Adicione o diretório ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou rode os testes com Python
python -m pytest
```

### Erro: Anthropic API Key

Para testes que fazem chamadas reais à API:

```bash
# Configure a chave
export ANTHROPIC_API_KEY=sk-ant-...

# Ou use um arquivo .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

Para testes que NÃO devem fazer chamadas reais, use mocking.

### Slow Tests

```bash
# Marcar testes lentos
@pytest.mark.slow
def test_slow_operation():
    ...

# Pular testes lentos
pytest -m "not slow"
```

---

## 🔮 Roadmap de Testes

### Próximos Testes a Implementar

- [ ] `test_motion_graphics_director_0.py`
  - Testar inicialização
  - Testar carregamento de prompts
  - Testar parsing de resposta LLM
  - Testar limite de 5 MGs
  
- [ ] `test_api_endpoints.py`
  - Testar `/health`
  - Testar `/directors`
  - Testar `/directors/level-0/motion-graphics/plan`
  - Testar validação de input
  - Testar tratamento de erros
  
- [ ] `test_llm_integration.py`
  - Testar chamada real à Anthropic API (opcional)
  - Testar retry logic
  - Testar timeout handling

---

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Mocking](https://docs.python.org/3/library/unittest.mock.html)

---

**Última atualização:** 05 Fevereiro 2026
