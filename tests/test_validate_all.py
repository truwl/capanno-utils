
import os
from tests.test_base import TestBase
from xd_cwl_utils.config import config
from xd_cwl_utils.validate import validate_tools_dir, validate_scripts_dir, validate_repo


class TestValidateDirectories(TestBase):

    def test_validate_tools_dir(self):
        validate_tools_dir(base_dir=config[os.environ['CONFIG_KEY']]['base_path'])
        return

    def test_validate_scripts_dir(self):
            validate_scripts_dir(base_dir=config[os.environ['CONFIG_KEY']]['base_path'])
            return

    # def test_validate_repo(self):
    #     validate_repo(base_dir=config[os.environ['CONFIG_KEY']]['base_path'])
    #     return