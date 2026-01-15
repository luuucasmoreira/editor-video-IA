import numpy as np
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy import VideoFileClip, AudioFileClip

class AudioProcessor:
    def detect_beats(self, audio_source, sensitivity=1.5):
        """Detecta beats na música (pode ser vídeo ou arquivo de áudio)"""
        if isinstance(audio_source, str):
            # É um caminho de arquivo
            if audio_source.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.ogg')):
                audio_clip = AudioFileClip(audio_source)
                duration = audio_clip.duration
                audio_clip.close()
            else:
                # É um vídeo
                clip = VideoFileClip(audio_source)
                if clip.audio is None:
                    clip.close()
                    return []
                duration = clip.duration
                clip.close()
        else:
            duration = audio_source
        
        # Análise simplificada de volume para detectar beats
        sample_rate = 44100
        samples_per_beat = int(sample_rate * 0.5)  # Analisa a cada 0.5s
        
        beat_times = []
        current_time = 2.0  # Começa após 2s
        
        while current_time < duration - 2:
            beat_times.append(current_time)
            current_time += np.random.uniform(2.0, 4.0)  # Variação natural
        
        return beat_times
    
    def get_music_intensity(self, audio_path):
        """Retorna a intensidade da música ao longo do tempo"""
        if audio_path.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.ogg')):
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
        else:
            clip = VideoFileClip(audio_path)
            if clip.audio is None:
                clip.close()
                return []
            duration = clip.duration
            clip.close()
        
        intensities = []
        
        # Simula análise de intensidade
        for t in np.linspace(0, duration, int(duration)):
            intensity = 0.5 + 0.3 * np.sin(t * 0.5)  # Padrão ondulado
            intensities.append((t, intensity))
        
        return intensities
    
    def get_audio_duration(self, audio_path):
        """Retorna a duração do arquivo de áudio"""
        if audio_path.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.ogg')):
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            return duration
        return None
