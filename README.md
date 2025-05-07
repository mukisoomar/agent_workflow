# 🧠 Agent Orchestrator Framework

This is a modular framework for orchestrating agents that process input files through a multi-step pipeline. Each agent performs a transformation on the input, and the output is passed downstream in a configurable flow.

---

## 📁 Folder Structure

```
agent_orchestrator_refactored/
├── agents/              # Contains BaseAgent and a generic Agent implementation
├── orchestrator/        # Orchestration logic to run agent pipelines
├── utils/               # Logging setup
├── config/              # Flow configuration (flow.json)
├── prompts/             # System prompt per agent (e.g., agent_generate_brd.txt)
├── repository/          # Input files to be processed
├── output/              # Output folder structured by input file name
├── main.py              # Entry point
├── requirements.txt
```

---

## ⚙️ How It Works

1. **Drop input files** (e.g., `.tal` files) into the `repository/` folder.
2. **Define agent flow** in `config/flow.json`.
3. **Provide a system prompt** in `prompts/{agent_name}.txt` for each agent.
4. Run the orchestrator:

```bash
python main.py
```

Each file in `repository/` is fed to the first agent. Outputs are written in `output/{filename}/` for every agent in the chain.

---

## 🔁 Sample `flow.json`

```json
{
  "agent_document_tal_code": ["agent_generate_brd"],
  "agent_generate_brd": ["agent_generate_java_tech_specs"],
  "agent_generate_java_tech_specs": ["agent_generate_java_code"],
  "agent_generate_java_code": []
}
```

This defines a sequence: `agent_document_tal_code → agent_generate_brd → agent_generate_java_tech_specs → agent_generate_java_code`.

---

## 🧩 Prompt Example

`prompts/agent_generate_brd.txt`:

```
You are a business analyst generating a BRD from the TAL code provided.
```

---

## 🔐 Optional: OpenAI Integration

To integrate real LLM APIs:

- Replace the simulated logic in `Agent.run()` with a call to `openai.ChatCompletion.create()`.
- Load your API key using `.env` or environment variables.

---

## ✅ Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 📦 Output Example

For a file named `sample1.tal`:

```
output/
└── sample1/
    ├── agent_document_tal_code.txt
    ├── agent_generate_brd.txt
    ├── agent_generate_java_tech_specs.txt
    └── agent_generate_java_code.txt
```

To specify a file name in the agent_config.json that appends custom text to the original file name, you can use a placeholder or a convention in the `output_file` field. For example, you can specify a suffix to be appended to the original file name.

### Example agent_config.json:

```json
{
  "agent_generate_java_code": {
    "provider": "gemini",
    "model": "gemini-2.5-pro-exp-03-25",
    "temperature": 0.1,
    "top_p": 0.9,
    "n": 1,
    "max_tokens": 1000000,
    "output_file_suffix": "_java_code"
  },
  "agent_generate_brd": {
    "provider": "gemini",
    "model": "gemini-2.5-pro-exp-03-25",
    "temperature": 0.1,
    "top_p": 0.9,
    "n": 1,
    "max_tokens": 1000000,
    "output_file_suffix": "_brd"
  },
  "agent_tal_tech_specs": {
    "provider": "gemini",
    "model": "gemini-2.5-pro-exp-03-25",
    "temperature": 0.1,
    "top_p": 0.9,
    "n": 1,
    "max_tokens": 1000000,
    "output_file_suffix": "_tech_specs"
  },
  "agent_call_external_service": {
    "output_file": "external_output.txt"
  }
}
```

### Updated Code to Handle Suffix:

You can modify the `execute` function to handle this logic. If `output_file_suffix` is specified in the agent_config.json, it will append the suffix to the original file name.

```python
def execute(agent_name, input_path, previous_agents=[]):
    try:
        logger.info(f"Executing {agent_name} on {input_path}...")
        agent = agents[agent_name]

        # Get the base output directory from the default_config.json
        base_output_dir = default_config.get("output_folder", "output")

        # Create a directory for the agent within the base output directory
        agent_output_dir = Path(base_output_dir) / agent_name
        agent_output_dir.mkdir(parents=True, exist_ok=True)

        # Determine the output file name
        agent_config = agent_configs.get(agent_name, {})
        if "output_file" in agent_config:
            # Use the explicitly specified output file name
            output_file_name = agent_config["output_file"]
        elif "output_file_suffix" in agent_config:
            # Append the suffix to the original input file name
            original_file_name = Path(input_path).stem
            output_file_name = f"{original_file_name}{agent_config['output_file_suffix']}.txt"
        else:
            # Default to {agent_name}.txt
            output_file_name = f"{agent_name}.txt"

        # Construct the full output path
        output_path = agent_output_dir / output_file_name

        # Gather outputs from previous agents for context
        previous_outputs = {p: output_map[p] for p in previous_agents if p in output_map}

        # Run the agent on the input file, passing previous outputs as context
        agent.run(input_path, output_path, previous_outputs)

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
```

### Explanation of how output files are generated:

1. **`output_file`**:

   - If explicitly specified in agent_config.json, it will use this value as the file name.

2. **`output_file_suffix`**:

   - If `output_file_suffix` is specified, it appends the suffix to the original input file name (e.g., `input_file_java_code.txt`).

3. **Default Behavior**:
   - If neither `output_file` nor `output_file_suffix` is specified, it defaults to `{agent_name}.txt`.

### Example Behavior:

- For `agent_generate_java_code`:
  - Input file: `example_input.txt`
  - Output file: `example_input_java_code.txt`
- For `agent_call_external_service`:
  - Output file: `external_output.txt` (explicitly specified in the config).

---

## 🙌 Extend This

- Add custom agent subclasses for advanced logic.
- Use LangChain, Gemini, or other LLMs.
- Add a Streamlit interface to visualize results.

---

## 🔐 API Key Setup

Create a `.env` file in the root directory with your OpenAI key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

Ensure you have [an OpenAI account](https://platform.openai.com/) and billing enabled.

You can also switch to Gemini API integration if needed by customizing the `Agent.run()` method.

---

## ⚙️ Model Configuration

### Global defaults

You can configure global model parameters in:

```
config/default_model_config.json
```

Example:

```json
{
  "model": "gpt-4",
  "temperature": 0.3,
  "max_tokens": 1024
}
```

### Per-agent overrides

Customize specific agents in:

```
config/agent_config.json
```

Example:

```json
{
  "agent_generate_brd": {
    "temperature": 0.2
  },
  "agent_generate_java_code": {
    "max_tokens": 2048
  }
}
```

Each agent will merge its config with the defaults and call OpenAI using its own settings.

---

## 🧠 OpenAI & Gemini Support

You can run the agent framework with either:

- `OpenAI` (ChatGPT)
- `Gemini` (Google)

### 🔧 To configure:

In `config/default_model_config.json` or per-agent in `agent_config.json`, specify:

```json
{
  "provider": "openai", // or "gemini"
  "model": "gpt-4", // or "gemini-pro"
  "temperature": 0.3,
  "max_tokens": 1024
}
```

---

## 🔐 API Key Setup

Add a `.env` file with one or both of:

```
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

---

## 📊 Token Usage Logging

Each agent logs:

- Prompt token count
- Completion token count
- Total token usage

Log files are written to:

```
logs/agent.log
```

This helps monitor cost and efficiency of each LLM call.

---

## 🧠 How Prompts Work in Agents

Each agent constructs a full conversation prompt before sending it to the LLM. This is based on three parts:

### 1. 🧾 System Prompt

- File: `prompts/{agent_name}/system.txt`
- This sets the behavior of the LLM (e.g., "You are an expert Java developer...")

### 2. 🧩 User Prompt Template

- File: `prompts/{agent_name}/user_template.txt`
- This is a template containing placeholders for context, such as:

```txt
Use the following business requirements and technical specs to generate Java code:

Business Requirements:
{{agent_generate_brd}}

Technical Specs:
{{agent_generate_java_tech_specs}}
```

- These placeholders are replaced with actual outputs from earlier agents by name.

### 3. 🧠 Assistant Context Messages

- Each previous agent's output is also added as a separate message in the conversation:

```json
{
  "role": "assistant",
  "content": "[Context from agent_generate_brd]:\n<output text here>"
}
```

This gives the LLM the full conversational history including prior content — which helps it make better decisions.

---

## 🗃 Example Message Construction

Let’s say `agent_generate_java_code` is being executed. Here's how its message list will look:

```json
[
  {
    "role": "system",
    "content": "You are an expert Java developer tasked with converting specs into Java classes."
  },
  {
    "role": "assistant",
    "content": "[Context from agent_generate_brd]:\n...BRD Output..."
  },
  {
    "role": "assistant",
    "content": "[Context from agent_generate_java_tech_specs]:\n...Tech Specs Output..."
  },
  {
    "role": "user",
    "content": "Use the following inputs to generate code:\nBRD:\n{{agent_generate_brd}}\nSpecs:\n{{agent_generate_java_tech_specs}}"
  }
]
```

Both the assistant context and user prompt contain the same values — but structured differently to align with how LLMs use context and instruction.

---

## 🏁 Final Output

After executing, the LLM response is saved to:

```
output/<input_filename>/<agent_name>.txt
```

Each agent receives its input from the original file or a previous output, and all context is propagated automatically.

---

## 🔌 Extending Agents for Custom Logic

You can create custom agents by subclassing the base `Agent` class. This allows you to run additional logic like calling external APIs, validating results, or preprocessing input data.

### 🧪 Example: Agent with External API Call

File: `agents/agent_call_external_service.py`

```python
import requests
from agents.agent import Agent

class AgentCallExternalService(Agent):
    def run(self, input_path, output_folder, previous_outputs=None):
        self.logger.info("Calling external service...")

        try:
            response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.logger.error(f"External call failed: {e}")
            raise RuntimeError("Could not fetch external data")

        # Add external data as context
        if previous_outputs is None:
            previous_outputs = {}
        previous_outputs["external_service"] = f"Todo fetched: {data['title']}"

        # Run the standard LLM agent logic
        super().run(input_path, output_folder, previous_outputs)
```

### 🧩 Configuration

#### `config/flow.json`

```json
{
  "agent_call_external_service": []
}
```

#### `config/agent_config.json`

```json
{
  "agent_call_external_service": {
    "output_file": "external_output.txt"
  }
}
```

### 🧠 Use Case

- Pre-fetch knowledge from APIs
- Query databases or search indexes
- Combine external reasoning with LLM output
