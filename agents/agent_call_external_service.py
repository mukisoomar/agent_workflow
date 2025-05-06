import requests
from agents.agent import Agent

class AgentCallExternalService(Agent):
    def run(self, input_path, output_folder, previous_outputs=None):
        self.logger.info(f"[{self.name}] Calling external service before LLM execution")

        # Step 1: Fetch external data (mock service)
        try:
            response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
            response.raise_for_status()
            external_data = response.json()
        except Exception as e:
            self.logger.error(f"[{self.name}] Failed to call external service: {e}")
            raise RuntimeError(f"External API call failed: {str(e)}")

        # Step 2: Add response to context
        if previous_outputs is None:
            previous_outputs = {}
        previous_outputs["external_service"] = f"Fetched Todo: {external_data['title']}"

        # Step 3: Call parent Agent run with extended context
        super().run(input_path, output_folder, previous_outputs)
