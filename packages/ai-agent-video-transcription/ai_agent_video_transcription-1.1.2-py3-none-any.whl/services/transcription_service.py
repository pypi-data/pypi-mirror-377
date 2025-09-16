import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import whisper


class TranscriptionService:
    """Service for managing transcription operations and history"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.history_file = self.config.get('history_file', 'transcription_history.json')
        self.models_cache = {}
        
        # Default configuration
        self.default_model = self.config.get('default_model', 'base')
        self.default_language = self.config.get('default_language', None)
        
    def load_model(self, model_size: str = None) -> whisper.Whisper:
        """Load and cache Whisper model"""
        model_size = model_size or self.default_model
        
        if model_size not in self.models_cache:
            try:
                self.models_cache[model_size] = whisper.load_model(model_size)
                print(f"Loaded Whisper model: {model_size}")
            except Exception as e:
                raise RuntimeError(f"Failed to load Whisper model '{model_size}': {e}")
        
        return self.models_cache[model_size]
    
    def transcribe_audio(self, audio_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transcribe audio file with specified options"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        options = options or {}
        model_size = options.get('model_size', self.default_model)
        language = options.get('language', self.default_language)
        
        try:
            # Load model
            model = self.load_model(model_size)
            
            # Transcription options
            transcribe_options = {
                'language': language,
                'verbose': options.get('verbose', True),
                'word_timestamps': options.get('word_timestamps', True),
                'temperature': options.get('temperature', 0.0),
                'compression_ratio_threshold': options.get('compression_ratio_threshold', 2.4),
                'logprob_threshold': options.get('logprob_threshold', -1.0),
                'no_speech_threshold': options.get('no_speech_threshold', 0.6),
            }
            
            # Remove None values
            transcribe_options = {k: v for k, v in transcribe_options.items() if v is not None}
            
            # Perform transcription
            result = model.transcribe(audio_path, **transcribe_options)
            
            # Process and structure the result
            transcription_result = self._process_transcription_result(result, audio_path, options)
            
            # Save to history
            self._save_to_history(transcription_result)
            
            return transcription_result
            
        except Exception as e:
            error_result = {
                'status': 'error',
                'error': str(e),
                'audio_path': audio_path,
                'timestamp': datetime.now().isoformat(),
                'options': options
            }
            self._save_to_history(error_result)
            raise RuntimeError(f"Transcription failed: {str(e)}")
    
    def _process_transcription_result(self, whisper_result: Dict[str, Any], audio_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw Whisper result into structured format"""
        
        # Extract basic information
        result = {
            'status': 'success',
            'audio_path': audio_path,
            'timestamp': datetime.now().isoformat(),
            'options': options,
            'model_used': options.get('model_size', self.default_model),
            'language_detected': whisper_result.get('language', 'unknown'),
            'text': whisper_result.get('text', '').strip(),
            'segments': [],
            'metadata': {
                'total_duration': 0,
                'total_segments': 0,
                'avg_confidence': 0,
                'words_count': 0
            }
        }
        
        # Process segments
        total_confidence = 0
        confidence_count = 0
        words_count = 0
        
        for segment in whisper_result.get('segments', []):
            segment_data = {
                'id': segment.get('id', 0),
                'seek': segment.get('seek', 0),
                'start': segment.get('start', 0),
                'end': segment.get('end', 0),
                'text': segment.get('text', '').strip(),
                'tokens': segment.get('tokens', []),
                'temperature': segment.get('temperature', 0.0),
                'avg_logprob': segment.get('avg_logprob', 0.0),
                'compression_ratio': segment.get('compression_ratio', 0.0),
                'no_speech_prob': segment.get('no_speech_prob', 0.0),
                'words': []
            }
            
            # Process word-level timestamps if available
            if 'words' in segment:
                for word in segment['words']:
                    word_data = {
                        'word': word.get('word', ''),
                        'start': word.get('start', 0),
                        'end': word.get('end', 0),
                        'probability': word.get('probability', 1.0)
                    }
                    segment_data['words'].append(word_data)
                    
                    # Accumulate confidence statistics
                    if word_data['probability'] > 0:
                        total_confidence += word_data['probability']
                        confidence_count += 1
                        words_count += 1
            
            result['segments'].append(segment_data)
        
        # Calculate metadata
        if result['segments']:
            result['metadata']['total_duration'] = result['segments'][-1]['end']
            result['metadata']['total_segments'] = len(result['segments'])
            
            if confidence_count > 0:
                result['metadata']['avg_confidence'] = total_confidence / confidence_count
            
            result['metadata']['words_count'] = words_count
        
        return result
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(whisper.tokenizer.LANGUAGES.values())
    
    def get_available_models(self) -> List[str]:
        """Get list of available Whisper models"""
        return ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
    
    def estimate_transcription_time(self, audio_duration: float, model_size: str = None) -> float:
        """Estimate transcription processing time"""
        model_size = model_size or self.default_model
        
        # Time multipliers based on model size (approximate)
        time_multipliers = {
            'tiny': 0.05,
            'base': 0.1,
            'small': 0.15,
            'medium': 0.25,
            'large': 0.4,
            'large-v2': 0.4,
            'large-v3': 0.45
        }
        
        multiplier = time_multipliers.get(model_size, 0.2)
        return audio_duration * multiplier
    
    def batch_transcribe(self, audio_files: List[str], options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Transcribe multiple audio files"""
        results = []
        
        for i, audio_path in enumerate(audio_files):
            try:
                print(f"Transcribing file {i+1}/{len(audio_files)}: {os.path.basename(audio_path)}")
                result = self.transcribe_audio(audio_path, options)
                results.append(result)
                
            except Exception as e:
                error_result = {
                    'status': 'error',
                    'error': str(e),
                    'audio_path': audio_path,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(error_result)
        
        return results
    
    def get_transcription_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get transcription history"""
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            # Return most recent entries
            return history[-limit:]
            
        except Exception as e:
            print(f"Failed to load history: {e}")
            return []
    
    def clear_history(self) -> bool:
        """Clear transcription history"""
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
            return True
        except Exception as e:
            print(f"Failed to clear history: {e}")
            return False
    
    def _save_to_history(self, result: Dict[str, Any]) -> None:
        """Save transcription result to history"""
        try:
            history = []
            
            # Load existing history
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Add new result
            history.append(result)
            
            # Keep only last 100 entries
            if len(history) > 100:
                history = history[-100:]
            
            # Save updated history
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Failed to save to history: {e}")
    
    def get_model_info(self, model_size: str = None) -> Dict[str, Any]:
        """Get information about a Whisper model"""
        model_size = model_size or self.default_model
        
        model_info = {
            'tiny': {
                'parameters': '39 M',
                'vram_required': '~1 GB',
                'relative_speed': '~32x',
                'description': 'Fastest, lowest accuracy'
            },
            'base': {
                'parameters': '74 M',
                'vram_required': '~1 GB',
                'relative_speed': '~16x',
                'description': 'Good balance of speed and accuracy'
            },
            'small': {
                'parameters': '244 M',
                'vram_required': '~2 GB',
                'relative_speed': '~6x',
                'description': 'Better accuracy, moderate speed'
            },
            'medium': {
                'parameters': '769 M',
                'vram_required': '~5 GB',
                'relative_speed': '~2x',
                'description': 'High accuracy, slower'
            },
            'large': {
                'parameters': '1550 M',
                'vram_required': '~10 GB',
                'relative_speed': '~1x',
                'description': 'Highest accuracy, slowest'
            },
            'large-v2': {
                'parameters': '1550 M',
                'vram_required': '~10 GB',
                'relative_speed': '~1x',
                'description': 'Improved version of large model'
            },
            'large-v3': {
                'parameters': '1550 M',
                'vram_required': '~10 GB',
                'relative_speed': '~1x',
                'description': 'Latest and most accurate model'
            }
        }
        
        return model_info.get(model_size, {
            'parameters': 'Unknown',
            'vram_required': 'Unknown',
            'relative_speed': 'Unknown',
            'description': 'Model information not available'
        })
    
    def cleanup_models(self) -> None:
        """Clear model cache to free memory"""
        self.models_cache.clear()
        print("Model cache cleared")