from . import main as legacy

def run_cognite_toolkit_build(project_path, env_vars=None):
    return legacy.run_cognite_toolkit_build(project_path, env_vars)

def run_cognite_toolkit_deploy(project_path, env_vars=None):
    return legacy.run_cognite_toolkit_deploy(project_path, env_vars)


