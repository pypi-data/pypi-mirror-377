import asyncio
from typing import Dict, Any, List, Optional
from .base_agent import BaseTranscriptionAgent
from .analyzer_agent import AnalyzerAgent
from .transcriber_agent import TranscriberAgent
from .processor_agent import ProcessorAgent
from .formatter_agent import FormatterAgent


class CoordinatorAgent(BaseTranscriptionAgent):
    """Main coordinator agent that orchestrates the entire transcription workflow"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="Workflow Coordinator",
            description="Coordinates the entire video transcription workflow across all specialized agents",
            config=config
        )
        
        # Initialize specialized agents
        self.analyzer = AnalyzerAgent(config.get('analyzer', {}) if config else {})
        self.transcriber = TranscriberAgent(config.get('transcriber', {}) if config else {})
        self.processor = ProcessorAgent(config.get('processor', {}) if config else {})
        self.formatter = FormatterAgent(config.get('formatter', {}) if config else {})
        
        # Workflow configuration
        self.enable_processing = config.get('enable_processing', True) if config else True
        self.output_formats = config.get('output_formats', ['txt', 'srt']) if config else ['txt', 'srt']
        
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete transcription workflow"""
        video_path = input_data.get('video_path')
        output_name = input_data.get('output_name', 'transcription')
        
        if not video_path:
            raise ValueError("video_path is required")
        
        workflow_results = {
            'video_path': video_path,
            'output_name': output_name,
            'steps': {},
            'final_outputs': {},
            'errors': []
        }
        
        try:
            # Step 1: Analyze video
            print("🔍 Analyzing video file...")
            analysis_result = await self.analyzer.execute({'video_path': video_path})
            workflow_results['steps']['analysis'] = analysis_result
            
            if analysis_result['status'] != 'success':
                workflow_results['errors'].append(f"Analysis failed: {analysis_result.get('error')}")
                return workflow_results
            
            metadata = analysis_result['metadata']
            print(f"✅ Video analyzed: {metadata['duration']:.2f}s, {metadata['video_resolution']}")
            
            # Step 2: Extract and transcribe audio
            print("🎵 Extracting audio and transcribing...")
            
            # First, extract audio from video
            from services.audio_service import AudioService
            audio_service = AudioService()
            audio_path = await audio_service.extract_audio(video_path)
            
            # Then transcribe
            transcribe_params = {
                'audio_path': audio_path,
                'metadata': metadata
            }
            
            # Add language parameter if provided
            if 'language' in input_data:
                transcribe_params['language'] = input_data['language']
            
            transcription_result = await self.transcriber.execute(transcribe_params)
            workflow_results['steps']['transcription'] = transcription_result
            
            if transcription_result['status'] != 'success':
                workflow_results['errors'].append(f"Transcription failed: {transcription_result.get('error')}")
                return workflow_results
            
            transcription_data = transcription_result['transcription']
            print(f"✅ Transcription completed: {len(transcription_data['segments'])} segments")
            
            # Step 3: Process transcription (optional)
            if self.enable_processing:
                print("📝 Processing transcription text...")
                processing_result = await self.processor.execute({
                    'transcription': transcription_data
                })
                workflow_results['steps']['processing'] = processing_result
                
                if processing_result['status'] == 'success':
                    transcription_data = processing_result['processed_transcription']
                    print("✅ Text processing completed")
                else:
                    workflow_results['errors'].append(f"Processing failed: {processing_result.get('error')}")
                    # Continue with unprocessed transcription
            
            # Step 4: Format outputs
            print(f"📄 Formatting outputs: {', '.join(self.output_formats)}")
            formatting_result = await self.formatter.execute({
                'transcription': transcription_data,
                'formats': self.output_formats,
                'output_name': output_name
            })
            workflow_results['steps']['formatting'] = formatting_result
            
            if formatting_result['status'] == 'success':
                workflow_results['final_outputs'] = formatting_result['output_files']
                print("✅ All outputs generated successfully!")
            else:
                workflow_results['errors'].append(f"Formatting failed: {formatting_result.get('error')}")
            
            # Clean up temporary audio file
            audio_service.cleanup_temp_file(audio_path)
            
            # Store complete workflow results in memory
            self.set_memory('last_workflow', workflow_results)
            
            return workflow_results
            
        except Exception as e:
            workflow_results['errors'].append(f"Workflow error: {str(e)}")
            return workflow_results
    
    async def execute_batch(self, video_files: List[str], base_output_name: str = "transcription") -> Dict[str, Any]:
        """Execute transcription workflow for multiple video files"""
        batch_results = {
            'total_files': len(video_files),
            'completed': 0,
            'failed': 0,
            'results': {},
            'errors': []
        }
        
        for i, video_path in enumerate(video_files):
            try:
                print(f"\n📹 Processing video {i+1}/{len(video_files)}: {video_path}")
                
                # Generate unique output name for each file
                import os
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                output_name = f"{base_output_name}_{video_name}"
                
                # Execute workflow for this video
                result = await self.execute({
                    'video_path': video_path,
                    'output_name': output_name
                })
                
                batch_results['results'][video_path] = result
                
                if result.get('errors'):
                    batch_results['failed'] += 1
                    batch_results['errors'].extend(result['errors'])
                else:
                    batch_results['completed'] += 1
                
            except Exception as e:
                batch_results['failed'] += 1
                batch_results['errors'].append(f"Error processing {video_path}: {str(e)}")
                batch_results['results'][video_path] = {'error': str(e)}
        
        print(f"\n🎉 Batch processing completed: {batch_results['completed']} successful, {batch_results['failed']} failed")
        
        return batch_results
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get status of the last workflow execution"""
        last_workflow = self.get_memory('last_workflow')
        
        if not last_workflow:
            return {'status': 'no_workflow_executed'}
        
        completed_steps = sum(1 for step in last_workflow['steps'].values() 
                            if step.get('status') == 'success')
        total_steps = len(last_workflow['steps'])
        
        return {
            'video_path': last_workflow.get('video_path'),
            'completed_steps': completed_steps,
            'total_steps': total_steps,
            'progress_percentage': (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            'errors': last_workflow.get('errors', []),
            'final_outputs': last_workflow.get('final_outputs', {}),
            'status': 'completed' if completed_steps == total_steps and not last_workflow.get('errors') else 'partial'
        }
    
    def configure_workflow(self, config: Dict[str, Any]) -> None:
        """Configure workflow settings"""
        if 'enable_processing' in config:
            self.enable_processing = config['enable_processing']
        
        if 'output_formats' in config:
            self.output_formats = config['output_formats']
        
        # Update agent configurations
        if 'transcriber' in config:
            self.transcriber.config.update(config['transcriber'])
            # Reload model if model_size changed
            if 'model_size' in config['transcriber']:
                self.transcriber.change_model(config['transcriber']['model_size'])
        
        if 'processor' in config:
            self.processor.config.update(config['processor'])
        
        if 'formatter' in config:
            self.formatter.config.update(config['formatter'])
    
    def get_agents_info(self) -> Dict[str, Any]:
        """Get information about all agents"""
        return {
            'analyzer': {
                'name': self.analyzer.name,
                'description': self.analyzer.description,
                'supported_formats': self.analyzer.supported_formats
            },
            'transcriber': {
                'name': self.transcriber.name,
                'description': self.transcriber.description,
                'model_size': self.transcriber.model_size,
                'language': self.transcriber.language
            },
            'processor': {
                'name': self.processor.name,
                'description': self.processor.description,
                'auto_punctuation': self.processor.auto_punctuation,
                'auto_capitalization': self.processor.auto_capitalization
            },
            'formatter': {
                'name': self.formatter.name,
                'description': self.formatter.description,
                'supported_formats': self.formatter.supported_formats,
                'output_directory': self.formatter.output_directory
            }
        }