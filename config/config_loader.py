import json
from pathlib import Path
from utils.logger import get_logger # Import the get_logger function

# Initialize a logger for the ConfigLoader module
logger = get_logger(__name__)

class ConfigLoader:
    _instance = None  # Class-level variable to hold the singleton instance

    def __new__(cls, config_paths=None):
        if cls._instance is None:
            logger.info("Creating a new instance of ConfigLoader.")
            # Create a new instance if it doesn't exist
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            # It's better to initialize the logger for the instance here or in __init__ if it were used.
            # However, for a singleton, a module-level logger or one initialized in __new__ for the first instance is fine.
            cls._instance._load_configs(config_paths)
        else:
            logger.debug("Returning existing instance of ConfigLoader.")
        return cls._instance

    def _load_configs(self, config_paths):
        """
        Load all configuration files into instance variables.
        :param config_paths: A dictionary containing paths to the config files.
        """
        logger.info("Starting to load configurations.")
        # Default paths if none are provided
        default_paths = {
            "default_config": "config/default_config.json",
            "agent_config": "config/agent_config.json",
            "flow_config": "config/flow.json"
        }
        
        # Use provided config_paths or fall back to default_paths
        effective_config_paths = config_paths or default_paths
        logger.debug(f"Using configuration paths: {effective_config_paths}")

        # Load each config file
        self.default_config = self._load_config_file(effective_config_paths["default_config"], "default_config")
        self.agent_config = self._load_config_file(effective_config_paths["agent_config"], "agent_config")
        self.flow_config = self._load_config_file(effective_config_paths["flow_config"], "flow_config")
        logger.info("All configurations loaded successfully.")

    def _load_config_file(self, file_path_str, config_name):
        """
        Load a single JSON configuration file.
        :param file_path_str: Path to the JSON file as a string.
        :param config_name: Name of the configuration being loaded (for logging).
        :return: Parsed JSON data as a dictionary.
        """
        logger.debug(f"Attempting to load {config_name} from path: {file_path_str}")
        config_file = Path(file_path_str)
        if not config_file.exists():
            logger.error(f"{config_name} file not found at path: {file_path_str}")
            raise FileNotFoundError(f"{config_name} configuration file not found: {file_path_str}")
        
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
            logger.info(f"Successfully loaded {config_name} from {file_path_str}.")
            logger.debug(f"Content of {config_name}: {data}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {config_name} file at {file_path_str}: {e}")
            raise  # Re-raise the exception after logging
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading {config_name} from {file_path_str}: {e}")
            raise # Re-raise the exception

    def get_default_config(self):
        """Return the default configuration."""
        logger.debug("Accessing default_config.")
        return self.default_config

    def get_agent_config(self):
        """Return the agent configuration."""
        logger.debug("Accessing agent_config.")
        return self.agent_config

    def get_flow_config(self):
        """Return the flow configuration."""
        logger.debug("Accessing flow_config.")
        return self.flow_config