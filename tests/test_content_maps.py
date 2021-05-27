import os
import tempfile
from tests.test_base import TestBase
from capanno_utils.repo_config import config
from capanno_utils.content_maps import make_tools_map, make_script_maps


class TestToolMaps(TestBase):

    def test_make_tools_map(self):
        make_tools_map(tempfile.NamedTemporaryFile().name)
        return

    def test_make_tools_map_with_exists_status(self):
        make_tools_map(tempfile.NamedTemporaryFile().name, specify_exists=True)
        return

    def test_make_script_maps(self):
        make_script_maps(tempfile.NamedTemporaryFile().name)
        return
