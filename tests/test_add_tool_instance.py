
from pathlib import Path
from tests.test_base import TestBase
from capanno_utils.add.add_tools import add_tool_instance
import capanno_utils.config as config


class TestAddToolInstance(TestBase):

    def test_add_tool_instance(self):
        tool_name = 'cat'
        tool_version = '8.x'
        subtool_name = config.main_tool_subtool_name
        instance_paths = add_tool_instance(tool_name, tool_version, subtool_name, init_job_file=True, root_repo_path=self.test_content_dir)  # returns 2 paths.
        for path in instance_paths:  # remove these here. Should always have two  paths since init_job_file is True.
            path = Path(path)
            path.unlink()
        return

