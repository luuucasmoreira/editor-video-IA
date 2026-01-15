# Church Reels Editor

Automação para editar vídeos de culto para Instagram Reels usando IA.

## Estrutura de Pastas

```
videos/     - Coloque os vídeos originais aqui
padrao/     - Coloque vídeos de referência do padrão desejado
musica/     - Coloque músicas para substituir o áudio (MP3, WAV, etc)
output/     - Vídeos editados serão salvos aqui
```

## Instalação

```bash
# Opção 1: Com UV (recomendado)
uv pip install -r requirements.txt

# Opção 2: Com pip normal
pip install -r requirements.txt
```

## Configuração

1. Copie `.env.example` para `.env`
2. Adicione sua chave do OpenRouter no `.env`

## Uso

```bash
# Opção 1: Com UV
uv run --no-project python main.py

# Opção 2: Python direto (após instalar dependências)
python main.py
```

## Funcionalidades

- **Compilação automática**: Junta múltiplos vídeos em um único Reel
- **Detecção inteligente**: Identifica os melhores momentos de cada vídeo
- **Sincronização com música**: Cortes alinhados com os beats
- **Análise de qualidade**: Seleciona trechos com melhor brilho/contraste
- **Formato Reels**: Otimizado para Instagram (9:16, 1080x1920)
- **Transições suaves**: Fade in/out entre clipes

## Como funciona

1. Coloque **múltiplos vídeos** na pasta `videos/` (pode ser muitos!)
2. Coloque **uma música** na pasta `musica/`
3. Execute `python main.py`
4. O sistema irá:
   - Ranquear vídeos por qualidade (brilho, contraste, movimento)
   - Selecionar os melhores (máx 15 por padrão)
   - Extrair os melhores momentos de cada vídeo
   - Juntar tudo em um único Reel
   - Sincronizar cortes com os beats da música
   - Salvar como `reel_compilado.mp4` na pasta `output/`

## Otimizado para muitos vídeos

- ✅ **Análise local**: Não usa IA para análise básica (grátis!)
- ✅ **Rápido**: Analisa apenas 3 frames por vídeo
- ✅ **Inteligente**: Ranqueia e seleciona os melhores automaticamente
- ✅ **Escalável**: Processa 8GB+ de vídeos sem problemas

**Custo de IA**: Apenas se ativar `USE_AI_ANALYSIS = True` no config.py (opcional)
# editor-video-IA
