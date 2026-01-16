try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
except ImportError:
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip

from pathlib import Path
import config
import numpy as np
import os

class VideoEditor:
    def __init__(self, pattern_analysis, beat_times, custom_audio=None, audio_start=0, audio_duration=None):
        self.pattern = pattern_analysis
        self.beats = beat_times
        self.custom_audio = custom_audio
        self.audio_start = audio_start  # Início do trecho de áudio a usar
        self.audio_duration = audio_duration  # Duração do trecho de áudio
    
    def crop_to_reels(self, clip):
        """Converte vídeo para formato Reels 9:16"""
        w, h = clip.size
        target_ratio = config.REELS_WIDTH / config.REELS_HEIGHT
        current_ratio = w / h
        
        if current_ratio > target_ratio:
            # Vídeo muito largo, corta os lados
            new_w = int(h * target_ratio)
            x_center = w / 2
            clip = clip.cropped(x1=x_center - new_w/2, x2=x_center + new_w/2)
        else:
            # Vídeo muito alto, corta topo/base
            new_h = int(w / target_ratio)
            y_center = h / 2
            clip = clip.cropped(y1=y_center - new_h/2, y2=y_center + new_h/2)
        
        # Usa new_size (com underscore)
        return clip.resized(new_size=(config.REELS_WIDTH, config.REELS_HEIGHT))
    
    def add_logo_at_end(self, clip, logo_path):
        """Adiciona logo no canto inferior direito nos últimos segundos do vídeo"""
        try:
            # Carrega a logo
            logo = ImageClip(logo_path)
            
            # Redimensiona logo para 20% da largura do vídeo
            logo_width = int(config.REELS_WIDTH * 0.2)
            logo = logo.resized(width=logo_width)
            
            # Posiciona no canto inferior direito com margem
            margin = 30
            logo_x = config.REELS_WIDTH - logo.w - margin
            logo_y = config.REELS_HEIGHT - logo.h - margin
            
            # Define quando a logo aparece (últimos X segundos)
            logo_start = max(0, clip.duration - config.LOGO_DURATION)
            logo = logo.with_start(logo_start).with_duration(config.LOGO_DURATION)
            logo = logo.with_position((logo_x, logo_y))
            
            # Adiciona fade in/out suave
            logo = logo.crossfadein(0.3).crossfadeout(0.3)
            
            # Sobrepõe logo no vídeo
            final_clip = CompositeVideoClip([clip, logo])
            
            return final_clip
        except Exception as e:
            print(f"      ⚠️  Erro ao adicionar logo: {e}")
            return clip
    
    def create_cuts(self, clip):
        """Cria cortes suaves baseados nos beats"""
        if not self.beats:
            return [clip]
        
        clips = []
        start = 0
        
        for beat_time in self.beats:
            if beat_time > clip.duration:
                break
            
            if beat_time - start >= config.MIN_CLIP_DURATION:
                subclip = clip.subclipped(start, beat_time)
                clips.append(subclip)
                start = beat_time
        
        # Adiciona último clipe
        if start < clip.duration - config.MIN_CLIP_DURATION:
            subclip = clip.subclipped(start, clip.duration)
            clips.append(subclip)
        
        return clips if clips else [clip]
    
    def edit_video(self, input_path, output_path):
        """Edita o vídeo completo"""
        print(f"Processando: {input_path}")
        
        clip = VideoFileClip(input_path)
        
        # Se tem áudio customizado, ajusta duração do vídeo
        if self.custom_audio:
            audio_clip = AudioFileClip(self.custom_audio)
            target_duration = min(audio_clip.duration, config.REELS_MAX_DURATION)
            
            # Ajusta velocidade do vídeo se necessário
            if clip.duration < target_duration:
                # Vídeo mais curto que música - loop ou slow motion
                speed_factor = clip.duration / target_duration
                clip = clip.fx(lambda c: c.speedx(speed_factor))
            elif clip.duration > target_duration:
                # Vídeo mais longo - corta
                clip = clip.subclipped(0, target_duration)
        else:
            # Limita duração para Reels
            if clip.duration > config.REELS_MAX_DURATION:
                clip = clip.subclipped(0, config.REELS_MAX_DURATION)
        
        # Converte para formato Reels
        clip = self.crop_to_reels(clip)
        
        # Cria cortes sincronizados
        clips = self.create_cuts(clip)
        
        # Concatena com transições
        if len(clips) > 1:
            final_clip = concatenate_videoclips(clips, method="compose")
        else:
            final_clip = clips[0]
        
        # Substitui áudio se fornecido
        if self.custom_audio:
            print(f"   🎵 Aplicando música customizada")
            audio_clip = AudioFileClip(self.custom_audio)
            
            # Ajusta duração do áudio para match com vídeo
            if audio_clip.duration > final_clip.duration:
                audio_clip = audio_clip.subclipped(0, final_clip.duration)
            
            final_clip = final_clip.with_audio(audio_clip)
        
        # Exporta
        print(f"Exportando para: {output_path}")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            bitrate='8000k'
        )
        
        clip.close()
        final_clip.close()
        
        print(f"✓ Vídeo salvo: {output_path}")
    
    def create_compilation(self, best_clips, output_path, audio_duration):
        """Cria compilação com os melhores momentos sincronizados"""
        print(f"   Carregando {len(best_clips)} clipes...")
        
        all_clips = []
        original_clips = []  # Guarda referências para fechar depois
        
        # Carrega e processa cada clipe
        for i, clip_info in enumerate(best_clips):
            print(f"   [{i+1}/{len(best_clips)}] Processando {Path(clip_info['path']).name}")
            
            clip = VideoFileClip(clip_info['path'])
            original_clips.append(clip)  # Guarda para fechar depois
            
            # Extrai o melhor momento
            start_time = clip_info['start']
            end_time = min(clip_info['end'], start_time + config.MAX_CLIP_DURATION)
            
            subclip = clip.subclipped(start_time, end_time)
            
            # Aplica slow motion de 0.8x
            print(f"      Aplicando slow motion ({config.SLOW_MOTION_SPEED}x)")
            # MoviePy 2.x usa with_speed_scaled (fator de velocidade)
            subclip = subclip.with_speed_scaled(config.SLOW_MOTION_SPEED)
            
            # Converte para formato Reels
            subclip = self.crop_to_reels(subclip)
            
            all_clips.append(subclip)
        
        # Concatena todos os clipes
        print(f"   Concatenando clipes...")
        final_clip = concatenate_videoclips(all_clips, method="compose")
        
        # Ajusta duração para match com música (se necessário, corta o vídeo)
        if final_clip.duration > audio_duration:
            print(f"   ✂️  Ajustando duração do vídeo final: {final_clip.duration:.1f}s -> {audio_duration:.1f}s")
            final_clip = final_clip.subclipped(0, audio_duration)
        
        # Adiciona música
        print(f"   🎵 Aplicando música")
        audio_clip = AudioFileClip(self.custom_audio)
        
        # Extrai apenas o trecho selecionado da música
        if self.audio_start > 0 or (self.audio_duration and self.audio_duration < audio_clip.duration):
            end_time = self.audio_start + (self.audio_duration or audio_clip.duration)
            audio_clip = audio_clip.subclipped(self.audio_start, min(end_time, audio_clip.duration))
        
        # Ajusta duração do áudio para match com vídeo
        if audio_clip.duration > final_clip.duration:
            audio_clip = audio_clip.subclipped(0, final_clip.duration)
        
        final_clip = final_clip.with_audio(audio_clip)
        
        # Adiciona logo no final se existir
        logo_path = os.path.join(config.FINAL_DIR, "logo.png")
        if os.path.exists(logo_path):
            print(f"   🎨 Adicionando logo no final do vídeo...")
            final_clip = self.add_logo_at_end(final_clip, logo_path)
        else:
            print(f"   ⚠️  Logo não encontrada em {logo_path}")
        
        # Exporta
        print(f"   💾 Exportando vídeo final...")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            bitrate='8000k'
        )
        
        # Fecha tudo depois de exportar
        final_clip.close()
        audio_clip.close()
        for clip in original_clips:
            clip.close()
        
        print(f"   ✓ Compilação salva: {output_path}")
