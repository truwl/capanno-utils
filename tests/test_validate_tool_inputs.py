import os
import unittest
from tests.test_base import TestBase
from capanno_utils.repo_config import config
from ruamel.yaml import safe_load
from capanno_utils.validate_inputs import validate_inputs_for_instance
from capanno_utils.helpers.get_paths import get_tool_instance_path, get_tool_sources

class TestValidateInputs(TestBase):

    # @unittest.skip("Comment out and run smaller tests to isolate problems.")
    def test_validate_tool_inputs_1(self):
        tool_name = 'cat'
        tool_version = '8.x'
        input_hash = '8a6c'
        tool_sources = get_tool_sources(tool_name, tool_version)
        instance_path = get_tool_instance_path(tool_name, tool_version, input_hash)
        validate_inputs_for_instance(instance_path, tool_sources['cwl'])
        return


    # @unittest.skip("Comment out and run smaller tests to isolate problems.")
    def test_validate_tool_inputs_2(self):
        tool_name = 'samtools'
        tool_version = '1.x'
        subtool = 'flagstat'
        instance_hash = '395d'
        tool_sources = get_tool_sources(tool_name, tool_version, subtool_name=subtool, base_dir=self.test_content_dir)
        instance_path = get_tool_instance_path(tool_name, tool_version, instance_hash, subtool_name=subtool, base_dir=self.test_content_dir)
        validate_inputs_for_instance(instance_path, tool_sources['cwl'])
        return
    #
    # # @unittest.skip('')
    # def test_validate_all_tool_inputs(self):
    #     tool_map = config[os.environ.get('CONFIG_KEY')]['content_maps_dir'] / 'tool-maps.yaml'  # Need to change this if want to do tests
    #     with tool_map.open('r') as tm:
    #         tool_map_dict = safe_load(tm)
    #     for tool_identifier, tool_data in tool_map_dict.items():
    #         if tool_data['type'] == 'parent':
    #             continue
    #         elif tool_data['type'] == 'tool':
    #             tool_name = tool_data['name']
    #
    #             raise NotImplementedError
    #     return

