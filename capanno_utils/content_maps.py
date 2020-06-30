import os
from pathlib import Path
from ruamel.yaml import safe_load, YAML
from capanno_utils.config import config
from capanno_utils.classes.metadata.script_metadata import ScriptMetadata
from capanno_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata
from capanno_utils.classes.metadata.workflow_metadata import WorkflowMetadata
from capanno_utils.helpers.get_paths import *


# get_cwl_tool, get_tool_metadata, get_tool_version_dir, \
#     get_script_version_dir, get_metadata_path, get_relative_path, get_workflow_version_dir, get_root_tools_dir, \
#     get_root_scripts_dir, get_workflows_root_dir, get_cwl_workflow

def make_tools_map(outfile_path=None, base_dir=None):
    """
    Make a yaml file that specifies paths and attributes of tools in tool_dir.
    :param tool_dir (Path): Path of directory that contains tools.
    :param outfile_name(str): name of file that will be made.
    :return:
        None
    """

    cwl_tools_dir = get_root_tools_dir(base_dir=base_dir)
    content_map = {}

    for tool_dir in cwl_tools_dir.iterdir():
        for version_dir in tool_dir.iterdir():
            tool_map = make_tool_version_dir_map(tool_dir.name, version_dir.name, base_dir=base_dir)
            content_map.update(tool_map)
    if outfile_path:
        outfile_path = Path(outfile_path)
        yaml = YAML(pure=True)
        yaml.default_flow_style = False
        yaml.indent(mapping=2, sequence=4, offset=2)
        with outfile_path.open('w') as outfile:
            yaml.dump(content_map, outfile)
    return content_map


def make_main_tool_map(tool_name, base_dir=None):
    """
    Make a yaml file that specifies paths and attributes of tools in a single tool directory. If outfile is provided, dump contents to outfile.

    """
    main_tool_map = {}
    tool_dir = get_main_tool_dir(tool_name, base_dir=base_dir)
    for version_dir in tool_dir.iterdir():
        main_tool_map.update(make_tool_version_dir_map(tool_name, version_dir.name, base_dir=base_dir))
    return main_tool_map


def make_tool_version_dir_map(tool_name, tool_version, base_dir=None):
    tool_version_map = {}

    tool_version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=base_dir)
    subdir_names = [subdir.name for subdir in tool_version_dir.iterdir()]

    parent_metadata_path = get_tool_metadata(tool_name, tool_version, parent=True, base_dir=base_dir)
    parent_metadata = ParentToolMetadata.load_from_file(parent_metadata_path)
    parent_rel_path = get_relative_path(parent_metadata_path, base_path=base_dir)
    tool_version_map[parent_metadata.identifier] = {'path': str(parent_rel_path),
                                                    'metadataStatus': parent_metadata.metadataStatus,
                                                    'name': parent_metadata.name,
                                                    'versionName': parent_metadata.softwareVersion.versionName,
                                                    'type': 'parent'}
    subdir_names.remove('common')
    for subdir_name in subdir_names:
        tool_name_length = len(
            tool_name)  # Use to get directory name string after 'tool_name'. In case there are underscores in tool_name.
        subtool_name = subdir_name[tool_name_length + 1:]
        if subtool_name == '':
            subtool_name = None
        subdir_map = make_subtool_map(tool_name, tool_version, subtool_name, base_dir=base_dir)
        tool_version_map.update(subdir_map)
    return tool_version_map


def make_subtool_map(tool_name, tool_version, subtool_name, base_dir=None):
    subtool_cwl_path = get_cwl_tool(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)
    subtool_rel_path = get_relative_path(subtool_cwl_path, base_path=base_dir)
    subtool_metadata_path = get_tool_metadata(tool_name, tool_version, subtool_name=subtool_name, parent=False,
                                              base_dir=base_dir)
    subtool_metadata = SubtoolMetadata.load_from_file(subtool_metadata_path)
    subdir_map = {}
    subdir_map[subtool_metadata.identifier] = {'path': str(subtool_rel_path), 'name': subtool_metadata.name,
                                               'metadataStatus': subtool_metadata.metadataStatus,
                                               'cwlStatus': subtool_metadata.cwlStatus, 'type': 'subtool'}
    return subdir_map


def make_tool_common_dir_map(tool_name, tool_version, base_dir):
    common_metadata_path = get_tool_common_dir(tool_name, tool_version, base_dir=base_dir) / common_tool_metadata_name
    common_metadata = ParentToolMetadata.load_from_file(common_metadata_path)
    common_dir_map = {}
    common_dir_map[common_metadata.identifier] = {'path': str(common_metadata_path),
                                                  'metadataStatus': common_metadata.metadataStatus,
                                                  'name': common_metadata.name,
                                                  'versionName': common_metadata.softwareVersion.versionName,
                                                  'type': 'parent'}
    return common_dir_map


def make_script_maps(outfile_path, base_dir=None):
    cwl_scripts_dir = get_root_scripts_dir(base_dir=base_dir)
    outfile_path = Path(outfile_path)
    script_maps = {}
    for group_dir in cwl_scripts_dir.iterdir():
        group_script_map = make_group_script_map(group_dir.name, base_dir=base_dir)
        script_maps.update(group_script_map)
    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    with outfile_path.open('w') as outfile:
        yaml.dump(script_maps, outfile)
    return


def make_group_script_map(group_name, base_dir=None):
    group_script_map = {}
    script_group_dir = get_script_group_dir(group_name, base_dir=base_dir)
    for project_dir in script_group_dir.iterdir():
        script_project_map = make_project_script_map(group_name, project_dir.name, base_dir=base_dir)
        group_script_map.update(script_project_map)
    return group_script_map


def make_project_script_map(group_name, project_name, base_dir=None):
    script_project_map = {}
    script_project_dir = get_script_project_dir(group_name, project_name, base_dir=base_dir)
    for version_dir in script_project_dir.iterdir():
        version_map = make_script_version_map(group_name, project_name, version_dir.name, base_dir=base_dir)
        script_project_map.update(version_map)
    return script_project_map


def make_script_version_map(group_name, project_name, version_name, base_dir=None):
    script_version_map = {}
    script_version_dir = get_script_version_dir(group_name, project_name, version_name, base_dir=base_dir)
    for script_dir in script_version_dir.iterdir():
        if script_dir.name == 'common':
            continue
        script_map = make_script_map(group_name, project_name, version_name, script_dir.name, base_dir=base_dir)
        script_version_map.update(script_map)
    return script_version_map


def make_script_map(group_name, project_name, version_name, script_name, base_dir=None):
    script_map = {}
    if script_name == 'common':  # script_name would also be common
        raise ValueError(f"Should not pass {script_name} to make map.")
    else:
        script_cwl_path = get_cwl_script(group_name, project_name, version_name, script_name, base_dir=base_dir)
        script_rel_path = get_relative_path(script_cwl_path, base_path=base_dir)
        metadata_path = get_metadata_path(script_cwl_path)
        script_metadata = ScriptMetadata.load_from_file(metadata_path)
        script_map[script_metadata.identifier] = {'path': str(script_rel_path), 'name': script_metadata.name,
                                                  'versionName': script_metadata.softwareVersion.versionName,
                                                  'metadataStatus': script_metadata.metadataStatus,
                                                  'cwlStatus': script_metadata.cwlStatus}
    return script_map


def make_workflow_maps(outfile_name='workflow-maps', base_dir=None):
    cwl_workflows_dir = get_workflows_root_dir(base_dir=base_dir)
    outfile_path = Path(outfile_name)
    master_workflow_map = {}
    for group_dir in cwl_workflows_dir.iterdir():
        for project_dir in group_dir.iterdir():
            for version_dir in project_dir.iterdir():
                for item in version_dir.iterdir():
                    if item.suffix == '.cwl':
                        workflow_dict = make_workflow_map(group_dir.name, project_dir.name, version_dir.name, item.stem,
                                                          base_dir=base_dir)
                        master_workflow_map.update(workflow_dict)
    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    with outfile_path.open('w') as outfile:
        yaml.dump(master_workflow_map, outfile)
    return


def make_workflow_map(group_name, project_name, version, workflow_name, base_dir=None):
    workflow_map = {}
    workflow_path = get_cwl_workflow(group_name, project_name, version, workflow_name, base_dir=base_dir)
    workflow_rel_path = get_relative_path(workflow_path, base_path=base_dir)
    workflow_metadata_path = get_metadata_path(workflow_path)
    workflow_metadata = WorkflowMetadata.load_from_file(workflow_metadata_path)
    workflow_map[workflow_metadata.identifier] = {'path': str(workflow_rel_path), 'name': workflow_metadata.name,
                                                  'versionName': workflow_metadata.softwareVersion.versionName,
                                                  'metadataStatus': workflow_metadata.metadataStatus,
                                                  'cwlStatus': workflow_metadata.cwlStatus}
    return workflow_map


def combine_yaml_files_into_dict(file_path, *file_paths):
    # make a 'master map' that contains all file
    combined_dict = {}
    with file_path.open('r') as f:
        combined_dict.update(safe_load(f))
    for file in file_paths:
        with file.open('r') as f:
            combined_dict.update(safe_load(f))
    return combined_dict


def make_master_map(file_name, *file_names, outfile_name="master_map"):
    file_path = config[os.environ['CONFIG_KEY']]['content_maps_dir'] / f"{file_name}.yaml"

    raise NotImplementedError


def get_tool_map():
    raise NotImplementedError


def add_to_map(path):
    """
    Add tools scripts and workflows with versions >= 1.0 to content_maps tool_maps, script_maps, or 'workflow_maps'.
    These maps provide an accessible way to work with content based on their identifiers.
    :param path:
    :return:
    """
    raise NotImplementedError


def get_tool_args_from_identifier(identifier, base_dir=None):
    base_dir = get_base_dir(base_dir)
    instance_hash = None
    if tool_instance_identifier_pattern.match(identifier):
        identifier, instance_hash = identifier[:-4], identifier[-4:]
    if parent_tool_identifier_pattern.match(identifier) | subtool_identifier_pattern.match(identifier):
        tools_map = make_tools_map(base_dir=base_dir)
        tool_path = tools_map[identifier]['path']
        tool_args = get_tool_args_from_path(tool_path)
    else:
        raise ValueError()
    return tool_args, instance_hash
