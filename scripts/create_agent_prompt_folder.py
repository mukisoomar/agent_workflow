import os
import sys

def create_agent_prompt_folder(agent_name):
    base_path = os.path.join("prompts", agent_name)
    os.makedirs(base_path, exist_ok=True)

    system_prompt_path = os.path.join(base_path, "system.txt")
    user_template_path = os.path.join(base_path, "user_template.txt")

    if not os.path.exists(system_prompt_path):
        with open(system_prompt_path, "w") as f:
            f.write("You are a helpful assistant specialized in {0} tasks.".format(agent_name))

    if not os.path.exists(user_template_path):
        with open(user_template_path, "w") as f:
            f.write("Process the input using prior outputs: {{previous_1}}, {{previous_2}}, etc.")

    print(f"Created prompt folder and templates for: {agent_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_agent_prompt_folder.py <agent_name>")
    else:
        create_agent_prompt_folder(sys.argv[1])
