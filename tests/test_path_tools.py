
import os
from tests.test_base import TestBase, test_constants
from xd_cwl_utils.helpers.get_paths import get_types_from_path, get_script_metadata, get_script_instance_path, get_cwl_script


class TestGetTypesFromPath(TestBase):

    def get_script_cwl_types(self):
        script_cwl_path = get_cwl_script(test_constants['script_group1'], test_constants['script_project1'],
                                         test_constants['script_version1'], 'encode_ataqc')
        type_tuple = get_types_from_path(script_cwl_path)


        script_instance_path = get_script_metadata(test_constants['script_group1'], test_constants['script_project1'],
                                         test_constants['script_version1'], 'encode_ataqc')