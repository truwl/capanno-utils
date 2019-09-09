
import os
from src.config import  config
from tests.test_base import TestBase
from src.helpers.get_paths import get_cwl_tool, get_tool_inputs
from src.classes.schema_salad.schema_salad import InputsSchema
from src.validate_tool_inputs import validate_tool_inputs

class TestValidateInputs(TestBase):

    def test_validate_tool_inputs_1(self):
        tool_name = 'cat'
        tool_version = '8.25'
        cwl_path = get_cwl_tool(tool_name, tool_version)
        inputs_schema = InputsSchema(cwl_path)
        document_path = get_tool_inputs(tool_name, tool_version, '8a6c')
        inputs_schema.validate_inputs(document_path)
        return

    def test_validate_tool_inputs_2(self):
        tool_name = 'samtools'
        tool_version = '1.3'
        subtool = 'flagstat'
        instance_hash = '395d'
        cwl_path = get_cwl_tool(tool_name, tool_version, subtool_name=subtool)
        inputs_schema = InputsSchema(cwl_path)
        document_path = get_tool_inputs(tool_name, tool_version, instance_hash, subtool_name=subtool)
        inputs_schema.validate_inputs(document_path)

        return
