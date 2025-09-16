"""
ChromaDB Memory Manager for Video Transcription Agent
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings


class MemoryManager:
    """Manages persistent memory using ChromaDB for the transcription agent"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client"""
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize collections
        self._init_collections()
    
    def _init_collections(self):
        """Initialize ChromaDB collections"""
        try:
            # Transcription history collection
            self.transcriptions = self.client.get_or_create_collection(
                name="transcriptions",
                metadata={"description": "Video transcription history"}
            )
            
            # Agent interactions collection
            self.interactions = self.client.get_or_create_collection(
                name="interactions",
                metadata={"description": "Agent interaction history"}
            )
            
            # Video metadata collection
            self.video_metadata = self.client.get_or_create_collection(
                name="video_metadata",
                metadata={"description": "Video file metadata and analysis"}
            )
            
            # Commands history collection
            self.commands = self.client.get_or_create_collection(
                name="commands",
                metadata={"description": "CLI commands history"}
            )
            
        except Exception as e:
            print(f"⚠️  Error initializing ChromaDB collections: {e}")
            # Fallback: create new collections
            self._reset_collections()
    
    def _reset_collections(self):
        """Reset all collections (use with caution)"""
        try:
            self.client.reset()
            self._init_collections()
        except Exception as e:
            print(f"❌ Error resetting collections: {e}")
    
    def _generate_id(self, content: str, prefix: str = "") -> str:
        """Generate unique ID for content"""
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.md5(f"{content}{timestamp}".encode()).hexdigest()[:8]
        return f"{prefix}{content_hash}" if prefix else content_hash
    
    def store_transcription(self, video_path: str, transcription_data: Dict[str, Any]) -> str:
        """Store transcription result in memory"""
        try:
            doc_id = self._generate_id(video_path, "trans_")
            
            # Prepare document
            document = json.dumps({
                "video_path": video_path,
                "transcription": transcription_data,
                "timestamp": datetime.now().isoformat()
            })
            
            # Store in ChromaDB
            self.transcriptions.add(
                documents=[document],
                ids=[doc_id],
                metadatas=[{
                    "video_path": video_path,
                    "duration": transcription_data.get("duration", 0),
                    "language": transcription_data.get("language", "unknown"),
                    "model_used": transcription_data.get("model_used", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }]
            )
            
            return doc_id
            
        except Exception as e:
            print(f"❌ Error storing transcription: {e}")
            return None
    
    def get_transcription_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transcription history"""
        try:
            results = self.transcriptions.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            history = []
            for doc, metadata in zip(results["documents"], results["metadatas"]):
                try:
                    data = json.loads(doc)
                    history.append({
                        "video_path": data["video_path"],
                        "timestamp": metadata["timestamp"],
                        "duration": metadata["duration"],
                        "language": metadata["language"],
                        "model_used": metadata["model_used"]
                    })
                except json.JSONDecodeError:
                    continue
            
            return sorted(history, key=lambda x: x["timestamp"], reverse=True)
            
        except Exception as e:
            print(f"❌ Error getting transcription history: {e}")
            return []
    
    def search_transcriptions(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search transcriptions by content"""
        try:
            results = self.transcriptions.query(
                query_texts=[query],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            
            matches = []
            for doc, metadata, distance in zip(
                results["documents"][0], 
                results["metadatas"][0], 
                results["distances"][0]
            ):
                try:
                    data = json.loads(doc)
                    matches.append({
                        "video_path": data["video_path"],
                        "transcription": data["transcription"],
                        "metadata": metadata,
                        "similarity": 1 - distance  # Convert distance to similarity
                    })
                except json.JSONDecodeError:
                    continue
            
            return matches
            
        except Exception as e:
            print(f"❌ Error searching transcriptions: {e}")
            return []
    
    def store_interaction(self, command: str, response: str, agent_name: str = "system") -> str:
        """Store agent interaction"""
        try:
            doc_id = self._generate_id(f"{command}{response}", "int_")
            
            document = json.dumps({
                "command": command,
                "response": response,
                "agent": agent_name,
                "timestamp": datetime.now().isoformat()
            })
            
            self.interactions.add(
                documents=[document],
                ids=[doc_id],
                metadatas=[{
                    "agent": agent_name,
                    "command_type": self._classify_command(command),
                    "timestamp": datetime.now().isoformat()
                }]
            )
            
            return doc_id
            
        except Exception as e:
            print(f"❌ Error storing interaction: {e}")
            return None
    
    def _classify_command(self, command: str) -> str:
        """Classify command type"""
        command_lower = command.lower()
        
        if any(word in command_lower for word in ["transcribir", "transcribe"]):
            return "transcription"
        elif any(word in command_lower for word in ["analizar", "analyze"]):
            return "analysis"
        elif any(word in command_lower for word in ["buscar", "search"]):
            return "search"
        elif any(word in command_lower for word in ["ayuda", "help"]):
            return "help"
        elif any(word in command_lower for word in ["salir", "exit", "quit"]):
            return "exit"
        else:
            return "general"
    
    def store_video_metadata(self, video_path: str, metadata: Dict[str, Any]) -> str:
        """Store video metadata"""
        try:
            doc_id = self._generate_id(video_path, "meta_")
            
            document = json.dumps({
                "video_path": video_path,
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            })
            
            self.video_metadata.add(
                documents=[document],
                ids=[doc_id],
                metadatas=[{
                    "video_path": video_path,
                    "duration": metadata.get("duration", 0),
                    "file_size": metadata.get("file_size", 0),
                    "resolution": metadata.get("video_resolution", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }]
            )
            
            return doc_id
            
        except Exception as e:
            print(f"❌ Error storing video metadata: {e}")
            return None
    
    def get_video_metadata(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Get stored video metadata"""
        try:
            results = self.video_metadata.get(
                where={"video_path": video_path},
                include=["documents", "metadatas"]
            )
            
            if results["documents"]:
                latest_doc = json.loads(results["documents"][-1])  # Get most recent
                return latest_doc["metadata"]
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting video metadata: {e}")
            return None
    
    def store_command(self, command: str, result: str, execution_time: float = 0) -> str:
        """Store command execution"""
        try:
            doc_id = self._generate_id(command, "cmd_")
            
            document = json.dumps({
                "command": command,
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })
            
            self.commands.add(
                documents=[document],
                ids=[doc_id],
                metadatas=[{
                    "command_type": self._classify_command(command),
                    "execution_time": execution_time,
                    "success": "error" not in result.lower(),
                    "timestamp": datetime.now().isoformat()
                }]
            )
            
            return doc_id
            
        except Exception as e:
            print(f"❌ Error storing command: {e}")
            return None
    
    def get_command_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent command history"""
        try:
            results = self.commands.get(
                limit=limit,
                include=["documents", "metadatas"]
            )
            
            history = []
            for doc, metadata in zip(results["documents"], results["metadatas"]):
                try:
                    data = json.loads(doc)
                    history.append({
                        "command": data["command"],
                        "result": data["result"],
                        "execution_time": data["execution_time"],
                        "timestamp": metadata["timestamp"],
                        "success": metadata["success"]
                    })
                except json.JSONDecodeError:
                    continue
            
            return sorted(history, key=lambda x: x["timestamp"], reverse=True)
            
        except Exception as e:
            print(f"❌ Error getting command history: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            stats = {
                "transcriptions_count": self.transcriptions.count(),
                "interactions_count": self.interactions.count(),
                "video_metadata_count": self.video_metadata.count(),
                "commands_count": self.commands.count(),
                "database_path": self.persist_directory
            }
            return stats
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {"error": str(e)}
    
    def clear_collection(self, collection_name: str) -> bool:
        """Clear specific collection"""
        try:
            if collection_name == "transcriptions":
                self.client.delete_collection("transcriptions")
                self.transcriptions = self.client.create_collection("transcriptions")
            elif collection_name == "interactions":
                self.client.delete_collection("interactions")
                self.interactions = self.client.create_collection("interactions")
            elif collection_name == "video_metadata":
                self.client.delete_collection("video_metadata")
                self.video_metadata = self.client.create_collection("video_metadata")
            elif collection_name == "commands":
                self.client.delete_collection("commands")
                self.commands = self.client.create_collection("commands")
            else:
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error clearing collection {collection_name}: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        try:
            # ChromaDB client doesn't require explicit closing
            pass
        except Exception as e:
            print(f"❌ Error closing memory manager: {e}")