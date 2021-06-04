import os
from tests.test_base import TestBase
from pathlib import Path
from ruamel.yaml import safe_load
from capanno_utils.repo_config import config
from capanno_utils.helpers.get_paths import get_metadata_path
from capanno_utils.validate_content import main

class TestValidateContent(TestBase):

    def test_validate_tool_metadata(self):
        self.update_tool_maps()
        with self.get_content_map_paths()['tool_maps'].open('r') as tm:
            tool_map_dict = safe_load(tm)
        base_path = config[os.environ['CONFIG_KEY']]['base_path']
        for identifier, values in tool_map_dict.items():
            path = base_path / values['metadataPath']

            tool_type = values['type']
            if tool_type == 'parent':
                if not 'common' in path.parts:  # values[type] would be better test.
                    raise ValueError(f"Have a parent tool that is not in a common directory {path}")
            meta_path = path

            main([str(meta_path), '-q'])

        return

    def test_validate_script_metadata(self):
        self.update_script_maps()
        script_map_path = self.get_content_map_paths()['script_maps']
        with script_map_path.open('r') as sm:
            script_map = safe_load(sm)
        base_path = config[os.environ['CONFIG_KEY']]['base_path']
        for script_identifier, script_values in script_map.items():
            metadata_path = base_path / get_metadata_path(Path(script_values['path']))
            main([str(metadata_path), '-q'])
        return


    def test_validate_workflow_metadata(self):
        self.update_workflow_maps()
        with self.get_content_map_paths()['workflow_maps'].open('r') as wm:
            workflow_map = safe_load(wm)
            base_path = config[os.environ['CONFIG_KEY']]['base_path']

        for workflow_identifier, workflow_map_values in workflow_map.items():
            metadata_path = base_path / workflow_map_values['metadataPath']
            main([str(metadata_path), '-q'])
        return