import os
import re
from pathlib import Path

from capanno_utils.repo_config import *


# IDEA: Using Path class, it might be better to generate the get methods by getting longest path, then using Path.parents
# for parent directories. More maintainable if we change path structure. Maybe not.

# Misc

def get_inputs_schema_template():
    schema_template_path = Path.cwd() / 'tests/test_files/schema_salad/inputs_schema_template.yml'

    return schema_template_path

def get_tools_index(base_dir=None):
    base_dir = get_base_dir(base_dir)
    tools_index = base_dir / tool_index_path


def get_base_dir(base_dir=None):
    if not base_dir:
        base_dir = config[os.environ['CONFIG_KEY']]['base_path']
    return Path(base_dir)


def get_base_dir_from_abs_path(absolute_path, bas_dir_name=content_repo_name):
    absolute_path = Path(absolute_path)
    if not absolute_path.is_absolute():
        raise ValueError(f"{absolute_path} is not an absolute path")
    absolute_path_parts = absolute_path.parts
    if not absolute_path_parts.count(bas_dir_name) == 1:
        raise ValueError(f"Expected the root repo name '{bas_dir_name}' to be path one time.")
    root_path_part_index = absolute_path_parts.index(bas_dir_name)
    base_dir = Path(*absolute_path_parts[:root_path_part_index + 1])
    return base_dir



# cwl-tools

def get_root_tools_dir(base_dir=None):
    if not base_dir:
        base_dir = get_base_dir()
    else:
        base_dir = Path(base_dir)
    tool_dir = base_dir / tools_dir_name
    return tool_dir


def get_main_tool_dir(tool_name, base_dir=None):
    root_tools_dir = get_root_tools_dir(base_dir)
    main_tool_dir = root_tools_dir / tool_name
    return main_tool_dir


def get_tool_version_dir(tool_name, tool_version, base_dir=None):
    version_dir = get_main_tool_dir(tool_name, base_dir=base_dir) / str(tool_version)
    return version_dir


def get_tool_dir(tool_name, tool_version, subtool_name=None, base_dir=None):
    tool_version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=base_dir)

    if subtool_name in (None, main_tool_subtool_name):
        tool_dir = tool_version_dir / tool_name
    else:
        tool_dir = tool_version_dir / f"{tool_name}_{subtool_name}"
    return tool_dir


def get_cwl_tool(tool_name, tool_version, subtool_name=None, base_dir=None):
    """Return cwl file for tool. If subtool_name not specfied, return main tool."""
    if not subtool_name or subtool_name == main_tool_subtool_name:
        tool_dir = get_tool_dir(tool_name, tool_version, subtool_name=main_tool_subtool_name, base_dir=base_dir)
        cwl_tool_path = tool_dir / f"{tool_name}.cwl"
    else:
        tool_dir = get_tool_dir(tool_name, tool_version, subtool_name, base_dir=base_dir)
        cwl_tool_path = tool_dir / f"{tool_name}-{subtool_name}.cwl"
    return cwl_tool_path


def get_tool_common_dir(tool_name, tool_version, base_dir=None):
    version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=base_dir)
    common_dir = version_dir / 'common'
    return common_dir


def get_tool_metadata(tool_name, tool_version, subtool_name=None, parent=False, base_dir=None):
    version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=base_dir)
    if parent:
        assert not subtool_name
        cwl_tool_metadata_path = get_tool_common_dir(tool_name, tool_version,
                                                     base_dir=base_dir) / common_tool_metadata_name
    else:
        tool_dir = get_tool_dir(tool_name, tool_version, subtool_name, base_dir)
        if subtool_name in (None, main_tool_subtool_name):
            cwl_tool_metadata_path = tool_dir / f"{tool_name}-metadata.yaml"
        else:
            cwl_tool_metadata_path = tool_dir / f"{tool_name}-{subtool_name}-metadata.yaml"
    return cwl_tool_metadata_path


def get_parent_tool_relative_path_string():
    """Used to populate Subtool.parentMetadata"""
    rel_path_to_parent = f"../../common/{common_tool_metadata_name}"
    return rel_path_to_parent


def get_tool_instances_dir(tool_name, tool_version, subtool_name=None, base_dir=None):
    cwl_tool_dir = get_tool_dir(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)
    instances_dir = cwl_tool_dir / instances_dir_name
    return instances_dir


def get_tool_instances_dir_from_cwl_path(cwl_path):
    cwl_path = Path(cwl_path)
    instances_dir = cwl_path.parent / instances_dir_name
    return instances_dir


def get_tool_instance_path(tool_name, tool_version, input_hash, subtool_name=None, base_dir=None):
    cwl_tool_inst_dir = get_tool_instances_dir(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)
    inputs_path = cwl_tool_inst_dir / f"{input_hash}.yaml"

    return inputs_path

def get_tool_instance_path_from_tool_instance_metadata_path(tool_instance_metadata_path):
    tool_instance_metadata_path = Path(tool_instance_metadata_path)
    instance_metadata_file_name = tool_instance_metadata_path.stem
    instance_file_name = f"{instance_metadata_file_name[:4]}.yaml"
    tool_instance_path = Path(tool_instance_metadata_path).parent/ instance_file_name
    return tool_instance_path

def get_tool_instance_metadata_path(tool_name, tool_version, input_hash, subtool_name=None, base_dir=None):
    cwl_tool_inst_dir = get_tool_instances_dir(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)
    instance_metadata_path = cwl_tool_inst_dir / f"{input_hash}-metadata.yaml"
    return instance_metadata_path

def get_subtool_metadata_path_from_tool_instance_metadata_path(tool_instance_path, base_dir=None):
    tool_instance_path_parts = Path(tool_instance_path).parts
    tool_name = tool_instance_path_parts[-5]
    tool_version = tool_instance_path_parts[-4]
    subtool_name = tool_instance_path_parts[-3]
    if subtool_name == tool_name:
        subtool_name = main_tool_subtool_name
    subtool_metadata_path = get_tool_metadata(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)
    return subtool_metadata_path


def get_tool_args_from_path(cwl_tool_path):
    cwl_tool_path = Path(cwl_tool_path)
    tool_type = get_tool_type_from_path(cwl_tool_path)
    path_parts = cwl_tool_path.parts

    tool_name = path_parts[-4]
    tool_version = path_parts[-3]
    subtool_name = path_parts[-2].split('_')[-1] if tool_type == 'subtool' else None

    return tool_name, tool_version, subtool_name


def get_tool_type_from_path(tool_path):
    tool_path = Path(tool_path)
    if tool_path.suffix == '.yaml':
        if not tool_path.parent.parts[-1] == 'common':
            raise ValueError(f"Provided a .yaml file {tool_path} for file that is not in a 'common' directory")
        tool_type = "parent"
    elif tool_path.suffix == '.cwl':
        tool_type = 'subtool'
    else:
        raise ValueError(f"Do not recognize {tool_path} as a path to a tool.")

    return tool_type


# cwl-scripts

def get_root_scripts_dir(base_dir=None):
    if not base_dir:
        base_dir = get_base_dir()
    else:
        base_dir = Path(base_dir)
    scripts_dir = base_dir / scripts_dir_name
    return scripts_dir


def get_script_group_dir(group_name, base_dir=None):
    scripts_root_dir = get_root_scripts_dir(base_dir=base_dir)
    scripts_group_dir = scripts_root_dir / group_name
    return scripts_group_dir


def get_script_project_dir(group_name, project_name, base_dir=None):
    scripts_group_dir = get_script_group_dir(group_name, base_dir=base_dir)
    script_project_dir = scripts_group_dir / project_name
    return script_project_dir


def get_script_version_dir(group_name, project_name, version, base_dir=None):
    script_ver_dir = get_script_project_dir(group_name, project_name, base_dir=base_dir) / version
    return script_ver_dir


def get_script_dir(group_name, project_name, version, script_name, base_dir=None):
    script_dir = get_script_version_dir(group_name, project_name, version, base_dir=base_dir) / script_name
    return script_dir

def get_cwl_script(group_name, project_name, version, script_name, base_dir=None):
    script_ver_dir = get_script_version_dir(group_name, project_name, version, base_dir=base_dir)
    script_path = script_ver_dir / script_name / f"{script_name}.cwl"
    return script_path


def get_script_metadata(group_name, project_name, version, script_name, base_dir=None):
    script_ver_dir = get_script_version_dir(group_name, project_name, version, base_dir=base_dir)
    script_metadata_path = script_ver_dir / script_name / f"{script_name}-metadata.yaml"
    return script_metadata_path


def get_script_instance_dir(group_name, project_name, version, script_name, base_dir=None):
    script_version_dir = get_script_version_dir(group_name, project_name, version, base_dir=base_dir)
    instances_dir = script_version_dir / script_name / instances_dir_name
    return instances_dir


def get_script_args_from_path(cwl_script_path):
    cwl_script_path = Path(cwl_script_path)
    script_name = cwl_script_path.stem
    path_parts = cwl_script_path.parts
    assert script_name == path_parts[-2]
    script_version = path_parts[-3]
    project_name = path_parts[-4]
    group_name = path_parts[-5]
    return group_name, project_name, script_version, script_name


def get_script_instance_path(group_name, project_name, version, script_name, instance_hash, base_dir=None):
    script_instance_dir = get_script_instance_dir(group_name, project_name, version, script_name, base_dir=base_dir)
    instance_path = script_instance_dir / f"{instance_hash}.yaml"
    return instance_path

def get_script_instance_metadata_path(group_name, project_name, version, script_name, instance_hash, base_dir=None):
    script_instance_dir = get_script_instance_dir(group_name, project_name, version, script_name, base_dir=base_dir)
    instance_metadata_path = script_instance_dir / f"{instance_hash}-metadata.yaml"
    return instance_metadata_path


# cwl-workflows

def get_workflows_root_dir(base_dir=None):
    if not base_dir:
        base_dir = get_base_dir()
    else:
        base_dir = Path(base_dir)
    workflows_dir = base_dir / workflows_dir_name
    return workflows_dir


def get_workflow_group_dir(group_name, base_dir=None):
    workflow_group_dir = get_workflows_root_dir(base_dir=base_dir) / group_name
    return workflow_group_dir


def get_workflow_project_dir(group_name, project_name, base_dir=None):
    workflow_project_dir = get_workflow_group_dir(group_name, base_dir=base_dir) / project_name
    return workflow_project_dir


def get_workflow_version_dir(group_name, project_name, version, base_dir=None):
    workflow_ver_dir = get_workflows_root_dir(base_dir=base_dir) / group_name / project_name / version
    return workflow_ver_dir


def get_cwl_workflow(group_name, project_name, version, workflow_name, base_dir=None):
    workflow_ver_dir = get_workflow_version_dir(group_name, project_name, version, base_dir=base_dir)
    workflow_path = workflow_ver_dir / f"{workflow_name}.cwl"
    return workflow_path


def get_workflow_metadata(group_name, project_name, version, workflow_name, base_dir=None):
    workflow_ver_dir = get_workflow_version_dir(group_name, project_name, version, base_dir=base_dir)
    workflow_metadata_path = workflow_ver_dir / f"{workflow_name}-metadata.yaml"
    return workflow_metadata_path


def get_workflow_inputs_dir(group_name, project_name, version, base_dir=None):
    cwl_workflow_dir = get_workflow_version_dir(group_name, project_name, version, base_dir=base_dir)
    instances_dir = cwl_workflow_dir / instances_dir_name
    return instances_dir


def get_workflow_instance_dir_from_cwl_path(cwl_path):
    cwl_path = Path(cwl_path)
    instances_dir = cwl_path.parent / instances_dir_name
    return instances_dir


def get_workflow_instance_path(group_name, project_name, version, instance_hash, base_dir=None):
    workflow_instances_dir = get_workflow_inputs_dir(group_name, project_name, version, base_dir=base_dir)
    instance_path = workflow_instances_dir / f"{instance_hash}.yaml"
    return instance_path

def get_workflow_instance_metadata(group_name, project_name, version, instance_hash, base_dir=None):
    workflow_instances_dir = get_workflow_inputs_dir(group_name, project_name, version, base_dir=base_dir)
    instance_metadata_path = workflow_instances_dir / f"{instance_hash}-metadata.yaml"
    return instance_metadata_path


def get_workflow_args_from_path(cwl_workflows_path):
    cwl_workflows_path = Path(cwl_workflows_path)
    path_parts = cwl_workflows_path.parts
    file_name = path_parts[-1]
    workflow_name = cwl_workflows_path.stem
    workflow_version = path_parts[-2]
    project_name = path_parts[-3]
    group_name = path_parts[-4]
    return group_name, project_name, workflow_version, workflow_name


# helpers

def get_relative_path(full_path, base_path=None):
    base_path = get_base_dir(base_dir=base_path)
    return full_path.relative_to(base_path)


def get_metadata_path(cwl_path):
    cwl_path = Path(cwl_path)
    path_dir = cwl_path.parent
    metafile_name = f"{cwl_path.stem}-metadata.yaml"
    metadata_path = path_dir / metafile_name
    return metadata_path


def get_file_type_from_main_dir(file_path):
    """
    Determine if a file is a metadata file or a cwl file from a subtool, script, or workflow directory.
    Raises an error if it doesn't look like either.
    """
    if file_path.suffix == '.cwl':
        file_type = 'cwl'

    elif file_path.suffix in ('.yaml', '.yml'):
        if '-metadata' in file_path.parts[-1]:  # have a metadata file
            file_type = 'metadata'
        else:
            raise ValueError(f"Cannot determine file type for {file_path}")
    else:
        raise ValueError(f"Cannot determine file type for {file_path}")
    return file_type


def get_file_type_from_instance_dir(file_path):
    """
    Determine if a file in an instance directory is an instance file or metadata file.
    Raises and error if it doesn't look like either.
    """
    if instance_file_pattern.match(file_path.name):
        file_type = 'instance'
    elif instance_metadata_file_pattern.match(file_path.name):
        file_type = 'instance_metadata'
    else:
        raise ValueError(f"Cannot determine file type in instances directory: {file_path}")
    return file_type


def check_common_metadata_file_name(file_path, method_type):
    """
    Determine if a file is a properly named common metadata file. If it isn't, raise an error.
    tool_file_name = common-metadata.yaml
    script_common_name = {script_specific}-metadata.yaml
    workflow_common_name = DON'T HAVE COMMON FOR WORKFLOWS YET.
    """
    if method_type == 'workflow':
        raise NotImplementedError(f"Common metadata has not been implemented for workflows yet.")
    elif method_type == 'tool':
        if not file_path.name == common_tool_metadata_name:
            raise ValueError(f"common metadadata files for tools must be named '{common_tool_metadata_name}'")
    elif method_type == 'script':
        if not script_common_metadata_file_pattern.match(file_path.name):
            raise ValueError(f"common metadadata files for scripts must be named")
    return


def get_type_from_file_path(abs_path, method_type):
    """
    Determine the type of file from its path.
    abs_path(Path): Path to a file. Should already be sure it is a file path, not a directory.


    """

    if abs_path.parts[-2] == instances_dir_name:
        file_type = get_file_type_from_instance_dir(abs_path)
    elif abs_path.parts[-2] == common_dir_name:
        # in a common directory. Works for tools, scripts, workflows.
        check_common_metadata_file_name(abs_path, method_type)
        file_type = 'common_metadata'
    else:  # Not in common or instances dir. In a subtool, script, or workflow directory.

        file_type = get_file_type_from_main_dir(abs_path)
    return file_type


def get_base_method_type_from_path(abs_path, cwl_root_repo_name=content_repo_name):
    """
    Given a path, determine if the path is in the tools, scripts, workflows, or root directory.
    """
    path_parts = abs_path.parts  # returns tuple.
    if tools_dir_name in path_parts:
        assert scripts_dir_name not in path_parts
        assert workflows_dir_name not in path_parts
        method_type = 'tool'

    elif scripts_dir_name in path_parts:
        assert workflows_dir_name not in path_parts
        method_type = 'script'

    elif workflows_dir_name in path_parts:
        method_type = 'workflow'

    elif path_parts[-1] == cwl_root_repo_name:
        method_type = 'repo_root'
    else:
        raise ValueError(f"{abs_path} does not seem to be a path in a cwl repo.")
    return method_type

def get_dir_type_from_path(abs_dir_path, cwl_root_repo_name=content_repo_name):
    """
    Get the type of a directory
    Allow optional parameter cwl_root_repo_name in case repo is called something other than `content_repo_name`(capanno at this time).
    Returns
     str: '' | ''
    """
    base_type = get_base_method_type_from_path(abs_dir_path)
    path_parts = abs_dir_path.parts
    if base_type == 'repo_root':
        dir_type = 'base_dir'
    elif base_type == 'tool':
        # dir type could be base_dir, tool_dir, version_dir, common_dir, subtool_dir, instances_dir
        if path_parts[-1] == tools_dir_name:
            assert path_parts[-2] == cwl_root_repo_name
            dir_type = 'base_dir'
        elif path_parts[-2] == tools_dir_name:
            assert path_parts[-3] == cwl_root_repo_name
            dir_type = 'tool_dir'
        elif path_parts[-3] == tools_dir_name:
            assert path_parts[-4] == cwl_root_repo_name
            dir_type = 'version_dir'
        elif path_parts[-4] == tools_dir_name:
            # could be common or main tool
            assert path_parts[-5] == cwl_root_repo_name
            if path_parts[-1] == 'common':
                dir_type = 'common_dir'
            else:
                dir_type = 'subtool_dir'
        elif path_parts[-5] == tools_dir_name:
            # Should be instances dir
            assert path_parts[-6] == cwl_root_repo_name
            dir_type = 'instance_dir'
        else:
            raise ValueError
    elif base_type == 'script':
        # dir type could be base_dir, group_dir, project_dir, version_dir, common_dir, script_dir, instances_dir
        if path_parts[-1] == scripts_dir_name:
            assert path_parts[-2] == cwl_root_repo_name
            dir_type = 'base_dir'
        elif path_parts[-2] == scripts_dir_name:
            assert path_parts[-3] == cwl_root_repo_name
            dir_type = 'group_dir'
        elif path_parts[-3] == scripts_dir_name:
            assert path_parts[-4] == cwl_root_repo_name
            dir_type = 'project_dir'
        elif path_parts[-4] == scripts_dir_name:
            assert path_parts[-5] == cwl_root_repo_name
            dir_type = 'version_dir'
        elif path_parts[-5] == scripts_dir_name:
            assert path_parts[-6] == cwl_root_repo_name
            # could be script_dir or common_dir.
            if path_parts[-1] == 'common':
                dir_type = 'common_dir'
            else:
                dir_type = 'script_dir'
        elif path_parts[-6] == scripts_dir_name:
            assert path_parts[-7] == cwl_root_repo_name
            dir_type = 'instance_dir'
        else:
            raise ValueError
    elif base_type == 'workflow':
        # dir type could be base_dir, group_dir, project_dir, version_dir, common_dir, script_dir, instances_dir
        raise NotImplementedError
    else:
        raise ValueError

    return base_type, dir_type

def get_types_from_path(path, cwl_root_repo_name=content_repo_name, base_path=None):
    """
    Get the type of file from the path.

    path(Path|str): the path of the file.

    return(tuple): ('worklfow' | 'tool' | 'script', 'metadata' | 'cwl')
    """

    path = Path(path)
    if base_path:
        path = Path(base_path) / path
    abs_path = path.resolve()

    method_type = get_base_method_type_from_path(abs_path, cwl_root_repo_name=cwl_root_repo_name)

    if method_type == 'repo_root':
        file_type = None

    else:
        if abs_path.is_dir():
            _, file_type = get_dir_type_from_path(abs_path, cwl_root_repo_name=cwl_root_repo_name)
        elif path.is_file():
            file_type = get_type_from_file_path(abs_path, method_type)
        else:
            if not path.exists():
                raise FileNotFoundError(f"{abs_path} does not exist.")
            raise TypeError(f"What kind of path is {abs_path} if it isn't a directory or file?")

    return method_type, file_type


