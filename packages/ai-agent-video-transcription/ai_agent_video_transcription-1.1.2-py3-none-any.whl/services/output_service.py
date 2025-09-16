import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class OutputService:
    """Service for managing output files and formats"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.base_output_dir = self.config.get('output_directory', './output')
        self.supported_formats = ['txt', 'srt', 'vtt', 'json', 'csv', 'docx']
        
        # Ensure output directory exists
        os.makedirs(self.base_output_dir, exist_ok=True)
    
    def save_transcription(self, transcription_data: Dict[str, Any], output_name: str, formats: List[str] = None) -> Dict[str, str]:
        """Save transcription in multiple formats"""
        formats = formats or ['txt']
        output_files = {}
        
        # Create subdirectory for this transcription
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = os.path.join(self.base_output_dir, f"{output_name}_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        
        for format_type in formats:
            if format_type not in self.supported_formats:
                print(f"Warning: Unsupported format '{format_type}' skipped")
                continue
            
            try:
                content = self._format_content(transcription_data, format_type)
                file_path = self._save_file(content, output_dir, output_name, format_type)
                output_files[format_type] = file_path
                
            except Exception as e:
                print(f"Error saving {format_type} format: {e}")
        
        # Save metadata file
        metadata_path = self._save_metadata(transcription_data, output_dir, output_name)
        output_files['metadata'] = metadata_path
        
        return output_files
    
    def _format_content(self, transcription_data: Dict[str, Any], format_type: str) -> str:
        """Format transcription content according to specified format"""
        
        if format_type == 'txt':
            return self._format_as_txt(transcription_data)
        elif format_type == 'srt':
            return self._format_as_srt(transcription_data)
        elif format_type == 'vtt':
            return self._format_as_vtt(transcription_data)
        elif format_type == 'json':
            return self._format_as_json(transcription_data)
        elif format_type == 'csv':
            return self._format_as_csv(transcription_data)
        elif format_type == 'docx':
            return self._format_as_docx(transcription_data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _format_as_txt(self, data: Dict[str, Any]) -> str:
        """Format as plain text"""
        lines = []
        
        # Header
        lines.append("VIDEO TRANSCRIPTION")
        lines.append("=" * 50)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if 'audio_path' in data:
            lines.append(f"Source: {data['audio_path']}")
        
        if 'language_detected' in data:
            lines.append(f"Language: {data['language_detected']}")
        
        if 'metadata' in data:
            metadata = data['metadata']
            lines.append(f"Duration: {metadata.get('total_duration', 0):.2f} seconds")
            lines.append(f"Segments: {metadata.get('total_segments', 0)}")
            
            if metadata.get('avg_confidence'):
                lines.append(f"Average Confidence: {metadata['avg_confidence']:.2%}")
        
        lines.append("=" * 50)
        lines.append("")
        
        # Main text
        lines.append("TRANSCRIPTION:")
        lines.append("-" * 20)
        lines.append("")
        lines.append(data.get('text', ''))
        
        # Detailed segments (optional)
        if data.get('segments') and len(data['segments']) > 1:
            lines.append("")
            lines.append("")
            lines.append("DETAILED SEGMENTS:")
            lines.append("-" * 30)
            lines.append("")
            
            for segment in data['segments']:
                start_time = self._seconds_to_readable_time(segment['start'])
                end_time = self._seconds_to_readable_time(segment['end'])
                lines.append(f"[{start_time} - {end_time}] {segment['text'].strip()}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def _format_as_srt(self, data: Dict[str, Any]) -> str:
        """Format as SRT subtitles"""
        srt_lines = []
        
        for i, segment in enumerate(data.get('segments', []), 1):
            start_time = self._seconds_to_srt_time(segment['start'])
            end_time = self._seconds_to_srt_time(segment['end'])
            
            srt_lines.append(str(i))
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(segment['text'].strip())
            srt_lines.append("")
        
        return '\n'.join(srt_lines)
    
    def _format_as_vtt(self, data: Dict[str, Any]) -> str:
        """Format as WebVTT"""
        vtt_lines = ["WEBVTT", ""]
        
        # Add metadata as notes
        if 'language_detected' in data:
            vtt_lines.append(f"NOTE Language: {data['language_detected']}")
        
        if 'metadata' in data and data['metadata'].get('total_duration'):
            vtt_lines.append(f"NOTE Duration: {data['metadata']['total_duration']:.2f}s")
        
        vtt_lines.append("")
        
        for segment in data.get('segments', []):
            start_time = self._seconds_to_vtt_time(segment['start'])
            end_time = self._seconds_to_vtt_time(segment['end'])
            
            vtt_lines.append(f"{start_time} --> {end_time}")
            vtt_lines.append(segment['text'].strip())
            vtt_lines.append("")
        
        return '\n'.join(vtt_lines)
    
    def _format_as_json(self, data: Dict[str, Any]) -> str:
        """Format as JSON"""
        output_data = {
            'transcription': {
                'text': data.get('text', ''),
                'language': data.get('language_detected', 'unknown'),
                'segments': data.get('segments', []),
                'metadata': data.get('metadata', {})
            },
            'processing_info': {
                'timestamp': datetime.now().isoformat(),
                'model_used': data.get('model_used', 'unknown'),
                'audio_source': data.get('audio_path', ''),
                'options': data.get('options', {})
            }
        }
        
        return json.dumps(output_data, indent=2, ensure_ascii=False)
    
    def _format_as_csv(self, data: Dict[str, Any]) -> str:
        """Format as CSV"""
        csv_lines = []
        
        # Header
        csv_lines.append("segment_id,start_time,end_time,duration,text,confidence")
        
        for segment in data.get('segments', []):
            duration = segment['end'] - segment['start']
            text = segment['text'].strip().replace('"', '""').replace('\n', ' ')
            
            # Calculate average confidence from words if available
            confidence = 1.0
            if segment.get('words'):
                word_confidences = [w.get('probability', 1.0) for w in segment['words']]
                confidence = sum(word_confidences) / len(word_confidences) if word_confidences else 1.0
            
            csv_lines.append(
                f"{segment['id']},{segment['start']:.3f},{segment['end']:.3f},"
                f"{duration:.3f},\"{text}\",{confidence:.3f}"
            )
        
        return '\n'.join(csv_lines)
    
    def _format_as_docx(self, data: Dict[str, Any]) -> str:
        """Format as structured document text (for DOCX conversion)"""
        lines = []
        
        # Title
        lines.append("VIDEO TRANSCRIPTION DOCUMENT")
        lines.append("=" * 40)
        lines.append("")
        
        # Metadata section
        lines.append("DOCUMENT INFORMATION")
        lines.append("-" * 25)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if 'audio_path' in data:
            lines.append(f"Source File: {Path(data['audio_path']).name}")
        
        lines.append(f"Language: {data.get('language_detected', 'Unknown')}")
        
        if 'metadata' in data:
            metadata = data['metadata']
            duration_min = metadata.get('total_duration', 0) / 60
            lines.append(f"Duration: {duration_min:.1f} minutes")
            lines.append(f"Total Segments: {metadata.get('total_segments', 0)}")
            lines.append(f"Word Count: {metadata.get('words_count', 0)}")
            
            if metadata.get('avg_confidence'):
                lines.append(f"Average Confidence: {metadata['avg_confidence']:.1%}")
        
        lines.append("")
        lines.append("")
        
        # Full transcription
        lines.append("FULL TRANSCRIPTION")
        lines.append("-" * 20)
        lines.append("")
        lines.append(data.get('text', ''))
        lines.append("")
        lines.append("")
        
        # Timestamped segments
        lines.append("TIMESTAMPED SEGMENTS")
        lines.append("-" * 25)
        lines.append("")
        
        for segment in data.get('segments', []):
            start_time = self._seconds_to_readable_time(segment['start'])
            end_time = self._seconds_to_readable_time(segment['end'])
            
            lines.append(f"[{start_time} - {end_time}]")
            lines.append(segment['text'].strip())
            lines.append("")
        
        return '\n'.join(lines)
    
    def _save_file(self, content: str, output_dir: str, base_name: str, format_type: str) -> str:
        """Save content to file"""
        filename = f"{base_name}.{format_type}"
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def _save_metadata(self, transcription_data: Dict[str, Any], output_dir: str, base_name: str) -> str:
        """Save metadata file"""
        metadata = {
            'transcription_info': {
                'source_file': transcription_data.get('audio_path', ''),
                'model_used': transcription_data.get('model_used', ''),
                'language_detected': transcription_data.get('language_detected', ''),
                'processing_options': transcription_data.get('options', {}),
                'timestamp': transcription_data.get('timestamp', datetime.now().isoformat())
            },
            'statistics': transcription_data.get('metadata', {}),
            'quality_metrics': {
                'total_segments': len(transcription_data.get('segments', [])),
                'avg_segment_length': self._calculate_avg_segment_length(transcription_data),
                'text_length': len(transcription_data.get('text', ''))
            }
        }
        
        metadata_path = os.path.join(output_dir, f"{base_name}_metadata.json")
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return metadata_path
    
    def _calculate_avg_segment_length(self, data: Dict[str, Any]) -> float:
        """Calculate average segment length in seconds"""
        segments = data.get('segments', [])
        if not segments:
            return 0.0
        
        total_duration = sum(segment['end'] - segment['start'] for segment in segments)
        return total_duration / len(segments)
    
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
    
    def _seconds_to_readable_time(self, seconds: float) -> str:
        """Convert seconds to readable time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def list_output_files(self, pattern: str = "*") -> List[Dict[str, Any]]:
        """List output files matching pattern"""
        files = []
        
        for root, dirs, filenames in os.walk(self.base_output_dir):
            for filename in filenames:
                if pattern == "*" or pattern in filename:
                    file_path = os.path.join(root, filename)
                    file_stat = os.stat(file_path)
                    
                    files.append({
                        'path': file_path,
                        'name': filename,
                        'size': file_stat.st_size,
                        'created': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
        
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up output files older than specified days"""
        import time
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        removed_count = 0
        
        for root, dirs, files in os.walk(self.base_output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except Exception as e:
                        print(f"Failed to remove {file_path}: {e}")
            
            # Remove empty directories
            if not os.listdir(root) and root != self.base_output_dir:
                try:
                    os.rmdir(root)
                except Exception:
                    pass
        
        return removed_count
    
    def get_output_summary(self) -> Dict[str, Any]:
        """Get summary of output directory"""
        total_files = 0
        total_size = 0
        format_counts = {}
        
        for root, dirs, files in os.walk(self.base_output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                total_files += 1
                total_size += os.path.getsize(file_path)
                
                # Count by format
                ext = Path(file).suffix.lower()
                format_counts[ext] = format_counts.get(ext, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'format_distribution': format_counts,
            'output_directory': self.base_output_dir
        }