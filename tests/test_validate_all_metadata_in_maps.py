import os
from tests.test_base import TestBase
from pathlib import Path
from ruamel.yaml import safe_load
from src.config import config
from src.helpers.get_paths import get_metadata_path
from src.validate_metadata import main

class TestValidateContent(TestBase):

    def test_validate_tools(self):
        tool_map = config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'tool-maps.yaml'
        with tool_map.open('r') as tm:
            tool_map_dict = safe_load(tm)
        for identifier, values in tool_map_dict.items():
            path = Path(values['path'])
            tool_type = values['type']
            if tool_type == 'parent':
                if not 'common' in path.parts:  # values[type] would be better test.
                    raise ValueError(f"Have a parent tool that is not in a common directory {path}")
                meta_type = 'parent_tool'
                meta_path = path
            else:  # either a subtool or standalone tool.
                meta_path = get_metadata_path(path)
                meta_type = tool_type
            main(meta_type, meta_path)
        return

    def test_validate_scripts(self):
        script_map_path = config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'script-maps.yaml'
        with script_map_path.open('r') as sm:
            script_map = safe_load(sm)
        for script_identifier, script_values in script_map.items():
            metadata_path = get_metadata_path(Path(script_values['path']))
            main('script', metadata_path)
        return


    def test_validate_workflows(self):
        workflow_maps_path =config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'workflow-maps.yaml'
        with workflow_maps_path.open('r') as wm:
            workflow_map = safe_load(wm)
        for workflow_identifier, workflow_values in workflow_map.items():
            metadata_path = get_metadata_path(workflow_values['path'])
            main('workflow', metadata_path)
        return