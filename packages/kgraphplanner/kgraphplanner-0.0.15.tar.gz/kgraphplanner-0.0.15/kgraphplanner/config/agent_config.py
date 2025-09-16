import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class AgentConfig:
    """Configuration manager for KGraphPlanner agents."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the agent configuration.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_data = {}
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """
        Load configuration from a YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_tool_config(self) -> Dict[str, Any]:
        """Get tool-specific configuration."""
        return self.get('tools', {})
    
    def get_tool_endpoint(self) -> Optional[str]:
        """Get the tool endpoint URL."""
        return self.get('tools.endpoint')
    
    def get_enabled_tools(self) -> list:
        """Get list of enabled tools."""
        return self.get('tools.enabled', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Get the full configuration as a dictionary."""
        return self.config_data.copy()