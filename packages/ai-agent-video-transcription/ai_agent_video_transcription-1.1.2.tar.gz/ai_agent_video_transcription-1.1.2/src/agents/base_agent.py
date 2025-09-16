from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain.agents import Agent
from langchain.callbacks.manager import CallbackManagerForChainRun


class BaseTranscriptionAgent(ABC):
    """Base class for all transcription agents"""
    
    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.config = config or {}
        self.memory = {}
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main functionality"""
        pass
    
    def get_memory(self, key: str) -> Any:
        """Get value from agent memory"""
        return self.memory.get(key)
    
    def set_memory(self, key: str, value: Any) -> None:
        """Set value in agent memory"""
        self.memory[key] = value
    
    def clear_memory(self) -> None:
        """Clear agent memory"""
        self.memory.clear()
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"