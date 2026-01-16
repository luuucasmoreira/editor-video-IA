# Church Reels Editor

Automação para editar vídeos de culto para Instagram Reels com efeitos profissionais.

## Estrutura de Pastas

```
videos/     - Coloque os vídeos originais aqui
musica/     - Coloque músicas para substituir o áudio (MP3, WAV, etc)
final/      - Coloque logo.png aqui (será adicionado ao final dos vídeos)
output/     - Vídeos editados serão salvos aqui
```

## Instalação

```bash
# Com UV (recomendado)
uv pip install -r requirements.txt

# Ou com pip normal
pip install -r requirements.txt
```

## Configuração (Opcional)

1. Copie `.env.example` para `.env`
2. Adicione sua chave do OpenRouter no `.env` (apenas se quiser usar análise com IA)

## Uso

```bash
# Com UV (recomendado)
uv run python main.py

# Ou Python direto
python main.py
```

## Funcionalidades Principais

### Edição Automática
- **Cortes de até 6 segundos**: Cada clipe tem duração máxima de 6 segundos
- **Slow motion 0.8x**: Aplica efeito cinematográfico em todos os cortes
- **Vídeo final de 1 minuto**: Duração máxima otimizada para Reels
- **Formato 9:16**: Vídeo vertical otimizado para Instagram (1080x1920)

### Áudio Inteligente
- **Melhor trecho da música**: Analisa energia e seleciona o melhor momento (evita intros/outros)
- **Sincronização com beats**: Cortes alinhados com os beats da música
- **Não começa do início**: Pula intros longas automaticamente

### Visual
- **Logo no final**: Adiciona logo.png nos últimos 3 segundos (canto inferior direito)
- **Fade in/out**: Transições suaves no logo
- **Seleção inteligente**: Escolhe os melhores momentos por brilho, contraste e movimento

## Como Usar

### Passo a Passo

1. **Adicione seus vídeos**
   - Coloque todos os vídeos na pasta `videos/`
   - Pode adicionar quantos quiser (o sistema seleciona os melhores)

2. **Adicione uma música**
   - Coloque um arquivo de áudio na pasta `musica/`
   - Formatos aceitos: MP3, WAV, M4A, AAC, OGG

3. **Adicione o logo (opcional)**
   - Coloque um arquivo `logo.png` na pasta `final/`
   - Será exibido nos últimos 3 segundos do vídeo

4. **Execute o editor**
   ```bash
   uv run python main.py
   ```

5. **Aguarde o processamento**
   - O sistema analisa a música
   - Seleciona os melhores vídeos
   - Extrai os melhores momentos (máx 6s cada)
   - Aplica slow motion 0.8x
   - Adiciona a música no melhor trecho
   - Adiciona o logo no final
   - Salva em `output/reel_compilado.mp4`

## Configurações Avançadas

Edite o arquivo `config.py` para ajustar:

```python
REELS_MAX_DURATION = 60          # Duração máxima do vídeo final (segundos)
MAX_CLIP_DURATION = 6.0          # Duração máxima de cada corte (segundos)
SLOW_MOTION_SPEED = 0.8          # Velocidade do slow motion (0.8 = 80%)
LOGO_DURATION = 3.0              # Duração da exibição do logo (segundos)
MAX_CLIPS_IN_COMPILATION = 15    # Máximo de clipes no vídeo final
```

## Otimizações

- **Análise local rápida**: Não requer IA para funcionalidade básica (grátis!)
- **3 frames por vídeo**: Análise ultra-rápida de qualidade
- **Escalável**: Processa dezenas de vídeos sem problemas
- **Memória eficiente**: Fecha clipes automaticamente após uso

## Análise com IA (Opcional)

Para ativar análise avançada com IA:
1. Configure `USE_AI_ANALYSIS = True` no `config.py`
2. Adicione sua chave OpenRouter no `.env`
3. Isso permite análise mais profunda dos vídeos (custo adicional)

## Troubleshooting

**Erro: "Nenhum vídeo encontrado"**
- Verifique se há vídeos na pasta `videos/`
- Formatos suportados: MP4, MOV, AVI, MKV

**Erro: "Nenhuma música encontrada"**
- Adicione pelo menos um arquivo de áudio na pasta `musica/`

**Logo não aparece**
- Verifique se o arquivo se chama exatamente `logo.png`
- Coloque na pasta `final/`

**Vídeo muito longo/curto**
- Ajuste `REELS_MAX_DURATION` no `config.py`
