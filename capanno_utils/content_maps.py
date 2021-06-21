from ruamel.yaml import safe_load
from capanno_utils.classes.metadata.script_metadata import ScriptMetadata
from capanno_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata
from capanno_utils.classes.metadata.workflow_metadata import WorkflowMetadata
from capanno_utils.helpers.dict_tools import no_clobber_update
from capanno_utils.helpers.file_management import dump_dict_to_yaml_output
from capanno_utils.helpers.get_paths import *


# Todo before stable release: update function names to be consistent.

def make_tool_identifiers_list(base_dir=None):
    tools_map = make_tools_map_dict(base_dir=base_dir)
    tool_identifiers = list(tools_map.keys())
    return tool_identifiers

def make_tools_index(base_dir, index_path=tool_index_path):
    tool_identifiers = make_tool_identifiers_list(base_dir=base_dir)
    root_repo_path = Path(base_dir)
    identifier_index_path = root_repo_path / identifier_index_dir
    if not identifier_index_path.exists():
        identifier_index_path.mkdir()
    index_path = Path(base_dir) / index_path
    with index_path.open('w') as index_file:
        index_file.writelines(f"{identifier}\n" for identifier in tool_identifiers)
    return index_path.resolve()


def make_tools_map_dict(base_dir=None, specify_exists=False):
    tools_dir = get_root_tools_dir(base_dir=base_dir)
    tools_map = {}

    for tool_dir in tools_dir.iterdir():
        if tool_dir.name == '.DS_Store':
            continue
        assert tool_dir.is_dir()
        for version_dir in tool_dir.iterdir():
            if version_dir.name == '.DS_Store':
                continue
            assert version_dir.is_dir()
            tool_map = make_tool_version_dir_map(tool_dir.name, version_dir.name, base_dir=base_dir, specify_exists=specify_exists)
            no_clobber_update(tools_map, tool_map)
    return tools_map

def make_tools_map(outfile_path=None, base_dir=None, specify_exists=False):
    """
    Make a yaml file that specifies paths and attributes of tools in tool_dir.
    :param tool_dir (Path): Path of directory that contains tools.
    :param outfile_name(str): name of file that will be made.
    :return:
        None
    """

    tools_map = make_tools_map_dict(base_dir=base_dir, specify_exists=specify_exists)
    dump_dict_to_yaml_output(tools_map, output=outfile_path)
    return outfile_path


def make_main_tool_map(tool_name, base_dir=None):
    """
    Make a yaml file that specifies paths and attributes of tools in a single tool directory. If outfile is provided, dump contents to outfile.

    """
    main_tool_map = {}
    tool_dir = get_main_tool_dir(tool_name, base_dir=base_dir)
    for version_dir in tool_dir.iterdir():
        no_clobber_update(main_tool_map, make_tool_version_dir_map(tool_name, version_dir.name, base_dir=base_dir))
    return main_tool_map


def make_tool_version_dir_map(tool_name, tool_version, base_dir=None, specify_exists=False):
    tool_version_map = {}

    tool_version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=base_dir)
    parent_metadata_path = get_tool_metadata(tool_name, tool_version, parent=True, base_dir=base_dir)
    parent_metadata = ParentToolMetadata.load_from_file(parent_metadata_path, check_index=False)
    parent_rel_path = get_relative_path(parent_metadata_path, base_path=base_dir)
    tool_version_map[parent_metadata.identifier] = {'metadataPath': str(parent_rel_path),
                                                    'metadataStatus': parent_metadata.metadataStatus,
                                                    'name': parent_metadata.name,
                                                    'versionName': parent_metadata.softwareVersion.versionName,
                                                    'type': 'parent'}
    for subtool_dir in tool_version_dir.iterdir():
        if subtool_dir.name in ['.DS_Store', 'common']:
            continue
        assert subtool_dir.is_dir(), subtool_dir.name+" is not a directory. You likely have an extra file."
        tool_name_length = len(
            tool_name)  # Use to get directory name string after 'tool_name'. In case there are underscores in tool_name.
        subtool_name = subtool_dir.name[tool_name_length + 1:]
        if subtool_name == '':
            subtool_name = None
        subdir_map = make_subtool_map(tool_name, tool_version, subtool_name, base_dir=base_dir, specify_exists=specify_exists)
        no_clobber_update(tool_version_map, subdir_map)
    return tool_version_map


def make_subtool_map(tool_name, tool_version, subtool_name, base_dir=None, specify_exists=False):
    subtool_metadata_path = get_tool_metadata(tool_name, tool_version, subtool_name=subtool_name, parent=False,
                                              base_dir=base_dir)
    subtool_metadata = SubtoolMetadata.load_from_file(subtool_metadata_path, check_index=False)
    subdir_map = {}
    subtool_rel_path = get_relative_path(subtool_metadata_path, base_path=base_dir)
    if specify_exists:
        files_exist = check_for_workflow_language_files(subtool_metadata_path)
        subdir_map[subtool_metadata.identifier] = {'metadataPath': str(subtool_rel_path),
                                               'name': subtool_metadata.name,
                                               'metadataStatus': subtool_metadata.metadataStatus,
                                               'cwlStatus': subtool_metadata.cwlStatus,
                                               'cwlExists': files_exist['cwl'],
                                               'nextflowStatus': subtool_metadata.nextflowStatus,
                                               'nextflowExists': files_exist['nextflow'],
                                               'snakemakeStatus': subtool_metadata.snakemakeStatus,
                                               'snakemakeExists': files_exist['snakemake'],
                                               'wdlStatus': subtool_metadata.wdlStatus,
                                               'wdlExists': files_exist['wdl'],
                                               'type': 'subtool'}
    else:
        subdir_map[subtool_metadata.identifier] = {'metadataPath': str(subtool_rel_path),
                                               'name': subtool_metadata.name,
                                               'metadataStatus': subtool_metadata.metadataStatus,
                                               'cwlStatus': subtool_metadata.cwlStatus,
                                               'nextflowStatus': subtool_metadata.nextflowStatus,
                                               'snakemakeStatus': subtool_metadata.snakemakeStatus,
                                               'wdlStatus': subtool_metadata.wdlStatus,
                                               'type': 'subtool'}
    return subdir_map



def make_tool_common_dir_map(tool_name, tool_version, base_dir):
    common_metadata_path = get_tool_common_dir(tool_name, tool_version, base_dir=base_dir) / common_tool_metadata_name
    common_metadata = ParentToolMetadata.load_from_file(common_metadata_path, check_index=False)
    common_dir_map = {}
    common_dir_map[common_metadata.identifier] = {'metadataPath': str(common_metadata_path),
                                                  'metadataStatus': common_metadata.metadataStatus,
                                                  'name': common_metadata.name,
                                                  'versionName': common_metadata.softwareVersion.versionName,
                                                  'type': 'parent'}
    return common_dir_map



def check_for_workflow_language_files(subtool_metadata_path):
    workflow_language_file_path_dict = get_tool_sources_from_metadata_path(subtool_metadata_path)
    files_exist = {}
    for source_type, source_path in workflow_language_file_path_dict.items():
        files_exist[source_type] = source_path.exists()
    return files_exist







def make_scripts_map_dict(base_dir=None):
    scripts_dir = get_root_scripts_dir(base_dir=base_dir)

    scripts_map = {}
    for group_dir in scripts_dir.iterdir():
        group_script_map = make_group_script_map(group_dir.name, base_dir=base_dir)
        no_clobber_update(scripts_map, group_script_map)
    return scripts_map

def make_script_maps(outfile_path, base_dir=None):
    scripts_map = make_scripts_map_dict(base_dir=base_dir)
    dump_dict_to_yaml_output(scripts_map, output=outfile_path)
    return


def make_group_script_map(group_name, base_dir=None):
    group_script_map = {}
    script_group_dir = get_script_group_dir(group_name, base_dir=base_dir)
    for project_dir in script_group_dir.iterdir():
        script_project_map = make_project_script_map(group_name, project_dir.name, base_dir=base_dir)
        no_clobber_update(group_script_map, script_project_map)
    return group_script_map


def make_project_script_map(group_name, project_name, base_dir=None):
    script_project_map = {}
    script_project_dir = get_script_project_dir(group_name, project_name, base_dir=base_dir)
    for version_dir in script_project_dir.iterdir():
        version_map = make_script_version_map(group_name, project_name, version_dir.name, base_dir=base_dir)
        no_clobber_update(script_project_map, version_map)
    return script_project_map


def make_script_version_map(group_name, project_name, version_name, base_dir=None):
    script_version_map = {}
    script_version_dir = get_script_version_dir(group_name, project_name, version_name, base_dir=base_dir)
    for script_dir in script_version_dir.iterdir():
        if script_dir.name == 'common':
            continue
        script_map = make_script_map(group_name, project_name, version_name, script_dir.name, base_dir=base_dir)
        no_clobber_update(script_version_map, script_map)
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

# Workflow maps

def make_workflow_maps_dict(base_dir=None):
    workflows_dir = get_workflows_root_dir(base_dir=base_dir)
    master_workflow_map = {}
    for group_dir in workflows_dir.iterdir():
        for project_dir in group_dir.iterdir():
            for version_dir in project_dir.iterdir():
                workflow_dict = make_workflow_map(group_dir.name, project_dir.name, version_dir.name,
                                                          base_dir=base_dir)
                no_clobber_update(master_workflow_map, workflow_dict)
    return master_workflow_map

def make_workflow_maps(outfile_name='workflow-maps', base_dir=None):
    master_workflow_map = make_workflow_maps_dict(base_dir=base_dir)
    dump_dict_to_yaml_output(master_workflow_map, output=outfile_name)
    return

def make_group_workflow_map(group_name, base_dir=None):
    group_workflow_map = {}
    workflow_group_dir = get_workflow_group_dir(group_name, base_dir)
    for project_dir in workflow_group_dir.iterdir():
        workflow_project_map = make_project_workflow_map(group_name, project_dir.name, base_dir)
        no_clobber_update(group_workflow_map, workflow_project_map)
    return group_workflow_map

def make_project_workflow_map(group_name, project_name, base_dir=None):
    workflow_project_map = {}
    workflow_project_dir = get_workflow_project_dir(group_name, project_name, base_dir)
    for version_dir in workflow_project_dir.iterdir():
        version_map = make_workflow_map(group_name, project_name, version_dir.name, project_name, base_dir)
        no_clobber_update(workflow_project_map, version_map)
    return workflow_project_map

def make_version_workflow_map(group_name, project_name, version_name, base_dir=None):
    workflow_version_map = make_workflow_map(group_name, project_name, version_name, project_name, base_dir)
    return workflow_version_map

def make_workflow_map(group_name, project_name, version, base_dir=None):
    workflow_map = {}
    workflow_metadata_path = get_workflow_metadata(group_name, project_name, version, base_dir=base_dir)
    workflow_metadata = WorkflowMetadata.load_from_file(workflow_metadata_path)
    workflow_metadata_rel_path = get_relative_path(workflow_metadata_path, base_path=base_dir)
    workflow_map[workflow_metadata.identifier] = {'metadataPath': str(workflow_metadata_rel_path), 'name': workflow_metadata.name,
                                                  'metadataStatus': workflow_metadata.metadataStatus,
                                                  'workflowLanguage': workflow_metadata.workflowLanguage,
                                                  'workflowStatus': workflow_metadata.workflowStatus,
                                                  'workflowPath': workflow_metadata.workflowFile,
                                                  'versionName': workflow_metadata.softwareVersion.versionName,
                                                }
    return workflow_map


def combine_yaml_files_into_dict(file_path, *file_paths):
    # make a 'master map' that contains all file
    combined_dict = {}
    with file_path.open('r') as f:
        no_clobber_update(combined_dict, safe_load(f))
    for file in file_paths:
        with file.open('r') as f:
            no_clobber_update(combined_dict, safe_load(f))
    return combined_dict


def make_master_map_dict(base_dir=None, specify_exists=False):
    master_map = {}
    master_map.update(make_tools_map_dict(base_dir=base_dir, specify_exists=specify_exists))
    master_map.update(make_scripts_map_dict(base_dir=base_dir))
    master_map.update(make_workflow_maps_dict(base_dir=base_dir))
    return master_map

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
        tool_path = tools_map[identifier]['metadataPath']
        tool_args = get_tool_args_from_path(tool_path)
    else:
        raise ValueError()
    return tool_args, instance_hash