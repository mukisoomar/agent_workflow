import sys
import os
import json
import unittest
from pathlib import Path
import shutil # For cleaning up the test config directory

# Adjust the Python path to include the project root directory
# This allows us to import modules from the 'config' and 'utils' directories
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config.config_loader import ConfigLoader
from utils.logger import get_logger

# Initialize a logger for the test module
logger = get_logger(__name__)

class TestConfigLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up for all tests in this class."""
        logger.info("Setting up TestConfigLoader tests.")
        # Define a temporary config directory for test files
        cls.test_config_dir = project_root / "Test" / "temp_config_for_test"
        cls.test_config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created temporary config directory: {cls.test_config_dir}")

        # Define paths for dummy config files
        cls.default_config_path = cls.test_config_dir / "default_config.json"
        cls.agent_config_path = cls.test_config_dir / "agent_config.json"
        cls.flow_config_path = cls.test_config_dir / "flow.json"
        cls.invalid_json_path = cls.test_config_dir / "invalid_json.json"

        # Create dummy config files
        cls.dummy_default_data = {"setting1": "value1", "default_setting": True}
        cls.dummy_agent_data = {"agent_A": {"param1": "a"}, "agent_B": {"param2": "b"}}
        cls.dummy_flow_data = {"start_agent": ["agent_A", "agent_B"]}

        with open(cls.default_config_path, 'w') as f:
            json.dump(cls.dummy_default_data, f)
        with open(cls.agent_config_path, 'w') as f:
            json.dump(cls.dummy_agent_data, f)
        with open(cls.flow_config_path, 'w') as f:
            json.dump(cls.dummy_flow_data, f)
        with open(cls.invalid_json_path, 'w') as f:
            f.write("{'invalid_json': True,}") # Malformed JSON

        logger.info("Created dummy configuration files for testing.")

        # Reset ConfigLoader._instance to None before each test class run
        # to ensure a fresh instance for this set of tests.
        ConfigLoader._instance = None


    @classmethod
    def tearDownClass(cls):
        """Tear down after all tests in this class."""
        logger.info("Tearing down TestConfigLoader tests.")
        if cls.test_config_dir.exists():
            shutil.rmtree(cls.test_config_dir)
            logger.info(f"Removed temporary config directory: {cls.test_config_dir}")
        ConfigLoader._instance = None # Clean up singleton instance

    def setUp(self):
        """Set up for each test method."""
        # Reset the singleton instance before each test method to ensure isolation
        # This is important if tests modify the instance or expect a fresh load.
        ConfigLoader._instance = None
        logger.debug(f"Running test: {self._testMethodName}")


    def test_singleton_instance(self):
        """Test that ConfigLoader returns a singleton instance."""
        logger.info("Testing singleton instance creation.")
        config_paths = {
            "default_config": str(self.default_config_path),
            "agent_config": str(self.agent_config_path),
            "flow_config": str(self.flow_config_path)
        }
        instance1 = ConfigLoader(config_paths)
        instance2 = ConfigLoader(config_paths)
        self.assertIs(instance1, instance2, "ConfigLoader should return the same instance.")
        logger.info("Singleton instance test passed.")

    def test_load_valid_configs(self):
        """Test loading of valid configuration files."""
        logger.info("Testing loading of valid configuration files.")
        config_paths = {
            "default_config": str(self.default_config_path),
            "agent_config": str(self.agent_config_path),
            "flow_config": str(self.flow_config_path)
        }
        loader = ConfigLoader(config_paths)
        self.assertEqual(loader.get_default_config(), self.dummy_default_data)
        self.assertEqual(loader.get_agent_config(), self.dummy_agent_data)
        self.assertEqual(loader.get_flow_config(), self.dummy_flow_data)
        logger.info("Valid configuration loading test passed.")

    def test_load_missing_default_config_file(self):
        """Test FileNotFoundError when the default_config.json is missing."""
        logger.info("Testing missing default_config.json.")
        missing_path = self.test_config_dir / "non_existent_default.json"
        config_paths = {
            "default_config": str(missing_path),
            "agent_config": str(self.agent_config_path),
            "flow_config": str(self.flow_config_path)
        }
        with self.assertRaises(FileNotFoundError):
            ConfigLoader(config_paths)
        logger.info("Missing default_config.json test passed.")

    def test_load_missing_agent_config_file(self):
        """Test FileNotFoundError when the agent_config.json is missing."""
        logger.info("Testing missing agent_config.json.")
        missing_path = self.test_config_dir / "non_existent_agent.json"
        config_paths = {
            "default_config": str(self.default_config_path),
            "agent_config": str(missing_path),
            "flow_config": str(self.flow_config_path)
        }
        with self.assertRaises(FileNotFoundError):
            ConfigLoader(config_paths)
        logger.info("Missing agent_config.json test passed.")


    def test_load_missing_flow_config_file(self):
        """Test FileNotFoundError when the flow_config.json is missing."""
        logger.info("Testing missing flow_config.json.")
        missing_path = self.test_config_dir / "non_existent_flow.json"
        config_paths = {
            "default_config": str(self.default_config_path),
            "agent_config": str(self.agent_config_path),
            "flow_config": str(missing_path)
        }
        with self.assertRaises(FileNotFoundError):
            ConfigLoader(config_paths)
        logger.info("Missing flow_config.json test passed.")

    def test_load_invalid_json_config(self):
        """Test json.JSONDecodeError for a malformed JSON file."""
        logger.info("Testing loading of invalid JSON configuration.")
        config_paths = {
            "default_config": str(self.invalid_json_path), # Using the invalid JSON here
            "agent_config": str(self.agent_config_path),
            "flow_config": str(self.flow_config_path)
        }
        with self.assertRaises(json.JSONDecodeError):
            ConfigLoader(config_paths)
        logger.info("Invalid JSON configuration test passed.")

    def test_get_configs_methods(self):
        """Test the getter methods for each configuration."""
        logger.info("Testing getter methods.")
        config_paths = {
            "default_config": str(self.default_config_path),
            "agent_config": str(self.agent_config_path),
            "flow_config": str(self.flow_config_path)
        }
        loader = ConfigLoader(config_paths)
        self.assertEqual(loader.get_default_config(), self.dummy_default_data, "get_default_config failed.")
        self.assertEqual(loader.get_agent_config(), self.dummy_agent_data, "get_agent_config failed.")
        self.assertEqual(loader.get_flow_config(), self.dummy_flow_data, "get_flow_config failed.")
        logger.info("Getter methods test passed.")

if __name__ == '__main__':
    logger.info("Starting ConfigLoader test suite.")
    unittest.main()
    logger.info("Finished ConfigLoader test suite.")
