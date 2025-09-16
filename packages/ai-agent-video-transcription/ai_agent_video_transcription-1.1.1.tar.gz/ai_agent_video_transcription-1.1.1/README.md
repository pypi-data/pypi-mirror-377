# 🎬 Video Transcription Agent

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/ai-agent-video-transcription.svg)](https://badge.fury.io/py/ai-agent-video-transcription)
[![Downloads](https://pepy.tech/badge/ai-agent-video-transcription)](https://pepy.tech/project/ai-agent-video-transcription)

> **Multi-agent AI system for video transcription using OpenAI Whisper, ChromaDB, and AutoGen**

Transform your videos into accurate transcriptions with an intelligent multi-agent system that combines the power of OpenAI Whisper, persistent memory with ChromaDB, and advanced agent coordination.

## ✨ Key Features

### 🤖 Multi-Agent Architecture
- **Intelligent Coordination**: Specialized agents work together seamlessly
- **Video Analysis**: Extract metadata, duration, and quality information
- **Audio Transcription**: High-accuracy speech-to-text using OpenAI Whisper
- **Text Processing**: Automatic punctuation, formatting, and error correction
- **Output Formatting**: Multiple formats (SRT, VTT, TXT, JSON, CSV, DOCX)
- **Quality Assurance**: Built-in validation and quality assessment

### 🧠 Persistent Memory with ChromaDB
- **Semantic Search**: Find content using natural language queries
- **Session History**: Keep track of all transcriptions across sessions
- **Metadata Storage**: Rich information about videos and processing
- **Trend Analysis**: Usage statistics and pattern recognition

### 💬 Interactive CLI Experience
- **Intuitive Commands**: Simple, English-based command interface
- **Auto-completion**: Tab completion for commands and file paths
- **Progress Indicators**: Real-time progress bars and status updates
- **Rich Interface**: Beautiful colors and formatting with Rich library
- **Error Handling**: Graceful error management and recovery

### 🎯 Advanced Capabilities
- **Multiple Video Formats**: MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V
- **Language Detection**: Automatic or manual language selection
- **Precise Timestamps**: Word-level timing accuracy
- **Batch Processing**: Handle multiple videos simultaneously
- **Quality Optimization**: Automatic recommendations for better results

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install ai-agent-video-transcription

# Or install from source
git clone https://github.com/lopand-solutions/video-transcription-agent.git
cd video-transcription-agent
pip install -e .
```

### Prerequisites

- **Python 3.9+**
- **FFmpeg** (for audio/video processing)

```bash
# Install FFmpeg
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg
```

### Basic Usage

#### Interactive CLI (Recommended)

```bash
# Start the interactive CLI
vt-cli

# Or use the full command
video-transcription-agent
```

**Available Commands:**
```
🚀 Main Commands:

  • discovery      - Find videos in current directory
  • select <ID>   - Select a video from discovery results
  • transcribe    - Transcribe video file (always in Spanish)
  • analyze       - Analyze video metadata
  • search        - Search in saved transcriptions
  • history       - Show transcription history
  • status        - Show system status
  • help          - Show all commands
  • exit          - Exit the program
```

#### Command Line Usage

```bash
# Transcribe a video file
vt-cli transcribe path/to/video.mp4

# Analyze video metadata
vt-cli analyze path/to/video.mp4

# Search in transcriptions
vt-cli search "artificial intelligence"

# Show system status
vt-cli status
```

#### Programmatic Usage

```python
import asyncio
from ai_agent_video_transcription import CoordinatorAgent

async def transcribe_video():
    # Configuration
    config = {
        'transcriber': {
            'model_size': 'base',  # tiny, base, small, medium, large
            'language': 'es'       # Force Spanish transcription
        },
        'formatter': {
            'output_directory': './output'
        },
        'output_formats': ['txt', 'srt']
    }
    
    # Create coordinator
    coordinator = CoordinatorAgent(config)
    
    # Execute transcription
    result = await coordinator.execute({
        'video_path': 'path/to/video.mp4',
        'output_name': 'my_transcription'
    })
    
    return result

# Run transcription
result = asyncio.run(transcribe_video())
print(f"Transcription completed: {result['final_outputs']}")
```

## 📖 Documentation

### Configuration

#### Environment Variables

```bash
# Optional: Set OpenAI API key for advanced features
export OPENAI_API_KEY="your_api_key_here"

# Optional: Custom ChromaDB directory
export CHROMADB_PERSIST_DIRECTORY="./my_chroma_db"
```

#### Configuration File

Create a `config.yaml` file for advanced configuration:

```yaml
transcriber:
  model_size: "base"  # tiny, base, small, medium, large, large-v2, large-v3
  language: "es"      # Force Spanish, or null for auto-detection
  temperature: 0.0

formatter:
  output_directory: "./output"
  supported_formats: ["txt", "srt", "vtt", "json"]

memory:
  persist_sessions: true
  session_timeout_minutes: 60
```

### Supported Formats

#### Input Video Formats
- MP4, AVI, MOV, MKV, FLV, WMV, WebM, M4V

#### Output Formats
- **TXT**: Plain text transcription
- **SRT**: SubRip subtitle format
- **VTT**: WebVTT subtitle format
- **JSON**: Structured data with timestamps
- **CSV**: Comma-separated values
- **DOCX**: Microsoft Word document

### Whisper Models

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| tiny | 39M | Fastest | Basic | Quick testing |
| base | 74M | Fast | Good | **Recommended** |
| small | 244M | Medium | Better | Balanced |
| medium | 769M | Slow | High | Quality focus |
| large | 1550M | Slowest | Highest | Best quality |

## 🏗️ Architecture

```
Video Transcription Agent
├── 🤖 Multi-Agent System
│   ├── Coordinator Agent (orchestrates workflow)
│   ├── Analyzer Agent (video metadata extraction)
│   ├── Transcriber Agent (Whisper-based transcription)
│   ├── Processor Agent (text enhancement)
│   └── Formatter Agent (output generation)
├── 🧠 Memory System (ChromaDB)
│   ├── Persistent storage
│   ├── Semantic search
│   └── Session management
└── 💬 CLI Interface
    ├── Interactive commands
    ├── Progress indicators
    └── Error handling
```

## 🔧 Advanced Usage

### Batch Processing

```python
# Process multiple videos
videos = ['video1.mp4', 'video2.mp4', 'video3.mp4']
results = await coordinator.execute_batch(videos, 'batch_output')
```

### Custom Memory Queries

```python
# Search in stored transcriptions
memory = MemoryManager()
results = memory.search_transcriptions("machine learning", limit=10)
```

### Quality Analysis

```python
# Analyze video quality before transcription
analyzer = AnalyzerAgent()
metadata = await analyzer.execute({'video_path': 'video.mp4'})
print(f"Quality Score: {metadata['quality_score']}")
```

## 🐛 Troubleshooting

### Common Issues

**FFmpeg not found:**
```bash
# Verify installation
ffmpeg -version

# Install if missing
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu
```

**Memory issues with large models:**
- Use smaller models: `tiny`, `base`, `small`
- Process videos in smaller segments
- Increase system RAM or use GPU acceleration

**Transcription in wrong language:**
- Set language explicitly: `language: "es"` in config
- Check audio quality and clarity
- Try different Whisper models

### Performance Optimization

- **GPU Acceleration**: Install CUDA-compatible PyTorch for faster processing
- **Model Caching**: Models are cached automatically after first use
- **Batch Processing**: Process multiple videos in sequence for efficiency

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech recognition models
- **ChromaDB** - Vector database for semantic search
- **AutoGen** - Multi-agent framework
- **Rich** - Beautiful terminal interfaces
- **FFmpeg** - Multimedia processing

## 📞 Support

- 📧 **Email**: contact@lopand.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/lopand-solutions/video-transcription-agent/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/lopand-solutions/video-transcription-agent/wiki)

---

**🎬 Transform your videos into accurate transcriptions with AI!** 🚀

Made with ❤️ by [Lopand Solutions](https://lopand.com)