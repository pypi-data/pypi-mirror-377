import os
import tempfile
from typing import Optional, Dict, Any
import ffmpeg

# Try to import pydub, fallback to ffmpeg-only if not available
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pydub not fully available ({e}), falling back to ffmpeg-only mode")
    AudioSegment = None
    PYDUB_AVAILABLE = False


class AudioService:
    """Service for handling audio extraction and processing"""
    
    def __init__(self):
        self.temp_files = []
        self.supported_audio_formats = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']
    
    async def extract_audio(self, video_path: str, output_path: Optional[str] = None, format: str = 'wav') -> str:
        """Extract audio from video file"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if output_path is None:
            # Create temporary file
            temp_fd, output_path = tempfile.mkstemp(suffix=f'.{format}')
            os.close(temp_fd)
            self.temp_files.append(output_path)
        
        try:
            # Extract audio using ffmpeg
            stream = ffmpeg.input(video_path)
            audio = stream.audio
            
            # Configure audio output based on format
            if format == 'wav':
                output_stream = ffmpeg.output(audio, output_path, acodec='pcm_s16le', ac=1, ar=16000)
            elif format == 'mp3':
                output_stream = ffmpeg.output(audio, output_path, acodec='mp3', ac=1, ar=16000)
            else:
                output_stream = ffmpeg.output(audio, output_path, ac=1, ar=16000)
            
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio: {str(e)}")
    
    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get audio file information"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            probe = ffmpeg.probe(audio_path)
            audio_stream = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            
            return {
                'file_path': audio_path,
                'file_size': os.path.getsize(audio_path),
                'duration': float(probe['format']['duration']),
                'codec': audio_stream['codec_name'],
                'sample_rate': int(audio_stream['sample_rate']),
                'channels': int(audio_stream['channels']),
                'bitrate': int(audio_stream.get('bit_rate', 0)),
                'format': probe['format']['format_name']
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to get audio info: {str(e)}")
    
    def convert_audio_format(self, input_path: str, output_path: str, target_format: str = 'wav') -> str:
        """Convert audio to specified format"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Audio file not found: {input_path}")
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if PYDUB_AVAILABLE:
                # Load audio using pydub
                audio = AudioSegment.from_file(input_path)
                
                # Convert to mono and set sample rate for better transcription
                audio = audio.set_channels(1)
                audio = audio.set_frame_rate(16000)
                
                # Export in target format
                audio.export(output_path, format=target_format)
            else:
                # Fallback to ffmpeg-only mode
                stream = ffmpeg.input(input_path)
                
                if target_format == 'wav':
                    output_stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le', ac=1, ar=16000)
                elif target_format == 'mp3':
                    output_stream = ffmpeg.output(stream, output_path, acodec='mp3', ac=1, ar=16000)
                else:
                    output_stream = ffmpeg.output(stream, output_path, ac=1, ar=16000)
                
                ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to convert audio: {str(e)}")
    
    def extract_audio_segment(self, input_path: str, start_time: float, duration: float, output_path: Optional[str] = None) -> str:
        """Extract a segment from audio file"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Audio file not found: {input_path}")
        
        if output_path is None:
            # Create temporary file
            temp_fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)
            self.temp_files.append(output_path)
        
        try:
            if PYDUB_AVAILABLE:
                # Load audio and extract segment using pydub
                audio = AudioSegment.from_file(input_path)
                start_ms = int(start_time * 1000)
                end_ms = int((start_time + duration) * 1000)
                
                segment = audio[start_ms:end_ms]
                segment.export(output_path, format='wav')
            else:
                # Fallback to ffmpeg for segment extraction
                stream = ffmpeg.input(input_path, ss=start_time, t=duration)
                output_stream = ffmpeg.output(stream, output_path, acodec='pcm_s16le')
                ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio segment: {str(e)}")
    
    def normalize_audio(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Normalize audio levels for better transcription"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Audio file not found: {input_path}")
        
        if output_path is None:
            # Create temporary file
            temp_fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)
            self.temp_files.append(output_path)
        
        try:
            if PYDUB_AVAILABLE:
                # Load and normalize audio using pydub
                audio = AudioSegment.from_file(input_path)
                
                # Normalize to -20 dBFS (good level for speech recognition)
                normalized_audio = audio.normalize().apply_gain(-20 - audio.dBFS)
                
                # Ensure mono and proper sample rate
                normalized_audio = normalized_audio.set_channels(1)
                normalized_audio = normalized_audio.set_frame_rate(16000)
                
                normalized_audio.export(output_path, format='wav')
            else:
                # Fallback to ffmpeg for normalization
                stream = ffmpeg.input(input_path)
                
                # Apply loudnorm filter for audio normalization
                normalized = ffmpeg.filter(stream, 'loudnorm', i=-20.0, lra=7.0, tp=-2.0)
                
                # Convert to mono and set sample rate
                output_stream = ffmpeg.output(normalized, output_path, acodec='pcm_s16le', ac=1, ar=16000)
                ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to normalize audio: {str(e)}")
    
    def reduce_noise(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Apply basic noise reduction to audio"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Audio file not found: {input_path}")
        
        if output_path is None:
            # Create temporary file
            temp_fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)
            self.temp_files.append(output_path)
        
        try:
            # Use ffmpeg for basic noise reduction
            stream = ffmpeg.input(input_path)
            
            # Apply high-pass filter to remove low-frequency noise
            filtered = ffmpeg.filter(stream, 'highpass', f=80)
            
            # Apply low-pass filter to remove high-frequency noise
            filtered = ffmpeg.filter(filtered, 'lowpass', f=8000)
            
            output_stream = ffmpeg.output(filtered, output_path, acodec='pcm_s16le')
            ffmpeg.run(output_stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to reduce noise: {str(e)}")
    
    def analyze_audio_quality(self, audio_path: str) -> Dict[str, Any]:
        """Analyze audio quality for transcription suitability"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            info = self.get_audio_info(audio_path)
            
            # Initialize default values
            rms = 0
            snr_estimate = 0
            
            if PYDUB_AVAILABLE:
                try:
                    audio = AudioSegment.from_file(audio_path)
                    
                    # Calculate audio statistics
                    rms = audio.rms
                    max_possible_amplitude = audio.max_possible_amplitude
                    snr_estimate = 20 * (rms / max_possible_amplitude) if max_possible_amplitude > 0 else 0
                except Exception:
                    # If pydub fails, continue with basic analysis
                    pass
            
            # Determine quality level based on file info
            sample_rate = info['sample_rate']
            channels = info['channels']
            duration = info['duration']
            
            quality_score = 0
            quality_factors = []
            
            # Sample rate assessment
            if sample_rate >= 44100:
                quality_score += 25
                quality_factors.append("Excellent sample rate")
            elif sample_rate >= 22050:
                quality_score += 20
                quality_factors.append("Good sample rate")
            elif sample_rate >= 16000:
                quality_score += 15
                quality_factors.append("Adequate sample rate")
            else:
                quality_score += 5
                quality_factors.append("Low sample rate")
            
            # Channel assessment
            if channels == 1:
                quality_score += 20
                quality_factors.append("Mono audio (good for speech)")
            elif channels == 2:
                quality_score += 15
                quality_factors.append("Stereo audio")
            else:
                quality_score += 10
                quality_factors.append(f"{channels} channels")
            
            # Duration assessment
            if duration < 1:
                quality_score += 5
                quality_factors.append("Very short audio")
            elif duration < 10:
                quality_score += 15
                quality_factors.append("Short audio")
            elif duration < 300:  # 5 minutes
                quality_score += 25
                quality_factors.append("Good duration")
            elif duration < 3600:  # 1 hour
                quality_score += 20
                quality_factors.append("Long audio")
            else:
                quality_score += 10
                quality_factors.append("Very long audio")
            
            # RMS/Volume assessment (only if pydub is available)
            if PYDUB_AVAILABLE and rms > 0:
                if rms > 1000:
                    quality_score += 25
                    quality_factors.append("Good audio levels")
                elif rms > 500:
                    quality_score += 20
                    quality_factors.append("Moderate audio levels")
                elif rms > 100:
                    quality_score += 15
                    quality_factors.append("Low audio levels")
                else:
                    quality_score += 5
                    quality_factors.append("Very low audio levels")
            else:
                # Default score when pydub is not available
                quality_score += 15
                quality_factors.append("Audio levels not analyzed (pydub unavailable)")
            
            # Determine overall quality
            if quality_score >= 80:
                overall_quality = "excellent"
            elif quality_score >= 60:
                overall_quality = "good"
            elif quality_score >= 40:
                overall_quality = "fair"
            else:
                overall_quality = "poor"
            
            return {
                'overall_quality': overall_quality,
                'quality_score': quality_score,
                'sample_rate': sample_rate,
                'channels': channels,
                'duration': duration,
                'rms': rms,
                'snr_estimate': snr_estimate,
                'file_size_mb': round(info['file_size'] / (1024 * 1024), 2),
                'quality_factors': quality_factors,
                'recommendations': self._get_audio_recommendations(overall_quality, info, quality_factors)
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze audio quality: {str(e)}")
    
    def _get_audio_recommendations(self, quality: str, info: Dict[str, Any], factors: list) -> list:
        """Get recommendations for improving audio quality"""
        recommendations = []
        
        if quality == "poor":
            recommendations.append("Consider re-recording with better audio equipment")
            recommendations.append("Try audio normalization and noise reduction")
        elif quality == "fair":
            recommendations.append("Consider applying audio normalization")
            recommendations.append("Try noise reduction if background noise is present")
        
        if info['sample_rate'] < 16000:
            recommendations.append("Consider upsampling to at least 16kHz for better transcription")
        
        if info['channels'] > 1:
            recommendations.append("Consider converting to mono for speech transcription")
        
        if info['duration'] > 3600:
            recommendations.append("Consider splitting long audio into smaller segments")
        
        return recommendations
    
    def cleanup_temp_file(self, file_path: str) -> None:
        """Clean up a specific temporary file"""
        try:
            if file_path in self.temp_files:
                self.temp_files.remove(file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass  # Ignore cleanup errors
    
    def cleanup_temp_files(self) -> None:
        """Clean up all temporary files created by this service"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception:
                pass  # Ignore cleanup errors
        
        self.temp_files.clear()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.cleanup_temp_files()