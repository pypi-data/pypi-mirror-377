from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class TranscriptionStatus(Enum):
    """Enumeration of transcription statuses"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WordTimestamp:
    """Data model for word-level timestamps"""
    word: str
    start: float
    end: float
    probability: float = 1.0
    
    @property
    def duration(self) -> float:
        """Get word duration"""
        return self.end - self.start
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'word': self.word,
            'start': self.start,
            'end': self.end,
            'duration': self.duration,
            'probability': self.probability
        }


@dataclass
class TranscriptionSegment:
    """Data model for transcription segments"""
    id: int
    start: float
    end: float
    text: str
    words: List[WordTimestamp] = field(default_factory=list)
    
    # Whisper-specific fields
    seek: int = 0
    tokens: List[int] = field(default_factory=list)
    temperature: float = 0.0
    avg_logprob: float = 0.0
    compression_ratio: float = 0.0
    no_speech_prob: float = 0.0
    
    @property
    def duration(self) -> float:
        """Get segment duration"""
        return self.end - self.start
    
    @property
    def word_count(self) -> int:
        """Get number of words in segment"""
        return len(self.text.split())
    
    @property
    def average_word_confidence(self) -> float:
        """Get average confidence of words in segment"""
        if not self.words:
            return 1.0
        
        confidences = [word.probability for word in self.words]
        return sum(confidences) / len(confidences)
    
    @property
    def speaking_rate(self) -> float:
        """Get speaking rate (words per minute)"""
        if self.duration == 0:
            return 0.0
        return (self.word_count / self.duration) * 60
    
    def get_words_in_timerange(self, start_time: float, end_time: float) -> List[WordTimestamp]:
        """Get words within a specific time range"""
        return [word for word in self.words 
                if word.start >= start_time and word.end <= end_time]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'start': self.start,
            'end': self.end,
            'duration': self.duration,
            'text': self.text,
            'word_count': self.word_count,
            'speaking_rate': self.speaking_rate,
            'average_confidence': self.average_word_confidence,
            'words': [word.to_dict() for word in self.words],
            'whisper_metadata': {
                'seek': self.seek,
                'tokens': self.tokens,
                'temperature': self.temperature,
                'avg_logprob': self.avg_logprob,
                'compression_ratio': self.compression_ratio,
                'no_speech_prob': self.no_speech_prob
            }
        }


@dataclass
class TranscriptionMetadata:
    """Data model for transcription metadata"""
    total_duration: float = 0.0
    total_segments: int = 0
    total_words: int = 0
    average_confidence: float = 0.0
    speaking_rate: float = 0.0  # words per minute
    
    # Quality metrics
    silence_ratio: float = 0.0
    speech_clarity_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'duration': self.total_duration,
            'segments_count': self.total_segments,
            'words_count': self.total_words,
            'average_confidence': self.average_confidence,
            'speaking_rate': self.speaking_rate,
            'quality_metrics': {
                'silence_ratio': self.silence_ratio,
                'speech_clarity_score': self.speech_clarity_score
            }
        }


@dataclass
class ProcessingOptions:
    """Data model for transcription processing options"""
    model_size: str = "base"
    language: Optional[str] = None
    temperature: float = 0.0
    compression_ratio_threshold: float = 2.4
    logprob_threshold: float = -1.0
    no_speech_threshold: float = 0.6
    
    # Processing flags
    enable_word_timestamps: bool = True
    enable_post_processing: bool = True
    auto_punctuation: bool = True
    auto_capitalization: bool = True
    remove_filler_words: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model_settings': {
                'model_size': self.model_size,
                'language': self.language,
                'temperature': self.temperature,
                'compression_ratio_threshold': self.compression_ratio_threshold,
                'logprob_threshold': self.logprob_threshold,
                'no_speech_threshold': self.no_speech_threshold
            },
            'processing_flags': {
                'enable_word_timestamps': self.enable_word_timestamps,
                'enable_post_processing': self.enable_post_processing,
                'auto_punctuation': self.auto_punctuation,
                'auto_capitalization': self.auto_capitalization,
                'remove_filler_words': self.remove_filler_words
            }
        }


@dataclass
class TranscriptionResult:
    """Comprehensive data model for transcription results"""
    
    # Core transcription data
    text: str
    language_detected: str
    segments: List[TranscriptionSegment] = field(default_factory=list)
    metadata: TranscriptionMetadata = field(default_factory=TranscriptionMetadata)
    
    # Processing information
    status: TranscriptionStatus = TranscriptionStatus.PENDING
    source_file: str = ""
    audio_file: str = ""
    processing_options: ProcessingOptions = field(default_factory=ProcessingOptions)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Error information
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Output information
    output_files: Dict[str, str] = field(default_factory=dict)
    
    @property
    def processing_time(self) -> Optional[float]:
        """Get processing time in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_completed(self) -> bool:
        """Check if transcription is completed"""
        return self.status == TranscriptionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if transcription failed"""
        return self.status == TranscriptionStatus.FAILED
    
    @property
    def has_warnings(self) -> bool:
        """Check if transcription has warnings"""
        return len(self.warnings) > 0
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message"""
        self.warnings.append(warning)
    
    def mark_started(self) -> None:
        """Mark transcription as started"""
        self.status = TranscriptionStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def mark_completed(self) -> None:
        """Mark transcription as completed"""
        self.status = TranscriptionStatus.COMPLETED
        self.completed_at = datetime.now()
        self._calculate_metadata()
    
    def mark_failed(self, error_message: str) -> None:
        """Mark transcription as failed"""
        self.status = TranscriptionStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()
    
    def _calculate_metadata(self) -> None:
        """Calculate and update metadata based on segments"""
        if not self.segments:
            return
        
        # Calculate basic metrics
        self.metadata.total_segments = len(self.segments)
        self.metadata.total_duration = self.segments[-1].end if self.segments else 0.0
        
        # Calculate word count and confidence
        total_words = 0
        total_confidence = 0.0
        confidence_count = 0
        
        for segment in self.segments:
            total_words += segment.word_count
            
            if segment.words:
                for word in segment.words:
                    total_confidence += word.probability
                    confidence_count += 1
        
        self.metadata.total_words = total_words
        
        if confidence_count > 0:
            self.metadata.average_confidence = total_confidence / confidence_count
        
        # Calculate speaking rate
        if self.metadata.total_duration > 0:
            self.metadata.speaking_rate = (total_words / self.metadata.total_duration) * 60
    
    def get_text_by_timerange(self, start_time: float, end_time: float) -> str:
        """Get transcribed text within a specific time range"""
        relevant_segments = [
            segment for segment in self.segments
            if segment.start < end_time and segment.end > start_time
        ]
        
        return ' '.join(segment.text.strip() for segment in relevant_segments)
    
    def get_segments_by_timerange(self, start_time: float, end_time: float) -> List[TranscriptionSegment]:
        """Get segments within a specific time range"""
        return [
            segment for segment in self.segments
            if segment.start < end_time and segment.end > start_time
        ]
    
    def search_text(self, query: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for text in transcription and return matches with timestamps"""
        if not case_sensitive:
            query = query.lower()
        
        matches = []
        
        for segment in self.segments:
            text = segment.text if case_sensitive else segment.text.lower()
            
            if query in text:
                # Find the position of the match
                start_pos = text.find(query)
                
                matches.append({
                    'segment_id': segment.id,
                    'start_time': segment.start,
                    'end_time': segment.end,
                    'text': segment.text,
                    'match_position': start_pos,
                    'match_text': segment.text[start_pos:start_pos + len(query)]
                })
        
        return matches
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about the transcription"""
        if not self.segments:
            return {'error': 'No segments available'}
        
        # Segment length statistics
        segment_durations = [segment.duration for segment in self.segments]
        segment_word_counts = [segment.word_count for segment in self.segments]
        
        # Speaking rate per segment
        speaking_rates = [segment.speaking_rate for segment in self.segments if segment.duration > 0]
        
        # Confidence statistics
        confidences = []
        for segment in self.segments:
            if segment.words:
                confidences.extend([word.probability for word in segment.words])
        
        return {
            'segments': {
                'count': len(self.segments),
                'avg_duration': sum(segment_durations) / len(segment_durations),
                'min_duration': min(segment_durations),
                'max_duration': max(segment_durations),
                'avg_words_per_segment': sum(segment_word_counts) / len(segment_word_counts)
            },
            'speaking_rate': {
                'overall_wpm': self.metadata.speaking_rate,
                'avg_segment_wpm': sum(speaking_rates) / len(speaking_rates) if speaking_rates else 0,
                'min_wpm': min(speaking_rates) if speaking_rates else 0,
                'max_wpm': max(speaking_rates) if speaking_rates else 0
            },
            'confidence': {
                'overall_average': self.metadata.average_confidence,
                'min_confidence': min(confidences) if confidences else 0,
                'max_confidence': max(confidences) if confidences else 0,
                'low_confidence_words': len([c for c in confidences if c < 0.5])
            },
            'timing': {
                'total_duration': self.metadata.total_duration,
                'processing_time': self.processing_time,
                'processing_ratio': self.processing_time / self.metadata.total_duration if self.processing_time and self.metadata.total_duration > 0 else None
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to comprehensive dictionary"""
        return {
            'transcription': {
                'text': self.text,
                'language': self.language_detected,
                'segments': [segment.to_dict() for segment in self.segments]
            },
            'metadata': self.metadata.to_dict(),
            'processing': {
                'status': self.status.value,
                'options': self.processing_options.to_dict(),
                'source_file': self.source_file,
                'audio_file': self.audio_file,
                'created_at': self.created_at.isoformat(),
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'processing_time': self.processing_time,
                'error_message': self.error_message,
                'warnings': self.warnings
            },
            'outputs': self.output_files,
            'statistics': self.get_statistics()
        }
    
    @classmethod
    def from_whisper_result(cls, whisper_result: Dict[str, Any], source_file: str = "", audio_file: str = "", options: ProcessingOptions = None) -> 'TranscriptionResult':
        """Create TranscriptionResult from Whisper output"""
        
        # Create segments
        segments = []
        for segment_data in whisper_result.get('segments', []):
            words = []
            
            # Process word timestamps if available
            if 'words' in segment_data:
                for word_data in segment_data['words']:
                    word = WordTimestamp(
                        word=word_data.get('word', ''),
                        start=word_data.get('start', 0),
                        end=word_data.get('end', 0),
                        probability=word_data.get('probability', 1.0)
                    )
                    words.append(word)
            
            segment = TranscriptionSegment(
                id=segment_data.get('id', 0),
                start=segment_data.get('start', 0),
                end=segment_data.get('end', 0),
                text=segment_data.get('text', '').strip(),
                words=words,
                seek=segment_data.get('seek', 0),
                tokens=segment_data.get('tokens', []),
                temperature=segment_data.get('temperature', 0.0),
                avg_logprob=segment_data.get('avg_logprob', 0.0),
                compression_ratio=segment_data.get('compression_ratio', 0.0),
                no_speech_prob=segment_data.get('no_speech_prob', 0.0)
            )
            segments.append(segment)
        
        # Create result
        result = cls(
            text=whisper_result.get('text', '').strip(),
            language_detected=whisper_result.get('language', 'unknown'),
            segments=segments,
            source_file=source_file,
            audio_file=audio_file,
            processing_options=options or ProcessingOptions()
        )
        
        result.mark_completed()
        return result