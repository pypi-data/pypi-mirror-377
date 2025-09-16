"""
Interactive CLI for Video Transcription Agent
Similar to Claude/Gemini interface with command-based interaction
"""

import asyncio
import os
import sys
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

# Rich imports for beautiful CLI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

# Prompt toolkit for better input handling
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, PathCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.shortcuts import clear

# Internal imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.coordinator_agent import CoordinatorAgent
from memory.memory_manager import MemoryManager
from utils.config_loader import ConfigLoader


class InteractiveCLI:
    """Interactive command-line interface for the transcription agent"""
    
    def __init__(self):
        self.console = Console()
        self.memory = MemoryManager()
        self.coordinator = None
        self.config_loader = ConfigLoader()
        self.history = InMemoryHistory()
        self.running = True
        
        # Command completer - English commands only
        self.commands = [
            'transcribe', 'analyze', 'search', 'discovery', 'discover',
            'select', 'history', 'config', 'status', 'help', 'clear',
            'exit', 'quit'
        ]
        
        self.command_completer = WordCompleter(
            self.commands + ['/transcribe', '/analyze', '/search', '/discovery', '/select', '/help', '/exit']
        )
        
        # Storage for discovered videos
        self.discovered_videos = []
        self.supported_video_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.mkv']
        self._last_selected_video = None
        
        # Session info
        self.session_start = datetime.now()
        self.commands_executed = 0
        
        # Initialize agent
        self._init_agent()
    
    def _init_agent(self):
        """Initialize the coordinator agent"""
        try:
            with self.console.status("[bold green]Initializing transcription agent..."):
                config = self.config_loader.get_default_config()
                self.coordinator = CoordinatorAgent(config)
            
            self.console.print("✅ [bold green]Agent initialized successfully[/bold green]")
            
        except Exception as e:
            self.console.print(f"❌ [bold red]Error initializing agent: {e}[/bold red]")
            sys.exit(1)
    
    def _display_welcome(self):
        """Display welcome screen"""
        welcome_text = Text()
        welcome_text.append("🎬 ", style="bold blue")
        welcome_text.append("Video Transcription Agent", style="bold cyan")
        welcome_text.append(" v1.0", style="dim")
        
        subtitle = Text()
        subtitle.append("Powered by ", style="dim")
        subtitle.append("Whisper", style="bold blue")
        subtitle.append(" • ", style="dim")
        subtitle.append("ChromaDB", style="bold green")
        subtitle.append(" • ", style="dim")
        subtitle.append("PyAutoGen", style="bold magenta")
        
        panel = Panel(
            Align.center(welcome_text + "\n" + subtitle),
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
        
        # Show available agents
        self._show_agents_info()
        
        # Show main commands on startup
        self._display_main_commands()
        
        # Show quick help
        self.console.print("[dim]💡 Type 'help' to see all available commands[/dim]")
        self.console.print("[dim]💡 Use Tab to autocomplete commands and file paths[/dim]")
        self.console.print()
    
    def _display_main_commands(self):
        """Display main commands on startup"""
        main_commands_text = Text()
        main_commands_text.append("🚀 Main Commands:\n", style="bold yellow")
        
        main_commands = [
            ("discovery", "Find videos in current directory"),
            ("select <ID>", "Select a video from discovery results"),
            ("transcribe [file]", "Transcribe video file (always in Spanish)"),
            ("analyze [file]", "Analyze video metadata"),
            ("search <query>", "Search in saved transcriptions"),
            ("history", "Show transcription history"),
            ("status", "Show system status"),
            ("help", "Show all commands"),
            ("exit", "Exit the program")
        ]
        
        for command, description in main_commands:
            main_commands_text.append(f"  • {command:<15}", style="bold cyan")
            main_commands_text.append(f" - {description}\n", style="white")
        
        panel = Panel(main_commands_text, title="Quick Start", border_style="green")
        self.console.print(panel)
    
    def _show_agents_info(self):
        """Display available agents information"""
        try:
            agents_info = self.coordinator.get_agents_info()
            
            table = Table(title="🤖 Available Agents", show_header=True, header_style="bold magenta")
            table.add_column("Agent", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Status", style="green")
            
            for agent_name, agent_info in agents_info.items():
                table.add_row(
                    agent_info['name'],
                    agent_info['description'],
                    "✅ Active"
                )
            
            self.console.print(table)
            self.console.print()
            
        except Exception as e:
            self.console.print(f"❌ Error mostrando información de agentes: {e}")
    
    def _parse_command(self, user_input: str) -> tuple[str, List[str]]:
        """Parse user command and arguments"""
        if not user_input.strip():
            return "", []
        
        # Handle slash commands
        if user_input.startswith('/'):
            user_input = user_input[1:]
        
        parts = user_input.strip().split()
        command = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        return command, args
    
    async def _execute_transcribe_command(self, args: List[str]) -> None:
        """Execute transcription command"""
        if not args:
            # Check if there's a previously selected video
            if self._last_selected_video:
                video_path = self._last_selected_video
                self.console.print(f"🎯 [green]Using selected video: {os.path.basename(video_path)}[/green]")
            else:
                # Interactive file selection - async safe
                import asyncio
                loop = asyncio.get_event_loop()
                video_path = await loop.run_in_executor(
                    None, 
                    lambda: prompt(
                        "📹 Video file path: ",
                        completer=PathCompleter()
                    )
                )
        else:
            video_path = " ".join(args)
        
        if not video_path:
            self.console.print("❌ [red]Video path required[/red]")
            return
        
        if not os.path.exists(video_path):
            self.console.print(f"❌ [red]File not found: {video_path}[/red]")
            return
        
        # Ask for output name - async safe
        import asyncio
        loop = asyncio.get_event_loop()
        output_name = await loop.run_in_executor(
            None,
            lambda: prompt(
                "📝 Output name (optional): ",
                default=Path(video_path).stem
            )
        )
        
        # Execute transcription with progress
        start_time = time.time()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("[cyan]Transcribing video...", total=None)
                
                # Force Spanish language for transcription
                self.console.print("🌍 [cyan]Forcing Spanish language for transcription[/cyan]")
                
                result = await self.coordinator.execute({
                    'video_path': video_path,
                    'output_name': output_name,
                    'language': 'es'  # Force Spanish
                })
                
                progress.update(task, completed=True)
            
            execution_time = time.time() - start_time
            
            # Store in memory
            if result and not result.get('errors'):
                # Extract transcription data for memory storage
                transcription_data = self._extract_transcription_data(result)
                if transcription_data:
                    self.memory.store_transcription(
                        video_path=video_path,
                        transcription_data=transcription_data
                    )
                
                self.memory.store_command(
                    f"transcribe {video_path}",
                    "Transcription completed successfully",
                    execution_time
                )
                
                # Show results
                self._display_transcription_result(result, execution_time)
            else:
                error_msg = "; ".join(result.get('errors', ['Unknown error']))
                self.console.print(f"❌ [red]Transcription error: {error_msg}[/red]")
                self.memory.store_command(
                    f"transcribe {video_path}",
                    f"Error: {error_msg}",
                    execution_time
                )
                
        except Exception as e:
            self.console.print(f"❌ [red]Unexpected error: {e}[/red]")
    
    async def _execute_analyze_command(self, args: List[str]) -> None:
        """Execute video analysis command"""
        if not args:
            self.console.print("❌ [red]Video path required[/red]")
            return
        
        video_path = " ".join(args)
        
        if not os.path.exists(video_path):
            self.console.print(f"❌ [red]File not found: {video_path}[/red]")
            return
        
        # Execute analysis with progress
        start_time = time.time()
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("[cyan]Analyzing video...", total=None)
                
                # Execute analysis using the analyzer agent
                result = await self.coordinator.analyzer.execute({'video_path': video_path})
                
                progress.update(task, completed=True)
            
            execution_time = time.time() - start_time
            
            # Store command execution
            self.memory.store_command(
                f"analyze {video_path}",
                "Analysis completed successfully",
                execution_time
            )
            
            # Display analysis results
            self._display_analysis_result(result, execution_time)
            
        except Exception as e:
            self.console.print(f"❌ [red]Analysis error: {e}[/red]")
            self.memory.store_command(
                f"analyze {video_path}",
                f"Error: {e}",
                execution_time
            )
    
    def _display_analysis_result(self, result: Dict[str, Any], execution_time: float):
        """Display video analysis results"""
        if result.get('status') != 'success':
            error_msg = result.get('error', 'Unknown error')
            self.console.print(f"❌ [red]Analysis failed: {error_msg}[/red]")
            return
        
        metadata = result.get('metadata', {})
        
        # Create analysis panel
        panel_content = Text()
        panel_content.append("📊 Video Analysis Results\n\n", style="bold cyan")
        
        # Basic file info
        panel_content.append("📁 File Information:\n", style="bold yellow")
        panel_content.append(f"  • Name: {os.path.basename(metadata.get('file_path', 'Unknown'))}\n", style="white")
        panel_content.append(f"  • Size: {metadata.get('file_size_mb', 0):.1f} MB\n", style="white")
        panel_content.append(f"  • Duration: {metadata.get('duration', 0):.1f} seconds\n", style="white")
        panel_content.append(f"  • Format: {metadata.get('format', 'Unknown')}\n\n", style="white")
        
        # Video quality info
        panel_content.append("🎬 Video Quality:\n", style="bold green")
        panel_content.append(f"  • Resolution: {metadata.get('video_resolution', 'Unknown')}\n", style="white")
        panel_content.append(f"  • FPS: {metadata.get('fps', 0):.1f}\n", style="white")
        panel_content.append(f"  • Bitrate: {metadata.get('video_bitrate', 0):.0f} kbps\n", style="white")
        panel_content.append(f"  • Codec: {metadata.get('video_codec', 'Unknown')}\n\n", style="white")
        
        # Audio quality info
        panel_content.append("🎵 Audio Quality:\n", style="bold blue")
        panel_content.append(f"  • Sample Rate: {metadata.get('audio_sample_rate', 0)} Hz\n", style="white")
        panel_content.append(f"  • Channels: {metadata.get('audio_channels', 0)}\n", style="white")
        panel_content.append(f"  • Bitrate: {metadata.get('audio_bitrate', 0):.0f} kbps\n", style="white")
        panel_content.append(f"  • Codec: {metadata.get('audio_codec', 'Unknown')}\n\n", style="white")
        
        # Analysis summary
        panel_content.append("📈 Analysis Summary:\n", style="bold magenta")
        panel_content.append(f"  • Execution Time: {execution_time:.2f}s\n", style="white")
        panel_content.append(f"  • Quality Score: {metadata.get('quality_score', 'N/A')}\n", style="white")
        
        # Recommendations if available
        recommendations = metadata.get('recommendations', [])
        if recommendations:
            panel_content.append("\n💡 Recommendations:\n", style="bold yellow")
            for rec in recommendations:
                panel_content.append(f"  • {rec}\n", style="white")
        
        panel = Panel(
            panel_content,
            title="✅ Video Analysis Completed",
            border_style="green"
        )
        
        self.console.print(panel)
    
    def _extract_transcription_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract transcription data from result for memory storage"""
        try:
            # Try to get transcription from different possible locations in result
            transcription_data = result.get('steps', {}).get('transcription', {})
            if transcription_data and 'transcription' in transcription_data:
                whisper_result = transcription_data['transcription']
                
                # Extract text from segments
                segments = whisper_result.get('segments', [])
                transcription_text = " ".join(segment.get('text', '') for segment in segments)
                
                # Prepare data for memory storage
                memory_data = {
                    'text': transcription_text,
                    'language': whisper_result.get('language', 'es'),
                    'duration': whisper_result.get('duration', 0),
                    'model_used': 'whisper',
                    'segments': segments,
                    'metadata': {
                        'timestamp': time.time(),
                        'execution_time': result.get('execution_time', 0)
                    }
                }
                
                return memory_data
            
            # Alternative: check for direct text in result
            if 'transcription_text' in result:
                return {
                    'text': result['transcription_text'],
                    'language': 'es',
                    'duration': result.get('duration', 0),
                    'model_used': 'whisper',
                    'metadata': {
                        'timestamp': time.time(),
                        'execution_time': result.get('execution_time', 0)
                    }
                }
            
            return {}
        except Exception as e:
            self.console.print(f"⚠️ [yellow]Warning: Could not extract transcription data for memory storage: {e}[/yellow]")
            return {}
    
    def _display_transcription_result(self, result: Dict[str, Any], execution_time: float):
        """Display transcription results"""
        panel_content = Text()
        
        # Basic info
        transcription_data = result.get('steps', {}).get('transcription', {})
        if transcription_data.get('transcription'):
            segments = transcription_data['transcription'].get('segments', [])
            panel_content.append(f"📊 Segments processed: {len(segments)}\n", style="cyan")
            panel_content.append(f"⏱️  Execution time: {execution_time:.2f}s\n", style="yellow")
            
            # Language detection
            if transcription_data['transcription'].get('language'):
                panel_content.append(f"🌍 Language detected: {transcription_data['transcription']['language']}\n", style="green")
        
        # Output files
        outputs = result.get('final_outputs', {})
        if outputs:
            panel_content.append("\n📄 Generated files:\n", style="bold cyan")
            for format_type, file_path in outputs.items():
                panel_content.append(f"  • {format_type.upper()}: {file_path}\n", style="white")
        
        panel = Panel(
            panel_content,
            title="✅ Transcription Completed",
            border_style="green"
        )
        
        self.console.print(panel)
    
    async def _execute_search_command(self, args: List[str]) -> None:
        """Execute search command"""
        if not args:
            import asyncio
            loop = asyncio.get_event_loop()
            query = await loop.run_in_executor(None, lambda: prompt("🔍 Search in transcriptions: "))
        else:
            query = " ".join(args)
        
        if not query:
            self.console.print("❌ [red]Search query required[/red]")
            return
        
        try:
            with self.console.status("[bold green]Searching in history..."):
                results = self.memory.search_transcriptions(query, limit=5)
            
            if not results:
                self.console.print(f"🔍 [yellow]No results found for: '{query}'[/yellow]")
                return
            
            # Display results
            table = Table(title=f"🔍 Search results: '{query}'", show_header=True)
            table.add_column("Video", style="cyan")
            table.add_column("Similarity", style="green")
            table.add_column("Date", style="yellow")
            
            for result in results:
                similarity_percent = f"{result['similarity']*100:.1f}%"
                timestamp = result['metadata'].get('timestamp', 'Unknown')
                video_name = os.path.basename(result['video_path'])
                
                table.add_row(video_name, similarity_percent, timestamp)
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"❌ [red]Search error: {e}[/red]")
    
    def _search_videos_in_directory(self, directory: str = None) -> List[str]:
        """Search for video files in directory and subdirectories"""
        if directory is None:
            directory = os.getcwd()
        
        video_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in self.supported_video_extensions:
                        # Get file info
                        stat_info = os.stat(file_path)
                        file_size = stat_info.st_size
                        file_mtime = stat_info.st_mtime
                        
                        video_files.append({
                            'path': file_path,
                            'name': file,
                            'size': file_size,
                            'modified': file_mtime,
                            'extension': file_ext,
                            'relative_path': os.path.relpath(file_path, directory)
                        })
            
            # Sort by modification time (newest first)
            video_files.sort(key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            self.console.print(f"❌ [red]Error searching videos: {e}[/red]")
            return []
        
        return video_files
    
    async def _execute_discovery_command(self, args: List[str]) -> None:
        """Execute discovery command to find video files"""
        # Determine search directory
        if args:
            search_dir = " ".join(args)
            if not os.path.exists(search_dir):
                self.console.print(f"❌ [red]Directory not found: {search_dir}[/red]")
                return
        else:
            search_dir = os.getcwd()
        
        self.console.print(f"🔍 [cyan]Searching videos in: {search_dir}[/cyan]")
        
        with self.console.status("[bold green]Scanning directories..."):
            self.discovered_videos = self._search_videos_in_directory(search_dir)
        
        if not self.discovered_videos:
            self.console.print("📂 [yellow]No video files found[/yellow]")
            self.console.print(f"Supported formats: {', '.join(self.supported_video_extensions).upper()}")
            return
        
        # Display results
        self.console.print(f"\n🎬 [green]Found {len(self.discovered_videos)} video(s):[/green]")
        
        table = Table(title="Discovered Videos", show_header=True)
        table.add_column("ID", style="cyan", min_width=3)
        table.add_column("Name", style="green", min_width=20)
        table.add_column("Size", style="yellow", min_width=8)
        table.add_column("Relative Path", style="blue", min_width=30)
        table.add_column("Format", style="magenta", min_width=6)
        
        for i, video in enumerate(self.discovered_videos, 1):
            # Format file size
            size_mb = video['size'] / (1024 * 1024)
            if size_mb < 1:
                size_str = f"{video['size'] / 1024:.1f} KB"
            else:
                size_str = f"{size_mb:.1f} MB"
            
            table.add_row(
                str(i),
                video['name'],
                size_str,
                video['relative_path'],
                video['extension'].upper()
            )
        
        self.console.print(table)
        
        # Show usage instructions
        self.console.print(f"\n💡 [dim]To select a video, use: [bold]select <ID>[/bold][/dim]")
        self.console.print(f"💡 [dim]Example: [bold]select 1[/bold] to select the first video[/dim]")
    
    async def _execute_select_command(self, args: List[str]) -> None:
        """Execute select command to choose a discovered video"""
        if not self.discovered_videos:
            self.console.print("❌ [red]No videos discovered. Run 'discovery' first[/red]")
            return
        
        if not args:
            self.console.print("❌ [red]Specify the video ID to select[/red]")
            self.console.print(f"💡 [dim]Example: select 1 (Available IDs: 1-{len(self.discovered_videos)})[/dim]")
            return
        
        try:
            video_id = int(args[0])
            if video_id < 1 or video_id > len(self.discovered_videos):
                self.console.print(f"❌ [red]Invalid ID. Must be between 1 and {len(self.discovered_videos)}[/red]")
                return
            
            selected_video = self.discovered_videos[video_id - 1]
            video_path = selected_video['path']
            
            # Show selected video info
            self.console.print(f"\n🎯 [green]Video selected:[/green]")
            
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="white")
            
            info_table.add_row("📁 File:", selected_video['name'])
            info_table.add_row("📍 Path:", selected_video['relative_path'])
            info_table.add_row("📏 Size:", f"{selected_video['size'] / (1024 * 1024):.1f} MB")
            info_table.add_row("🎬 Format:", selected_video['extension'].upper())
            
            self.console.print(info_table)
            
            # Ask what to do with the selected video
            self.console.print(f"\n💡 [dim]What do you want to do with this video?[/dim]")
            self.console.print(f"💡 [dim]1. Type: [bold]transcribe[/bold] to transcribe it[/dim]")
            self.console.print(f"💡 [dim]2. Type: [bold]analyze[/bold] to analyze it[/dim]")
            
            # Store the selected video path for easy access
            self._last_selected_video = video_path
            
            # Add to memory for future reference
            self.memory.store_command(
                f"select {video_id}",
                f"Selected: {selected_video['name']}",
                0.1
            )
            
        except ValueError:
            self.console.print(f"❌ [red]ID must be a valid number[/red]")
        except Exception as e:
            self.console.print(f"❌ [red]Error selecting video: {e}[/red]")
    
    def _execute_history_command(self) -> None:
        """Execute history command"""
        try:
            history = self.memory.get_transcription_history(limit=10)
            
            if not history:
                self.console.print("📋 [yellow]No transcription history[/yellow]")
                return
            
            table = Table(title="📋 Transcription History", show_header=True)
            table.add_column("Video", style="cyan")
            table.add_column("Duration", style="green")
            table.add_column("Language", style="blue")
            table.add_column("Model", style="magenta")
            table.add_column("Date", style="yellow")
            
            for item in history:
                video_name = os.path.basename(item['video_path'])
                duration = f"{item['duration']:.1f}s" if item['duration'] else "N/A"
                language = item['language'] or "Auto"
                model = item['model_used'] or "N/A"
                timestamp = item['timestamp'][:19]  # Remove microseconds
                
                table.add_row(video_name, duration, language, model, timestamp)
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"❌ [red]Error getting history: {e}[/red]")
    
    def _execute_status_command(self) -> None:
        """Execute status command"""
        try:
            # Memory stats
            stats = self.memory.get_stats()
            
            # Agent status
            workflow_status = self.coordinator.get_workflow_status()
            
            # Session info
            session_duration = datetime.now() - self.session_start
            
            # Create status panel
            status_text = Text()
            status_text.append("🔄 System Status\n\n", style="bold cyan")
            
            # Session info
            status_text.append("📊 Current Session:\n", style="bold yellow")
            status_text.append(f"  • Duration: {str(session_duration).split('.')[0]}\n", style="white")
            status_text.append(f"  • Commands executed: {self.commands_executed}\n", style="white")
            status_text.append(f"  • Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n\n", style="white")
            
            # Memory stats
            status_text.append("💾 Memory (ChromaDB):\n", style="bold green")
            status_text.append(f"  • Transcriptions: {stats.get('transcriptions_count', 0)}\n", style="white")
            status_text.append(f"  • Interactions: {stats.get('interactions_count', 0)}\n", style="white")
            status_text.append(f"  • Video metadata: {stats.get('video_metadata_count', 0)}\n", style="white")
            status_text.append(f"  • Commands: {stats.get('commands_count', 0)}\n\n", style="white")
            
            # Last workflow
            if workflow_status.get('status') != 'no_workflow_executed':
                status_text.append("🎬 Last Workflow:\n", style="bold magenta")
                status_text.append(f"  • Video: {os.path.basename(workflow_status.get('video_path', 'N/A'))}\n", style="white")
                status_text.append(f"  • Progress: {workflow_status.get('progress_percentage', 0):.1f}%\n", style="white")
                status_text.append(f"  • Status: {workflow_status.get('status', 'unknown')}\n", style="white")
            
            panel = Panel(status_text, border_style="blue")
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"❌ [red]Error getting status: {e}[/red]")
    
    def _execute_help_command(self) -> None:
        """Execute help command"""
        help_text = Text()
        help_text.append("📚 Available Commands\n\n", style="bold cyan")
        
        commands_info = [
            ("transcribe <file>", "Transcribe a video file", "🎵"),
            ("analyze <file>", "Analyze video metadata", "🔍"),
            ("search <query>", "Search in saved transcriptions", "🔎"),
            ("discovery [directory]", "Find videos in current or specified directory", "🔍"),
            ("select <ID>", "Select a video from discovery results by ID", "🎯"),
            ("history", "Show transcription history", "📋"),
            ("status", "Show system status", "📊"),
            ("config", "Configure the agent", "⚙️"),
            ("clear", "Clear the screen", "🧹"),
            ("help", "Show this help", "❓"),
            ("exit", "Exit the program", "👋")
        ]
        
        for command, description, icon in commands_info:
            help_text.append(f"{icon} ", style="bold")
            help_text.append(f"{command:<20}", style="bold cyan")
            help_text.append(f" - {description}\n", style="white")
        
        help_text.append("\n💡 Tips:\n", style="bold yellow")
        help_text.append("  • Use Tab to autocomplete commands and paths\n", style="dim")
        help_text.append("  • Commands can use '/' prefix (/transcribe)\n", style="dim")
        help_text.append("  • Ctrl+C to cancel an operation\n", style="dim")
        help_text.append("  • Use absolute or relative file paths\n", style="dim")
        help_text.append("  • discovery automatically searches subdirectories\n", style="dim")
        help_text.append("  • select saves the video for use with transcribe/analyze\n", style="dim")
        help_text.append("  • All transcriptions are automatically saved in Spanish\n", style="dim")
        
        panel = Panel(help_text, border_style="blue")
        self.console.print(panel)
    
    async def _process_command(self, command: str, args: List[str]) -> None:
        """Process user command"""
        start_time = time.time()
        
        try:
            # Store interaction
            full_command = f"{command} {' '.join(args)}" if args else command
            
            if command == 'transcribe':
                await self._execute_transcribe_command(args)
            
            elif command == 'analyze':
                if not args:
                    # Check if there's a previously selected video
                    if self._last_selected_video:
                        video_path = self._last_selected_video
                        self.console.print(f"🎯 [green]Using selected video: {os.path.basename(video_path)}[/green]")
                    else:
                        import asyncio
                        loop = asyncio.get_event_loop()
                        video_path = await loop.run_in_executor(
                            None, 
                            lambda: prompt("📹 Video file path: ", completer=PathCompleter())
                        )
                else:
                    video_path = " ".join(args)
                
                if os.path.exists(video_path):
                    await self._execute_analyze_command([video_path])
                else:
                    self.console.print(f"❌ [red]File not found: {video_path}[/red]")
            
            elif command == 'search':
                await self._execute_search_command(args)
            
            elif command in ['discovery', 'discover']:
                await self._execute_discovery_command(args)
            
            elif command == 'select':
                await self._execute_select_command(args)
            
            elif command == 'history':
                self._execute_history_command()
            
            elif command == 'status':
                self._execute_status_command()
            
            elif command == 'config':
                self.console.print("⚙️ [yellow]Advanced configuration not implemented yet[/yellow]")
            
            elif command == 'clear':
                clear()
                self._display_welcome()
            
            elif command == 'help':
                self._execute_help_command()
            
            elif command in ['exit', 'quit']:
                self.console.print("👋 [yellow]Goodbye![/yellow]")
                self.running = False
            
            else:
                self.console.print(f"❓ [red]Unknown command: '{command}'. Type 'help' to see available commands.[/red]")
            
            # Store command execution
            execution_time = time.time() - start_time
            self.memory.store_command(full_command, "Command executed", execution_time)
            self.commands_executed += 1
            
        except KeyboardInterrupt:
            self.console.print("\n⚠️ [yellow]Operation cancelled by user[/yellow]")
        except Exception as e:
            self.console.print(f"❌ [red]Error executing command: {e}[/red]")
    
    async def run(self):
        """Main CLI loop"""
        try:
            # Clear screen and show welcome
            clear()
            self._display_welcome()
            
            # Main interaction loop
            while self.running:
                try:
                    # Get user input with completion - use async-safe approach
                    import asyncio
                    
                    def get_input():
                        return prompt(
                            "🎬 transcriptor> ",
                            completer=self.command_completer,
                            history=self.history
                        )
                    
                    # Run prompt in executor to avoid async conflicts
                    loop = asyncio.get_event_loop()
                    user_input = await loop.run_in_executor(None, get_input)
                    
                    if not user_input.strip():
                        continue
                    
                    # Parse and execute command
                    command, args = self._parse_command(user_input)
                    if command:
                        await self._process_command(command, args)
                    
                except KeyboardInterrupt:
                    # Handle Ctrl+C gracefully
                    if Confirm.ask("\nAre you sure you want to exit?", default=False):
                        break
                    else:
                        self.console.print()
                        continue
                
                except EOFError:
                    # Handle Ctrl+D
                    break
        
        finally:
            # Cleanup
            if hasattr(self, 'memory'):
                self.memory.close()
            self.console.print("\n👋 [green]Session ended![/green]")


async def main():
    """Entry point for the interactive CLI"""
    cli = InteractiveCLI()
    await cli.run()


if __name__ == "__main__":
    from utils.async_helper import run_async
    run_async(main())