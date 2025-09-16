#!/usr/bin/env python3
"""
Video Transcription Agent - Main Entry Point
Multi-agent AI system for video transcription using LangChain and AutoGen
"""

import asyncio
import sys
from pathlib import Path

from cli.interactive_cli import InteractiveCLI
from utils.async_helper import run_async


def main():
    """Main entry point for the video transcription agent"""
    try:
        # Create and run CLI
        cli = InteractiveCLI()
        
        # Use safe async runner that handles both contexts
        run_async(cli.run())
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Transcription agent terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()