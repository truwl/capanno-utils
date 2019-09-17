
import os
from tests.test_base import TestBase
from xd_cwl_utils.config import config
from xd_cwl_utils.validate import validate_tools_dir, validate_scripts_dir


class TestValidateDirectories(TestBase):

    def test_validate_tools_dir(self):
        validate_tools_dir()
        return

    def test_validate_scripts_dir(self):
        validate_scripts_dir()
