
import os
from tests.test_base import TestBase, test_constants
from capanno_utils.helpers.get_paths import *
    # get_types_from_path, get_script_metadata, get_script_instance_path, \
    # get_cwl_script, get_cwl_tool, get_tool_common_dir, main_tool_subtool_name, get_tool_metadata, \
    # get_tool_instance_path, get_tool_instance_metadata_path, get_cwl_workflow, get_workflow_metadata, \
    # get_workflow_instance_path, get_workflow_instance_metadata


class TestGetTypesFromPath(TestBase):

    def test_get_type_from_script_paths(self):

        # Script cwl path
        script_cwl_path = get_cwl_script(test_constants['script_group1'], test_constants['script_project1'],
                                         test_constants['script_version1'], 'encode_ataqc')
        cwl_script_type_tuple = get_types_from_path(str(script_cwl_path))
        self.assertEqual(cwl_script_type_tuple, ('script', 'cwl'))
        script_metadata_path = get_script_metadata(test_constants['script_group1'], test_constants['script_project1'],
                                         test_constants['script_version1'], 'encode_ataqc')

        # Script metadata path
        script_metadata_type_tuple = get_types_from_path(str(script_metadata_path))
        self.assertEqual(script_metadata_type_tuple, ('script', 'metadata'))

        # Script instance/metadata paths. ToDo Need to have a script instance to test.

        # script_instance_path = get_script_instance_path(test_constants['script_group1'], test_constants['script_project1'],
        #                                  test_constants['script_version1'], 'encode_ataqc', '1234')
        # script_instance_type_tuple = get_types_from_path(script_instance_path)

        return

    def test_get_type_from_tool_paths(self):

        tool_name = 'gawk'
        tool_version = '4.1.x'
        subtool_name = main_tool_subtool_name
        instance_hash = '1c10'

        common_metadata_path = get_tool_common_dir(tool_name, tool_version) / 'common-metadata.yaml'
        common_tool_type_tuple = get_types_from_path(common_metadata_path)
        self.assertEqual(common_tool_type_tuple, ('tool', 'common_metadata'))

        tool_sources = get_tool_sources(tool_name, tool_version, subtool_name)
        cwl_tool_type_tuple = get_types_from_path(tool_sources['cwl'])
        self.assertEqual(cwl_tool_type_tuple, ('tool', 'cwl'))

        tool_metadata_path = get_tool_metadata(tool_name, tool_version)
        tool_metadata_type_tuple = get_types_from_path(tool_metadata_path)
        self.assertEqual(tool_metadata_type_tuple, ('tool', 'metadata'))

        tool_instance_path = get_tool_instance_path(tool_name, tool_version, instance_hash)
        tool_instance_type_tuple = get_types_from_path(tool_instance_path)
        self.assertEqual(tool_instance_type_tuple, ('tool', 'instance'))

        tool_instance_metadata_path = get_tool_instance_metadata_path(tool_name, tool_version, instance_hash)
        tool_instance_metadata_type_tuple = get_types_from_path(tool_instance_metadata_path)
        self.assertEqual(tool_instance_metadata_type_tuple, ('tool', 'instance_metadata'))

        return

    def test_get_type_from_workflow_path(self):

        group_name = 'example_workflows'
        project_name = 'cat_sort'
        workflow_version = 'master'
        workflow_name = 'cat_sort'
        input_hash = 'ecd8'

        workflow_cwl_path = get_workflow_sources(group_name, project_name, workflow_version, workflow_name)['cwl']
        cwl_workflow_type_tuple = get_types_from_path(workflow_cwl_path)
        self.assertEqual(cwl_workflow_type_tuple, ('workflow', 'cwl'))

        workflow_metadata_path = get_workflow_metadata(group_name, project_name, workflow_version)
        workflow_metadata_type_tuple = get_types_from_path(workflow_metadata_path)
        self.assertEqual(workflow_metadata_type_tuple, ('workflow', 'metadata'))

        workflow_instance_path = get_workflow_instance_path(group_name, project_name, workflow_version, input_hash)
        workflow_instance_type_tuple = get_types_from_path(workflow_instance_path)
        self.assertEqual(workflow_instance_type_tuple, ('workflow', 'instance'))

        workflow_instance_metadata_path = get_workflow_instance_metadata(group_name, project_name, workflow_version, input_hash)
        workflow_instance_metadata_type_tuple = get_types_from_path(workflow_instance_metadata_path)
        self.assertEqual(workflow_instance_metadata_type_tuple, ('workflow', 'instance_metadata'))
        return


    def test_get_type_from_tool_dirs(self):

        tool_name = 'gawk'
        tool_version = '4.1.x'
        subtool_name = main_tool_subtool_name  # Is used by default if not specified.
        cwl_root_repo_name = self.test_content_dir.stem

        root_tools_dir = get_root_tools_dir()
        root_tools_dir_type_tuple = get_types_from_path(root_tools_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(root_tools_dir_type_tuple, ('tool', 'base_dir'))


        tool_dir = get_main_tool_dir(tool_name)
        tool_dir_type_tuple = get_types_from_path(tool_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(tool_dir_type_tuple, ('tool', 'tool_dir'))

        tool_version_dir = get_tool_version_dir(tool_name, tool_version)
        tool_version_dir_type_tuple = get_types_from_path(tool_version_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(tool_version_dir_type_tuple, ('tool', 'version_dir'))

        tool_common_dir = get_tool_common_dir(tool_name, tool_version)
        tool_common_dir_type_tuple = get_types_from_path(tool_common_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(tool_common_dir_type_tuple, ('tool', 'common_dir'))

        subtool_dir = get_tool_dir(tool_name, tool_version)
        subtool_dir_type_tuple = get_types_from_path(subtool_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(subtool_dir_type_tuple, ('tool', 'subtool_dir'))

        tool_instance_dir = get_tool_instances_dir(tool_name, tool_version)
        tool_instance_dir_type_tuple = get_types_from_path(tool_instance_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(tool_instance_dir_type_tuple, ('tool', 'instance_dir'))
        return

    def test_get_type_from_script_dirs(self):

        group_name = 'ENCODE-DCC'
        project_name = 'atac-seq-pipeline'
        script_version = '1.1.x'
        script_name = 'encode_ataqc'
        cwl_root_repo_name = self.test_content_dir.stem

        root_scripts_dir = get_root_scripts_dir()
        root_scripts_dir_tuple_type = get_types_from_path(root_scripts_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(root_scripts_dir_tuple_type, ('script', 'base_dir'))

        script_group_dir = get_script_group_dir(group_name)
        script_group_dir_type_tuple = get_types_from_path(script_group_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(script_group_dir_type_tuple, ('script', 'group_dir'))

        script_project_dir = get_script_project_dir(group_name, project_name)
        script_project_dir_type_tuple = get_types_from_path(script_project_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(script_project_dir_type_tuple, ('script', 'project_dir'))

        script_version_dir = get_script_version_dir(group_name, project_name, script_version)
        script_version_type_tuple = get_types_from_path(script_version_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(script_version_type_tuple, ('script', 'version_dir'))

        script_dir = get_script_dir(group_name, project_name, script_version, script_name)
        script_dir_type_tuple = get_types_from_path(script_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(script_dir_type_tuple, ('script', 'script_dir'))

        script_instance_dir = get_script_instance_dir(group_name, project_name, script_version, script_name)
        script_instance_dir_tuple = get_types_from_path(script_instance_dir, root_repo_name=cwl_root_repo_name)
        self.assertEqual(script_instance_dir_tuple, ('script', 'instance_dir'))



        return


