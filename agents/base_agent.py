from abc import ABC, abstractmethod
from utils.logger import get_logger
from pathlib import Path

class BaseAgent(ABC):
    def __init__(self, name, config_loader):
        """
        Initialize the BaseAgent with the agent name and a ConfigLoader instance.
        :param name: The name of the agent.
        :param config_loader: An instance of ConfigLoader to access all configurations.
        """
        self.name = name
        self.config_loader = config_loader
        self.logger = get_logger(name)

        # Load configurations
        self.default_config = self.config_loader.get_default_config()
        self.agent_config = self.config_loader.get_agent_config().get(name, {})
        self.flow_config = self.config_loader.get_flow_config()

        # Merge default and agent-specific configurations
        self.config = {**self.default_config.get("default_agent_config", {}), **self.agent_config}

        # Ensure the output directory exists
        Path("output").mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def run(self, input_path, output_path, previous_output=None):
        """
        Abstract method to be implemented by subclasses.
        :param input_path: Path to the input file.
        :param output_path: Path to the output file.
        :param previous_output: Outputs from previous agents in the flow.
        """
        pass
