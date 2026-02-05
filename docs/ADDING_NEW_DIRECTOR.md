# 📖 Como Adicionar um Novo Director

Este guia explica como adicionar um novo Director ao sistema.

---

## 🎯 Passo 1: Escolher o Nível

Primeiro, determine em que nível seu Director se encaixa:

| Nível | Tipo de Decisão | Quando Usar |
|-------|-----------------|-------------|
| **+2** | Meta/Executive | Decisões de negócio, multi-plataforma |
| **+1** | Strategic/Creative | Visão criativa, narrativa global |
| **0** | Tactical/Core | Elementos visuais específicos |
| **-1** | Operational | Otimizações, ajustes finos |
| **-2** | Micro/Validation | Validações técnicas granulares |

**Exemplo:**
- Planejar B-roll → **Level 0** (tático, elemento específico)
- Definir estilo global → **Level +1** (estratégico, visão global)
- Otimizar timings → **Level -1** (operacional, ajustes)

---

## 📁 Passo 2: Criar Estrutura de Arquivos

### 2.1 Criar arquivo do Director

```bash
# Formato: {nome}_director_{nivel}.py
# Localização: app/directors/level_{nivel}/

# Exemplo para BrollDirector0:
touch app/directors/level_0/broll_director_0.py
```

### 2.2 Criar pasta de prompts

```bash
# Formato: app/prompts/level_{nivel}/{nome}_director_{nivel}/
mkdir -p app/prompts/level_0/broll_director_0

# Criar arquivos de prompts
touch app/prompts/level_0/broll_director_0/system_prompt.txt
touch app/prompts/level_0/broll_director_0/examples.json
```

---

## 💻 Passo 3: Implementar o Director

### 3.1 Template Base

```python
# app/directors/level_0/novo_director_0.py

"""
🎬 Novo Director 0

Descrição do que este director faz.

NÍVEL: 0 (Tactical/Core)

CONHECE:
- Lista de informações que tem acesso

DECIDE:
- Lista de decisões que toma
"""

import json
import logging
from pathlib import Path
from typing import Dict
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class NovoDirector0:
    """
    Descrição curta do director
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = self._load_system_prompt()
        self.examples = self._load_examples()
        logger.info("🎬 NovoDirector0 inicializado")
    
    def _load_system_prompt(self) -> str:
        """Carrega system prompt do arquivo"""
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "level_0" / "novo_director_0" / "system_prompt.txt"
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_examples(self) -> Dict:
        """Carrega exemplos do arquivo"""
        examples_path = Path(__file__).parent.parent.parent / "prompts" / "level_0" / "novo_director_0" / "examples.json"
        
        with open(examples_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def plan(
        self,
        user_prompt: str,
        context: Dict,
        max_tokens: int = 4000
    ) -> Dict:
        """
        Planeja ações baseado em contexto
        
        Args:
            user_prompt: Prompt do usuário
            context: Contexto completo
            max_tokens: Máximo de tokens
        
        Returns:
            {
                "status": "success",
                "level": 0,
                "director": "NovoDirector0",
                "plan": {...},
                "tokens_used": 1234
            }
        """
        logger.info(f"🎬 [DIRECTOR0] Planejando...")
        
        try:
            # Montar mensagem
            user_message = self._build_user_message(user_prompt, context)
            
            # Chamar Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.7,
                system=self.system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            # Parse resposta
            response_text = response.content[0].text
            plan = json.loads(response_text)
            
            logger.info(f"✅ [DIRECTOR0] Plano criado")
            
            return {
                "status": "success",
                "level": 0,
                "director": "NovoDirector0",
                "plan": plan,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
        
        except Exception as e:
            logger.error(f"❌ [DIRECTOR0] Erro: {e}")
            return {
                "status": "error",
                "level": 0,
                "director": "NovoDirector0",
                "error": str(e)
            }
    
    def _build_user_message(self, user_prompt: str, context: Dict) -> str:
        """Monta mensagem estruturada para LLM"""
        return f"""
## PROMPT DO USUÁRIO
{user_prompt}

## CONTEXTO
{json.dumps(context, indent=2, ensure_ascii=False)}

Analise e crie um plano estruturado.
"""


# Singleton
_director = None

def get_novo_director_0(api_key: str, model: str = None):
    global _director
    if _director is None:
        _director = NovoDirector0(api_key, model or "claude-3-5-sonnet-20241022")
    return _director
```

---

## 📝 Passo 4: Criar System Prompt

```txt
# app/prompts/level_0/novo_director_0/system_prompt.txt

Você é um **{Nome} Director** especializado em {área}.

## SUA MISSÃO

{Descrição detalhada da missão}

## CONTEXTO DISPONÍVEL

{Lista de informações que a LLM tem acesso}

## DECISÕES QUE VOCÊ TOMA

{Lista de decisões que deve tomar}

## REGRAS

{Regras específicas}

## FORMATO DE OUTPUT

{Estrutura JSON esperada}
```

---

## 🔌 Passo 5: Registrar no Main.py

### 5.1 Importar Director

```python
# app/main.py

from directors.level_0.novo_director_0 import get_novo_director_0
```

### 5.2 Criar Endpoint

```python
@app.post("/directors/level-0/novo/plan")
async def plan_novo(request: Dict):
    """
    Planeja usando NovoDirector0
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="API Key não configurada")
    
    try:
        user_prompt = request.get('user_prompt')
        raw_context = request.get('context', {})
        
        # Construir contexto
        context_builder = get_context_builder()
        optimized_context = context_builder.build_novo_context(raw_context)
        
        # Chamar Director
        director = get_novo_director_0(
            api_key=ANTHROPIC_API_KEY,
            model=ANTHROPIC_MODEL
        )
        
        result = await director.plan(
            user_prompt=user_prompt,
            context=optimized_context
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 5.3 Atualizar endpoint `/directors`

```python
@app.get("/directors")
async def list_directors():
    return {
        "level_0": [
            {
                "name": "MotionGraphicsDirector0",
                "endpoint": "/directors/level-0/motion-graphics/plan"
            },
            {
                "name": "NovoDirector0",  # ← ADICIONAR AQUI
                "endpoint": "/directors/level-0/novo/plan"
            }
        ]
    }
```

---

## 🧪 Passo 6: Criar Testes

```python
# tests/test_novo_director_0.py

import pytest
from app.directors.level_0.novo_director_0 import NovoDirector0

@pytest.mark.asyncio
async def test_novo_director_basic():
    director = NovoDirector0(api_key="test")
    
    result = await director.plan(
        user_prompt="Teste",
        context={"test": "data"}
    )
    
    assert result['status'] == 'success'
    assert result['level'] == 0
```

---

## 📚 Passo 7: Documentar

### 7.1 Atualizar README.md

Adicionar na seção "Directors Implementados":

```markdown
### Level 0 (Tactical/Core)

- **NovoDirector0** ✅ - {Descrição curta}
  - Conhece: {lista}
  - Decide: {lista}
  - Output: {formato}
```

### 7.2 Criar documentação específica (se necessário)

```bash
touch docs/NOVO_DIRECTOR_0.md
```

---

## ✅ Checklist de Implementação

- [ ] Escolher nível apropriado
- [ ] Criar arquivo do director
- [ ] Criar system prompt
- [ ] Criar examples.json
- [ ] Implementar classe Director
- [ ] Adicionar método no ContextBuilder (se necessário)
- [ ] Registrar no main.py
- [ ] Criar testes
- [ ] Documentar no README.md
- [ ] Testar endpoint
- [ ] Commit e push

---

## 🚀 Exemplo Completo: BrollDirector0

```bash
# 1. Criar arquivos
mkdir -p app/directors/level_0
mkdir -p app/prompts/level_0/broll_director_0
touch app/directors/level_0/broll_director_0.py
touch app/prompts/level_0/broll_director_0/system_prompt.txt
touch app/prompts/level_0/broll_director_0/examples.json

# 2. Implementar (seguir template acima)

# 3. Registrar em main.py
# (adicionar import e endpoint)

# 4. Testar
curl -X POST http://localhost:5025/directors/level-0/broll/plan \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "...", "context": {...}}'

# 5. Commit
git add .
git commit -m "feat: Adicionar BrollDirector0"
git push
```

---

**Última atualização:** 05 Fevereiro 2026
