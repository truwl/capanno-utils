import os
from tests.test_base import TestBase
from pathlib import Path
from ruamel.yaml import safe_load
from xd_cwl_utils.config import config
from xd_cwl_utils.helpers.get_paths import get_metadata_path
from xd_cwl_utils.validate_metadata import main

class TestValidateContent(TestBase):

    def test_validate_tools(self):
        self.update_tool_maps()
        with self.get_content_map_paths()['tool_maps'].open('r') as tm:
            tool_map_dict = safe_load(tm)
        base_path = config[os.environ['CONFIG_KEY']]['base_path']
        for identifier, values in tool_map_dict.items():
            path = base_path / values['path']

            tool_type = values['type']
            if tool_type == 'parent':
                if not 'common' in path.parts:  # values[type] would be better test.
                    raise ValueError(f"Have a parent tool that is not in a common directory {path}")
                meta_type = 'parent_tool'
                meta_path = path
            else:  # either a subtool or standalone tool.
                meta_path = get_metadata_path(path)
                meta_type = tool_type
            main([meta_type, str(meta_path)])
        return

    def test_validate_scripts(self):
        self.update_script_maps()
        script_map_path = self.get_content_map_paths()['script_maps']
        with script_map_path.open('r') as sm:
            script_map = safe_load(sm)
        base_path = config[os.environ['CONFIG_KEY']]['base_path']
        for script_identifier, script_values in script_map.items():
            metadata_path = base_path / get_metadata_path(Path(script_values['path']))
            main(['script', str(metadata_path)])
        return


    def test_validate_workflows(self):
        self.update_workflow_maps()
        with self.get_content_map_paths()['workflow_maps'].open('r') as wm:
            workflow_map = safe_load(wm)
            base_path = config[os.environ['CONFIG_KEY']]['base_path']

        for workflow_identifier, workflow_values in workflow_map.items():
            metadata_path = base_path / get_metadata_path(workflow_values['path'])
            main(['workflow', str(metadata_path)])
        return