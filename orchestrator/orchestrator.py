import json
from pathlib import Path
from utils.logger import get_logger
import os

def run_orchestration(repo_path=None, output_base_path=None):
    logger = get_logger("Orchestrator")
    logger.info("Starting orchestration run")

    logger.info("Loading config/flow.json")
    with open("config/flow.json") as f:
        flow = json.load(f)

    logger.info("Loading config/default.json")
    with open("config/default_config.json") as f:
        default_config = json.load(f)

    logger.info("Loading config/agent_config.json")
    with open("config/agent_config.json") as f:
        agent_configs = json.load(f)

    logger.info("Importing Agent class")
    from agents.agent import Agent

    agents = {}
    for agent_name in flow:
        logger.info(f"Initializing agent: {agent_name}")
        prompt_path = f"prompts/{agent_name}.txt"
        merged_config = {**default_config.get("model", {}), **agent_configs.get(agent_name, {})}
        agents[agent_name] = Agent(agent_name, config=merged_config)

    initial_agent = list(flow.keys())[0]

    repo_folder = Path(repo_path) if repo_path else Path("repository")
    output_root = Path(output_base_path) if output_base_path else Path("output")

    repo_folder.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    for file_path in repo_folder.glob("*.*"):
        if file_path.name == "__init__.py":
            continue  # Skip Python package files

        input_file_name = file_path.stem
        logger.info(f"\n=== Processing input file: {file_path.name} ===")
        output_subfolder = output_root / input_file_name
        output_subfolder.mkdir(parents=True, exist_ok=True)

        output_map = {}

        def execute(agent_name, input_path, previous_agents=[]):
            try:
                logger.info(f"Executing {agent_name} on {input_path}...")
                agent = agents[agent_name]
                output_path = output_subfolder / f"{agent_name}.txt"
                previous_outputs = {p: output_map[p] for p in previous_agents if p in output_map}
                agent.run(input_path, output_path, previous_outputs)

                with open(output_path, 'r') as f:
                    current_output = f.read()
                output_map[agent_name] = current_output

                for next_agent in flow.get(agent_name, []):
                    execute(next_agent, output_path, previous_agents + [agent_name])
            except Exception as e:
                logger.error(f"Stopping flow: {agent_name} failed: {str(e)}")
                return

        logger.info(f"Starting flow from agent: {initial_agent}")
        execute(initial_agent, file_path)
