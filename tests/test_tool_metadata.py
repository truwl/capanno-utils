import os
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from ruamel.yaml import safe_load
from tests.test_base import TestBase
from xd_cwl_utils.config import config
from xd_cwl_utils.classes.metadata.tool_metadata import ToolMetadata, ParentToolMetadata, SubtoolMetadata
from xd_cwl_utils.add.add_tools import add_tool, add_subtool, add_parent_tool


class TestMakeToolMetadata(TestBase):
    test_dict = {'name':'some_name', 'bad': 'Should not work.', 'softwareVersion': 1}

    def test_make_tool_metadata(self):
        tm = ToolMetadata(name=TestMakeToolMetadata.test_dict['name'], softwareVersion=TestMakeToolMetadata.test_dict['softwareVersion'])
        self.assertTrue(tm.name == TestMakeToolMetadata.test_dict['name'])

    def test_bad_kwarg(self):
        with self.assertRaises(AttributeError):
            tm = ToolMetadata(bad=TestMakeToolMetadata.test_dict['bad'])

    def test_make_file(self):
        tm = ToolMetadata(name=TestMakeToolMetadata.test_dict['name'], softwareVersion=0.1)
        with NamedTemporaryFile(prefix='tool_test', suffix='.yaml', delete=True) as tf:
            temp_file_name = tf.name
            tm.mk_file(temp_file_name, replace_none=False)
            with open(temp_file_name, 'r') as f:
                test_file_dict = safe_load(f)
        self.assertEqual(test_file_dict['name'], TestMakeToolMetadata.test_dict['name'])

    def test_make_from_biotools(self):
        biotools_id = 'star'
        biotools_meta = ToolMetadata.create_from_biotools(biotools_id, softwareVersion=1)
        with NamedTemporaryFile(prefix='biotools', suffix='.yaml', delete=True) as tf:
            biotools_meta.mk_file(tf.name, replace_none=True)
        return

class TestMakeParentToolMetadata(TestBase):
    test_dict = {'name': 'parent_name', 'bad': 'A bad key or value.'}

    def test_make_parent_metadata(self):
        p_metadata = ParentToolMetadata(name=TestMakeParentToolMetadata.test_dict['name'], softwareVersion=1)
        self.assertTrue(p_metadata.name == TestMakeParentToolMetadata.test_dict['name'])

    def test_make_file(self):
        p_metadata = ParentToolMetadata(name=TestMakeParentToolMetadata.test_dict['name'], softwareVersion=1)
        with NamedTemporaryFile(prefix='', suffix='', delete=True) as tf:
            p_metadata.mk_file(tf.name, replace_none=True)
            with open(tf.name, 'r') as file:
                test_file_dict = safe_load(file)
        self.assertEqual(test_file_dict['name'], TestMakeParentToolMetadata.test_dict['name'])


class TestMakeSubtoolMetadata(TestBase):
    test_dict = {'name': 'subtool_name', 'bad': 'A bad key or value.'}
    def test_make_subtool_metadata(self):
        p_metadata = ParentToolMetadata(name=TestMakeParentToolMetadata.test_dict['name'], softwareVersion=1, featureList=['subtool_name'])
        st_metadata = SubtoolMetadata(name=TestMakeSubtoolMetadata.test_dict['name'], _parentMetadata=p_metadata)
        self.assertTrue(st_metadata.name == TestMakeSubtoolMetadata.test_dict['name'])




class TestAddTools(TestBase):

    _foo_tool_name = "ReallyRidiculousToolName"  # Make variable name different so don't overwrite or inadvertently access.
    _foo_softwareVersion = "ThisIsAWeirdSoftwareVersion"
    _foo_subtool_name = 'YeahNo'

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        test_dir = Path().cwd() / 'cwl-tools' / self._foo_tool_name
        shutil.rmtree(test_dir)  # dangerous. Make sure cls.tool_name isn't messed with.


    def test_add_tool(self):
        new_tool_path = add_tool(self._foo_tool_name, self._foo_softwareVersion)
        return

    def test_add_parent_tool(self):
        new_tool_path = add_parent_tool(self._foo_tool_name, self._foo_softwareVersion, self._foo_subtool_name)
        return

    def test_add_subtool(self):
        parent_tool_path = add_parent_tool(self._foo_tool_name, self._foo_softwareVersion, self._foo_subtool_name)
        subtool_path = add_subtool(parent_tool_path, self._foo_subtool_name)
        return

