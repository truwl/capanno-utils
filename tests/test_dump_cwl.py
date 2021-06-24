
from tests.test_base import TestBase
from tempfile import NamedTemporaryFile
from capanno_utils import repo_config
from capanno_utils.helpers.get_paths import get_tool_sources
from capanno_utils.classes.cwl.common_workflow_language import load_document

class TestDumpCwlTool(TestBase):

    def test_dump_to_file(self):
        tool_name = 'cat'
        tool_version = '8.x'
        subtool_name = repo_config.main_tool_subtool_name
        tool_sources = get_tool_sources(tool_name, tool_version, subtool_name, base_dir=self.test_content_dir)
        command_line_tool = load_document(str(tool_sources['cwl']))
        with NamedTemporaryFile() as tf:
            command_line_tool.dump_cwl(tf.name)
            assert True
        return

    def test_dump_to_string(self):
        tool_name = 'cat'
        tool_version = '8.x'
        subtool_name = repo_config.main_tool_subtool_name
        tool_sources = get_tool_sources(tool_name, tool_version, subtool_name, base_dir=self.test_content_dir)
        command_line_tool = load_document(str(tool_sources['cwl']))
        cwl_string = command_line_tool.dump_cwl_str()
        return


class TestDumpCwlWorkflow(TestBase):
    pass