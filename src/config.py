import configparser
import tempfile
from pathlib import Path

test_rel_content_path = Path.cwd() / 'tests' / 'test_files' / 'test_content'
content_base_path = Path.cwd()

# Default values for using tool in repos.
_default = {
    'cwl_tool_directory': content_base_path / 'cwl-tools',
    'cwl_script_dir': content_base_path / 'cwl-scripts',
    'cwl_workflows_dir': test_rel_content_path / 'cwl-workflows',
    'content_maps_dir': Path.cwd() / 'content_maps',
    'temp_dir': tempfile.TemporaryDirectory(prefix='cwlTest_')
}

# Test values for running unit tests.
_test = {
    'cwl_tool_dir': test_rel_content_path / 'cwl-tools',
    'cwl_script_dir': test_rel_content_path / 'cwl-scripts',
    'cwl_workflows_dir': test_rel_content_path / 'cwl-workflows',
    'content_maps_dir': test_rel_content_path / 'content_maps',
    'temp_dir': tempfile.TemporaryDirectory(prefix='cwlTest_'),
}


config = {'TEST': _test, 'DEFAULT': _default}