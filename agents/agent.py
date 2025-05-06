import re
from agents.base_agent import BaseAgent
from pathlib import Path
import json
from utils.llm_interface import LLMService

class Agent(BaseAgent):
    def __init__(self, name, config):
        super().__init__(name, config)
        self.logger.info(f"Initializing Agent: {name}")
        self.model_config = self.load_model_config(name)
        self.llm = LLMService(self.model_config)

    def load_model_config(self, agent_name):
        self.logger.info(f"Loading model config for {agent_name}")
        with open("config/default_model_config.json") as f:
            default_config = json.load(f)
        with open("config/agent_config.json") as f:
            overrides = json.load(f).get(agent_name, {})
        return {**default_config, **overrides}

    def load_user_prompt_template(self, template_path, context_vars):
        self.logger.info(f"Loading user prompt template: {template_path}")
        if not Path(template_path).exists():
            return ""
        template = Path(template_path).read_text()
        try:
            return template.format(**context_vars)
        except KeyError as e:
            self.logger.error(f"Missing placeholder key: {e}")
            return template

    def extract_code_block(self, text):
        self.logger.info("Extracting block between ```Agent Response Start``` and ```Agent Response End```")
        match = re.search(r"```Agent Response Start```\n(.*?)```Agent Response End```", text, re.DOTALL)
        if not match:
            raise ValueError("Expected block not found between 'Agent Response Start' and 'Agent Response End'.")
        return match.group(1).strip()

    def run(self, input_path, output_folder, previous_outputs=None):
        self.logger.info(f"Running agent {self.name}...")

        try:
            # Load prompts
            system_prompt_path = Path(f"prompts/{self.name}/system.txt")
            system_prompt = system_prompt_path.read_text() if system_prompt_path.exists() else "You are a helpful assistant."

            user_template_path = Path(f"prompts/{self.name}/user_template.txt")
            context_vars = previous_outputs if previous_outputs else {}
            user_prompt = self.load_user_prompt_template(user_template_path, context_vars)

            # Build messages
            messages = [{"role": "system", "content": system_prompt}]

            if previous_outputs:
                for agent_name, output in previous_outputs.items():
                    messages.append({
                        "role": "assistant",
                        "content": f"[Context from {agent_name}]:\n{output.strip()}"
                    })

            if not previous_outputs and input_path.exists():
                with open(input_path, 'r') as f:
                    input_content = f.read().strip()
                    messages.append({
                        "role": "assistant",
                        "content": f"[Original file input]:\n{input_content}"
                    })

            messages.append({"role": "user", "content": user_prompt})

            # Call LLM
            self.logger.info(f"Sending request to LLM for {self.name}")
            response = self.llm.chat(messages)
            content = response.choices[0].message.content

            # Extract code block
            output = self.extract_code_block(content)

            # Use configured output file name
            output_file_name = self.model_config.get("output_file", f"{self.name}.txt")
            output_path = Path(output_folder) / output_file_name

            with open(output_path, 'w') as f:
                f.write(output)

        except Exception as e:
            self.logger.error(f"{self.name} failed: {str(e)}")
            raise RuntimeError(f"Agent {self.name} failed: {str(e)}")
