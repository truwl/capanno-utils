import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from ruamel.yaml import safe_load
from tests.test_base import TestBase, test_constants
from xd_cwl_utils.config import config
from xd_cwl_utils.helpers.get_paths import get_tool_metadata
from xd_cwl_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata
from xd_cwl_utils.add.add_tools import add_tool, add_subtool



class TestMakeParentToolMetadata(TestBase):
    test_dict = {'name': 'parent_name', 'bad': 'A bad key or value.'}

    def test_make_parent_metadata(self):
        p_metadata = ParentToolMetadata(name=TestMakeParentToolMetadata.test_dict['name'], softwareVersion=test_constants['test_software_version'])
        self.assertTrue(p_metadata.name == TestMakeParentToolMetadata.test_dict['name'])

    def test_make_file(self):
        p_metadata = ParentToolMetadata(name=TestMakeParentToolMetadata.test_dict['name'], softwareVersion=test_constants['test_software_version'])
        with TemporaryDirectory(prefix='xD_test1', suffix='') as tmpdir:
            parent_metadata_path = get_tool_metadata(TestMakeParentToolMetadata.test_dict['name'], test_constants['test_software_version']['versionName'], parent=True, base_dir=tmpdir)
            if not parent_metadata_path.exists():
                parent_metadata_path.parent.mkdir(parents=True)
            p_metadata.mk_file(base_dir=tmpdir, replace_none=True)
            with parent_metadata_path.open('r') as file:
                test_file_dict = safe_load(file)
        self.assertEqual(test_file_dict['name'], TestMakeParentToolMetadata.test_dict['name'])


class TestMakeSubtoolMetadata(TestBase):
    test_dict = {'name': 'subtool_name', 'bad': 'A bad key or value.'}
    def test_make_subtool_metadata(self):
        p_metadata = ParentToolMetadata(name=TestMakeParentToolMetadata.test_dict['name'], softwareVersion=test_constants['test_software_version'], featureList=['subtool_name'])
        st_metadata = SubtoolMetadata(name=TestMakeSubtoolMetadata.test_dict['name'], _parentMetadata=p_metadata)
        self.assertTrue(st_metadata.name == TestMakeSubtoolMetadata.test_dict['name'])

    def test_make_file(self):
        with TemporaryDirectory(prefix="xD_test") as tmpdir:
            add_tool('test1', '1.0', 'subtool1', root_repo_path=tmpdir)
            assert True
        return