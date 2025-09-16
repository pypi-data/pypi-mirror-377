from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


@dataclass
class VideoMetadata:
    """Data model for video file metadata"""
    
    file_path: str
    file_size: int
    duration: float
    format_name: str
    bitrate: int
    
    # Video stream information
    video_codec: str
    video_width: int
    video_height: int
    video_fps: float
    pixel_format: Optional[str] = None
    video_bitrate: int = 0
    
    # Audio stream information
    has_audio: bool = False
    audio_codec: Optional[str] = None
    audio_sample_rate: Optional[int] = None
    audio_channels: Optional[int] = None
    audio_bitrate: int = 0
    
    # Analysis metadata
    analyzed_at: datetime = field(default_factory=datetime.now)
    quality_assessment: Optional[Dict[str, Any]] = None
    
    @property
    def filename(self) -> str:
        """Get filename without path"""
        return Path(self.file_path).name
    
    @property
    def file_extension(self) -> str:
        """Get file extension"""
        return Path(self.file_path).suffix.lower()
    
    @property
    def resolution_string(self) -> str:
        """Get resolution as string (e.g., '1920x1080')"""
        return f"{self.video_width}x{self.video_height}"
    
    @property
    def total_pixels(self) -> int:
        """Get total number of pixels"""
        return self.video_width * self.video_height
    
    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio"""
        return self.video_width / self.video_height if self.video_height > 0 else 0
    
    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes"""
        return self.duration / 60
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)
    
    @property
    def is_hd(self) -> bool:
        """Check if video is HD (720p or higher)"""
        return self.total_pixels >= 1280 * 720
    
    @property
    def is_full_hd(self) -> bool:
        """Check if video is Full HD (1080p)"""
        return self.total_pixels >= 1920 * 1080
    
    @property
    def is_4k(self) -> bool:
        """Check if video is 4K"""
        return self.total_pixels >= 3840 * 2160
    
    def get_quality_level(self) -> str:
        """Get video quality level as string"""
        if self.is_4k:
            return "4K"
        elif self.is_full_hd:
            return "Full HD"
        elif self.is_hd:
            return "HD"
        elif self.total_pixels >= 854 * 480:
            return "SD"
        else:
            return "Low"
    
    def get_audio_quality_level(self) -> str:
        """Get audio quality level as string"""
        if not self.has_audio:
            return "None"
        
        if not self.audio_sample_rate:
            return "Unknown"
        
        if self.audio_sample_rate >= 48000:
            return "Excellent"
        elif self.audio_sample_rate >= 44100:
            return "High"
        elif self.audio_sample_rate >= 22050:
            return "Good"
        else:
            return "Fair"
    
    def estimate_transcription_time(self, model_complexity: str = "base") -> float:
        """Estimate transcription time based on video duration and model complexity"""
        complexity_multipliers = {
            "tiny": 0.05,
            "base": 0.1,
            "small": 0.15,
            "medium": 0.25,
            "large": 0.4
        }
        
        multiplier = complexity_multipliers.get(model_complexity, 0.1)
        return self.duration * multiplier
    
    def is_suitable_for_transcription(self) -> tuple[bool, List[str]]:
        """Check if video is suitable for transcription and return issues if any"""
        issues = []
        
        # Check if audio exists
        if not self.has_audio:
            issues.append("No audio track found")
        
        # Check audio quality
        if self.audio_sample_rate and self.audio_sample_rate < 16000:
            issues.append("Low audio sample rate may affect transcription quality")
        
        # Check duration
        if self.duration < 1:
            issues.append("Video too short (less than 1 second)")
        elif self.duration > 7200:  # 2 hours
            issues.append("Very long video - consider splitting into segments")
        
        # Check file size
        if self.file_size_mb > 2000:  # 2GB
            issues.append("Large file size may require more processing time")
        
        return len(issues) == 0, issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'file_info': {
                'path': self.file_path,
                'filename': self.filename,
                'extension': self.file_extension,
                'size_bytes': self.file_size,
                'size_mb': self.file_size_mb
            },
            'duration': {
                'seconds': self.duration,
                'minutes': self.duration_minutes
            },
            'video': {
                'codec': self.video_codec,
                'resolution': self.resolution_string,
                'width': self.video_width,
                'height': self.video_height,
                'fps': self.video_fps,
                'pixel_format': self.pixel_format,
                'bitrate': self.video_bitrate,
                'quality_level': self.get_quality_level(),
                'total_pixels': self.total_pixels,
                'aspect_ratio': self.aspect_ratio
            },
            'audio': {
                'has_audio': self.has_audio,
                'codec': self.audio_codec,
                'sample_rate': self.audio_sample_rate,
                'channels': self.audio_channels,
                'bitrate': self.audio_bitrate,
                'quality_level': self.get_audio_quality_level()
            },
            'format': {
                'name': self.format_name,
                'bitrate': self.bitrate
            },
            'analysis': {
                'analyzed_at': self.analyzed_at.isoformat(),
                'quality_assessment': self.quality_assessment
            }
        }
    
    @classmethod
    def from_ffmpeg_probe(cls, probe_data: Dict[str, Any], file_path: str) -> 'VideoMetadata':
        """Create VideoMetadata from ffmpeg probe data"""
        format_info = probe_data['format']
        
        # Find video and audio streams
        video_stream = next((s for s in probe_data['streams'] if s['codec_type'] == 'video'), None)
        audio_stream = next((s for s in probe_data['streams'] if s['codec_type'] == 'audio'), None)
        
        if not video_stream:
            raise ValueError("No video stream found in file")
        
        # Parse frame rate
        fps = 0.0
        if 'r_frame_rate' in video_stream:
            try:
                fps = eval(video_stream['r_frame_rate'])
            except:
                fps = 0.0
        
        return cls(
            file_path=file_path,
            file_size=int(format_info.get('size', 0)),
            duration=float(format_info['duration']),
            format_name=format_info['format_name'],
            bitrate=int(format_info.get('bit_rate', 0)),
            
            video_codec=video_stream['codec_name'],
            video_width=int(video_stream['width']),
            video_height=int(video_stream['height']),
            video_fps=fps,
            pixel_format=video_stream.get('pix_fmt'),
            video_bitrate=int(video_stream.get('bit_rate', 0)),
            
            has_audio=audio_stream is not None,
            audio_codec=audio_stream['codec_name'] if audio_stream else None,
            audio_sample_rate=int(audio_stream['sample_rate']) if audio_stream else None,
            audio_channels=int(audio_stream['channels']) if audio_stream else None,
            audio_bitrate=int(audio_stream.get('bit_rate', 0)) if audio_stream else 0
        )