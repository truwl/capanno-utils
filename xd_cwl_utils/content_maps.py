import os
from pathlib import Path
from ruamel.yaml import safe_load, YAML
from xd_cwl_utils.config import config
from xd_cwl_utils.classes.metadata.script_metadata import ScriptMetadata
from xd_cwl_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata
from xd_cwl_utils.classes.metadata.workflow_metadata import WorkflowMetadata
from xd_cwl_utils.helpers.get_paths import get_cwl_tool, get_tool_metadata, get_tool_version_dir, \
    get_script_version_dir, get_metadata_path, get_relative_path, get_workflow_version_dir, get_root_tools_dir, \
    get_root_scripts_dir, get_workflows_root_dir, get_cwl_workflow

def make_tools_map(outfile_path, base_dir=None):
    """
    Make a yaml file that specifies paths and attributes of tools in tool_dir.
    :param tool_dir (Path): Path of directory that contains tools.
    :param outfile_name(str): name of file that will be made.
    :return:
        None
    """

    cwl_tools_dir = get_root_tools_dir(base_dir=base_dir)
    content_map = {}
    outfile_path = Path(outfile_path)
    for tool_dir in  cwl_tools_dir.iterdir():
        for version_dir in tool_dir.iterdir():
            tool_map = make_tool_map(tool_dir.name, version_dir.name, base_dir=base_dir)
            content_map.update(tool_map)
    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    with outfile_path.open('w') as outfile:
        yaml.dump(content_map, outfile)
    return


def make_tool_map(tool_name, tool_version, base_dir=None):
    tool_map = {}
    tool_version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=base_dir)
    subdir_names = [subdir.name for subdir in tool_version_dir.iterdir()]

    parent_metadata_path = get_tool_metadata(tool_name, tool_version, parent=True, base_dir=base_dir)
    parent_metadata = ParentToolMetadata.load_from_file(parent_metadata_path)
    parent_rel_path = get_relative_path(parent_metadata_path, base_path=base_dir)
    tool_map[parent_metadata.identifier] = {'path': str(parent_rel_path), 'metadataStatus': parent_metadata.metadataStatus, 'name': parent_metadata.name, 'versionName': parent_metadata.softwareVersion.versionName, 'type': 'parent'}
    subdir_names.remove('common')
    tool_name_len = len(tool_name)
    for subdir_name in subdir_names:
        assert subdir_name[:tool_name_len] == tool_name
        subtool_name_parts = subdir_name[tool_name_len:].split('_')
        subtool_name_parts_len = len(subtool_name_parts)
        if subtool_name_parts_len > 2:
            subtool_name = '_'.join(subtool_name_parts[1:])
        elif subtool_name_parts_len == 2:  # The common case.
            subtool_name = subdir_name.split('_')[1]
        elif subtool_name_parts_len == 1: # have a subtool that is the 'main' part of the tool; i.e. not a submodule. e.g. md5sum and md5sum_check
            subtool_name = None
        else:
            raise NotImplementedError(
                f"There are zero underscores in a subtool directory {subdir_name}. Can't handle this yet.")
        # Lots that could happen here. tool name could have an underscore, etc.
        subtool_cwl_path = get_cwl_tool(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)
        subtool_rel_path = get_relative_path(subtool_cwl_path, base_path=base_dir)
        subtool_metadata_path = get_tool_metadata(tool_name, tool_version, subtool_name=subtool_name, parent=False, base_dir=base_dir)
        subtool_metadata = SubtoolMetadata.load_from_file(subtool_metadata_path)
        tool_map[subtool_metadata.identifier] = {'path': str(subtool_rel_path), 'name': subtool_metadata.name, 'metadataStatus': subtool_metadata.metadataStatus, 'cwlStatus': subtool_metadata.cwlStatus, 'type': 'subtool'}
    return tool_map


def make_script_maps(outfile_path, base_dir=None):
    cwl_scripts_dir = get_root_scripts_dir(base_dir=base_dir)
    outfile_path = Path(outfile_path)
    script_maps = {}
    for group_dir in cwl_scripts_dir.iterdir():
        for project_dir in group_dir.iterdir():
            for version_dir in project_dir.iterdir():
                script_maps.update(make_script_map(group_dir.name, project_dir.name, version_dir.name, base_dir=base_dir))
    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    with outfile_path.open('w') as outfile:
        yaml.dump(script_maps, outfile)
    return


def make_script_map(group_name, project_name, version, base_dir=None):
    script_map = {}
    script_ver_dir = get_script_version_dir(group_name, project_name, version, base_dir=base_dir)
    for script_dir in script_ver_dir.iterdir():
        if script_dir.name == 'common':
            continue
        script_cwl_path = script_dir / f"{script_dir.name}.cwl"
        script_rel_path = get_relative_path(script_cwl_path, base_path=base_dir)
        metadata_path = get_metadata_path(script_cwl_path)
        script_metadata = ScriptMetadata.load_from_file(metadata_path)
        script_map[script_metadata.identifier] = {'path': str(script_rel_path), 'name': script_metadata.name, 'versionName': script_metadata.softwareVersion.versionName, 'metadataStatus': script_metadata.metadataStatus, 'cwlStatus': script_metadata.cwlStatus}
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
                        workflow_dict = make_workflow_map(group_dir.name, project_dir.name, version_dir.name, item.stem, base_dir=base_dir)
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
    workflow_map[workflow_metadata.identifier] = {'path': str(workflow_rel_path), 'name': workflow_metadata.name, 'versionName': workflow_metadata.softwareVersion.versionName, 'metadataStatus': workflow_metadata.metadataStatus, 'cwlStatus': workflow_metadata.cwlStatus}
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