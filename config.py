import os
from dotenv import load_dotenv

load_dotenv()

# Configurações
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Pastas
VIDEOS_DIR = "videos"
PADRAO_DIR = "padrao"
MUSICA_DIR = "musica"
OUTPUT_DIR = "output"
FINAL_DIR = "final"  # Pasta para logo

# Formato Reels
REELS_WIDTH = 1080
REELS_HEIGHT = 1920
REELS_MAX_DURATION = 60  # segundos (máximo 1 minuto para reels)

# Edição
TRANSITION_DURATION = 0.3  # segundos
MIN_CLIP_DURATION = 2.0  # segundos
MAX_CLIP_DURATION = 6.0  # duração máxima de cada corte (6 segundos)
MIN_MOMENT_DURATION = 3.0  # duração mínima de um momento extraído
MAX_CLIPS_IN_COMPILATION = 15  # máximo de clipes no compilado final
SLOW_MOTION_SPEED = 0.8  # velocidade do slow motion (0.8 = 80% da velocidade normal)
LOGO_DURATION = 3.0  # duração da exibição do logo no final (segundos)

# Análise de vídeo
USE_AI_ANALYSIS = True  # True = usa IA (custa $), False = análise local (grátis)
SAMPLE_FRAMES = 3  # número de frames para analisar por vídeo
