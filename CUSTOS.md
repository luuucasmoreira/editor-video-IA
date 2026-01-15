# Custos e Performance

## Análise Local (Padrão) - GRÁTIS 💰

O sistema usa análise local por padrão, **sem custo de IA**:

- Analisa brilho, contraste e movimento
- Processa apenas 3 frames por vídeo (super rápido)
- Ranqueia vídeos por qualidade
- Seleciona melhores momentos automaticamente

**Performance com 8GB de vídeos:**
- ~50-100 vídeos curtos (1-2min cada)
- Análise: ~5-10 minutos
- Processamento: ~10-20 minutos
- **Custo: R$ 0,00**

## Análise com IA (Opcional) - PAGO 💳

Se ativar `USE_AI_ANALYSIS = True` no `config.py`:

- Usa OpenRouter + GPT-4o-mini
- Análise mais sofisticada de conteúdo
- Detecta rostos, emoções, momentos importantes

**Custo estimado (GPT-4o-mini):**
- ~$0.15 por 1M tokens de entrada
- ~$0.60 por 1M tokens de saída
- Para 50 vídeos: ~$0.10-0.30 (R$ 0,50-1,50)

## Recomendação

Para vídeos de culto, a **análise local é suficiente**:
- Identifica momentos bem iluminados
- Detecta movimento (louvor, pregação)
- Evita trechos escuros ou parados
- **Totalmente grátis**

Use IA apenas se precisar de análise avançada (detectar pessoas específicas, emoções, etc).
