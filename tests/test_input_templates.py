
from tests.test_base import TestBase
from capanno_utils.config import config
from capanno_utils.helpers.get_paths import *
from capanno_utils.classes.schema_salad.schema_salad import InputsSchema


class TestMakeCommandLineToolInputsTemplate(TestBase):

    def test_make_command_line_tool_input_template(self):
        tool_name = 'STAR'
        version_name = '2.5'
        subtool_name = 'alignReads'
        cwl_tool = get_cwl_tool(tool_name, version_name, subtool_name, base_dir=self.test_content_dir)
        inputs_schema = InputsSchema(cwl_tool)
        inputs_schema.make_template()
