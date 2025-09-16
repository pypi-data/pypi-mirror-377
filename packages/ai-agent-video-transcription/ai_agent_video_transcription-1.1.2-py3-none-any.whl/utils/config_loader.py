import os
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv


class ConfigLoader:
    """Configuration loader with support for multiple sources and environments"""
    
    def __init__(self, config_dir: str = "config", env_file: str = ".env"):
        self.config_dir = Path(config_dir)
        self.env_file = env_file
        self.config_cache = {}
        
        # Load environment variables
        if os.path.exists(env_file):
            load_dotenv(env_file)
    
    def load_config(self, config_name: str, reload: bool = False) -> Dict[str, Any]:
        """Load configuration from file with caching"""
        
        if config_name in self.config_cache and not reload:
            return self.config_cache[config_name]
        
        config_data = {}
        
        # Try different file formats
        config_files = [
            self.config_dir / f"{config_name}.yaml",
            self.config_dir / f"{config_name}.yml", 
            self.config_dir / f"{config_name}.json",
            Path(f"{config_name}.yaml"),
            Path(f"{config_name}.yml"),
            Path(f"{config_name}.json")
        ]
        
        for config_file in config_files:
            if config_file.exists():
                config_data = self._load_file(config_file)
                break
        
        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data, config_name)
        
        # Cache the configuration
        self.config_cache[config_name] = config_data
        
        return config_data
    
    def _load_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from file based on extension"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == '.json':
                    return json.load(f) or {}
                else:
                    return {}
        except Exception as e:
            print(f"Error loading config file {file_path}: {e}")
            return {}
    
    def _apply_env_overrides(self, config: Dict[str, Any], config_name: str) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration"""
        
        # Convert config_name to uppercase for env var prefix
        env_prefix = f"{config_name.upper()}_"
        
        # Get all environment variables with the prefix
        env_overrides = {
            key[len(env_prefix):]: value
            for key, value in os.environ.items()
            if key.startswith(env_prefix)
        }
        
        # Apply overrides using dot notation
        for env_key, env_value in env_overrides.items():
            self._set_nested_value(config, env_key.lower(), self._parse_env_value(env_value))
        
        return config
    
    def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any) -> None:
        """Set nested configuration value using dot notation"""
        keys = key_path.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type"""
        # Try to parse as JSON first (for complex types)
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Parse boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for the video transcription agent"""
        return {
            'analyzer': {
                'supported_formats': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'],
                'max_file_size_mb': 2000,
                'max_duration_hours': 2
            },
            'transcriber': {
                'model_size': 'base',
                'language': None,
                'temperature': 0.0,
                'compression_ratio_threshold': 2.4,
                'logprob_threshold': -1.0,
                'no_speech_threshold': 0.6,
                'enable_word_timestamps': True
            },
            'processor': {
                'auto_punctuation': True,
                'auto_capitalization': True,
                'remove_filler_words': False,
                'language': 'en'
            },
            'formatter': {
                'output_directory': './output',
                'default_formats': ['txt', 'srt'],
                'supported_formats': ['txt', 'srt', 'vtt', 'json', 'csv', 'docx']
            },
            'coordinator': {
                'enable_processing': True,
                'output_formats': ['txt', 'srt'],
                'parallel_processing': False,
                'max_concurrent_jobs': 1
            },
            'memory': {
                'persist_sessions': True,
                'session_timeout_minutes': 60,
                'max_history_entries': 100
            },
            'logging': {
                'level': 'INFO',
                'file': 'transcription.log',
                'max_size_mb': 10,
                'backup_count': 3
            }
        }
    
    def get_whisper_models_config(self) -> Dict[str, Any]:
        """Get Whisper models configuration"""
        return {
            'models': {
                'tiny': {
                    'parameters': '39M',
                    'vram_required_gb': 1,
                    'relative_speed': 32,
                    'description': 'Fastest, lowest accuracy',
                    'recommended_for': ['quick_testing', 'low_resource_systems']
                },
                'base': {
                    'parameters': '74M',
                    'vram_required_gb': 1,
                    'relative_speed': 16,
                    'description': 'Good balance of speed and accuracy',
                    'recommended_for': ['general_use', 'production']
                },
                'small': {
                    'parameters': '244M',
                    'vram_required_gb': 2,
                    'relative_speed': 6,
                    'description': 'Better accuracy, moderate speed',
                    'recommended_for': ['higher_accuracy', 'good_hardware']
                },
                'medium': {
                    'parameters': '769M',
                    'vram_required_gb': 5,
                    'relative_speed': 2,
                    'description': 'High accuracy, slower',
                    'recommended_for': ['professional_use', 'accuracy_critical']
                },
                'large': {
                    'parameters': '1550M',
                    'vram_required_gb': 10,
                    'relative_speed': 1,
                    'description': 'Highest accuracy, slowest',
                    'recommended_for': ['maximum_accuracy', 'high_end_hardware']
                },
                'large-v2': {
                    'parameters': '1550M',
                    'vram_required_gb': 10,
                    'relative_speed': 1,
                    'description': 'Improved version of large model',
                    'recommended_for': ['maximum_accuracy', 'latest_improvements']
                },
                'large-v3': {
                    'parameters': '1550M',
                    'vram_required_gb': 10,
                    'relative_speed': 1,
                    'description': 'Latest and most accurate model',
                    'recommended_for': ['cutting_edge_accuracy', 'research']
                }
            },
            'model_selection': {
                'auto_select_based_on': ['duration', 'quality_requirements', 'available_resources'],
                'duration_thresholds': {
                    'short': {'max_minutes': 5, 'recommended_model': 'small'},
                    'medium': {'max_minutes': 30, 'recommended_model': 'base'},
                    'long': {'max_minutes': 120, 'recommended_model': 'base'},
                    'very_long': {'max_minutes': float('inf'), 'recommended_model': 'tiny'}
                }
            }
        }
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        environment = os.getenv('ENVIRONMENT', 'development').lower()
        
        base_config = {
            'environment': environment,
            'debug': environment == 'development',
            'log_level': 'DEBUG' if environment == 'development' else 'INFO'
        }
        
        if environment == 'development':
            base_config.update({
                'transcriber': {'model_size': 'tiny'},  # Faster for development
                'coordinator': {'enable_processing': False},  # Skip processing for speed
                'logging': {'level': 'DEBUG'}
            })
        elif environment == 'production':
            base_config.update({
                'transcriber': {'model_size': 'base'},
                'coordinator': {'enable_processing': True},
                'logging': {'level': 'INFO'}
            })
        
        return base_config
    
    def save_config(self, config_name: str, config_data: Dict[str, Any], format: str = 'yaml') -> bool:
        """Save configuration to file"""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            if format.lower() in ['yaml', 'yml']:
                config_file = self.config_dir / f"{config_name}.yaml"
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(config_data, f, default_flow_style=False, allow_unicode=True)
            elif format.lower() == 'json':
                config_file = self.config_dir / f"{config_name}.json"
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Update cache
            self.config_cache[config_name] = config_data
            
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def merge_configs(self, *configs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries"""
        result = {}
        
        for config in configs:
            result = self._deep_merge(result, config)
        
        return result
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate transcriber config
        if 'transcriber' in config:
            transcriber_config = config['transcriber']
            valid_models = ['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3']
            
            model_size = transcriber_config.get('model_size', 'base')
            if model_size not in valid_models:
                issues.append(f"Invalid model_size '{model_size}'. Must be one of: {valid_models}")
            
            temperature = transcriber_config.get('temperature', 0.0)
            if not 0.0 <= temperature <= 1.0:
                issues.append(f"Temperature must be between 0.0 and 1.0, got {temperature}")
        
        # Validate formatter config
        if 'formatter' in config:
            formatter_config = config['formatter']
            output_dir = formatter_config.get('output_directory', './output')
            
            try:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create output directory '{output_dir}': {e}")
        
        # Validate analyzer config
        if 'analyzer' in config:
            analyzer_config = config['analyzer']
            max_size = analyzer_config.get('max_file_size_mb', 2000)
            
            if max_size <= 0:
                issues.append(f"max_file_size_mb must be positive, got {max_size}")
        
        return issues
    
    def get_config_template(self) -> str:
        """Get a YAML template for configuration"""
        return '''# Video Transcription Agent Configuration

# Video Analyzer Settings
analyzer:
  supported_formats: ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
  max_file_size_mb: 2000
  max_duration_hours: 2

# Transcriber Settings (Whisper)
transcriber:
  model_size: base  # tiny, base, small, medium, large, large-v2, large-v3
  language: null    # Auto-detect if null, or specify language code (e.g., 'en', 'es')
  temperature: 0.0  # 0.0 for deterministic output
  compression_ratio_threshold: 2.4
  logprob_threshold: -1.0
  no_speech_threshold: 0.6
  enable_word_timestamps: true

# Text Processor Settings
processor:
  auto_punctuation: true
  auto_capitalization: true
  remove_filler_words: false
  language: en

# Output Formatter Settings
formatter:
  output_directory: ./output
  default_formats: [txt, srt]
  supported_formats: [txt, srt, vtt, json, csv, docx]

# Workflow Coordinator Settings
coordinator:
  enable_processing: true
  output_formats: [txt, srt]
  parallel_processing: false
  max_concurrent_jobs: 1

# Memory and Session Settings
memory:
  persist_sessions: true
  session_timeout_minutes: 60
  max_history_entries: 100

# Logging Settings
logging:
  level: INFO
  file: transcription.log
  max_size_mb: 10
  backup_count: 3
'''
    
    def create_config_file(self, config_name: str = 'default') -> str:
        """Create a default configuration file"""
        config_file = self.config_dir / f"{config_name}.yaml"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(self.get_config_template())
        
        return str(config_file)
    
    def list_configs(self) -> List[str]:
        """List available configuration files"""
        if not self.config_dir.exists():
            return []
        
        configs = []
        
        for file_path in self.config_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.yaml', '.yml', '.json']:
                configs.append(file_path.stem)
        
        return sorted(configs)
    
    def clear_cache(self) -> None:
        """Clear configuration cache"""
        self.config_cache.clear()