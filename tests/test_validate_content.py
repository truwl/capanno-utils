from unittest import skip
from tests.test_base import TestBase
from capanno_utils.repo_config import config
from capanno_utils.helpers.get_paths import *
from capanno_utils.validate_content import main as validate_content


# @skip('')
class TestValidateTools(TestBase):

    def test_validate_main_tool_dir(self):
        tool_name = 'STAR'
        test_repo_path = self.test_content_dir
        main_tool_dir = get_main_tool_dir(tool_name, base_dir=test_repo_path)
        validate_content([str(main_tool_dir), '-p', str(test_repo_path), '-q'])
        return

    def test_validate_tool_version_dir(self):
        tool_name = 'samtools'
        version_name = '1.x'
        tool_version_dir = get_tool_version_dir(tool_name, version_name, base_dir=self.test_content_dir)
        validate_content([str(tool_version_dir), '-p', str(self.test_content_dir), '-q'])
        return

    def test_validate_subtool_dir(self):
        tool_name = 'md5sum'
        version_name = '8.x'
        subtool_name = 'check'
        subtool_dir = get_tool_dir(tool_name, version_name, subtool_name, base_dir=self.test_content_dir)
        validate_content([str(subtool_dir), '-p', str(self.test_content_dir), '-q'])
        return

    def test_validate_main_subtool_dir(self):
        tool_name = 'md5sum'
        version_name = '8.x'
        subtool_name = None
        subtool_dir = get_tool_dir(tool_name, version_name, subtool_name, base_dir=self.test_content_dir)
        validate_content([str(subtool_dir), '-p', str(self.test_content_dir), '-q'])
        return

    def test_validate_common_dir(self):
        tool_name = 'md5sum'
        version_name = '8.x'
        common_dir = get_tool_common_dir(tool_name, version_name, base_dir=self.test_content_dir)
        validate_content([str(common_dir), '-p', str(self.test_content_dir), '-q'])
        return

    def test_validate_instance_dir(self):
        tool_name = 'gawk'
        version_name = '4.1.x'
        subtool_name = None
        instances_dir = get_tool_instances_dir(tool_name, version_name, subtool_name=subtool_name,
                                               base_dir=self.test_content_dir)
        validate_content([str(instances_dir), '-p', str(self.test_content_dir), '-q'])
        return

# @skip('')
class TestValidateScripts(TestBase):

    def test_validate_group_script_dir(self):
        group_name = 'ENCODE-DCC'
        script_group_dir = get_script_group_dir(group_name, base_dir=self.test_content_dir)
        validate_content([str(script_group_dir), '-p', str(self.test_content_dir), '-q'])
        return

    def test_validate_project_script_dir(self):
        group_name = 'ENCODE-DCC'
        project_name = 'atac-seq-pipeline'
        script_project_dir = get_script_project_dir(group_name, project_name, base_dir=self.test_content_dir)
        validate_content([str(script_project_dir), '-p', str(self.test_content_dir), '-q'])
        return

    def test_validate_version_script_dir(self):
        group_name = 'ENCODE-DCC'
        project_name = 'atac-seq-pipeline'
        version_name = '1.1.x'
        script_version_dir = get_script_version_dir(group_name, project_name, version_name,
                                                    base_dir=self.test_content_dir)
        validate_content([str(script_version_dir), '-p', str(self.test_content_dir), '-q'])
        return

    def test_validate_script_dir(self):
        group_name = 'ENCODE-DCC'
        project_name = 'atac-seq-pipeline'
        version_name = '1.1.x'
        script_name = 'encode_ataqc'
        script_dir = get_script_dir(group_name, project_name, version_name, script_name,
                                    base_dir=self.test_content_dir)
        validate_content([str(script_dir), '-p', str(self.test_content_dir), '-q'])
        return

    def test_validate_script_instance_dir(self):
        group_name = 'ENCODE-DCC'
        project_name = 'atac-seq-pipeline'
        version_name = '1.1.x'
        script_name = 'encode_bam2ta'  # No instances in there, but might as well have a test.
        script_instance_dir = get_script_instance_dir(group_name, project_name, version_name, script_name,
                                                      base_dir=self.test_content_dir)
        validate_content([str(script_instance_dir), '-p', str(self.test_content_dir), '-q'])
        return
