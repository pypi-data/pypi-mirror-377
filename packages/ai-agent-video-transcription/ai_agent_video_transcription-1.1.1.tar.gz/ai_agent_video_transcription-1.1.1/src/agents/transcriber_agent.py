import whisper
import tempfile
import os
from typing import Dict, Any, Optional
from .base_agent import BaseTranscriptionAgent


class TranscriberAgent(BaseTranscriptionAgent):
    """Agent responsible for transcribing audio to text using Whisper"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Transcriptor de Audio",
            description="Transcribe audio de archivos de video a texto usando OpenAI Whisper",
            config=config
        )
        
        # Whisper model configuration
        self.model_size = config.get('model_size', 'base') if config else 'base'
        self.language = config.get('language', None) if config else None
        self.model = None
        
        # Load Whisper model
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            self.model = whisper.load_model(self.model_size)
            print(f"Loaded Whisper model: {self.model_size}")
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio from video file"""
        audio_path = input_data.get('audio_path')
        video_metadata = input_data.get('metadata', {})
        
        if not audio_path:
            raise ValueError("audio_path is required")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Get language from input_data or use default from config
            transcription_language = input_data.get('language', self.language)
            
            # Transcribe audio using Whisper
            result = self.model.transcribe(
                audio_path,
                language=transcription_language,
                verbose=True,
                word_timestamps=True
            )
            
            # Extract transcription data
            transcription_data = {
                'text': result['text'].strip(),
                'language': transcription_language or result['language'],  # Use forced language or detected
                'segments': [],
                'duration': video_metadata.get('duration', 0)
            }
            
            # Process segments with timestamps
            for segment in result['segments']:
                segment_data = {
                    'id': segment['id'],
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'words': []
                }
                
                # Add word-level timestamps if available
                if 'words' in segment:
                    for word in segment['words']:
                        word_data = {
                            'word': word['word'],
                            'start': word['start'],
                            'end': word['end'],
                            'probability': word.get('probability', 1.0)
                        }
                        segment_data['words'].append(word_data)
                
                transcription_data['segments'].append(segment_data)
            
            # Store in memory for other agents
            self.set_memory('last_transcription', transcription_data)
            
            return {
                'status': 'success',
                'transcription': transcription_data,
                'agent': self.name,
                'model_used': self.model_size
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'agent': self.name
            }
    
    def change_model(self, model_size: str) -> bool:
        """Change Whisper model size"""
        valid_models = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
        
        if model_size not in valid_models:
            raise ValueError(f"Invalid model size. Choose from: {valid_models}")
        
        try:
            self.model_size = model_size
            self._load_model()
            return True
        except Exception:
            return False
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return list(whisper.tokenizer.LANGUAGES.values())
    
    def estimate_accuracy(self, audio_quality: str, background_noise: str) -> float:
        """Estimate transcription accuracy based on audio quality"""
        base_accuracy = 0.95
        
        quality_factors = {
            'excellent': 1.0,
            'good': 0.95,
            'fair': 0.85,
            'poor': 0.70
        }
        
        noise_factors = {
            'none': 1.0,
            'low': 0.95,
            'medium': 0.85,
            'high': 0.70
        }
        
        quality_factor = quality_factors.get(audio_quality.lower(), 0.80)
        noise_factor = noise_factors.get(background_noise.lower(), 0.80)
        
        return base_accuracy * quality_factor * noise_factor