import configparser
import tempfile
from pathlib import Path

test_rel_content_path = Path.cwd() / 'tests' / 'test_files' / 'test_content'
travis_root = Path('/home/travis/build/xDBio-Inc/cwl-source')
content_base_path = Path.cwd()

tools_dir_name = 'cwl-tools'
scripts_dir_name = 'cwl-scripts'
workflow_dir_name = 'cwl-workflows'
content_maps_dir_name = 'content_maps'


def make_config_dict(base_path):
    base_path = Path(base_path)  # Make sure any string values are turned into Path objects.
    config_dict = {
        'base_path': base_path,
        'content_maps_dir': base_path / content_maps_dir_name,
        'temp_dir': tempfile.TemporaryDirectory(prefix='cwlTest_'),
    }
    return config_dict


# Default values for using tool in repos.
_default = make_config_dict(content_base_path)

# Test values for running unit tests.
_test = make_config_dict(test_rel_content_path)

_travis = make_config_dict(travis_root)

config = {'TEST': _test, 'DEFAULT': _default, 'TRAVIS': _travis}
