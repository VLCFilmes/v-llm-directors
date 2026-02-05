# 🎬 V-LLM Directors

Sistema hierárquico de LLMs para decisões estratégicas, táticas e operacionais em produção de vídeo.

## 🏗️ Arquitetura

Directors são organizados em **níveis de abstração**:

```
LEVEL +2: Meta/Executive      → Decisões de negócio
LEVEL +1: Strategic/Creative  → Visão criativa global
LEVEL  0: Tactical/Core       → Decisões táticas (⭐ COMEÇAMOS AQUI)
LEVEL -1: Operational         → Otimizações operacionais
LEVEL -2: Micro/Validation    → Validações técnicas
```

## 📊 Hierarquia Visual

```
┌─────────────────────────────────────┐
│  DIRECTOR+2 (Meta/Executive)        │
│  Ex: MonetizationDirector+2         │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  DIRECTOR+1 (Strategic)             │
│  Ex: CreativeDirector+1             │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  DIRECTOR0 (Tactical) ⭐            │
│  Ex: MotionGraphicsDirector0        │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  DIRECTOR-1 (Operational)           │
│  Ex: TimingOptimizer-1              │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  DIRECTOR-2 (Micro)                 │
│  Ex: CodeValidator-2                │
└─────────────────────────────────────┘
```

## 🎯 Directors Implementados

### Level 0 (Tactical/Core)

- **MotionGraphicsDirector0** ✅ - Planeja motion graphics baseado em contexto completo
  - Conhece: transcrição, timestamps, layout de texto, posições
  - Decide: onde/quando/que tipo de MG usar
  - Output: Plano estruturado de motion graphics

## 🚀 Como Usar

### Instalação

```bash
# Clonar repo
git clone https://github.com/VLCFilmes/v-llm-directors.git
cd v-llm-directors

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com sua API key da Anthropic

# Rodar
python -m uvicorn app.main:app --reload --port 5025
```

### API Endpoints

#### POST /directors/level-0/motion-graphics/plan

Planeja motion graphics baseado em contexto completo.

**Request:**
```json
{
  "user_prompt": "Crie setas e grifados destacando pontos importantes",
  "context": {
    "transcription": "Olá! Hoje vamos falar sobre...",
    "words": [
      {
        "word": "IMPORTANTE",
        "start": 2.5,
        "end": 3.1,
        "emphasis": true
      }
    ],
    "text_layout": [
      {
        "group_index": 0,
        "words": [
          {
            "text": "IMPORTANTE",
            "canvas_position": {"x": 540, "y": 1440},
            "dimensions": {"width": 200, "height": 60}
          }
        ]
      }
    ],
    "canvas": {"width": 1080, "height": 1920},
    "duration": 15.0,
    "style": "modern"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "level": 0,
  "director": "MotionGraphicsDirector0",
  "plan": {
    "motion_graphics": [
      {
        "id": "mg_001",
        "type": "arrow_pointing",
        "target_word": "IMPORTANTE",
        "timing": {
          "start": 2.3,
          "duration": 0.8
        },
        "position_strategy": "above_text",
        "config": {
          "direction": "down",
          "color": "#FF6B35",
          "size": 30
        },
        "reasoning": "Destacar palavra-chave com antecipação visual"
      }
    ],
    "total": 3,
    "reasoning": "Escolhi 3 MGs para não poluir visualmente..."
  }
}
```

## 📚 Documentação Completa

Para informações detalhadas, consulte a documentação completa na pasta `docs/`:

| Documento | Descrição |
|-----------|-----------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura completa do sistema |
| [API.md](docs/API.md) | Referência completa da API |
| [LEVELS_HIERARCHY.md](docs/LEVELS_HIERARCHY.md) | Hierarquia de níveis dos Directors |
| [ADDING_NEW_DIRECTOR.md](docs/ADDING_NEW_DIRECTOR.md) | Guia para adicionar novos Directors |
| [examples/README.md](examples/README.md) | Exemplos de uso e testes |
| [tests/README.md](tests/README.md) | Guia de testes |

---

## 🔧 Desenvolvimento

### Adicionar Novo Director

1. Escolher nível apropriado (+2, +1, 0, -1, -2)
2. Criar arquivo em `app/directors/level_{nível}/{nome}_director_{nível}.py`
3. Criar prompts em `app/prompts/level_{nível}/{nome}_director_{nível}/`
4. Registrar no orchestrator
5. Adicionar testes
6. Documentar em `docs/`

Ver: [docs/ADDING_NEW_DIRECTOR.md](docs/ADDING_NEW_DIRECTOR.md)

## 📚 Documentação

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitetura geral
- [LEVELS_HIERARCHY.md](docs/LEVELS_HIERARCHY.md) - Hierarquia de níveis
- [ADDING_NEW_DIRECTOR.md](docs/ADDING_NEW_DIRECTOR.md) - Como adicionar directors
- [API.md](docs/API.md) - Documentação da API

## 🏭 Integração com Pipeline

```python
# v-api/orchestrator integrando com LLM Directors

# Step 11: Positioning de texto
text_layout = positioning_service.calculate_positions(...)

# Step 11.6: LLM Director planeja MGs
mg_plan = requests.post(
    'http://v-llm-directors:5025/directors/level-0/motion-graphics/plan',
    json={
        'user_prompt': mg_prompt,
        'context': {
            'transcription': transcription,
            'text_layout': text_layout['sentences'],
            'canvas': canvas,
            'duration': duration
        }
    }
)

# Step 11.7: Executar plano (v-services)
for mg in mg_plan['motion_graphics']:
    render_result = v_services.render_motion_graphic(mg)
```

## 🌟 Roadmap

### Fase 1 (Atual)
- ✅ Arquitetura de níveis
- ✅ MotionGraphicsDirector0
- ⏳ Integração com v-api
- ⏳ Testes end-to-end

### Fase 2 (Futuro)
- ⏳ BrollDirector0 (inserção de imagens)
- ⏳ ZoomDirector0 (planejamento de zooms)
- ⏳ EffectsDirector0 (efeitos visuais)

### Fase 3 (Futuro)
- ⏳ CreativeDirector+1 (visão criativa global)
- ⏳ ContentDirector+1 (estrutura narrativa)

### Fase 4 (Futuro)
- ⏳ TimingOptimizer-1 (otimização de timings)
- ⏳ LayoutOptimizer-1 (otimização de layouts)

## 🔐 Segurança

- API Key da Anthropic via variável de ambiente
- Rate limiting configurável
- Timeout protection
- Logs completos de decisões

## 📊 Monitoramento

- Tempo de resposta por director
- Tokens consumidos
- Taxa de sucesso/falha
- Decisões tomadas (logs estruturados)

## 🤝 Contribuindo

1. Fork o repo
2. Crie branch (`git checkout -b feature/novo-director`)
3. Commit mudanças (`git commit -m 'Add NovoDirector+1'`)
4. Push para branch (`git push origin feature/novo-director`)
5. Abra Pull Request

## 📝 License

MIT License - Ver [LICENSE](LICENSE)

---

**Última atualização:** 05 Fevereiro 2026  
**Versão:** 1.0.0  
**Status:** 🚧 Em Desenvolvimento
