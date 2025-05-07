import json
from pathlib import Path
from utils.logger import get_logger
import os

def run_orchestration(repo_path=None, output_base_path=None):
    logger = get_logger("Orchestrator")
    logger.info("Starting orchestration run")

    # Load the agent execution flow from config
    logger.info("Loading config/flow.json")
    with open("config/flow.json") as f:
        flow = json.load(f)

    # Load default configuration for agents and system
    logger.info("Loading config/default_config.json")
    with open("config/default_config.json") as f:
        default_config = json.load(f)

    # Load agent-specific configuration overrides
    logger.info("Loading config/agent_config.json")
    with open("config/agent_config.json") as f:
        agent_configs = json.load(f)

    # Import the Agent class (imported here to avoid circular imports or unnecessary imports if not running orchestration)
    logger.info("Importing Agent class")
    from agents.agent import Agent

    agents = {}
    # Initialize each agent defined in the flow
    for agent_name in flow:
        logger.info(f"Initializing agent: {agent_name}")

        # Directory containing prompt templates for this agent
        prompt_path = f"prompts/{agent_name}/"  

        # Merge default agent config with agent-specific config
        merged_config = {**default_config.get("default_agent_config", {}), **agent_configs.get(agent_name, {})}
        agents[agent_name] = Agent(agent_name, config=merged_config)

        print (f"Agent Name: {agent_name}\n==")
        print (f"Agent Merged Config:\n {merged_config} \n\n")

  

    # Get the first agent in the flow as the starting point
    initial_agent = list(flow.keys())[0]
    print(f"Initial Agent: {initial_agent}")

    # Determine the repository folder to use, from argument or config
    repo_folder_config = default_config.get("repository_folder", "repository")
    repo_folder = Path(repo_path) if repo_path else Path(repo_folder_config)

    print(f"Repo folder : {repo_folder}")

    # Determine the output root directory, from argument or config
    output_root_config = default_config.get("output_folder", "output")
    output_root = Path(output_base_path) if output_base_path else Path(output_root_config)

    print(f"Output Root folder : {output_root}")

    # Ensure the repository and output directories exist
    repo_folder.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    # Iterate over each file in the repository folder (excluding __init__.py)
    for file_path in repo_folder.glob("*.*"):
        if file_path.name == "__init__.py":
            continue  # Skip Python package files

        # File path name without extension
        input_file_name = file_path.stem
        print(f"File Path name without extension: {input_file_name}")
        logger.info(f"\n=== Processing input file: {file_path.name} ===")

        

        # Create a subfolder in the output directory for this input file
        output_subfolder = output_root / input_file_name
        output_subfolder.mkdir(parents=True, exist_ok=True)

        print(f"Output Sub folder : {output_subfolder}")

        output_map = {}  # Stores outputs from each agent for this input file

        # Recursive function to execute an agent and its downstream agents in the flow
        def execute(agent_name, input_file, previous_agents=[]):
            try:
                logger.info(f"Executing {agent_name} on {input_file}...")
                agent = agents[agent_name]

                print(f"Agent Name : {agent}")

                # Get the base output directory from the default_config.json
                base_output_dir = default_config.get("output_folder", "output")
                print(f"base_output_dir : {base_output_dir}")

                # Create a directory for the agent within the base output directory
                # agent_output_dir = Path(base_output_dir) / agent_name
                # agent_output_dir.mkdir(parents=True, exist_ok=True)
                # print(f"agent_output_dir : {agent_output_dir}")

                # # Determine the output file name
                # agent_config = agent_configs.get(agent_name, {})
                # if "output_file" in agent_config:
                #     # Use the explicitly specified output file name
                #     output_file_name = agent_config["output_file"]
                # elif "output_file_suffix" in agent_config:
                #     # Append the suffix to the original input file name
                #     original_file_name = Path(input_path).stem
                #     output_file_name = f"{original_file_name}{agent_config['output_file_suffix']}.txt"
                # else:
                #     # Default to {agent_name}.txt
                #     output_file_name = f"{agent_name}.txt"

                # # Construct the full output path
                # output_path = agent_output_dir / output_file_name

                
                # Gather outputs from previous agents for context
                previous_outputs = {p: output_map[p] for p in previous_agents if p in output_map}

                # Create a subfolder in the output directory for this input file
                output_subfolder = output_root / input_file_name
                output_subfolder.mkdir(parents=True, exist_ok=True)

                print (f"output_subfolder: {output_subfolder}")

    

                # Run the agent on the input file, passing previous outputs as context
                # agent.run(input_path, output_path, previous_outputs)
                agent.run(input_file, output_subfolder, previous_outputs)

                # Read and store the agent's output for use by downstream agents
                # Agent determines the output file name
                output_file = agent.get_output_file_name(input_file) 
                output_path = output_subfolder / output_file
                
                # Read and store the agent's output for use by downstream agents
                with open(output_path, 'r') as f:
                    current_output = f.read()
                output_map[agent_name] = current_output

                # Recursively execute downstream agents as defined in the flow
                for next_agent in flow.get(agent_name, []):
                    execute(next_agent, output_path, previous_agents + [agent_name])
            except Exception as e:
                logger.error(f"Stopping flow: {agent_name} failed: {str(e)}")
                return

        # Start the agent execution flow for this input file
        logger.info(f"Starting flow from agent: {initial_agent}")
        print (f"fiel_path: {file_path}")

        # Noe file_path is the path to the file and includes name
        execute(initial_agent, file_path)
