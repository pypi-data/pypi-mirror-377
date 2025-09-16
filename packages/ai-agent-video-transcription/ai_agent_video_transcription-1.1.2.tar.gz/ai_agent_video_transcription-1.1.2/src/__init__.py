"""
Video Transcription Agent

A multi-agent AI system for video transcription using LangChain and AutoGen.
"""

__version__ = "1.1.0"
__author__ = "Lopand Solutions"
__email__ = "contact@lopand.com"
__description__ = "Multi-agent AI system for video transcription using LangChain and AutoGen"

# Import main components for easy access
from .agents.coordinator_agent import CoordinatorAgent
from .agents.analyzer_agent import AnalyzerAgent
from .agents.transcriber_agent import TranscriberAgent
from .agents.formatter_agent import FormatterAgent
from .agents.processor_agent import ProcessorAgent
from .memory.memory_manager import MemoryManager
from .cli.interactive_cli import InteractiveCLI

__all__ = [
    "CoordinatorAgent",
    "AnalyzerAgent", 
    "TranscriberAgent",
    "FormatterAgent",
    "ProcessorAgent",
    "MemoryManager",
    "InteractiveCLI",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
