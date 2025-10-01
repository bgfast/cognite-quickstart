import os

def find_readme_for_config(project_path: str, config_file: str) -> str | None:
    env_name = config_file.replace('config.', '').replace('.yaml', '')
    readme_patterns = [
        f"README.{env_name}.md",
        f"readme.{env_name}.md",
        f"README.{env_name}.MD",
        f"readme.{env_name}.MD",
    ]
    for pattern in readme_patterns:
        p = os.path.join(project_path, pattern)
        if os.path.exists(p):
            return p
    for root, _, files in os.walk(project_path):
        for file in files:
            if file in readme_patterns:
                return os.path.join(root, file)
    return None

def read_readme_content(readme_path: str) -> str:
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading README: {e}"


