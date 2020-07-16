import tempfile
from unittest import TestCase
import os
from pathlib import Path
from capanno_utils.config import config
from capanno_utils.content_maps import make_tools_map, make_workflow_maps, make_script_maps

test_constants = {'script_group1': 'ENCODE-DCC', 'script_version1': '1.1.x', 'script_project1': 'atac-seq-pipeline',
                  'test_software_version': {'versionName': 'test_version'}}


class TestBase(TestCase):
    projects_path = Path(__file__).parents[2]
    src_content_dir = projects_path / 'cwl-source'
    test_content_dir = Path(__file__).parent / 'test_files' / 'cwl-source'
    invalid_content_dir = Path(__file__).parent / 'test_files' / 'invalid_content'  # Will copy data here, then modify to make invalid.

    def get_content_map_paths(self):
        return {'tool_maps': config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'tool-maps.yaml',
                'script_maps': config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'script-maps.yaml',
                'workflow_maps': config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'workflow-maps.yaml'}

    def update_tool_maps(self):
        outfile_path = self.get_content_map_paths()['tool_maps']
        make_tools_map(outfile_path)

    def update_script_maps(self):
        outfile_path = self.get_content_map_paths()['script_maps']
        make_script_maps(outfile_path)

    def update_workflow_maps(self):
        outfile_path = self.get_content_map_paths()['workflow_maps']
        make_workflow_maps(outfile_path)

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        pass
