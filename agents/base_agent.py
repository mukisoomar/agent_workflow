from abc import ABC, abstractmethod
from utils.logger import get_logger
from pathlib import Path

class BaseAgent(ABC):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.logger = get_logger(name)
        Path("output").mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def run(self, input_path, output_path, previous_output=None):
        pass
