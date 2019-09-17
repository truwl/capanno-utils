
import os
from tests.test_base import TestBase
from xd_cwl_utils.config import config
from xd_cwl_utils.validate import validate_tools_dir


class TestValidateDirectories(TestBase):

    def test_validate_tools_dir(self):
        tools_dir = config[os.environ['CONFIG_KEY']]['cwl_tool_dir']
        print(tools_dir)
        validate_tools_dir(tools_dir)
        return