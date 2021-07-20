
from shutil import copytree, move
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest import skip
from capanno_utils.repo_config import tools_dir_name
from tests.test_base import TestBase
from capanno_utils.add_content import main as add_content_main
from capanno_utils.helpers.get_paths import *

# @skip('')
class TestAddToolMain(TestBase):
    # @skip('')
    def test_add_tool(self):
        with TemporaryDirectory(prefix='test_add_tool_') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_name = 'test_1'
            tool_version = 'fake.1'
            add_content_main(['--no-refresh-index', '-p', tmp_dir, 'tool', tool_name, tool_version, "--has-primary"])
        return

    # @skip('')
    def test_add_tool_with_subtools(self):
        with TemporaryDirectory(prefix='test_add_w_subtools_') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_name = 'test_2'
            tool_version = 'fake.2'
            subtools = ['subtool1', 'subtool2', 'subtool3']
            add_content_main(['--no-refresh-index', '-p', tmp_dir, 'tool', tool_name, tool_version] + subtools)
        return

    # @skip('')
    def test_add_tool_with_biotools_id(self):
        with TemporaryDirectory(prefix='with_biotools_') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_name = 'test_biotools'
            tool_version = 'fake.3'
            biotools_id = 'malvirus'
            subtools = ['subtool1', 'subtool2', 'subtool3']
            options = ['--biotoolsID', biotools_id]
            add_content_main(['--no-refresh-index', '-p', tmp_dir, 'tool', tool_name, tool_version] + subtools + options)
        return

    def test_add_tool_with_subtools_with_init_urls(self):
        cwl_url = 'https://raw.githubusercontent.com/common-workflow-library/bio-cwl-tools/release/bandage/bandage-image.cwl'
        tool_name = 'test_biotools'
        tool_version = 'fake.3'
        biotools_id = 'malvirus'
        subtools = ['subtool1', 'subtool2', 'subtool3']
        options = ['--biotoolsID', biotools_id]
        init_cwl = ['--init-cwl', f"subtool1={cwl_url}", f"subtool2={cwl_url}"]
        with TemporaryDirectory(prefix='add_with_url') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            add_content_main(
                ['--no-refresh-index', '-p', tmp_dir, 'tool', tool_name, tool_version] + subtools + options + init_cwl)

    def test_add_tool_with_subtools_with_init_url_main_only(self):
        cwl_url = 'https://raw.githubusercontent.com/common-workflow-library/bio-cwl-tools/release/bandage/bandage-image.cwl'
        tool_name = 'test_biotools'
        tool_version = 'fake.3'
        biotools_id = 'malvirus'
        options = ['--biotoolsID', biotools_id, '--has-primary']
        init_cwl = ['--init-cwl', cwl_url]
        with TemporaryDirectory(prefix='add_with_url') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            add_content_main(
                ['--no-refresh-index', '-p', tmp_dir, 'tool', tool_name, tool_version] + options + init_cwl)

    # @skip('')
    def test_add_subtool(self):
        with TemporaryDirectory(prefix='add_subtool_') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_name = 'test_4'
            tool_version = 'fake.4'
            subtool_name = 'new_subtool'
            add_content_main(['--no-refresh-index', '-p', tmp_dir, 'tool', tool_name, tool_version])
            add_content_main(['-p', tmp_dir, 'subtool', tool_name, tool_version, subtool_name, '-u'])
        return

    def test_add_tool_with_existing_cwl_url(self):
        cwl_url = 'https://raw.githubusercontent.com/common-workflow-library/bio-cwl-tools/release/bandage/bandage-image.cwl'
        biotools_id = 'bandage'
        tool_name = 'bandage'
        tool_version = 'fake.6'
        subtool_name = 'image'
        with TemporaryDirectory(prefix='add_tool_with_cwl_') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            add_content_main(['--no-refresh-index', '-p', tmp_dir, 'tool', tool_name, tool_version, '--biotoolsID', biotools_id])
            add_content_main(['-p', tmp_dir, 'subtool', tool_name, tool_version, subtool_name, '-u', '--init-cwl', cwl_url])
            assert True
        return

    def test_add_tool_instance(self):
        tool_name = 'STAR'
        tool_version = '2.5'
        subtool_name = 'alignReads'
        tool_directory = get_main_tool_dir(tool_name, base_dir=self.test_content_dir)
        with TemporaryDirectory() as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            tool_temp_path = Path(tmp_dir) / tools_dir_name / tool_name
            copytree(tool_directory, tool_temp_path)
            add_content_main(['-p', tmp_dir, 'tool-instance', tool_name, tool_version, subtool_name])
            assert True  # Just provides a place for a breakpoint to take a look.at tmp_dir
        return

    def test_add_tool_with_wdl_url(self):
        wdl_url = 'https://github.com/broadinstitute/warp/raw/develop/tasks/skylab/CreateCountMatrix.wdl'
        tool_name = 'who_cares'
        tool_version = 'fake.fake'
        subtool_name = 'test_wdl_subtool'
        with TemporaryDirectory(prefix='add_tool_with_wdl') as tmp_dir:
            self.make_empty_tools_index(tmp_dir)
            add_content_main(
                ['--no-refresh-index', '-p', tmp_dir, 'tool', tool_name, tool_version])
            add_content_main(
                ['-p', tmp_dir, 'subtool', tool_name, tool_version, subtool_name, '-u', '--init-wdl', wdl_url])
            assert True
        return



# @skip('')
class TestAddScriptMain(TestBase):

    def test_add_common_script(self):
        with TemporaryDirectory() as tmp_dir:
            group_name = 'test_group1'
            project_name = 'fake_project_1'
            script_version = '1.nope'
            file_name = "some_filename"
            add_content_main(['-p', tmp_dir, 'common-script', group_name, project_name, script_version, file_name])
        return

    def test_add_script(self):
        with TemporaryDirectory() as tmp_dir:
            group_name = 'test_group2'
            project_name = 'fake_project_2'
            script_name = 'new_script_2'
            script_version = '2.nope'
            add_content_main(['-p', tmp_dir, 'script', group_name, project_name, script_version, script_name])
        return
