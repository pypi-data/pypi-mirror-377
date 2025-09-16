"""
Linteum Verba - Rich Text Editor
Configuration Manager Module
"""
import os
import logging
import toml
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages editor configuration using TOML files"""
    
    DEFAULT_CONFIG = {
        "editor": {
            "font_family": "JetBrains Mono",
            "font_size": 12,
            "language": "python"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager

        Args:
            config_path: Path to the configuration file, or None to use default location
        """
        if config_path is None:
            # Default to a config.toml file in the user's home directory
            self.config_path = os.path.join(os.path.expanduser("~"), "linteum_verba_config.toml")
        else:
            self.config_path = config_path

        self.config = self.DEFAULT_CONFIG.copy()

        # Try to load the configuration file if it exists
        if os.path.exists(self.config_path):
            self.load_config()
        else:
            logger.info(f"No configuration file found at {self.config_path}, using defaults")
    
    def load_config(self, config_path: Optional[str] = None) -> bool:
        """
        Load configuration from a TOML file
        
        Args:
            config_path: Path to the configuration file, or None to use the current path
            
        Returns:
            bool: True if the configuration was loaded successfully, False otherwise
        """
        if config_path:
            self.config_path = config_path
        
        try:
            if os.path.exists(self.config_path):
                logger.info(f"Loading configuration from {self.config_path}")
                loaded_config = toml.load(self.config_path)
                
                # Merge with defaults to ensure all required keys exist
                self._merge_config(loaded_config)
                
                logger.info(f"Configuration loaded successfully: {self.config}")
                return True
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                # Reset to defaults when file not found
                self.config = self.DEFAULT_CONFIG.copy()
                return False
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Reset to defaults on error
            self.config = self.DEFAULT_CONFIG.copy()
            return False
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """
        Save configuration to a TOML file
        
        Args:
            config_path: Path to the configuration file, or None to use the current path
            
        Returns:
            bool: True if the configuration was saved successfully, False otherwise
        """
        if config_path:
            self.config_path = config_path

        if not self.config_path:
            logger.error("Cannot save configuration, no path specified.")
            return False

        try:
            logger.info(f"Saving configuration to {self.config_path}")

            # Ensure directory exists
            config_dir = os.path.dirname(os.path.abspath(self.config_path))
            os.makedirs(config_dir, exist_ok=True)

            # Write the configuration file
            with open(self.config_path, 'w', encoding='utf-8') as f:
                toml.dump(self.config, f)

            logger.info("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_value(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            section: The configuration section
            key: The configuration key
            default: Default value to return if the key is not found
            
        Returns:
            The configuration value, or the default if not found
        """
        try:
            return self.config.get(section, {}).get(key, default)
        except Exception as e:
            logger.error(f"Error getting configuration value {section}.{key}: {e}")
            return default
    
    def set_value(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value
        
        Args:
            section: The configuration section
            key: The configuration key
            value: The value to set
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        logger.debug(f"Set configuration value {section}.{key} = {value}")
    
    def _merge_config(self, loaded_config: Dict[str, Any]) -> None:
        """
        Merge loaded configuration with defaults
        
        Args:
            loaded_config: The loaded configuration
        """
        for section, values in self.DEFAULT_CONFIG.items():
            if section not in loaded_config:
                loaded_config[section] = {}
            
            for key, default_value in values.items():
                if key not in loaded_config[section]:
                    loaded_config[section][key] = default_value
        
        self.config = loaded_config

    def create_default_config(self) -> None:
        """Create a default configuration file if it doesn't exist"""
        if not os.path.exists(self.config_path):
            logger.info(f"Creating default configuration file at {self.config_path}")
            self.save_config()
