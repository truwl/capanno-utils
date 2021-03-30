
from tests.test_base import TestBase
from tempfile import NamedTemporaryFile
from ruamel.yaml import YAML, dump
from capanno_utils.repo_config import config
from capanno_utils.helpers.get_paths import *
from capanno_utils.classes.schema_salad.schema_salad import InputsSchema


class TestMakeCommandLineToolInputsTemplate(TestBase):

    def test_make_command_line_tool_input_template(self):
        tool_name = 'STAR'
        version_name = '2.5'
        subtool_name = 'alignReads'
        tool_sources = get_tool_sources(tool_name, version_name, subtool_name, base_dir=self.test_content_dir)
        inputs_schema = InputsSchema(tool_sources['cwl'])
        template = inputs_schema.make_template()
        yaml = YAML()
        with NamedTemporaryFile(delete=True, prefix=f"{tool_name + subtool_name + version_name}template_", suffix='.yml') as tmp:
            yaml.dump(template, tmp)
            assert True
        return

    def test_make_clt_template_2(self):
        cwl_tool = self.test_files_dir / 'cwl-misc' / 'test_command_line_tool.cwl'
        inputs_schema = InputsSchema(cwl_tool)
        template = inputs_schema.make_template()
        yaml = YAML()
        with NamedTemporaryFile(delete=True, prefix='test_template_', suffix='.yml') as tmp:
            yaml.dump(template, tmp)
        return