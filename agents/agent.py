import re
from agents.base_agent import BaseAgent
from pathlib import Path
import json
from utils.llm_interface import LLMService

class Agent(BaseAgent):
    def __init__(self, name, config):
        # Initialize the base class (BaseAgent) with the agent's name and configuration
        super().__init__(name, config)
        # Log the initialization of the agent
        self.logger.info(f"Initializing Agent: {name}")

        # Muki: Commenting this out as no need to load configs again here.
        # Done in the orchestrator
        # # Load the model configuration specific to this agent
        # self.model_config = self.load_model_config(name)

        # Initialize the LLM (Large Language Model) service with the loaded model configuration
        self.llm = LLMService(self.config)

# Muki: Loaded from Orchestrator. This is not needed
    # def load_model_config(self, agent_name):
    #     # Log the action of loading the model configuration for the agent
    #     self.logger.info(f"Loading model config for {agent_name}")
    #     # Load the default model configuration from a JSON file
    #     with open("config/default_model_config.json") as f:
    #         default_config = json.load(f)
    #     # Load agent-specific configuration overrides from a JSON file
    #     with open("config/agent_config.json") as f:
    #         overrides = json.load(f).get(agent_name, {})
    #     # Merge the default configuration with the agent-specific overrides
    #     # Agent-specific overrides take precedence over default values
    #     return {**default_config, **overrides}

    def load_user_prompt_template(self, template_path, context_vars):
        # Log the path of the user prompt template being loaded
        self.logger.info(f"Loading user prompt template: {template_path}")
        # Check if the template file exists
        if not Path(template_path).exists():
            # If the file does not exist, log a warning and return an empty string
            self.logger.warning(f"User prompt template not found: {template_path}")
            return ""
        # Read the contents of the template file
        template = Path(template_path).read_text()
        try:
            # Attempt to format the template with the provided context variables
            # Replace placeholders in the template (e.g., {variable_name}) with actual values from context_vars
            return template.format(**context_vars)
        except KeyError as e:
            # If a placeholder in the template is missing from context_vars, log an error
            self.logger.error(f"Missing placeholder key in user prompt template {template_path}: {e}")
            # Return the unformatted template as a fallback
            return template

    def extract_code_block(self, text):
        # Log the action of extracting a code block from the text
        self.logger.info("Extracting code block between triple backticks")
        # Use a regular expression to find content enclosed in triple backticks (```)
        # The pattern matches ``` optionally followed by a language identifier (e.g., ```python),
        # then captures any characters (.*?) until the next triple backticks.
        match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
        if not match:
            # If no match is found, raise a ValueError
            raise ValueError("Expected code block not found between triple backticks.")
        # Extract the content inside the backticks and strip any leading/trailing whitespace
        code_content = match.group(1).strip()
        # Return the extracted content, removing the triple backticks
        return f"{code_content}"

    def get_output_file_name(self, input_path):
        """
        Determine the output file name based on the agent's configuration.
        If `output_file` is specified in the config, use it.
        If `output_file_suffix` is specified, append it to the input file name.
        Otherwise, default to `{agent_name}.txt`.
        """
        # Check for explicit output file name in the agent's configuration
        if "output_file" in self.config:
            return self.config["output_file"]

        # Check for a suffix to append to the input file name
        if "output_file_suffix" in self.config:
            original_file_name = Path(input_path).stem
            return f"{original_file_name}{self.config['output_file_suffix']}"

        # Default to `{agent_name}.txt`
        return f"{self.name}.txt"

    def run(self, input_file, output_dir, previous_outputs=None):
        self.logger.info(f"Running agent {self.name}...")

        try:
            # --- Load Prompts ---
            system_prompt_path = Path(f"prompts/{self.name}/system.txt")
            system_prompt = system_prompt_path.read_text() if system_prompt_path.exists() else "You are a helpful assistant."

            user_template_path = Path(f"prompts/{self.name}/user_template.txt")
            context_vars = previous_outputs.copy() if previous_outputs else {}

            # If no previous outputs and input file exists, read its content
            if not previous_outputs and input_file and Path(input_file).exists():
                self.logger.info(f"Reading initial input file: {input_file}")
                with open(input_file, 'r') as f:
                    input_content = f.read().strip()
                context_vars['input_content'] = input_content

            # Load and format the user prompt using the template and context_vars
            user_prompt = self.load_user_prompt_template(user_template_path, context_vars)

            # --- Build Messages for LLM ---
            messages = [{"role": "system", "content": system_prompt}]
            if previous_outputs:
                for agent_name_prev, output_prev in previous_outputs.items():
                    messages.append({
                        "role": "assistant",
                        "content": f"[Context from {agent_name_prev}]:\n{output_prev.strip()}"
                    })
            print(f"User Prompt: \n {user_prompt}")

            messages.append({"role": "user", "content": user_prompt})

            # --- Call LLM ---
            self.logger.info(f"Sending request to LLM for agent {self.name}")
            response = self.llm.chat(messages)
            content = response.choices[0].message.content

            print(f"Response: \n {content}")

            # --- Process and Save Output ---
            output = self.extract_code_block(content)

            # Determine the output file name
            output_file_name = self.get_output_file_name(input_file)
            output_path = Path(output_dir) / output_file_name

            # Ensure the parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the extracted output to the specified file
            self.logger.info(f"Writing output for agent {self.name} to {output_path}")
            with open(output_path, 'w') as f:
                f.write(output)

        except Exception as e:
            # Log and raise an error if the agent fails
            self.logger.error(f"Agent {self.name} failed: {str(e)}")
            raise RuntimeError(f"Agent {self.name} failed: {str(e)}")
