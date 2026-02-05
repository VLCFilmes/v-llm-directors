# 🏗️ Arquitetura V-LLM Directors

## 🎯 Visão Geral

V-LLM Directors é um sistema **hierárquico de LLMs** para tomada de decisões em produção de vídeo.

Ao invés de uma única LLM gigante tentando fazer tudo, temos **múltiplos Directors especializados**, cada um focado em decisões específicas e organizados em **níveis de abstração**.

---

## 🧩 Componentes Principais

### 1. Directors (Decisores)

**O que são:**
- LLMs especializadas em decisões específicas
- Organizadas em níveis de abstração (+2, +1, 0, -1, -2)
- Cada uma com seu system prompt otimizado

**Responsabilidades:**
- Receber contexto estruturado
- Tomar decisões estratégicas/táticas/operacionais
- Retornar planos estruturados (JSON)

**Exemplo:**
```python
MotionGraphicsDirector0:
  - Conhece: posições de texto, timestamps
  - Decide: onde/quando colocar motion graphics
  - Retorna: JSON com plano de MGs
```

### 2. Context Builder (Construtor de Contexto)

**O que faz:**
- Recebe contexto "bruto" do orquestrador
- Otimiza e estrutura para cada Director
- Remove informações desnecessárias
- Adiciona informações derivadas

**Exemplo:**
```python
Input (bruto):
  - 5000 palavras com timestamps
  - 200 elementos de layout
  
Output (otimizado):
  - Top 20 palavras importantes
  - Áreas ocupadas (resumo)
  - Espaços vazios calculados
  - Constraints aplicados
```

### 3. Orchestrator (Orquestrador)

**O que faz:**
- Coordena chamadas entre Directors
- Gerencia fluxo de informação
- Coleta resultados
- Trata erros

**Fluxo:**
```
Orquestrador → Director+1 (criativo)
            ↓
            Director0 (tático)
            ↓
            Director-1 (otimização)
```

---

## 📐 Arquitetura de Sistema

```
┌─────────────────────────────────────────────────┐
│                   V-API                         │
│           (Orquestrador Principal)              │
└─────────────────┬───────────────────────────────┘
                  │
                  │ HTTP Request
                  │
┌─────────────────▼───────────────────────────────┐
│              V-LLM DIRECTORS                    │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  FastAPI Main App                       │   │
│  │  - Endpoints por nível                  │   │
│  │  - Validação de requests                │   │
│  │  - Rate limiting                        │   │
│  └──────────────┬──────────────────────────┘   │
│                 │                               │
│  ┌──────────────▼──────────────────────────┐   │
│  │  Context Builder                        │   │
│  │  - Otimiza contexto                     │   │
│  │  - Estrutura dados                      │   │
│  └──────────────┬──────────────────────────┘   │
│                 │                               │
│  ┌──────────────▼──────────────────────────┐   │
│  │  Directors (Level 0, +1, -1...)         │   │
│  │  - System Prompts                       │   │
│  │  - Anthropic Claude API                 │   │
│  │  - JSON Output                          │   │
│  └──────────────┬──────────────────────────┘   │
│                 │                               │
│                 │ JSON Plan                     │
│                 ▼                               │
└─────────────────────────────────────────────────┘
                  │
                  │ Return Plan
                  │
┌─────────────────▼───────────────────────────────┐
│              V-SERVICES                         │
│        (Executores: Manim, PNGs...)             │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Dados

### Exemplo: Motion Graphics

```
1. V-API (Step 11.6)
   └─> POST /directors/level-0/motion-graphics/plan
       Payload: {
         user_prompt: "Crie setas e grifados",
         context: {
           transcription: "...",
           text_layout: [{...}, {...}],
           canvas: {width, height},
           duration: 15.0
         }
       }

2. V-LLM Directors
   a) FastAPI recebe request
   b) Context Builder otimiza contexto
   c) MotionGraphicsDirector0 chama Claude
   d) Claude retorna plano JSON
   e) Director valida e retorna

   Response: {
     status: "success",
     plan: {
       motion_graphics: [
         {
           id: "mg_001",
           type: "arrow_pointing",
           target_word: "IMPORTANTE",
           timing: {start: 2.3, duration: 0.8},
           config: {...}
         }
       ]
     }
   }

3. V-API (Step 11.7)
   Recebe plano e executa cada MG:
   
   Para cada motion_graphic em plano:
     └─> POST v-services/motion-graphics/render
         Payload: {
           template: "arrow_pointing",
           config: {...}
         }
   
   Resultado: Lista de .mov files renderizados

4. V-Editor-Python (Step 12+)
   Recebe .mov files e posições
   Compõe vídeo final
```

---

## 🗂️ Estrutura de Diretórios

```
v-llm-directors/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app
│   │
│   ├── directors/                   # Directors por nível
│   │   ├── level_plus_2/
│   │   ├── level_plus_1/
│   │   ├── level_0/                 # ⭐ ATUAL
│   │   │   ├── __init__.py
│   │   │   └── motion_graphics_director_0.py
│   │   ├── level_minus_1/
│   │   └── level_minus_2/
│   │
│   ├── orchestrator/                # Lógica de orquestração
│   │   ├── __init__.py
│   │   └── context_builder.py
│   │
│   ├── prompts/                     # System prompts
│   │   ├── level_0/
│   │   │   └── motion_graphics_director_0/
│   │   │       ├── system_prompt.txt
│   │   │       └── examples.json
│   │   └── ...
│   │
│   └── utils/                       # Utilidades
│
├── docs/                            # Documentação
│   ├── ARCHITECTURE.md
│   ├── LEVELS_HIERARCHY.md
│   ├── ADDING_NEW_DIRECTOR.md
│   └── API.md
│
├── examples/                        # Exemplos
│   ├── prompts/
│   └── responses/
│
├── tests/                           # Testes
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔐 Segurança

### API Key Management

- **Anthropic API Key** via variável de ambiente
- NUNCA commitar chaves no código
- Usar `.env` local, `.env.example` no repo

### Rate Limiting

```python
# Configurável via .env
MAX_REQUESTS_PER_MINUTE=60
MAX_TOKENS_PER_REQUEST=4000
```

### Timeout Protection

```python
# Timeout para chamadas LLM
LLM_TIMEOUT_SECONDS=60

# Timeout para request completo
REQUEST_TIMEOUT_SECONDS=120
```

---

## 📊 Logging e Monitoramento

### Logs Estruturados

```python
logger.info("🎬 [DIRECTOR0] Planejando motion graphics...")
logger.info(f"   Prompt: {user_prompt[:100]}...")
logger.info(f"✅ [DIRECTOR0] Plano criado: 3 MGs")
```

### Métricas

- Tempo de resposta por director
- Tokens consumidos
- Taxa de sucesso/falha
- Número de decisões por tipo

---

## 🔮 Escalabilidade Futura

### Horizontal (Mais Directors no Mesmo Nível)

```
Level 0 atual:
- MotionGraphicsDirector0

Level 0 futuro:
- MotionGraphicsDirector0
- BrollDirector0
- ZoomDirector0
- EffectsDirector0
- TransitionDirector0
```

### Vertical (Mais Níveis)

```
Futuro:
+3 → Business Intelligence
+2 → Meta/Executive
+1 → Strategic/Creative
 0 → Tactical/Core ⭐
-1 → Operational
-2 → Micro/Validation
-3 → Hardware-specific
```

### Multi-Model

```python
# Usar diferentes modelos por director
MotionGraphicsDirector0:
  model: claude-3-5-sonnet  # Criativo

CodeValidator-2:
  model: claude-3-haiku     # Rápido e preciso
```

---

## 🤝 Integração com Pipeline

### v-api/orchestrator.py

```python
# Step 11.6: Chamar LLM Director
if motion_graphics_prompt:
    mg_plan = requests.post(
        'http://v-llm-directors:5025/directors/level-0/motion-graphics/plan',
        json={
            'user_prompt': motion_graphics_prompt,
            'context': {
                'transcription': transcription,
                'words': words_with_timestamps,
                'text_layout': text_layout['sentences'],
                'canvas': {'width': 1080, 'height': 1920},
                'duration': duration
            }
        }
    )
    
    # Step 11.7: Executar plano
    for mg in mg_plan['plan']['motion_graphics']:
        render_result = v_services.render_motion_graphic(mg)
```

---

## 🧪 Testing

### Unit Tests

```python
# Testar Directors isoladamente
test_motion_graphics_director_0.py:
  - test_basic_plan()
  - test_empty_context()
  - test_max_mgs_limit()
```

### Integration Tests

```python
# Testar fluxo completo
test_integration.py:
  - test_full_flow_motion_graphics()
  - test_error_handling()
```

---

**Última atualização:** 05 Fevereiro 2026
