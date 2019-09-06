import os
from pathlib import Path
from tests.test_base import TestBase
from src.config import config
from src.content_maps import make_tools_map, make_script_map, make_script_maps

class TestToolMaps(TestBase):

    def test_make_tools_map(self):
        tools_dir = config[os.environ.get('CONFIG_KEY')]['cwl_tool_dir']
        outfile_path = config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'tool-maps.yaml'
        make_tools_map(tools_dir, outfile_path)
        return


    def test_make_script_map(self):
        group_name = 'ENCODE-DCC'
        project = 'atac-seq-pipeline'
        version = 'v1.1'
        make_script_map(group_name, project, version)

    def test_make_script_maps(self):
        make_script_maps()
        return