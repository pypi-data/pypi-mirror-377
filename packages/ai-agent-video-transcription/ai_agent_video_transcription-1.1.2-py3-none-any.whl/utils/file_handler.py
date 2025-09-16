import os
import shutil
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import yaml
from datetime import datetime


class FileHandler:
    """Utility class for file operations"""
    
    def __init__(self):
        self.temp_files = []
        self.temp_dirs = []
    
    def validate_path(self, path: str, must_exist: bool = True) -> bool:
        """Validate if path exists and is accessible"""
        if not path:
            return False
        
        path_obj = Path(path)
        
        if must_exist:
            return path_obj.exists()
        else:
            # Check if parent directory exists for new files
            return path_obj.parent.exists()
    
    def ensure_directory(self, directory: str) -> str:
        """Ensure directory exists, create if not"""
        Path(directory).mkdir(parents=True, exist_ok=True)
        return directory
    
    def get_safe_filename(self, filename: str) -> str:
        """Get a safe filename by removing/replacing invalid characters"""
        # Replace common invalid characters
        invalid_chars = '<>:"/\\|?*'
        safe_name = filename
        
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Remove multiple consecutive underscores
        while '__' in safe_name:
            safe_name = safe_name.replace('__', '_')
        
        # Remove leading/trailing underscores and dots
        safe_name = safe_name.strip('_.')
        
        # Ensure filename is not empty
        if not safe_name:
            safe_name = 'untitled'
        
        return safe_name
    
    def get_unique_filename(self, directory: str, base_name: str, extension: str = '') -> str:
        """Get a unique filename in the directory"""
        if not extension.startswith('.') and extension:
            extension = '.' + extension
        
        base_path = Path(directory) / f"{base_name}{extension}"
        
        if not base_path.exists():
            return str(base_path)
        
        # Add counter to make it unique
        counter = 1
        while True:
            new_path = Path(directory) / f"{base_name}_{counter}{extension}"
            if not new_path.exists():
                return str(new_path)
            counter += 1
    
    def create_temp_file(self, suffix: str = '', prefix: str = 'temp_', directory: str = None) -> str:
        """Create a temporary file and track it for cleanup"""
        fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=directory)
        os.close(fd)
        self.temp_files.append(path)
        return path
    
    def create_temp_directory(self, prefix: str = 'temp_dir_') -> str:
        """Create a temporary directory and track it for cleanup"""
        path = tempfile.mkdtemp(prefix=prefix)
        self.temp_dirs.append(path)
        return path
    
    def copy_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """Copy file from source to destination"""
        try:
            if not self.validate_path(source, must_exist=True):
                return False
            
            dest_path = Path(destination)
            
            if dest_path.exists() and not overwrite:
                return False
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, destination)
            return True
            
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    def move_file(self, source: str, destination: str, overwrite: bool = False) -> bool:
        """Move file from source to destination"""
        try:
            if not self.validate_path(source, must_exist=True):
                return False
            
            dest_path = Path(destination)
            
            if dest_path.exists() and not overwrite:
                return False
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(source, destination)
            return True
            
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file safely"""
        try:
            if self.validate_path(file_path, must_exist=True):
                os.remove(file_path)
                return True
            return False
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed file information"""
        if not self.validate_path(file_path, must_exist=True):
            return None
        
        try:
            path_obj = Path(file_path)
            stat = path_obj.stat()
            
            return {
                'path': str(path_obj.absolute()),
                'name': path_obj.name,
                'stem': path_obj.stem,
                'extension': path_obj.suffix,
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'accessed': datetime.fromtimestamp(stat.st_atime),
                'is_file': path_obj.is_file(),
                'is_directory': path_obj.is_dir(),
                'permissions': oct(stat.st_mode)[-3:]
            }
            
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None
    
    def find_files(self, directory: str, pattern: str = '*', recursive: bool = True) -> List[str]:
        """Find files matching pattern in directory"""
        if not self.validate_path(directory, must_exist=True):
            return []
        
        try:
            path_obj = Path(directory)
            
            if recursive:
                files = path_obj.rglob(pattern)
            else:
                files = path_obj.glob(pattern)
            
            return [str(f) for f in files if f.is_file()]
            
        except Exception as e:
            print(f"Error finding files: {e}")
            return []
    
    def find_directories(self, directory: str, pattern: str = '*', recursive: bool = True) -> List[str]:
        """Find directories matching pattern"""
        if not self.validate_path(directory, must_exist=True):
            return []
        
        try:
            path_obj = Path(directory)
            
            if recursive:
                dirs = path_obj.rglob(pattern)
            else:
                dirs = path_obj.glob(pattern)
            
            return [str(d) for d in dirs if d.is_dir()]
            
        except Exception as e:
            print(f"Error finding directories: {e}")
            return []
    
    def read_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Read JSON file safely"""
        if not self.validate_path(file_path, must_exist=True):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            return None
    
    def write_json(self, data: Dict[str, Any], file_path: str, indent: int = 2) -> bool:
        """Write data to JSON file safely"""
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error writing JSON file: {e}")
            return False
    
    def read_yaml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Read YAML file safely"""
        if not self.validate_path(file_path, must_exist=True):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
                
        except Exception as e:
            print(f"Error reading YAML file: {e}")
            return None
    
    def write_yaml(self, data: Dict[str, Any], file_path: str) -> bool:
        """Write data to YAML file safely"""
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
            
            return True
            
        except Exception as e:
            print(f"Error writing YAML file: {e}")
            return False
    
    def read_text(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Read text file safely"""
        if not self.validate_path(file_path, must_exist=True):
            return None
        
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
                
        except Exception as e:
            print(f"Error reading text file: {e}")
            return None
    
    def write_text(self, text: str, file_path: str, encoding: str = 'utf-8') -> bool:
        """Write text to file safely"""
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(text)
            
            return True
            
        except Exception as e:
            print(f"Error writing text file: {e}")
            return False
    
    def get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        if not self.validate_path(directory, must_exist=True):
            return 0
        
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
            
            return total_size
            
        except Exception as e:
            print(f"Error calculating directory size: {e}")
            return 0
    
    def clean_directory(self, directory: str, keep_hidden: bool = True) -> int:
        """Clean directory contents, return number of files removed"""
        if not self.validate_path(directory, must_exist=True):
            return 0
        
        removed_count = 0
        
        try:
            for item in os.listdir(directory):
                if keep_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(directory, item)
                
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    removed_count += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    removed_count += 1
            
            return removed_count
            
        except Exception as e:
            print(f"Error cleaning directory: {e}")
            return 0
    
    def archive_directory(self, directory: str, archive_path: str, format: str = 'zip') -> bool:
        """Create archive of directory"""
        if not self.validate_path(directory, must_exist=True):
            return False
        
        try:
            # Ensure archive directory exists
            Path(archive_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Remove extension from archive_path for shutil.make_archive
            archive_base = str(Path(archive_path).with_suffix(''))
            
            shutil.make_archive(archive_base, format, directory)
            return True
            
        except Exception as e:
            print(f"Error creating archive: {e}")
            return False
    
    def extract_archive(self, archive_path: str, extract_to: str) -> bool:
        """Extract archive to directory"""
        if not self.validate_path(archive_path, must_exist=True):
            return False
        
        try:
            # Ensure extraction directory exists
            self.ensure_directory(extract_to)
            
            shutil.unpack_archive(archive_path, extract_to)
            return True
            
        except Exception as e:
            print(f"Error extracting archive: {e}")
            return False
    
    def cleanup_temp_files(self) -> int:
        """Clean up all temporary files and directories"""
        cleaned_count = 0
        
        # Clean up temporary files
        for temp_file in self.temp_files[:]:  # Copy list to avoid modification during iteration
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    cleaned_count += 1
                self.temp_files.remove(temp_file)
            except Exception as e:
                print(f"Failed to clean up temp file {temp_file}: {e}")
        
        # Clean up temporary directories
        for temp_dir in self.temp_dirs[:]:  # Copy list to avoid modification during iteration
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    cleaned_count += 1
                self.temp_dirs.remove(temp_dir)
            except Exception as e:
                print(f"Failed to clean up temp directory {temp_dir}: {e}")
        
        return cleaned_count
    
    def get_available_space(self, path: str) -> Optional[int]:
        """Get available disk space in bytes"""
        try:
            if os.name == 'nt':  # Windows
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(path),
                    ctypes.pointer(free_bytes),
                    None,
                    None
                )
                return free_bytes.value
            else:  # Unix-like
                statvfs = os.statvfs(path)
                return statvfs.f_frsize * statvfs.f_bavail
                
        except Exception as e:
            print(f"Error getting available space: {e}")
            return None
    
    def __del__(self):
        """Clean up when object is destroyed"""
        self.cleanup_temp_files()