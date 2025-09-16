import json
import os
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseTranscriptionAgent


class FormatterAgent(BaseTranscriptionAgent):
    """Agent responsible for formatting transcription output in various formats"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Formateador de Salida",
            description="Formatea la salida de transcripción en varios formatos (SRT, VTT, TXT, JSON, etc.)",
            config=config
        )
        
        self.supported_formats = ['srt', 'vtt', 'txt', 'json', 'csv', 'docx']
        self.output_directory = config.get('output_directory', './output') if config else './output'
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format transcription in specified formats"""
        transcription_data = input_data.get('transcription')
        formats = input_data.get('formats', ['txt'])
        output_name = input_data.get('output_name', 'transcription')
        
        if not transcription_data:
            raise ValueError("transcription data is required")
        
        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)
        
        try:
            output_files = {}
            
            for format_type in formats:
                if format_type not in self.supported_formats:
                    continue
                
                output_content = self._format_transcription(transcription_data, format_type)
                file_path = self._save_output(output_content, format_type, output_name)
                output_files[format_type] = file_path
            
            # Store in memory for other agents
            self.set_memory('last_output_files', output_files)
            
            return {
                'status': 'success',
                'output_files': output_files,
                'agent': self.name
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'agent': self.name
            }
    
    def _format_transcription(self, transcription_data: Dict[str, Any], format_type: str) -> str:
        """Format transcription data according to specified format"""
        if format_type == 'srt':
            return self._format_as_srt(transcription_data)
        elif format_type == 'vtt':
            return self._format_as_vtt(transcription_data)
        elif format_type == 'txt':
            return self._format_as_txt(transcription_data)
        elif format_type == 'json':
            return self._format_as_json(transcription_data)
        elif format_type == 'csv':
            return self._format_as_csv(transcription_data)
        elif format_type == 'docx':
            return self._format_as_docx(transcription_data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _format_as_srt(self, transcription_data: Dict[str, Any]) -> str:
        """Format as SRT subtitles"""
        srt_content = []
        
        for i, segment in enumerate(transcription_data['segments'], 1):
            start_time = self._seconds_to_srt_time(segment['start'])
            end_time = self._seconds_to_srt_time(segment['end'])
            
            srt_content.extend([
                str(i),
                f"{start_time} --> {end_time}",
                segment['text'].strip(),
                ""
            ])
        
        return '\n'.join(srt_content)
    
    def _format_as_vtt(self, transcription_data: Dict[str, Any]) -> str:
        """Format as WebVTT subtitles"""
        vtt_content = ["WEBVTT", ""]
        
        for segment in transcription_data['segments']:
            start_time = self._seconds_to_vtt_time(segment['start'])
            end_time = self._seconds_to_vtt_time(segment['end'])
            
            vtt_content.extend([
                f"{start_time} --> {end_time}",
                segment['text'].strip(),
                ""
            ])
        
        return '\n'.join(vtt_content)
    
    def _format_as_txt(self, transcription_data: Dict[str, Any]) -> str:
        """Format as plain text"""
        header = f"Transcription\n"
        header += f"Duration: {transcription_data.get('duration', 0):.2f} seconds\n"
        header += f"Language: {transcription_data.get('language', 'Unknown')}\n"
        header += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += "=" * 50 + "\n\n"
        
        return header + transcription_data.get('text', '')
    
    def _format_as_json(self, transcription_data: Dict[str, Any]) -> str:
        """Format as JSON"""
        output_data = {
            'metadata': {
                'duration': transcription_data.get('duration', 0),
                'language': transcription_data.get('language', 'Unknown'),
                'generated_at': datetime.now().isoformat(),
                'agent': self.name
            },
            'transcription': {
                'text': transcription_data.get('text', ''),
                'segments': transcription_data.get('segments', [])
            }
        }
        
        return json.dumps(output_data, indent=2, ensure_ascii=False)
    
    def _format_as_csv(self, transcription_data: Dict[str, Any]) -> str:
        """Format as CSV"""
        csv_content = ["segment_id,start_time,end_time,duration,text"]
        
        for segment in transcription_data.get('segments', []):
            duration = segment['end'] - segment['start']
            text = segment['text'].strip().replace('"', '""')  # Escape quotes
            
            csv_content.append(
                f"{segment['id']},{segment['start']:.2f},{segment['end']:.2f},"
                f"{duration:.2f},\"{text}\""
            )
        
        return '\n'.join(csv_content)
    
    def _format_as_docx(self, transcription_data: Dict[str, Any]) -> str:
        """Format as DOCX (returns formatted text for now)"""
        # For a full DOCX implementation, you would use python-docx library
        # This is a simplified version that returns formatted text
        
        content = []
        content.append("TRANSCRIPTION DOCUMENT")
        content.append("=" * 30)
        content.append("")
        content.append(f"Duration: {transcription_data.get('duration', 0):.2f} seconds")
        content.append(f"Language: {transcription_data.get('language', 'Unknown')}")
        content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        content.append("CONTENT:")
        content.append("-" * 20)
        content.append("")
        
        # Add segments with timestamps
        for segment in transcription_data.get('segments', []):
            timestamp = f"[{self._seconds_to_readable_time(segment['start'])} - {self._seconds_to_readable_time(segment['end'])}]"
            content.append(f"{timestamp} {segment['text'].strip()}")
            content.append("")
        
        return '\n'.join(content)
    
    def _save_output(self, content: str, format_type: str, output_name: str) -> str:
        """Save formatted content to file"""
        filename = f"{output_name}.{format_type}"
        file_path = os.path.join(self.output_directory, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"
    
    def _seconds_to_vtt_time(self, seconds: float) -> str:
        """Convert seconds to VTT time format"""
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
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(file_path) if os.path.exists(file_path) else 0
    
    def generate_summary_report(self, transcription_data: Dict[str, Any], output_files: Dict[str, str]) -> str:
        """Generate a summary report of the transcription process"""
        report = []
        report.append("TRANSCRIPTION SUMMARY REPORT")
        report.append("=" * 40)
        report.append("")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Duration: {transcription_data.get('duration', 0):.2f} seconds")
        report.append(f"Language: {transcription_data.get('language', 'Unknown')}")
        report.append(f"Segments: {len(transcription_data.get('segments', []))}")
        report.append("")
        report.append("OUTPUT FILES:")
        report.append("-" * 20)
        
        for format_type, file_path in output_files.items():
            file_size = self.get_file_size(file_path)
            report.append(f"{format_type.upper()}: {file_path} ({file_size} bytes)")
        
        return '\n'.join(report)