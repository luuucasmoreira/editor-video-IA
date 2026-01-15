import os
from pathlib import Path
from openai import OpenAI
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip
import base64
import config
import numpy as np

class VideoAnalyzer:
    def __init__(self):
        if config.OPENROUTER_API_KEY:
            self.client = OpenAI(
                api_key=config.OPENROUTER_API_KEY,
                base_url=config.OPENROUTER_BASE_URL
            )
        else:
            self.client = None
    
    def extract_frames(self, video_path, num_frames=5):
        """Extrai frames do vídeo para análise"""
        clip = VideoFileClip(video_path)
        duration = clip.duration
        frames = []
        
        for i in range(num_frames):
            time = (duration / num_frames) * i
            frame = clip.get_frame(time)
            frames.append(frame)
        
        clip.close()
        return frames
    
    def find_best_moments(self, video_path, target_duration=10):
        """Identifica os melhores momentos do vídeo (análise local, sem IA)"""
        clip = VideoFileClip(video_path)
        duration = clip.duration
        
        # Se vídeo é curto, usa quase tudo
        if duration <= target_duration + 4:
            best_moment = {
                'start': 1.0,
                'end': min(duration - 1, target_duration),
                'score': 100,
                'duration': min(duration - 2, target_duration)
            }
            clip.close()
            return best_moment
        
        # Análise rápida: amostra poucos frames
        best_moments = []
        
        # Divide vídeo em segmentos
        num_segments = max(2, int(duration / 10))  # Segmentos de ~10s
        segment_duration = duration / num_segments
        
        for i in range(num_segments):
            start = i * segment_duration + 1  # Pula 1s do início
            end = min(start + target_duration, (i + 1) * segment_duration - 1)
            
            if end - start >= config.MIN_MOMENT_DURATION:
                # Analisa apenas 3 frames por segmento (rápido!)
                scores = []
                for sample in range(config.SAMPLE_FRAMES):
                    sample_time = start + (end - start) * (sample / config.SAMPLE_FRAMES)
                    frame = clip.get_frame(sample_time)
                    
                    # Métricas de qualidade
                    brightness = np.mean(frame)
                    contrast = np.std(frame)
                    
                    # Detecta movimento (diferença entre canais)
                    motion = np.std([np.std(frame[:,:,c]) for c in range(3)])
                    
                    # Score: prefere vídeos bem iluminados, com contraste e movimento
                    score = (brightness * 0.3 + contrast * 0.5 + motion * 0.2)
                    scores.append(score)
                
                avg_score = np.mean(scores)
                
                best_moments.append({
                    'start': start,
                    'end': end,
                    'score': avg_score,
                    'duration': end - start
                })
        
        clip.close()
        
        # Ordena por score
        best_moments.sort(key=lambda x: x['score'], reverse=True)
        
        return best_moments[0] if best_moments else None
    
    def rank_videos(self, video_paths, max_videos=None):
        """Ranqueia vídeos por qualidade (análise local, sem IA)"""
        print(f"\n📊 Analisando qualidade de {len(video_paths)} vídeos...")
        
        ranked = []
        
        for i, video_path in enumerate(video_paths, 1):
            try:
                clip = VideoFileClip(video_path)
                duration = clip.duration
                
                # Amostra apenas 3 frames do vídeo inteiro
                scores = []
                for sample in range(config.SAMPLE_FRAMES):
                    time = duration * (sample / config.SAMPLE_FRAMES)
                    frame = clip.get_frame(time)
                    
                    brightness = np.mean(frame)
                    contrast = np.std(frame)
                    motion = np.std([np.std(frame[:,:,c]) for c in range(3)])
                    
                    score = brightness * 0.3 + contrast * 0.5 + motion * 0.2
                    scores.append(score)
                
                avg_score = np.mean(scores)
                
                ranked.append({
                    'path': video_path,
                    'score': avg_score,
                    'duration': duration
                })
                
                clip.close()
                
                print(f"   [{i}/{len(video_paths)}] {Path(video_path).name}: score {avg_score:.1f}")
                
            except Exception as e:
                print(f"   ⚠️  Erro ao analisar {Path(video_path).name}: {e}")
        
        # Ordena por score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        
        # Limita quantidade se especificado
        if max_videos and len(ranked) > max_videos:
            print(f"\n   ✂️  Selecionando top {max_videos} vídeos de {len(ranked)}")
            ranked = ranked[:max_videos]
        
        return ranked
    
    def analyze_pattern(self, padrao_video_path):
        """Analisa o vídeo padrão e retorna características"""
        clip = VideoFileClip(padrao_video_path)
        
        analysis = {
            "duration": clip.duration,
            "fps": clip.fps,
            "size": clip.size,
            "has_audio": clip.audio is not None
        }
        
        clip.close()
        
        # Usar IA para análise mais profunda
        if self.client:
            prompt = f"""Analise este vídeo de culto e descreva:
1. Ritmo de cortes (rápido/médio/lento)
2. Estilo de transições
3. Momentos de destaque
4. Sincronização com música

Responda em formato JSON com: cut_rhythm, transition_style, highlights, music_sync"""
            
            try:
                response = self.client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                analysis["ai_insights"] = response.choices[0].message.content
            except Exception as e:
                print(f"Erro na análise IA: {e}")
                analysis["ai_insights"] = "Análise padrão: cortes médios, transições suaves"
        else:
            analysis["ai_insights"] = "Análise padrão: cortes médios, transições suaves"
        
        return analysis
