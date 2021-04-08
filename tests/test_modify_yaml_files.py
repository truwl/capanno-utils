
from distutils.dir_util import copy_tree  # b/c shutil.copytree does not support existing dest directories until Python 3.8.
from tempfile import NamedTemporaryFile, TemporaryDirectory
from ruamel.yaml import round_trip_dump, round_trip_load, YAML
from pathlib import Path
from unittest import skip
from tests.test_base import TestBase, test_constants
from capanno_utils.repo_config import content_repo_name
from capanno_utils.repo_config import tools_dir_name
from capanno_utils.helpers.modify_yaml_files import add_field_to_to_yaml_file, update_subtool_metadata_files

class TestModifyYamlFiles(TestBase):
    def test_add_field_to_yaml_file(self):
        test_dict = {'key0': 'value_0', 'key1': 'value_1'}
        yaml = YAML()
        update_dict = {'key_new0': 'new_value0', 'key_new1': 'new_value1'}
        with NamedTemporaryFile(mode='w', prefix='test_addfield1', suffix='.yaml') as tf1: # Create a temporary yaml file
            yaml.dump(test_dict, tf1)
            add_field_to_to_yaml_file(update_dict, tf1.name, after_key='key0')
            assert True
        return

    @skip('')
    def test_modify_yaml_file(self):
        update_dict = {'snakemakeStatus': 'Incomplete', 'nextflowStatus': 'Incomplete', 'wdlStatus': 'Incomplete'}


        with TemporaryDirectory(prefix='test_modify_yaml') as td:
            copy_tree(str(self.test_content_dir), td)
            test_file_path = Path(td) / tools_dir_name / 'gawk' / '4.1.x' / 'gawk' / 'gawk-metadata.yaml'
            update_subtool_metadata_files(test_file_path, update_dict, after_key='cwlStatus')
            assert True
        return

    # @skip('')
    def test_modify_tool_metadata(self):
        update_dict = {'snakemakeStatus': 'Incomplete', 'nextflowStatus': 'Incomplete', 'wdlStatus': 'Incomplete'}

        with TemporaryDirectory(prefix='test_modify_yaml') as td:
            temp_content_dir = f"{td}/{content_repo_name}"
            copy_tree(str(self.test_content_dir), temp_content_dir)
            test_file_path = Path(temp_content_dir) / tools_dir_name
            update_subtool_metadata_files(test_file_path, update_dict, after_key='cwlStatus', base_dir=temp_content_dir)
            assert True
        return