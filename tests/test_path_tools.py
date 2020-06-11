
import os
from tests.test_base import TestBase, test_constants
from xd_cwl_utils.helpers.get_paths import get_types_from_path, get_script_metadata, get_script_instance_path, get_cwl_script, get_cwl_tool, get_tool_common_dir, main_tool_subtool_name, get_tool_metadata, get_tool_instance_path, get_tool_instance_metadata_path


class TestGetTypesFromPath(TestBase):

    def test_get_type_from_script_paths(self):

        # Script cwl path
        script_cwl_path = get_cwl_script(test_constants['script_group1'], test_constants['script_project1'],
                                         test_constants['script_version1'], 'encode_ataqc')
        cwl_script_type_tuple = get_types_from_path(str(script_cwl_path))
        self.assertEqual(cwl_script_type_tuple, ('script', 'cwl'))
        script_metadata_path = get_script_metadata(test_constants['script_group1'], test_constants['script_project1'],
                                         test_constants['script_version1'], 'encode_ataqc')

        # Script metadata path
        script_metadata_type_tuple = get_types_from_path(str(script_metadata_path))
        self.assertEqual(script_metadata_type_tuple, ('script', 'metadata'))

        # Script instance/metadata paths. ToDo Need to have a script instance to test.

        # script_instance_path = get_script_instance_path(test_constants['script_group1'], test_constants['script_project1'],
        #                                  test_constants['script_version1'], 'encode_ataqc', '1234')
        # script_instance_type_tuple = get_types_from_path(script_instance_path)

        return

    def test_get_type_from_tool_paths(self):

        tool_name = 'gawk'
        tool_version = '4.1.x'
        subtool_name = main_tool_subtool_name
        instance_hash = '1c10'

        common_metadata_path = get_tool_common_dir(tool_name, tool_version) / 'common-metadata.yaml'
        common_tool_type_tuple = get_types_from_path(common_metadata_path)
        self.assertEqual(common_tool_type_tuple, ('tool', 'common_metadata'))

        tool_cwl_path = get_cwl_tool(tool_name, tool_version, subtool_name)
        cwl_tool_type_tuple = get_types_from_path(tool_cwl_path)
        self.assertEqual(cwl_tool_type_tuple, ('tool', 'cwl'))

        tool_metadata_path = get_tool_metadata(tool_name, tool_version)
        tool_metadata_type_tuple = get_types_from_path(tool_metadata_path)
        self.assertEqual(tool_metadata_type_tuple, ('tool', 'metadata'))

        tool_instance_path = get_tool_instance_path(tool_name, tool_version, instance_hash)
        tool_instance_type_tuple = get_types_from_path(tool_instance_path)
        self.assertEqual(tool_instance_type_tuple, ('tool', 'instance'))

        tool_instance_metadata_path = get_tool_instance_metadata_path(tool_name, tool_version, instance_hash)
        tool_instance_metadata_type_tuple = get_types_from_path(tool_instance_metadata_path)
        self.assertEqual(tool_instance_metadata_type_tuple, ('tool', 'instance_metadata'))

        return