import os
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import ffmpeg


class VideoService:
    """Service for handling video file operations"""
    
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v']
        self.temp_files = []
    
    def validate_video_file(self, video_path: str) -> bool:
        """Validate if the video file exists and is supported"""
        if not os.path.exists(video_path):
            return False
        
        file_extension = Path(video_path).suffix.lower()
        return file_extension in self.supported_formats
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get detailed video information using ffmpeg"""
        if not self.validate_video_file(video_path):
            raise ValueError(f"Invalid or unsupported video file: {video_path}")
        
        try:
            probe = ffmpeg.probe(video_path)
            
            # Extract video stream info
            video_streams = [s for s in probe['streams'] if s['codec_type'] == 'video']
            audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
            
            if not video_streams:
                raise ValueError("No video stream found in file")
            
            video_stream = video_streams[0]
            audio_stream = audio_streams[0] if audio_streams else None
            
            info = {
                'file_path': video_path,
                'file_size': os.path.getsize(video_path),
                'format': probe['format'],
                'duration': float(probe['format']['duration']),
                'bitrate': int(probe['format'].get('bit_rate', 0)),
                'video': {
                    'codec': video_stream['codec_name'],
                    'width': int(video_stream['width']),
                    'height': int(video_stream['height']),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')),
                    'pixel_format': video_stream.get('pix_fmt'),
                    'bitrate': int(video_stream.get('bit_rate', 0))
                },
                'audio': None
            }
            
            if audio_stream:
                info['audio'] = {
                    'codec': audio_stream['codec_name'],
                    'sample_rate': int(audio_stream['sample_rate']),
                    'channels': int(audio_stream['channels']),
                    'bitrate': int(audio_stream.get('bit_rate', 0)),
                    'duration': float(audio_stream.get('duration', info['duration']))
                }
            
            return info
            
        except Exception as e:
            raise RuntimeError(f"Failed to get video info: {str(e)}")
    
    def discover_videos(self, directory: str, recursive: bool = True) -> List[str]:
        """Discover video files in a directory"""
        video_files = []
        
        if not os.path.exists(directory):
            return video_files
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if Path(file).suffix.lower() in self.supported_formats:
                        video_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path) and Path(file).suffix.lower() in self.supported_formats:
                    video_files.append(file_path)
        
        return sorted(video_files)
    
    def convert_video_format(self, input_path: str, output_path: str, target_format: str = 'mp4') -> str:
        """Convert video to specified format"""
        if not self.validate_video_file(input_path):
            raise ValueError(f"Invalid input video file: {input_path}")
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert video using ffmpeg
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to convert video: {str(e)}")
    
    def extract_video_segment(self, input_path: str, start_time: float, duration: float, output_path: Optional[str] = None) -> str:
        """Extract a segment from video"""
        if not self.validate_video_file(input_path):
            raise ValueError(f"Invalid input video file: {input_path}")
        
        if output_path is None:
            # Create temporary file
            temp_fd, output_path = tempfile.mkstemp(suffix='.mp4')
            os.close(temp_fd)
            self.temp_files.append(output_path)
        
        try:
            # Extract segment using ffmpeg
            stream = ffmpeg.input(input_path, ss=start_time, t=duration)
            stream = ffmpeg.output(stream, output_path, vcodec='copy', acodec='copy')
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract video segment: {str(e)}")
    
    def get_video_thumbnail(self, input_path: str, timestamp: float = 0, output_path: Optional[str] = None) -> str:
        """Extract a thumbnail from video at specified timestamp"""
        if not self.validate_video_file(input_path):
            raise ValueError(f"Invalid input video file: {input_path}")
        
        if output_path is None:
            # Create temporary file
            temp_fd, output_path = tempfile.mkstemp(suffix='.jpg')
            os.close(temp_fd)
            self.temp_files.append(output_path)
        
        try:
            # Extract thumbnail using ffmpeg
            stream = ffmpeg.input(input_path, ss=timestamp)
            stream = ffmpeg.output(stream, output_path, vframes=1)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract thumbnail: {str(e)}")
    
    def get_video_quality_info(self, video_path: str) -> Dict[str, Any]:
        """Analyze video quality and provide recommendations"""
        info = self.get_video_info(video_path)
        
        video_info = info['video']
        audio_info = info.get('audio')
        
        # Determine video quality level
        resolution = video_info['width'] * video_info['height']
        
        if resolution >= 3840 * 2160:  # 4K
            quality_level = 'excellent'
        elif resolution >= 1920 * 1080:  # 1080p
            quality_level = 'high'
        elif resolution >= 1280 * 720:  # 720p
            quality_level = 'good'
        elif resolution >= 854 * 480:  # 480p
            quality_level = 'fair'
        else:
            quality_level = 'poor'
        
        # Audio quality assessment
        audio_quality = 'none'
        if audio_info:
            sample_rate = audio_info['sample_rate']
            if sample_rate >= 48000:
                audio_quality = 'excellent'
            elif sample_rate >= 44100:
                audio_quality = 'high'
            elif sample_rate >= 22050:
                audio_quality = 'good'
            else:
                audio_quality = 'fair'
        
        return {
            'video_quality': quality_level,
            'audio_quality': audio_quality,
            'resolution': f"{video_info['width']}x{video_info['height']}",
            'total_pixels': resolution,
            'fps': video_info['fps'],
            'has_audio': audio_info is not None,
            'file_size_mb': round(info['file_size'] / (1024 * 1024), 2),
            'duration_minutes': round(info['duration'] / 60, 2),
            'recommendations': self._get_quality_recommendations(quality_level, audio_quality, info)
        }
    
    def _get_quality_recommendations(self, video_quality: str, audio_quality: str, info: Dict[str, Any]) -> List[str]:
        """Get recommendations based on video quality"""
        recommendations = []
        
        if video_quality in ['poor', 'fair']:
            recommendations.append("Consider using a higher quality video for better transcription accuracy")
        
        if audio_quality in ['poor', 'fair']:
            recommendations.append("Audio quality may affect transcription accuracy")
        elif audio_quality == 'none':
            recommendations.append("No audio track found - cannot transcribe")
        
        if info['duration'] > 3600:  # More than 1 hour
            recommendations.append("Long video detected - consider splitting into smaller segments")
        
        file_size_mb = info['file_size'] / (1024 * 1024)
        if file_size_mb > 1000:  # More than 1GB
            recommendations.append("Large file size - processing may take longer")
        
        return recommendations
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files created by this service"""
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