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
  "provider": "openai",     // or "gemini"
  "model": "gpt-4",         // or "gemini-pro"
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
