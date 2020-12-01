#
# * This file is subject to the terms and conditions defined in
# * file 'LICENSE.txt', which is part of this source code package.

import os
from pathlib import Path
from ruamel.yaml import safe_load
from capanno_utils.repo_config import config
from tests.test_base import TestBase, test_constants
from capanno_utils.classes.metadata.script_metadata import ScriptMetadata
from capanno_utils.helpers.get_paths import get_cwl_script, get_metadata_path

class TestScriptMetadata(TestBase):

    # def test_make_script_metadata_from_kwargs(self):
    #     kwargs = {'name': 'test_script', 'softwareVersion': test_constants['test_software_version'], 'identifier': 'ST_abcdef.12'}
    #     st_metadata = ScriptMetadata(**kwargs)
    #     self.assertEqual(st_metadata.name, kwargs['name'])
    #     self.assertEqual(st_metadata.identifier, kwargs['identifier'])
    #     return
    #
    # def test_mk_file_from_script_metadata(self):
    #     kwargs = {'name': 'test_script', 'softwareVersion': test_constants['test_software_version'], 'identifier': 'ST_abcdef.12'}
    #     st_metadata = ScriptMetadata(**kwargs)
    #     test_filename = Path(config[os.environ.get('CONFIG_KEY')]['temp_dir'].name) / 'script_test_metadata.yaml'
    #     st_metadata.mk_file(test_filename)
    #     with test_filename.open('r') as file:
    #         test_file_dict = safe_load(file)
    #     self.assertEqual(test_file_dict['identifier'], kwargs['identifier'])
    #     os.remove(test_filename)
    #
    # def test_make_script_metadata_from_file(self):
    #     script_path = get_cwl_script(test_constants['script_group1'], test_constants['script_project1'],test_constants['script_version1'], 'encode_ataqc')
    #     metadata_path = get_metadata_path(script_path)
    #     st_metadata = ScriptMetadata.load_from_file(metadata_path)
    #     return

    # @skip("Pass")
    def test_mk_file_with_inherited_data(self):
        script_cwl_path = get_cwl_script(test_constants['script_group1'], test_constants['script_project1'],test_constants['script_version1'], 'encode_ataqc')
        metadata_path = get_metadata_path(script_cwl_path)
        st_metadata = ScriptMetadata.load_from_file(metadata_path)
        test_filename = Path(config[os.environ.get('CONFIG_KEY')]['temp_dir'].name) / 'script2_test_metadata.yaml'
        st_metadata.mk_completed_file(test_filename)
        with test_filename.open('r') as file:
            test_file_dict = safe_load(file)
        self.assertEqual(test_file_dict['license'], 'MIT')
        os.remove(test_filename)
        return

    # def test_mk_file_without_inherited_data(self):
    #     script_cwl_path = get_cwl_script(test_constants['script_group1'], test_constants['script_project1'],test_constants['script_version1'], 'encode_ataqc')
    #     metadata_path = get_metadata_path(script_cwl_path)
    #     st_metadata = ScriptMetadata.load_from_file(metadata_path)
    #     test_filename = Path(config[os.environ.get('CONFIG_KEY')]['temp_dir'].name) / 'script3_test_metadata.yaml'
    #     st_metadata.mk_file(test_filename)
    #     with test_filename.open('r') as file:
    #         test_file_dict = safe_load(file)
    #     with self.assertRaises(KeyError):
    #         license = test_file_dict['license']
    #     os.remove(test_filename)
    #     return