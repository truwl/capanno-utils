import os
import tempfile
from tests.test_base import TestBase
from xd_cwl_utils.config import config
from xd_cwl_utils.content_maps import make_tools_map, make_script_map, make_script_maps

class TestToolMaps(TestBase):

    def test_make_tools_map(self):
        outfile_path = config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'tool-maps.yaml'
        make_tools_map(outfile_path)
        return


    def test_make_script_map(self):
        group_name = 'ENCODE-DCC'
        project = 'atac-seq-pipeline'
        version = 'v1.1'
        make_script_map(group_name, project, version)

    def test_make_script_maps(self):

        make_script_maps(tempfile.NamedTemporaryFile().name)
        return