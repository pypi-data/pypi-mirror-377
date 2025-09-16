import re
from typing import Dict, Any, List
from .base_agent import BaseTranscriptionAgent


class ProcessorAgent(BaseTranscriptionAgent):
    """Agent responsible for processing and improving transcription text"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Procesador de Texto",
            description="Procesa y mejora el texto de transcripción con puntuación, formato y corrección de errores",
            config=config
        )
        
        # Processing configuration
        self.auto_punctuation = config.get('auto_punctuation', True) if config else True
        self.auto_capitalization = config.get('auto_capitalization', True) if config else True
        self.remove_filler_words = config.get('remove_filler_words', False) if config else False
        self.language = config.get('language', 'en') if config else 'en'
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process transcription text"""
        transcription_data = input_data.get('transcription')
        
        if not transcription_data:
            raise ValueError("transcription data is required")
        
        try:
            processed_data = transcription_data.copy()
            
            # Process main text
            processed_data['text'] = self._process_text(transcription_data['text'])
            
            # Process segments
            processed_segments = []
            for segment in transcription_data['segments']:
                processed_segment = segment.copy()
                processed_segment['text'] = self._process_text(segment['text'])
                processed_segments.append(processed_segment)
            
            processed_data['segments'] = processed_segments
            
            # Add processing metadata
            processing_info = {
                'auto_punctuation': self.auto_punctuation,
                'auto_capitalization': self.auto_capitalization,
                'remove_filler_words': self.remove_filler_words,
                'language': self.language
            }
            
            # Store in memory for other agents
            self.set_memory('last_processed', processed_data)
            self.set_memory('processing_info', processing_info)
            
            return {
                'status': 'success',
                'processed_transcription': processed_data,
                'processing_info': processing_info,
                'agent': self.name
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'agent': self.name
            }
    
    def _process_text(self, text: str) -> str:
        """Apply text processing rules"""
        if not text:
            return text
        
        processed_text = text.strip()
        
        # Remove filler words if enabled
        if self.remove_filler_words:
            processed_text = self._remove_filler_words(processed_text)
        
        # Add punctuation if enabled
        if self.auto_punctuation:
            processed_text = self._add_punctuation(processed_text)
        
        # Apply capitalization if enabled
        if self.auto_capitalization:
            processed_text = self._apply_capitalization(processed_text)
        
        # Clean up extra spaces
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        return processed_text
    
    def _remove_filler_words(self, text: str) -> str:
        """Remove common filler words"""
        filler_words = {
            'en': ['um', 'uh', 'ah', 'er', 'hmm', 'like', 'you know', 'basically', 'actually'],
            'es': ['eh', 'este', 'pues', 'bueno', 'o sea', 'digamos', 'verdad'],
            'fr': ['euh', 'ben', 'quoi', 'enfin', 'donc', 'voilà'],
        }
        
        words_to_remove = filler_words.get(self.language, filler_words['en'])
        
        for filler in words_to_remove:
            # Remove filler words (case insensitive)
            pattern = r'\b' + re.escape(filler) + r'\b'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def _add_punctuation(self, text: str) -> str:
        """Add basic punctuation based on patterns"""
        # Add periods at the end if missing
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Add commas before common conjunctions
        text = re.sub(r'\s+(and|but|or|so|yet)\s+', r', \1 ', text, flags=re.IGNORECASE)
        
        # Add question marks for question patterns
        question_patterns = [
            r'\b(what|where|when|why|how|who|which|can|could|would|will|is|are|do|does|did)\b.*\?*$'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, text, re.IGNORECASE) and not text.endswith('?'):
                text = text.rstrip('.') + '?'
                break
        
        return text
    
    def _apply_capitalization(self, text: str) -> str:
        """Apply proper capitalization"""
        if not text:
            return text
        
        # Capitalize first letter
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Capitalize after periods, question marks, exclamation marks
        text = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        # Capitalize proper nouns (basic implementation)
        proper_nouns = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                       'january', 'february', 'march', 'april', 'may', 'june',
                       'july', 'august', 'september', 'october', 'november', 'december']
        
        for noun in proper_nouns:
            pattern = r'\b' + noun + r'\b'
            text = re.sub(pattern, noun.capitalize(), text, flags=re.IGNORECASE)
        
        return text
    
    def add_timestamps_to_text(self, transcription_data: Dict[str, Any], format_type: str = 'srt') -> str:
        """Add timestamps to text in specified format"""
        if format_type == 'srt':
            return self._format_as_srt(transcription_data)
        elif format_type == 'vtt':
            return self._format_as_vtt(transcription_data)
        else:
            return transcription_data.get('text', '')
    
    def _format_as_srt(self, transcription_data: Dict[str, Any]) -> str:
        """Format transcription as SRT subtitles"""
        srt_content = []
        
        for i, segment in enumerate(transcription_data['segments'], 1):
            start_time = self._seconds_to_srt_time(segment['start'])
            end_time = self._seconds_to_srt_time(segment['end'])
            
            srt_content.append(f"{i}")
            srt_content.append(f"{start_time} --> {end_time}")
            srt_content.append(segment['text'])
            srt_content.append("")
        
        return '\n'.join(srt_content)
    
    def _format_as_vtt(self, transcription_data: Dict[str, Any]) -> str:
        """Format transcription as WebVTT subtitles"""
        vtt_content = ["WEBVTT", ""]
        
        for segment in transcription_data['segments']:
            start_time = self._seconds_to_vtt_time(segment['start'])
            end_time = self._seconds_to_vtt_time(segment['end'])
            
            vtt_content.append(f"{start_time} --> {end_time}")
            vtt_content.append(segment['text'])
            vtt_content.append("")
        
        return '\n'.join(vtt_content)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convert seconds to VTT time format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"