from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class ToolContext:
    def __init__(self, config: Dict[str, Any], artifacts_path: str):
        self._config = config
        # Store the provided path and ensure the directory exists.
        self._artifacts_dir = Path(artifacts_path)
        self._artifacts_dir.mkdir(parents=True, exist_ok=True)
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieves a configuration value (e.g., an API key)
        provided by the end-user when they configured the Agent.
        """
        return self._config.get(key, default)

    def get_artifacts_path(self, filename: str) -> Path:
        """
        Returns a secure, writable path for creating a new file (artifact).
        This ensures files are saved in the correct, isolated directory.
        
        Args:
            filename (str): The desired name for the file.
            
        Returns:
            A Path object representing the full, secure path to the new file.
        """
        if '/' in filename or '\\' in filename or '..' in filename:
            raise ValueError("Filename cannot contain directory paths or slashes.")
        
        return self._artifacts_dir / filename
    
class BaseTool(ABC):
    """
    The base class for all AgentForge tools.
    Your tool class must inherit from this.
    """

    def __init__(self, context: ToolContext):
        self.context = context

    @abstractmethod
    def run(self, **kwargs) -> str:
        """
        The entry point for your tool.
        The arguments are provided by the LLM based on your manifest.
        Must return a string.
        """
        pass