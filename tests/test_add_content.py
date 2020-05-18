
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import skip
from tests.test_base import TestBase
from xd_cwl_utils.add_content import main as add_content_main

# @skip('')
class TestAddToolMain(TestBase):
    # @skip('')
    def test_add_tool(self):
        with TemporaryDirectory() as tmp_dir:
            tool_name = 'test_1'
            tool_version = 'fake.1'
            temp_path = Path(tmp_dir)
            new_directory = temp_path / 'cwl-source'
            new_directory.mkdir()
            add_content_main([f"-p {new_directory}", 'tool', tool_name, tool_version, f"--has_primary"])
        return

    # @skip('')
    def test_add_tool_with_subtools(self):
        with TemporaryDirectory() as tmp_dir:
            tool_name = 'test_2'
            tool_version = 'fake.2'
            subtools = ['subtool1', 'subtool2', 'subtool3']
            temp_path = Path(tmp_dir)
            new_directory = temp_path / 'cwl-source'
            new_directory.mkdir()
            add_content_main([f"-p {new_directory}", 'tool', tool_name, tool_version] + subtools)
        return

    # @skip('')
    def test_add_tool_with_biotools_id(self):
        with TemporaryDirectory() as tmp_dir:
            tool_name = 'test_biotools'
            tool_version = 'fake.3'
            biotools_id = 'malvirus'
            subtools = ['subtool1', 'subtool2', 'subtool3']
            options = ['--biotoolsID', biotools_id]
            temp_path = Path(tmp_dir)
            new_directory = temp_path / 'cwl-source'
            new_directory.mkdir()
            add_content_main([f"-p {new_directory}", 'tool', tool_name, tool_version] + subtools + options)
        return

    def test_add_subtool(self):
        with TemporaryDirectory() as tmp_dir:
            tool_name = 'test_4'
            tool_version = 'fake.4'
            subtool_name = 'new_subtool'
            temp_path = Path(tmp_dir)
            new_directory = temp_path / 'cwl-source'
            new_directory.mkdir()
            add_content_main([f"-p {new_directory}", 'tool', tool_name, tool_version])
            add_content_main([f"-p {new_directory}", 'subtool', tool_name, tool_version, subtool_name, '-u'])
        return


class TestAddScriptMain(TestBase):

    def test_add_common_script(self):
        with TemporaryDirectory() as tmp_dir:
            group_name = 'test_group1'
            project_name = 'fake_project_1'
            script_version = '1.nope'
            file_name = "some_filename"
            temp_path = Path(tmp_dir)
            new_directory = temp_path / 'cwl-scripts'
            new_directory.mkdir()
            add_content_main([f"-p {new_directory}", 'common_script', group_name, project_name, script_version, file_name])
        return

    def test_add_script(self):
        with TemporaryDirectory() as tmp_dir:
            group_name = 'test_group2'
            project_name = 'fake_project_2'
            script_name = 'new_script_2'
            script_version = '2.nope'
            temp_path = Path(tmp_dir)
            new_directory = temp_path / 'cwl-scripts'
            new_directory.mkdir()
            add_content_main([f"-p {new_directory}", 'script', group_name, project_name, script_version, script_name])
        return