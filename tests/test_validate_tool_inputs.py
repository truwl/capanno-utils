import os
import unittest
from tests.test_base import TestBase
from src.config import config
from ruamel.yaml import safe_load
from src.validate_inputs import validate_inputs_for_instance
from src.helpers.get_paths import get_cwl_tool, get_tool_instance_path
from src.classes.schema_salad.schema_salad import InputsSchema

class TestValidateInputs(TestBase):

    # @unittest.skip("Comment out and run smaller tests to isolate problems.")
    def test_validate_tool_inputs_1(self):
        tool_name = 'cat'
        tool_version = '8.25'
        input_hash = '8a6c'
        validate_inputs_for_instance(tool_name, tool_version, input_hash)
        return


    # @unittest.skip("Comment out and run smaller tests to isolate problems.")
    def test_validate_tool_inputs_2(self):
        tool_name = 'samtools'
        tool_version = '1.3'
        subtool = 'flagstat'
        instance_hash = '395d'
        validate_inputs_for_instance(tool_name, tool_version, instance_hash, subtool_name=subtool)
        return

    @unittest.skip('')
    def test_validate_all_tool_inputs(self):
        tool_map = config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'tool-maps.yaml'
        with tool_map.open('r') as tm:
            tool_map_dict = safe_load(tm)
        for tool_identifier, tool_data in tool_map_dict.items():
            if tool_data['type'] == 'parent':
                continue
            elif tool_data['type'] == 'tool':
                tool_name = tool_data['name']

                raise NotImplementedError
        return

