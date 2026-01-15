import os
from pathlib import Path
from video_analyzer import VideoAnalyzer
from audio_processor import AudioProcessor
from video_editor import VideoEditor
import config

def setup_directories():
    """Cria as pastas necessárias"""
    for dir_path in [config.VIDEOS_DIR, config.PADRAO_DIR, config.MUSICA_DIR, config.OUTPUT_DIR]:
        Path(dir_path).mkdir(exist_ok=True)

def get_video_files(directory):
    """Retorna lista de arquivos de vídeo"""
    extensions = ['.mp4', '.mov', '.avi', '.mkv']
    files = []
    
    for ext in extensions:
        files.extend(Path(directory).glob(f'*{ext}'))
    
    return [str(f) for f in files]

def get_audio_files(directory):
    """Retorna lista de arquivos de áudio"""
    extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg']
    files = []
    
    for ext in extensions:
        files.extend(Path(directory).glob(f'*{ext}'))
    
    return [str(f) for f in files]

def main():
    print("🎬 Church Reels Editor - Compilação Automática")
    print("=" * 50)
    
    # Setup
    setup_directories()
    
    # Verifica API key
    if not config.OPENROUTER_API_KEY:
        print("⚠️  OPENROUTER_API_KEY não configurada no .env")
        print("Continuando sem análise IA avançada...")
    
    # Analisa vídeo padrão
    padrao_videos = get_video_files(config.PADRAO_DIR)
    
    if padrao_videos:
        print(f"\n📋 Analisando padrão: {padrao_videos[0]}")
        analyzer = VideoAnalyzer()
        pattern = analyzer.analyze_pattern(padrao_videos[0])
        print(f"   Duração: {pattern['duration']:.1f}s")
        print(f"   FPS: {pattern['fps']}")
    else:
        print("\n⚠️  Nenhum vídeo padrão encontrado em 'padrao/'")
        print("   Usando configurações padrão...")
        pattern = {"duration": 30, "fps": 30}
        analyzer = VideoAnalyzer()
    
    # Verifica músicas customizadas
    musicas = get_audio_files(config.MUSICA_DIR)
    
    if not musicas:
        print(f"\n❌ Nenhuma música encontrada em '{config.MUSICA_DIR}/'")
        print("   Coloque uma música na pasta 'musica/' para criar o compilado.")
        return
    
    custom_audio = musicas[0]
    print(f"\n🎵 Usando música: {Path(custom_audio).name}")
    
    # Processa vídeos
    input_videos = get_video_files(config.VIDEOS_DIR)
    
    if not input_videos:
        print(f"\n❌ Nenhum vídeo encontrado em '{config.VIDEOS_DIR}/'")
        print("   Coloque seus vídeos na pasta 'videos/' e execute novamente.")
        return
    
    print(f"\n🎥 Encontrados {len(input_videos)} vídeo(s) para compilar")
    
    # Detecta beats na música
    audio_proc = AudioProcessor()
    beats = audio_proc.detect_beats(custom_audio)
    audio_duration = audio_proc.get_audio_duration(custom_audio)
    print(f"   Duração da música: {audio_duration:.1f}s")
    print(f"   Encontrados {len(beats)} pontos de corte")
    
    # Se tem muitos vídeos, ranqueia e seleciona os melhores
    if len(input_videos) > config.MAX_CLIPS_IN_COMPILATION:
        print(f"\n⚡ Muitos vídeos! Selecionando os {config.MAX_CLIPS_IN_COMPILATION} melhores...")
        ranked_videos = analyzer.rank_videos(input_videos, config.MAX_CLIPS_IN_COMPILATION)
        selected_videos = [v['path'] for v in ranked_videos]
    else:
        selected_videos = input_videos
    
    # Extrai melhores momentos de cada vídeo selecionado
    print(f"\n🔍 Extraindo melhores momentos de {len(selected_videos)} vídeo(s)...")
    best_clips = []
    
    # Calcula duração ideal por vídeo
    target_clip_duration = min(audio_duration / len(selected_videos), 12)
    
    for i, video_path in enumerate(selected_videos, 1):
        print(f"   [{i}/{len(selected_videos)}] {Path(video_path).name}")
        
        best_moment = analyzer.find_best_moments(video_path, target_clip_duration)
        
        if best_moment:
            print(f"      ✓ Momento: {best_moment['start']:.1f}s - {best_moment['end']:.1f}s (score: {best_moment['score']:.1f})")
            best_clips.append({
                'path': video_path,
                'start': best_moment['start'],
                'end': best_moment['end'],
                'score': best_moment['score']
            })
    
    if not best_clips:
        print("\n❌ Não foi possível extrair momentos dos vídeos")
        return
    
    # Cria compilação
    print(f"\n🎬 Criando compilação com {len(best_clips)} clipes...")
    editor = VideoEditor(pattern, beats, custom_audio)
    output_path = os.path.join(config.OUTPUT_DIR, "reel_compilado.mp4")
    
    editor.create_compilation(best_clips, output_path, audio_duration)
    
    print("\n" + "=" * 50)
    print(f"✅ Compilação concluída!")
    print(f"📁 Vídeo salvo em: {output_path}")

if __name__ == "__main__":
    main()
