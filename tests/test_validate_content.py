
from tests.test_base import TestBase
from xd_cwl_utils.config import config
from xd_cwl_utils.helpers.get_paths import *
from xd_cwl_utils.validate_content import main as validate_content


class TestValidateTools(TestBase):

    def test_validate_main_tool_dir(self):
        tool_name = 'STAR'
        test_repo_path = self.test_content_dir
        main_tool_dir = get_main_tool_dir(tool_name, base_dir=test_repo_path)
        validate_content([str(main_tool_dir), '-p', str(test_repo_path)])
        return

    def test_validate_tool_version_dir(self):
        tool_name = 'samtools'
        version_name = '1.x'
        tool_version_dir = get_tool_version_dir(tool_name, version_name, base_dir=self.test_content_dir)
        validate_content([str(tool_version_dir), '-p', str(self.test_content_dir)])
        return

    def test_validate_subtool_dir(self):
        tool_name = 'md5sum'
        version_name = '8.x'
        subtool_name = 'check'
        subtool_dir = get_tool_dir(tool_name, version_name, subtool_name, base_dir=self.test_content_dir)
        validate_content([str(subtool_dir), '-p', str(self.test_content_dir)])
        return

    def test_validate_main_subtool_dir(self):
        tool_name = 'md5sum'
        version_name = '8.x'
        subtool_name = None
        subtool_dir = get_tool_dir(tool_name, version_name, subtool_name, base_dir=self.test_content_dir)
        validate_content([str(subtool_dir), '-p', str(self.test_content_dir)])
        return

    def test_validate_common_dir(self):
        tool_name = 'md5sum'
        version_name = '8.x'
        common_dir = get_tool_common_dir(tool_name, version_name, base_dir=self.test_content_dir)
        validate_content([str(common_dir), '-p', str(self.test_content_dir)])
        return