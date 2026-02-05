# 📚 V-LLM Directors - Examples

Esta pasta contém exemplos práticos de como usar a API do V-LLM Directors.

---

## 📁 Estrutura

```
examples/
├── prompts/                    # Exemplos de requests
│   ├── tutorial_3_passos.json
│   └── video_promocional.json
│
├── responses/                  # Exemplos de responses
│   ├── tutorial_3_passos_response.json
│   └── video_promocional_response.json
│
├── test_api.py                 # Script Python de teste
└── README.md                   # Este arquivo
```

---

## 🚀 Como Usar

### 1. Testar API com Python Script

```bash
# Certifique-se de que o serviço está rodando
docker-compose up -d v-llm-directors

# Execute o script de teste
python examples/test_api.py
```

**O que o script faz:**
- ✅ Testa health check
- ✅ Lista directors disponíveis
- ✅ Testa planejamento de motion graphics (tutorial)
- ✅ Testa planejamento de motion graphics (promocional)
- 💾 Salva responses geradas em `examples/responses/`

---

### 2. Usar Exemplos com cURL

#### Health Check
```bash
curl http://localhost:5025/health
```

#### List Directors
```bash
curl http://localhost:5025/directors
```

#### Plan Motion Graphics (Tutorial)
```bash
curl -X POST http://localhost:5025/directors/level-0/motion-graphics/plan \
  -H "Content-Type: application/json" \
  -d @examples/prompts/tutorial_3_passos.json
```

#### Plan Motion Graphics (Promocional)
```bash
curl -X POST http://localhost:5025/directors/level-0/motion-graphics/plan \
  -H "Content-Type: application/json" \
  -d @examples/prompts/video_promocional.json
```

---

### 3. Usar em Python (httpx)

```python
import httpx
import json

async def plan_motion_graphics():
    # Carregar exemplo
    with open('examples/prompts/tutorial_3_passos.json', 'r') as f:
        data = json.load(f)
    
    # Fazer request
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            'http://localhost:5025/directors/level-0/motion-graphics/plan',
            json={
                'user_prompt': data['user_prompt'],
                'context': data['context']
            }
        )
        
        result = response.json()
        
        if result['status'] == 'success':
            print(f"✅ Plano criado com {len(result['plan']['motion_graphics'])} MGs")
        else:
            print(f"❌ Erro: {result['error']}")
        
        return result

# Executar
import asyncio
result = asyncio.run(plan_motion_graphics())
```

---

## 📋 Exemplos Disponíveis

### 1. Tutorial com 3 Passos

**Arquivo:** `prompts/tutorial_3_passos.json`

**Cenário:**
- Vídeo tutorial explicando 3 passos
- Palavras-chave: "Passo 1", "Passo 2", "Passo 3"
- Ações: "Abra", "Clique", "Salve"

**User Prompt:**
> "Crie setas apontando para os números dos passos e grife as palavras importantes"

**Resultado Esperado:**
- Setas apontando para "1", "2", "3"
- Grifados em "aplicativo", "configurações", "preferências"
- Total: ~5 motion graphics

---

### 2. Vídeo Promocional

**Arquivo:** `prompts/video_promocional.json`

**Cenário:**
- Vídeo promocional de produto
- Benefícios: "Economize tempo", "Aumente produtividade"
- CTA: "Comece grátis hoje"

**User Prompt:**
> "Destaque os benefícios e chame atenção para o CTA"

**Resultado Esperado:**
- Checkmarks validando benefícios
- Underline em "revolucionário"
- Círculo pulsante em "grátis"
- Total: ~4 motion graphics

---

## 🎯 Criando Seus Próprios Exemplos

### Template de Prompt

```json
{
  "description": "Descrição do cenário",
  "user_prompt": "Instrução para a LLM",
  "context": {
    "transcription": "Texto completo...",
    "words": [
      {
        "word": "palavra",
        "start_time": 0.0,
        "end_time": 0.5,
        "confidence": 0.95,
        "emphasis": true
      }
    ],
    "text_layout": [
      {
        "id": "sentence_001",
        "text": "Texto da frase",
        "position": {"x": 100, "y": 200, "width": 880, "height": 100},
        "timing": {"start_time": 0.0, "end_time": 2.0},
        "words": ["Texto", "da", "frase"]
      }
    ],
    "canvas": {"width": 1080, "height": 1920},
    "duration": 10.0,
    "style": {
      "primary_color": "#FF6B35",
      "accent_color": "#F7931E",
      "theme": "energetic"
    }
  }
}
```

**Salve como:** `prompts/meu_exemplo.json`

**Teste com:**
```bash
curl -X POST http://localhost:5025/directors/level-0/motion-graphics/plan \
  -H "Content-Type: application/json" \
  -d @examples/prompts/meu_exemplo.json
```

---

## 🔍 Entendendo os Responses

### Estrutura da Resposta

```json
{
  "status": "success",
  "director": "MotionGraphicsDirector0",
  "plan": {
    "motion_graphics": [
      {
        "id": "mg_001",
        "type": "arrow_pointing",
        "target_word": "tutorial",
        "target_element_id": "sentence_001",
        "timing": {
          "start_time": 0.5,
          "duration": 0.8
        },
        "config": {
          "direction": "down_right",
          "color": "#FF6B35",
          "stroke_width": 8
        },
        "justification": "Razão da decisão"
      }
    ],
    "reasoning": {
      "strategy": "Estratégia geral",
      "total_elements": 3
    }
  },
  "llm_usage": {
    "model": "claude-3-5-sonnet-20241022",
    "total_tokens": 2843
  }
}
```

### Campos Importantes

| Campo | Descrição |
|-------|-----------|
| `status` | "success" ou "error" |
| `plan.motion_graphics[]` | Array de motion graphics planejados |
| `plan.motion_graphics[].type` | Tipo (arrow, oval, circle, etc.) |
| `plan.motion_graphics[].timing` | start_time e duration |
| `plan.motion_graphics[].config` | Configurações específicas |
| `plan.reasoning` | Justificativa estratégica |
| `llm_usage` | Tokens consumidos |

---

## 📊 Tipos de Motion Graphics

### Arrows
- `arrow_pointing`
- `curved_arrow`
- `straight_arrow`

### Highlights
- `oval_highlight`
- `rectangle_highlight`
- `underline`
- `bracket_highlight`

### Shapes
- `circle_attention`
- `checkmark`
- `loading_spinner`
- `progress_bar`

---

## 🐛 Troubleshooting

### Erro: Connection refused

```bash
# Verifique se o serviço está rodando
docker-compose ps v-llm-directors

# Inicie se necessário
docker-compose up -d v-llm-directors

# Veja os logs
docker-compose logs -f v-llm-directors
```

### Erro: Timeout

```bash
# Aumente o timeout no script Python
async with httpx.AsyncClient(timeout=180.0) as client:
    ...
```

### Erro: Invalid JSON

- Verifique o formato do arquivo de prompt
- Use um validator JSON online
- Compare com os exemplos fornecidos

---

## 📝 Notas

- **ANTHROPIC_API_KEY:** Certifique-se de ter configurado no `.env`
- **Timeout:** Requests podem levar 30-90 segundos (chamadas LLM)
- **Limites:** Máximo de 5 motion graphics por vídeo (configurável)
- **Rate Limiting:** 60 requests/minuto (padrão)

---

**Última atualização:** 05 Fevereiro 2026
