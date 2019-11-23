

from tempfile import TemporaryDirectory
from tests.test_base import TestBase
from xd_cwl_utils.add.add_tools import add_tool, add_subtool

class TestAddTool(TestBase):

    def test_add_parent_only(self):
        with TemporaryDirectory() as tmp_dir:
            tool_name = 'test__1'
            tool_version = '123'
            new_path = add_tool(tool_name, tool_version, root_repo_path=tmp_dir)
        # print(new_path)
        return



    def test_add_with_main(self):
        with TemporaryDirectory() as tmp_dir:
            tool_name = 'test___2'
            tool_version = '123'
            new_path = add_tool(tool_name, tool_version, has_primary=True, root_repo_path=tmp_dir)
            # print(new_path)
        return


    def test_add_with_subtools(self):
        with TemporaryDirectory() as tmp_dir:
            tool_name = 'test___3'
            tool_version = '123'
            new_path = add_tool(tool_name, tool_version, subtool_names=['first', 'second'], has_primary=True, root_repo_path=tmp_dir)
            # print(new_path)
        return

    def test_add_parent_then_subtool(self):
        with TemporaryDirectory() as tmp_dir:
            tool_name = 'test_tool'
            tool_version = '0.1'
            add_tool(tool_name, tool_version, root_repo_path=tmp_dir)
            add_subtool(tool_name, tool_version, 'subtool1', root_repo_path=tmp_dir, update_featureList=True)
            assert True
        return


    def test_add_multiple(self):
        with TemporaryDirectory() as tmp_dir:
            add_tool('fake_1', '123', root_repo_path=tmp_dir)  # parent only.
            add_tool('fake_2', '123', has_primary=True, root_repo_path=tmp_dir)  # # parent with main tool
            add_tool('fake_3', '123', subtool_names=['first', 'second'], has_primary=True,
                     root_repo_path=tmp_dir)
            assert True
        return