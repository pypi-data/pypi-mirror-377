import os
from typing import Dict, Any
from pathlib import Path
import ffmpeg
from .base_agent import BaseTranscriptionAgent


class AnalyzerAgent(BaseTranscriptionAgent):
    """Agent responsible for analyzing video files and extracting metadata"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Analizador de Video",
            description="Analiza archivos de video para extraer metadatos, duración e información de calidad",
            config=config
        )
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video file and return metadata"""
        video_path = input_data.get('video_path')
        
        if not video_path:
            raise ValueError("video_path is required")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Check if file format is supported
        file_extension = Path(video_path).suffix.lower()
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported video format: {file_extension}")
        
        try:
            # Extract video metadata using ffmpeg
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            # Calculate file size in MB
            file_size_bytes = os.path.getsize(video_path)
            file_size_mb = file_size_bytes / (1024 * 1024)
            
            # Calculate FPS properly
            fps_str = video_info.get('r_frame_rate', '0/1')
            try:
                fps = eval(fps_str) if '/' in fps_str else float(fps_str)
            except:
                fps = 0.0
            
            # Get bitrates
            video_bitrate = int(video_info.get('bit_rate', 0)) // 1000  # Convert to kbps
            audio_bitrate = int(audio_info.get('bit_rate', 0)) // 1000 if audio_info else 0  # Convert to kbps
            
            metadata = {
                'file_path': video_path,
                'file_size': file_size_bytes,
                'file_size_mb': file_size_mb,
                'duration': float(probe['format']['duration']),
                'format': probe['format']['format_name'],
                'video_codec': video_info['codec_name'],
                'video_resolution': f"{video_info['width']}x{video_info['height']}",
                'fps': fps,
                'video_bitrate': video_bitrate,
                'has_audio': audio_info is not None,
                'audio_codec': audio_info['codec_name'] if audio_info else None,
                'audio_sample_rate': int(audio_info['sample_rate']) if audio_info else None,
                'audio_channels': int(audio_info['channels']) if audio_info else None,
                'audio_bitrate': audio_bitrate,
                'bitrate': int(probe['format'].get('bit_rate', 0)) // 1000,  # Total bitrate in kbps
                'quality_score': self._calculate_quality_score(video_info, audio_info, file_size_mb)
            }
            
            # Store in memory for other agents
            self.set_memory('last_analysis', metadata)
            
            return {
                'status': 'success',
                'metadata': metadata,
                'agent': self.name
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'agent': self.name
            }
    
    def discover_videos(self, directory: str) -> list:
        """Discover video files in a directory"""
        video_files = []
        
        if not os.path.exists(directory):
            return video_files
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in self.supported_formats:
                    video_files.append(os.path.join(root, file))
        
        return video_files
    
    def _calculate_quality_score(self, video_info: dict, audio_info: dict, file_size_mb: float) -> str:
        """Calculate a quality score based on video and audio parameters"""
        try:
            score = 0
            
            # Video quality factors
            width = video_info.get('width', 0)
            height = video_info.get('height', 0)
            
            if width >= 1920 and height >= 1080:
                score += 40  # 1080p or higher
            elif width >= 1280 and height >= 720:
                score += 30  # 720p
            elif width >= 854 and height >= 480:
                score += 20  # 480p
            else:
                score += 10  # Lower resolution
            
            # Audio quality factors
            if audio_info:
                sample_rate = int(audio_info.get('sample_rate', 0))
                channels = int(audio_info.get('channels', 0))
                
                if sample_rate >= 44100:
                    score += 20
                elif sample_rate >= 22050:
                    score += 15
                else:
                    score += 10
                
                if channels >= 2:
                    score += 10
                else:
                    score += 5
            
            # File size efficiency (higher bitrate = better quality)
            if file_size_mb > 0:
                # This is a rough estimation
                if file_size_mb > 100:  # Large file, likely good quality
                    score += 20
                elif file_size_mb > 50:
                    score += 15
                elif file_size_mb > 10:
                    score += 10
                else:
                    score += 5
            
            # Convert score to rating
            if score >= 80:
                return "Excellent"
            elif score >= 60:
                return "Good"
            elif score >= 40:
                return "Fair"
            elif score >= 20:
                return "Poor"
            else:
                return "Very Poor"
                
        except Exception:
            return "Unknown"
    
    def estimate_transcription_time(self, duration: float) -> float:
        """Estimate transcription processing time based on video duration"""
        # Rough estimate: transcription takes about 10-20% of video duration
        return duration * 0.15