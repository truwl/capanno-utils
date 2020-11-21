import os
import unittest
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from ruamel.yaml import safe_load
from tests.test_base import TestBase, test_constants
from capanno_utils.repo_config import config
from capanno_utils.helpers.get_paths import get_tool_metadata
from capanno_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata
from capanno_utils.add.add_tools import add_tool, add_subtool


# @unittest.skip('')
class TestMakeParentToolMetadata(TestBase):
    test_dict = {'name': 'parent_name', 'bad': 'A bad key or value.'}

    def test_make_parent_metadata(self):
        p_metadata = ParentToolMetadata(name=TestMakeParentToolMetadata.test_dict['name'], softwareVersion=test_constants['test_software_version'])
        self.assertTrue(p_metadata.name == TestMakeParentToolMetadata.test_dict['name'])

    def test_make_file(self):
        with TemporaryDirectory(prefix='xD_test1', suffix='') as tmpdir:
            p_metadata = ParentToolMetadata(name=TestMakeParentToolMetadata.test_dict['name'],
                                            softwareVersion=test_constants['test_software_version'], check_index=False, root_repo_path=tmpdir)
            self.make_empty_tools_index(tmpdir)
            parent_metadata_path = get_tool_metadata(TestMakeParentToolMetadata.test_dict['name'], test_constants['test_software_version']['versionName'], parent=True, base_dir=tmpdir)
            if not parent_metadata_path.exists():
                parent_metadata_path.parent.mkdir(parents=True)
            p_metadata.mk_file(base_dir=tmpdir, replace_none=True, update_index=True)  # Don't try to update an index file. There isn't one.
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
            self.make_empty_tools_index(tmpdir)
            add_tool('test1', '1.0', 'subtool1', root_repo_path=tmpdir, refresh_index=False)
            assert True
        return