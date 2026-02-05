# 🌐 API Documentation - V-LLM Directors

## Base URL

```
http://localhost:5025
```

**Produção:**
```
http://v-llm-directors:5025
```

---

## 📡 Endpoints

### 1. Root - Informações do Serviço

```http
GET /
```

**Response:**
```json
{
  "service": "v-llm-directors",
  "version": "1.0.0",
  "description": "Hierarchical LLM Directors for video production decisions",
  "status": "running"
}
```

---

### 2. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "v-llm-directors",
  "timestamp": "2026-02-05T10:30:45.123Z"
}
```

---

### 3. List Directors

```http
GET /directors
```

Lista todos os Directors disponíveis organizados por nível.

**Response:**
```json
{
  "levels": {
    "+2": [],
    "+1": [],
    "0": [
      {
        "id": "motion_graphics_director_0",
        "name": "Motion Graphics Director Level 0",
        "description": "Planeja motion graphics baseado em contexto de vídeo",
        "endpoint": "/directors/level-0/motion-graphics/plan",
        "level": 0,
        "type": "motion_graphics"
      }
    ],
    "-1": [],
    "-2": []
  },
  "total_directors": 1
}
```

---

## 🎬 Level 0 Directors

### Motion Graphics Director 0

Planeja motion graphics baseado em contexto completo do vídeo.

---

#### Plan Motion Graphics (Completo)

```http
POST /directors/level-0/motion-graphics/plan
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**

```json
{
  "user_prompt": "Crie setas apontando para as palavras importantes e grife os pontos-chave",
  "context": {
    "transcription": "Bem-vindo ao tutorial. Passo um: abra o aplicativo.",
    "words": [
      {
        "word": "Bem-vindo",
        "start_time": 0.0,
        "end_time": 0.5,
        "confidence": 0.98
      },
      {
        "word": "tutorial",
        "start_time": 0.6,
        "end_time": 1.0,
        "confidence": 0.95,
        "emphasis": true
      }
    ],
    "text_layout": [
      {
        "id": "sentence_001",
        "text": "Bem-vindo ao tutorial",
        "position": {
          "x": 100,
          "y": 200,
          "width": 880,
          "height": 100
        },
        "timing": {
          "start_time": 0.0,
          "end_time": 2.0
        },
        "words": ["Bem-vindo", "ao", "tutorial"]
      }
    ],
    "canvas": {
      "width": 1080,
      "height": 1920
    },
    "duration": 15.0,
    "style": {
      "primary_color": "#FF6B35",
      "accent_color": "#F7931E",
      "theme": "energetic"
    }
  }
}
```

**Validação Pydantic:**

```python
class VideoContext(BaseModel):
    transcription: str
    words: List[Dict]
    text_layout: List[Dict]
    canvas: Dict[str, int]
    duration: float
    style: Optional[Dict] = None

class MotionGraphicsPlanRequest(BaseModel):
    user_prompt: str
    context: VideoContext
    max_tokens: Optional[int] = 4000
```

**Response (Success):**

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
          "stroke_width": 8,
          "animation_style": "draw_in"
        },
        "justification": "Destacar palavra-chave 'tutorial' no início do vídeo"
      },
      {
        "id": "mg_002",
        "type": "oval_highlight",
        "target_word": "aplicativo",
        "target_element_id": "sentence_002",
        "timing": {
          "start_time": 3.2,
          "duration": 1.0
        },
        "config": {
          "color": "#F7931E",
          "stroke_width": 6,
          "padding": 15,
          "style": "hand_drawn",
          "rotation": -5
        },
        "justification": "Enfatizar ação principal do passo 1"
      }
    ],
    "reasoning": {
      "strategy": "Usar setas para chamar atenção inicial e grifados para ações-chave",
      "total_elements": 2,
      "empty_spaces_used": ["top_right", "mid_center"],
      "avoided_overlaps": true
    }
  },
  "llm_usage": {
    "model": "claude-3-5-sonnet-20241022",
    "input_tokens": 2456,
    "output_tokens": 387,
    "total_tokens": 2843
  }
}
```

**Response (Error):**

```json
{
  "status": "error",
  "director": "MotionGraphicsDirector0",
  "error": "Failed to parse LLM response as JSON",
  "details": "Invalid JSON format in response",
  "raw_response": "..."
}
```

**Status Codes:**

- `200 OK` - Plano criado com sucesso
- `400 Bad Request` - Dados inválidos (Pydantic validation error)
- `500 Internal Server Error` - Erro ao chamar LLM ou processar

---

#### Plan Motion Graphics (Simplificado)

```http
POST /directors/level-0/motion-graphics/plan-simple
```

Versão simplificada para testes rápidos, sem validação estrita de Pydantic.

**Request Body:**

```json
{
  "user_prompt": "Adicione setas e grifados",
  "context": {
    "transcription": "Texto do vídeo...",
    "text_layout": [...]
  }
}
```

**Response:**

Mesma estrutura da versão completa.

---

## 🔍 Request Examples

### cURL

```bash
# Health Check
curl http://localhost:5025/health

# List Directors
curl http://localhost:5025/directors

# Plan Motion Graphics
curl -X POST http://localhost:5025/directors/level-0/motion-graphics/plan \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Crie setas apontando",
    "context": {
      "transcription": "Bem-vindo ao tutorial",
      "words": [],
      "text_layout": [],
      "canvas": {"width": 1080, "height": 1920},
      "duration": 10.0
    }
  }'
```

### Python (httpx)

```python
import httpx

async def plan_motion_graphics(prompt: str, context: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:5025/directors/level-0/motion-graphics/plan',
            json={
                'user_prompt': prompt,
                'context': context
            },
            timeout=120.0
        )
        return response.json()

# Uso
result = await plan_motion_graphics(
    prompt="Adicione setas",
    context={...}
)
```

### JavaScript (fetch)

```javascript
async function planMotionGraphics(prompt, context) {
  const response = await fetch(
    'http://localhost:5025/directors/level-0/motion-graphics/plan',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_prompt: prompt,
        context: context
      })
    }
  );
  
  return await response.json();
}

// Uso
const result = await planMotionGraphics(
  "Adicione setas",
  {...}
);
```

---

## 📋 Context Structure

### Transcription

```json
{
  "transcription": "String completa da transcrição do vídeo"
}
```

### Words

```json
{
  "words": [
    {
      "word": "tutorial",
      "start_time": 0.5,
      "end_time": 1.0,
      "confidence": 0.95,
      "emphasis": true
    }
  ]
}
```

### Text Layout

```json
{
  "text_layout": [
    {
      "id": "sentence_001",
      "text": "Bem-vindo ao tutorial",
      "position": {
        "x": 100,
        "y": 200,
        "width": 880,
        "height": 100
      },
      "timing": {
        "start_time": 0.0,
        "end_time": 2.0
      },
      "words": ["Bem-vindo", "ao", "tutorial"]
    }
  ]
}
```

### Canvas

```json
{
  "canvas": {
    "width": 1080,
    "height": 1920
  }
}
```

### Duration

```json
{
  "duration": 15.0
}
```

### Style (Optional)

```json
{
  "style": {
    "primary_color": "#FF6B35",
    "accent_color": "#F7931E",
    "theme": "energetic"
  }
}
```

---

## 📤 Output Structure

### Motion Graphics Plan

```json
{
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
          "stroke_width": 8,
          "animation_style": "draw_in"
        },
        "justification": "Razão para essa decisão"
      }
    ],
    "reasoning": {
      "strategy": "Estratégia geral adotada",
      "total_elements": 2,
      "empty_spaces_used": ["top_right"],
      "avoided_overlaps": true
    }
  }
}
```

### Supported Motion Graphics Types

#### Arrows
- `arrow_pointing`
- `curved_arrow`
- `straight_arrow`

#### Highlights
- `oval_highlight`
- `rectangle_highlight`
- `underline`
- `bracket_highlight`

#### Shapes
- `circle_attention`
- `checkmark`
- `loading_spinner`
- `progress_bar`

---

## ⚙️ Configuration

### Environment Variables

```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Server
HOST=0.0.0.0
PORT=5025
DEBUG=false

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
MAX_TOKENS_PER_REQUEST=4000

# Timeouts
LLM_TIMEOUT_SECONDS=60
REQUEST_TIMEOUT_SECONDS=120

# Logging
LOG_LEVEL=INFO
```

---

## 🚨 Error Handling

### Error Response Format

```json
{
  "status": "error",
  "director": "MotionGraphicsDirector0",
  "error": "Error description",
  "details": "Additional details",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_INPUT` | Pydantic validation failed | Check request format |
| `LLM_TIMEOUT` | LLM took too long | Retry or simplify context |
| `JSON_PARSE_ERROR` | LLM didn't return valid JSON | Retry |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry |
| `NO_ANTHROPIC_KEY` | API key not configured | Set `ANTHROPIC_API_KEY` |

---

## 📊 Rate Limiting

```
Default: 60 requests/minute
Max tokens: 4000 tokens/request
```

**Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1643990400
```

---

## 🔐 Authentication

**Atualmente:** Sem autenticação (serviço interno).

**Futuro:** API Key via header:
```
Authorization: Bearer YOUR_API_KEY
```

---

## 📈 Monitoring

### Health Check

```bash
# Simples
curl http://localhost:5025/health

# Com timeout
curl --max-time 5 http://localhost:5025/health
```

### Logs

```bash
# Docker Compose
docker-compose logs -f v-llm-directors

# Docker
docker logs -f v-llm-directors
```

---

**Última atualização:** 05 Fevereiro 2026
