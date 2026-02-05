# 📊 Hierarquia de Níveis de Directors

## 🎯 Conceito

Directors são organizados em **níveis de abstração** representados por números:

- **Positivo (+)**: Mais abstrato, decisões estratégicas e de negócio
- **Zero (0)**: Ponto pivô, decisões táticas sobre elementos específicos
- **Negativo (-)**: Mais concreto, decisões operacionais e validações

Esta hierarquia permite **crescimento orgânico** em ambas as direções:
- Adicionar Directors mais abstratos (creative, business) → +1, +2, +3...
- Adicionar Directors mais concretos (optimization, validation) → -1, -2, -3...

---

## 📋 Níveis Definidos

### LEVEL +2: Meta/Executive 🏢

**Responsabilidade:** Decisões de negócio e distribuição multi-plataforma

**Conhece:**
- Métricas de negócio (ROI, engagement)
- Características de cada plataforma (YouTube, TikTok, Instagram)
- Dados de audiência
- Objetivos de monetização

**Decide:**
- Estratégia de distribuição (onde publicar)
- Otimizações para monetização (ads, patrocínios)
- Adaptações por plataforma (crops, formatos)
- Estratégia de longo prazo

**Exemplos de Directors:**
- `MultiPlatformDirector+2`: Decide adaptações para cada plataforma
- `MonetizationDirector+2`: Otimiza para ads e receita
- `AudienceDirector+2`: Adapta para audiência-alvo

**Status:** 🔮 Futuro

---

### LEVEL +1: Strategic/Creative 🎨

**Responsabilidade:** Visão criativa global e estrutura narrativa

**Conhece:**
- Contexto completo do conteúdo
- Objetivos criativos
- Tom e estilo desejados
- Storytelling principles

**Decide:**
- Estilo visual global (moderno, minimalista, bold)
- Estrutura narrativa (hook, build-up, payoff)
- Tom do vídeo (sério, descontraído, educacional)
- Paleta de cores global
- Ritmo e pacing

**Exemplos de Directors:**
- `CreativeDirector+1`: Define visão criativa global
- `ContentDirector+1`: Estrutura narrativa e storytelling
- `StyleDirector+1`: Define estilo visual consistente

**Status:** 🔮 Futuro

---

### LEVEL 0: Tactical/Core ⭐ (PONTO CENTRAL)

**Responsabilidade:** Decisões táticas sobre elementos visuais específicos

**Conhece:**
- Layout completo (posições de todos os elementos)
- Timestamps precisos
- Posições de texto (X, Y, width, height)
- Bounding boxes e espaços vazios
- Durações e timings

**Decide:**
- **ONDE** colocar cada elemento visual
- **QUANDO** aparecer/desaparecer
- **QUE TIPO** de elemento usar
- **COMO** posicionar sem sobrepor
- **CORES e ESTILOS** de cada elemento

**Exemplos de Directors:**
- `MotionGraphicsDirector0` ✅: Planeja motion graphics
- `BrollDirector0` 🔮: Planeja inserção de B-roll/imagens
- `ZoomDirector0` 🔮: Planeja zooms estratégicos
- `EffectsDirector0` 🔮: Planeja efeitos visuais
- `TransitionDirector0` 🔮: Planeja transições entre cenas

**Status:** ⭐ **IMPLEMENTADO** (MotionGraphicsDirector0)

---

### LEVEL -1: Operational/Optimization 🔧

**Responsabilidade:** Otimizações operacionais e ajustes finos

**Conhece:**
- Planos dos Directors de nível 0
- Métricas de performance
- Constraints técnicos
- Limitações de hardware/render

**Decide:**
- Ajustes de timing para melhor performance
- Otimizações de layout (evitar re-renders)
- Simplificações para reduzir tempo de render
- Priorização quando há conflitos

**Exemplos de Directors:**
- `TimingOptimizer-1`: Otimiza timings para fluidez
- `LayoutOptimizer-1`: Otimiza layouts para performance
- `CacheOptimizer-1`: Maximiza uso de cache
- `RenderOptimizer-1`: Reduz tempo de render

**Status:** 🔮 Futuro

---

### LEVEL -2: Micro/Validation 🔬

**Responsabilidade:** Validações técnicas granulares e micro-otimizações

**Conhece:**
- Código gerado (Manim, Python)
- Constraints de hardware específicos
- Regras de segurança
- Performance benchmarks

**Decide:**
- Validação de código (segurança, sintaxe)
- Micro-otimizações de performance
- Substituições técnicas (ex: trocar biblioteca)
- Fallbacks quando algo falha

**Exemplos de Directors:**
- `CodeValidator-2`: Valida código Manim gerado
- `SecurityValidator-2`: Verifica segurança do código
- `PerformanceValidator-2`: Valida performance esperada
- `FallbackSelector-2`: Escolhe fallback quando falha

**Status:** 🔮 Futuro

---

## 🔄 Comunicação Entre Níveis

### Hierarquia de Delegação

```
+2 (Meta)
 └─> Delega para +1
     +1 (Strategic)
      └─> Delega para 0
          0 (Tactical) ⭐
           └─> Delega para -1
               -1 (Operational)
                └─> Delega para -2
                    -2 (Micro)
```

### Fluxo de Informação

```
↓ DELEGAÇÃO (top-down)
+2 → +1 → 0 → -1 → -2

↑ FEEDBACK (bottom-up)
-2 → -1 → 0 → +1 → +2
```

### Exemplo de Fluxo Completo (Futuro)

```
1. CreativeDirector+1 decide:
   "Vídeo deve ter estilo moderno e minimalista"

2. MotionGraphicsDirector0 recebe:
   Contexto + Diretriz de estilo = "moderno e minimalista"
   Decide: "3 MGs simples, cores suaves, sem exageros"

3. TimingOptimizer-1 ajusta:
   Recebe plano de 3 MGs
   Otimiza: "MG #2 atrasa 0.1s para melhor sincronia"

4. CodeValidator-2 valida:
   Verifica código Manim gerado
   Aprova ou sugere correções
```

---

## 🎯 Quando Usar Cada Nível

### Use LEVEL +2 quando:
- Decisões afetam múltiplas plataformas
- Considerações de monetização
- Estratégia de longo prazo

### Use LEVEL +1 quando:
- Decisões criativas globais
- Definir tom e estilo
- Estruturar narrativa

### Use LEVEL 0 quando: ⭐
- Decisões sobre elementos visuais específicos
- Planejar onde/quando/como de cada elemento
- **ESTE É O NÍVEL PRINCIPAL DE DECISÕES TÁTICAS**

### Use LEVEL -1 quando:
- Otimizar planos já criados
- Ajustar timings e layouts
- Resolver conflitos

### Use LEVEL -2 quando:
- Validar código gerado
- Verificar segurança
- Micro-otimizações

---

## 📝 Nomenclatura

### Formato de Nomes

```
{Função}Director{Nível}
```

**Exemplos:**
- `MotionGraphicsDirector0`
- `CreativeDirector+1` (ou `CreativeDirectorPlus1` no código)
- `TimingOptimizer-1` (ou `TimingOptimizerMinus1` no código)

### Formato de Arquivos

```
{nome}_director_{nivel}.py
```

**Exemplos:**
- `motion_graphics_director_0.py`
- `creative_director_plus_1.py`
- `timing_optimizer_minus_1.py`

### Estrutura de Pastas

```
app/directors/
├── level_plus_2/
├── level_plus_1/
├── level_0/          ⭐ HOJE
├── level_minus_1/
└── level_minus_2/
```

---

## 🔮 Roadmap de Implementação

### Fase 1 (Atual)
- ✅ Level 0: MotionGraphicsDirector0

### Fase 2 (Curto Prazo)
- ⏳ Level 0: BrollDirector0
- ⏳ Level 0: ZoomDirector0
- ⏳ Level 0: EffectsDirector0

### Fase 3 (Médio Prazo)
- ⏳ Level +1: CreativeDirector+1
- ⏳ Level +1: ContentDirector+1
- ⏳ Level -1: TimingOptimizer-1

### Fase 4 (Longo Prazo)
- ⏳ Level +2: MultiPlatformDirector+2
- ⏳ Level -2: CodeValidator-2

---

**Última atualização:** 05 Fevereiro 2026  
**Status:** 🚧 Em Desenvolvimento
