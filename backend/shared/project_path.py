from pathlib import Path

project_path = Path(__file__).parents[1]
root_path = project_path.parent
secret_path = root_path / 'secret'
test_path = root_path / 'tests'
logs_path = root_path / 'logs'
static_path = project_path / 'static'
modules_path = project_path / 'modules'