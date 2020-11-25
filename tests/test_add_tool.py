

from tempfile import TemporaryDirectory
from tests.test_base import TestBase
from capanno_utils.add.add_tools import add_tool, add_subtool
from capanno_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata
from capanno_utils.helpers.get_paths import get_tool_metadata
from capanno_utils.content_maps import make_tools_index
from capanno_utils.exceptions import InIndexError

class TestAddTool(TestBase):

    def test_add_parent_only(self):
        with TemporaryDirectory(prefix='dont_see me_') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_name = 'test__1'
            tool_version = '123'
            add_tool(tool_name, tool_version, root_repo_path=tmp_dir, refresh_index=False)  # Index is not refreshed because there is nothing in the content repo. Will throw FileNotFound error when trying to traverse directories.
            # the tool added should be the only identifier in the index.
            parent_metadata_path = get_tool_metadata(tool_name, tool_version, parent=True, base_dir=tmp_dir)
            with self.assertRaises(InIndexError):  # This should fail because trying to assign identifier that is already uses (by itself).
                parent_metadata = ParentToolMetadata.load_from_file(parent_metadata_path, _in_index=False,
                                                                    root_repo_path=tmp_dir)
                assert True
            parent_metadata = ParentToolMetadata.load_from_file(parent_metadata_path, root_repo_path=tmp_dir) # this should succeed with the _in_index flag.
            assert True
        return


    def test_add_with_main(self):
        with TemporaryDirectory() as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_name = 'test___2'
            tool_version = '123'
            add_tool(tool_name, tool_version, has_primary=True, root_repo_path=tmp_dir, refresh_index=False)
        return


    def test_add_with_subtools(self):
        with TemporaryDirectory() as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_name = 'test___3'
            tool_version = '123'
            add_tool(tool_name, tool_version, subtool_names=['first', 'second'], has_primary=True, root_repo_path=tmp_dir, refresh_index=False)
            assert True
        return

    def test_add_parent_then_subtool(self):
        with TemporaryDirectory() as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_name = 'test_tool'
            tool_version = '0.1'
            add_tool(tool_name, tool_version, root_repo_path=tmp_dir, refresh_index=False)
            add_subtool(tool_name, tool_version, 'subtool1', root_repo_path=tmp_dir, update_featureList=True)
            assert True
        return


    def test_add_multiple(self):
        with TemporaryDirectory() as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            add_tool('fake_1', '123', root_repo_path=tmp_dir, refresh_index=False)  # parent only. Don't try to assemble index. Paths it would need to access aren't there yet.
            add_tool('fake_2', '123', has_primary=True, root_repo_path=tmp_dir)  # # parent with main tool
            add_tool('fake_3', '123', subtool_names=['first', 'second'], has_primary=True,
                     root_repo_path=tmp_dir)
            assert True
        return

    def test_handle_duplicate_subtool_identifier(self):
        """
        Add subtools one at a time.
        :return:
        """
        tool_name = 'samtools'
        tool_version = '1.x'
        subtool_name = 'dict'  # both subtool identifiers start with 'bb'
        subtool_name_2 = 'faidx'
        with TemporaryDirectory() as temp_dir:
            self.make_empty_tools_index(temp_dir)
            add_tool(tool_name, tool_version, subtool_name, root_repo_path=temp_dir, refresh_index=False)
            add_subtool(tool_name, tool_version, subtool_name_2, root_repo_path=temp_dir, update_featureList=True)
            subtool_1_metadata_path = get_tool_metadata(tool_name, tool_version, subtool_name, base_dir=temp_dir)
            subtool_2_metadata_path = get_tool_metadata(tool_name, tool_version, subtool_name_2, base_dir=temp_dir)
            with self.assertRaises(InIndexError):
                subtool_1_metadata = SubtoolMetadata.load_from_file(subtool_1_metadata_path, _in_index=False, root_repo_path=temp_dir)
            subtool_1_metadata = SubtoolMetadata.load_from_file(subtool_1_metadata_path, _in_index=True, root_repo_path=temp_dir)
            subtool_2_metadata = SubtoolMetadata.load_from_file(subtool_2_metadata_path, _in_index=True,
                                                            root_repo_path=temp_dir)
        self.assertNotEqual(subtool_1_metadata.identifier, subtool_2_metadata.identifier)

        return

    def test_handle_duplicate_subtool_identifier_2(self):
        """
        Add two subtools and parent with one command.
        :return:
        """
        tool_name = 'samtools'
        tool_version = '1.x'
        subtool_name = 'dict'  # both subtool identifiers start with 'bb'
        subtool_name_2 = 'faidx'
        with TemporaryDirectory() as temp_dir:
            self.make_empty_tools_index(temp_dir)
            add_tool(tool_name, tool_version, [subtool_name, subtool_name_2], root_repo_path=temp_dir, refresh_index=False)
            subtool_1_metadata_path = get_tool_metadata(tool_name, tool_version, subtool_name, base_dir=temp_dir)
            subtool_2_metadata_path = get_tool_metadata(tool_name, tool_version, subtool_name_2, base_dir=temp_dir)
            subtool_1_metadata = SubtoolMetadata.load_from_file(subtool_1_metadata_path)
            subtool_2_metadata = SubtoolMetadata.load_from_file(subtool_2_metadata_path)
        self.assertNotEqual(subtool_1_metadata.identifier, subtool_2_metadata.identifier)
        return