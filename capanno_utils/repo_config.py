# Someday these files will be stored in the content repo themselves.

import os
import re
import tempfile
from pathlib import Path

test_rel_content_path = Path.cwd() / 'tests' / 'test_files' / 'capanno'
if os.environ.get('TRAVIS_BUILD_DIR'):
    travis_root = Path(os.environ['TRAVIS_BUILD_DIR']) / 'tests' / 'test_files' / 'capanno'
else:
    travis_root = Path.cwd()

content_base_path = Path.cwd()

content_maps_dir_name = 'content_maps'

main_tool_subtool_name = '__main__'  # store here so can change easily. This is the 'name' of the main tool (categorized as a subtool).

instance_file_pattern = re.compile(r'[0-9a-f]{4}\.ya?ml')

instance_metadata_file_pattern = re.compile(r'[0-9a-f]{4}-metadata\.ya?ml')

metadata_file_pattern = re.compile(r'[.0-9A-Za-z_-]+-metadata\.ya?ml')

parent_tool_identifier_pattern = re.compile(r'TL_[0-9a-f]{6}\.[0-9a-f]{2}$')

subtool_identifier_pattern = re.compile(r'TL_[0-9a-f]{6}_[0-9a-f]{2}\.[0-9a-f]{2}$')

tool_instance_identifier_pattern = re.compile(r'TL_[0-9a-f]{6}_[0-9a-f]{2}\.[0-9a-f]{2}\.[0-9a-f]{4}$')

workflow_identifier_pattern = re.compile(r'WF_[0-9a-f]{6}\.[0-9a-f]{2}$')

workflow_instance_identifier_pattern = re.compile(r'WF_[0-9a-f]{6}\.[0-9a-f]{2}\.[0-9a-f]{4}$')

common_dir_name = 'common'

common_tool_metadata_name = 'common-metadata.yaml'

instances_dir_name = 'instances'

content_repo_name = 'capanno'

tools_dir_name = 'tools'

scripts_dir_name = 'scripts'

workflows_dir_name = 'workflows'

tool_identifier_prefix = 'TL'

script_identifier_prefix = 'ST'

worklfow_identifier_prefix = 'WF'

tools_map_name = '.tools_map.yaml'

scripts_maps_name = '.scripts_map.yaml'

workflow_maps_name = 'workflows_map.yaml'  # why are the others hidden and this one isn't?

identifier_index_dir = Path('.cache')

tool_index_file_name = 'tools_index'

tool_index_path = identifier_index_dir / tool_index_file_name


def make_config_dict(base_path):
    base_path = Path(base_path)  # Make sure any string values are turned into Path objects.
    config_dict = {
        'base_path': base_path,
        'content_maps_dir': base_path / content_maps_dir_name,
        'temp_dir': tempfile.TemporaryDirectory(prefix=f"{content_repo_name}_Test_"),
    }
    return config_dict


# Default values for using tool in repos.
_default = make_config_dict(content_base_path)

# Test values for running unit tests.
_test = make_config_dict(test_rel_content_path)

_travis = make_config_dict(travis_root)

config = {'TEST': _test, 'DEFAULT': _default, 'TRAVIS': _travis}


def make_full_config_dict():
    config_dict = _default
    constants = dict([
        ('content_maps_dir_name', 'content_maps'),
        ('main_tool_subtool_name', '__main__'),
        ('common_dir_name', 'common'),
        ('common_tool_metadata_name', 'common-metadata.yaml'),
        ('instances_dir_name', 'instances'),
        ('content_repo_name', 'capanno'),
        ('tools_dir_name', 'tools'),
        ('scripts_dir_name', 'scripts'),
        ('workflows_dir_name', 'workflows'),
        ('scripts_maps_name', '.scripts_map.yaml'),
        ('workflow_maps_name', 'workflows_map.yaml'),
        ('tool_index_file_name', 'tools_index'),
    ])
    config_dict.update(constants)
    return config_dict

config_dict = make_full_config_dict()
