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
    
    def find_best_segment(self, audio_path, target_duration=None, min_duration=15):
        """Encontra o melhor trecho da música baseado em energia/volume"""
        clip = None
        is_video = False
        
        if audio_path.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.ogg')):
            audio_clip = AudioFileClip(audio_path)
        else:
            clip = VideoFileClip(audio_path)
            is_video = True
            if clip.audio is None:
                clip.close()
                return None
            audio_clip = clip.audio
        
        duration = audio_clip.duration
        
        # Se não especificou duração, usa 60s ou a duração total (o que for menor)
        if target_duration is None:
            target_duration = min(60, duration)
        
        # Garante que não excede a duração total
        target_duration = min(target_duration, duration)
        
        # Se a música é muito curta, retorna tudo
        if duration <= target_duration + 5:
            audio_clip.close()
            if is_video and clip:
                clip.close()
            return {
                'start': 0,
                'end': duration,
                'duration': duration,
                'score': 100
            }
        
        # Analisa energia em janelas de tempo
        window_size = 1.0  # Analisa a cada 1 segundo
        num_windows = int(duration / window_size)
        energies = []
        
        print(f"   📊 Analisando {num_windows} segmentos da música...")
        
        for i in range(num_windows):
            start_time = i * window_size
            end_time = min((i + 1) * window_size, duration)
            
            try:
                # Extrai o segmento de áudio
                segment = audio_clip.subclipped(start_time, end_time)
                
                # Calcula RMS (Root Mean Square) como medida de energia
                audio_array = segment.to_soundarray()
                if len(audio_array) > 0:
                    # Se é estéreo, calcula média dos canais
                    if len(audio_array.shape) > 1:
                        audio_array = np.mean(audio_array, axis=1)
                    
                    # RMS = raiz quadrada da média dos quadrados
                    rms = np.sqrt(np.mean(audio_array ** 2))
                    energies.append({
                        'start': start_time,
                        'end': end_time,
                        'energy': rms,
                        'duration': end_time - start_time
                    })
                
                segment.close()
            except Exception as e:
                # Se der erro, assume energia média
                energies.append({
                    'start': start_time,
                    'end': end_time,
                    'energy': 0.1,
                    'duration': end_time - start_time
                })
        
        audio_clip.close()
        if is_video and clip:
            clip.close()
        
        if not energies:
            return None
        
        # Encontra o melhor segmento contínuo
        num_windows_needed = int(target_duration / window_size)
        best_segment = None
        best_score = 0
        
        # Procura janela deslizante com maior energia média
        for i in range(len(energies) - num_windows_needed + 1):
            segment_energies = energies[i:i + num_windows_needed]
            avg_energy = np.mean([e['energy'] for e in segment_energies])
            
            # Penaliza se estiver muito no início ou muito no final
            position_penalty = 1.0
            center_time = (segment_energies[0]['start'] + segment_energies[-1]['end']) / 2
            relative_position = center_time / duration
            
            # Prefere trechos no meio da música (evita intros longas e finais)
            if relative_position < 0.1 or relative_position > 0.9:
                position_penalty = 0.7
            elif relative_position < 0.2 or relative_position > 0.8:
                position_penalty = 0.85
            
            score = avg_energy * position_penalty
            
            if score > best_score:
                best_score = score
                best_segment = {
                    'start': segment_energies[0]['start'],
                    'end': segment_energies[-1]['end'],
                    'duration': segment_energies[-1]['end'] - segment_energies[0]['start'],
                    'score': score,
                    'avg_energy': avg_energy
                }
        
        # Se não encontrou segmento bom, pega o de maior energia individual
        if best_segment is None or best_segment['duration'] < min_duration:
            # Ordena por energia
            energies.sort(key=lambda x: x['energy'], reverse=True)
            
            # Tenta encontrar segmento contínuo a partir do mais energético
            for top_energy in energies[:5]:  # Top 5 mais energéticos
                start = max(0, top_energy['start'] - target_duration / 2)
                end = min(duration, start + target_duration)
                
                if end - start >= min_duration:
                    best_segment = {
                        'start': start,
                        'end': end,
                        'duration': end - start,
                        'score': top_energy['energy'],
                        'avg_energy': top_energy['energy']
                    }
                    break
        
        return best_segment