
from shutil import copytree
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.test_base import TestBase
from capanno_utils.add.add_tools import add_tool_instance
from capanno_utils.helpers.get_paths import get_tool_version_dir
import capanno_utils.repo_config as config


class TestAddToolInstance(TestBase):

    def test_add_tool_instance(self):
        tool_name = 'cat'
        tool_version = '8.x'
        subtool_name = config.main_tool_subtool_name
        tool_version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=self.test_content_dir)
        with TemporaryDirectory(prefix=f"{type(self).__name__}_") as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_version_temp_path = Path(tmp_dir) / config.tools_dir_name / tool_name / tool_version
            copytree(tool_version_dir, tool_version_temp_path)  # Copy things to a temp directory so don't screw up real one.
            instance_paths = add_tool_instance(tool_name, tool_version, subtool_name, init_job_file=True,
                                               root_repo_path=tmp_dir)  # returns 2 paths.
            assert True
        return


