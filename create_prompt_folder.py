import os
from pathlib import Path

def create_agent_prompt_folder(agent_name):
    folder_path = Path("prompts") / agent_name
    folder_path.mkdir(parents=True, exist_ok=True)

    system_prompt_path = folder_path / "system.txt"
    user_template_path = folder_path / "user_template.txt"

    if not system_prompt_path.exists():
        system_prompt_path.write_text("You are a helpful assistant for the agent: " + agent_name)

    if not user_template_path.exists():
        user_template_path.write_text("Input received. Prior outputs were:\n{{previous_1}}\n{{previous_2}}")

    print(f"Created prompt folder: {folder_path}")
    print(f"- {system_prompt_path}")
    print(f"- {user_template_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python create_prompt_folder.py <agent_name>")
    else:
        create_agent_prompt_folder(sys.argv[1])
