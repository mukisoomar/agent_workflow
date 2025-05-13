# 
#------NEW CODE ----
from config.config_loader import ConfigLoader
from agents.agent import Agent
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
#------NEW CODE ----
# Ensure the repository (input) and output directories exist
def ensure_directories_exist(repo_folder, output_root):
    """
    Ensure that the repository folder (read-only) and output folder (writable) exist.
    """
    # Repo folder is the input folder where data/code files exist. This is read-only.
    if not repo_folder.exists():
        raise FileNotFoundError(f"Repository folder does not exist: {repo_folder}")
    logger.info(f"Repository folder exists: {repo_folder}")

    # Output folder is the location where each agent will write data. This is writable.
    output_root.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output folder ensured: {output_root}")

def run_orchestration(repo_path=None, output_base_path=None):

    #------NEW CODE ----
    logger.info("Starting orchestration run")

    # Load configurations using ConfigLoader
    config_loader = ConfigLoader()
    default_config = config_loader.get_default_config()
    flow_config = config_loader.get_flow_config()
    agent_config = config_loader.get_agent_config()

    # Determine repository and output directories
    repo_folder = Path(repo_path) if repo_path else Path(default_config.get("repository_folder", "repository"))
    output_root = Path(output_base_path) if output_base_path else Path(default_config.get("output_folder", "output"))

    # Ensure the directories exist
    ensure_directories_exist(repo_folder, output_root)    

    # # Load the agent execution flow from config
    # logger.info("Loading config/flow.json")
    # with open("config/flow.json") as f:
    #     flow = json.load(f)

    # # Load default configuration for agents and system
    # logger.info("Loading config/default_config.json")
    # with open("config/default_config.json") as f:
    #     default_config = json.load(f)

    # # Load agent-specific configuration overrides
    # logger.info("Loading config/agent_config.json")
    # with open("config/agent_config.json") as f:
    #     agent_configs = json.load(f)

    # # Import the Agent class (imported here to avoid circular imports or unnecessary imports if not running orchestration)
    # logger.info("Importing Agent class")
    # from agents.agent import Agent

    #------NEW CODE ----
    # Determine repository and output directories

    agents = {}
    # # Initialize each agent defined in the flow
    for agent_name in flow_config:
        agents[agent_name] = Agent(agent_name, config_loader)
    #     logger.info(f"Initializing agent: {agent_name}")

    #     # Directory containing prompt templates for this agent
    #     prompt_path = f"prompts/{agent_name}/"  

    #     # Merge default agent config with agent-specific config
    #     merged_config = {**default_config.get("default_agent_config", {}), **agent_configs.get(agent_name, {})}
    #     agents[agent_name] = Agent(agent_name, config=merged_config)

    #     print (f"Agent Name: {agent_name}\n==")
    #     print (f"Agent Merged Config:\n {merged_config} \n\n")

  

    # # Get the first agent in the flow as the starting point
    # initial_agent = list(flow.keys())[0]
    # print(f"Initial Agent: {initial_agent}")

    # # Determine the repository folder to use, from argument or config
    # repo_folder_config = default_config.get("repository_folder", "repository")
    # repo_folder = Path(repo_path) if repo_path else Path(repo_folder_config)

    # print(f"Repo folder : {repo_folder}")

    # # Determine the output root directory, from argument or config
    # output_root_config = default_config.get("output_folder", "output")
    # output_root = Path(output_base_path) if output_base_path else Path(output_root_config)

    # print(f"Output Root folder : {output_root}")

    # # Ensure the repository and output directories exist
    # repo_folder.mkdir(parents=True, exist_ok=True)
    # output_root.mkdir(parents=True, exist_ok=True)

    # Iterate over each file in the repository folder (excluding __init__.py)
    for file_path in repo_folder.glob("*.*"):
        if file_path.name == "__init__.py":
            continue  # Skip Python package files

        # # File path name without extension
        # input_file_name = file_path.stem
        # print(f"File Path name without extension: {input_file_name}")
        # logger.info(f"\n=== Processing input file: {file_path.name} ===")

        

        # # Create a subfolder in the output directory for this input file
        # output_subfolder = output_root / input_file_name
        # output_subfolder.mkdir(parents=True, exist_ok=True)

        # print(f"Output Sub folder : {output_subfolder}")

        input_file_name = file_path.stem
        output_subfolder = output_root / input_file_name
        output_subfolder.mkdir(parents=True, exist_ok=True)

        logger.info(f"Processing file: {file_path.name}")
        logger.info(f"Output subfolder: {output_subfolder}")

        output_map = {}  # Stores outputs from each agent for this input file

        # Recursive function to execute an agent and its downstream agents in the flow
        def execute(agent_name, input_file, previous_agents=[]):
            try:
                logger.info(f"Executing {agent_name} on {input_file}...")
                agent = agents[agent_name]

                # Gather outputs from previous agents for context
                previous_outputs = {p: output_map[p] for p in previous_agents if p in output_map}

                # Run the agent on the input file, passing previous outputs as context
                agent.run(input_file, output_subfolder, previous_outputs)

                # Determine the output file name
                output_file = agent.get_output_file_name(input_file)
                output_path = output_subfolder / output_file

                # Read and store the agent's output for use by downstream agents
                with open(output_path, 'r') as f:
                    current_output = f.read()
                output_map[agent_name] = current_output

                # Recursively execute downstream agents as defined in the flow
                for next_agent in flow_config.get(agent_name, []):
                    execute(next_agent, output_path, previous_agents + [agent_name])
            except Exception as e:
                logger.error(f"Stopping flow: {agent_name} failed: {str(e)}")
                return

        # Start the agent execution flow for this input file
        initial_agent = list(flow_config.keys())[0]
        logger.info(f"Starting flow from agent: {initial_agent}")
        execute(initial_agent, file_path)
