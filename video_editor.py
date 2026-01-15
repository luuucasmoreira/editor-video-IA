try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
except ImportError:
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip

from pathlib import Path
import config
import numpy as np

class VideoEditor:
    def __init__(self, pattern_analysis, beat_times, custom_audio=None):
        self.pattern = pattern_analysis
        self.beats = beat_times
        self.custom_audio = custom_audio
    
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
            subclip = clip.subclipped(clip_info['start'], clip_info['end'])
            
            # Converte para formato Reels
            subclip = self.crop_to_reels(subclip)
            
            all_clips.append(subclip)
        
        # Concatena todos os clipes
        print(f"   Concatenando clipes...")
        final_clip = concatenate_videoclips(all_clips, method="compose")
        
        # Ajusta duração para match com música
        if final_clip.duration > audio_duration:
            # Acelera levemente se necessário
            speed_factor = final_clip.duration / audio_duration
            if speed_factor <= 1.3:  # Máximo 30% mais rápido
                final_clip = final_clip.speedx(speed_factor)
            else:
                # Corta se muito longo
                final_clip = final_clip.subclipped(0, audio_duration)
        elif final_clip.duration < audio_duration:
            # Desacelera levemente se necessário
            speed_factor = final_clip.duration / audio_duration
            if speed_factor >= 0.8:  # Máximo 20% mais lento
                final_clip = final_clip.speedx(speed_factor)
        
        # Adiciona música
        print(f"   🎵 Aplicando música")
        audio_clip = AudioFileClip(self.custom_audio)
        
        if audio_clip.duration > final_clip.duration:
            audio_clip = audio_clip.subclipped(0, final_clip.duration)
        
        final_clip = final_clip.with_audio(audio_clip)
        
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
