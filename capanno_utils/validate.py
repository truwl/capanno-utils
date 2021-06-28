import tempfile
import logging
from pathlib import Path
from ruamel.yaml import safe_load
from semantic_version import Version
from capanno_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata
from capanno_utils.classes.metadata.script_metadata import ScriptMetadata, CommonScriptMetadata
from capanno_utils.classes.metadata.workflow_metadata import WorkflowMetadata
from .content_maps import *
from .helpers.get_paths import get_metadata_path, get_base_dir, get_tool_sources_from_metadata_path, get_workflow_sources_from_metadata_path
from .helpers.validate_cwl import validate_cwl_doc
from .helpers.validate_wdl import validate_wdl_doc
from .validate_inputs import validate_all_inputs_for_tool


def metadata_validator_factory(class_to_validate):
    def metadata_validator(metadata_path):
        try:
            metadata_instance = class_to_validate.load_from_file(metadata_path)
            # print(f"Metadata in {metadata_path} is valid {str(class_to_validate)}")
            logging.info(f"Metadata in {metadata_path} is valid {str(class_to_validate)}")
        except:
            logging.error(f"{str(class_to_validate)} in {metadata_path} failed validation.")
            raise
        return

    return metadata_validator


validate_parent_tool_metadata = metadata_validator_factory(ParentToolMetadata)
validate_subtool_metadata = metadata_validator_factory(SubtoolMetadata)
validate_script_metadata = metadata_validator_factory(ScriptMetadata)
validate_common_script_metadata = metadata_validator_factory(CommonScriptMetadata)
validate_workflow_metadata = metadata_validator_factory(WorkflowMetadata)


def validate_tool_content_from_map(tool_map_dict, base_dir=None):
    """
    tool_map(dict): Keys are identifers, values are dict with path, metadataStatus, name, versionName, and type keys.
    """
    validate_statuses = ('Draft', 'Released')
    if base_dir is None:
        base_dir = get_base_dir()
    for identifier, values in tool_map_dict.items():
        metadata_path = base_dir / values['metadataPath']
        tool_type = values['type']

        if tool_type == 'parent':  # could now also get type directly from path.
            if not 'common' in metadata_path.parts:
                raise ValueError(f"")
            validate_parent_tool_metadata(metadata_path)
        else:  # is a subtool
            validate_subtool_metadata(metadata_path)
            tool_sources = get_tool_sources_from_metadata_path(metadata_path)
            cwl_path, wdl_path, sm_path, nf_path = tuple(tool_sources.values())
            cwl_status = values['cwlStatus']
            if cwl_status in validate_statuses:
                validate_cwl_doc(cwl_path)
                validate_all_inputs_for_tool(cwl_path)
            if values['wdlStatus'] in validate_statuses:
                validate_wdl_doc(wdl_path)
            if values['nextflowStatus'] in validate_statuses:
                if not nf_path.exists():
                    raise FileNotFoundError(f"{str(nf_path)} does not exist.")
                logging.info(f"Nexflow files are not validated. {nf_path}")
            if values['snakemakeStatus'] in validate_statuses:
                if not sm_path.exists():
                    raise FileNotFoundError(f"{str(sm_path)} does not exist.")
                logging.info(f"Snakemake files are not validated {sm_path}")
    return


def validate_tools_dir(base_dir=None):
    """
    Validate all cwl files, metadata files, instances and instance metadata in a tools directory
    :return:
    """

    tool_map_dict = make_tools_map_dict(base_dir=base_dir)
    validate_tool_content_from_map(tool_map_dict, base_dir)

    return


def validate_main_tool_directory(tool_name, base_dir=None):
    """
    Validate all content in a tool directory. All versions, subtools, etc.
    """
    tool_map_dict = make_main_tool_map(tool_name, base_dir=base_dir)
    validate_tool_content_from_map(tool_map_dict, base_dir)
    return


def validate_tool_version_dir(tool_name, tool_version, base_dir=None):
    tool_version_map = make_tool_version_dir_map(tool_name, tool_version, base_dir=base_dir)
    validate_tool_content_from_map(tool_version_map, base_dir=base_dir)
    return


def validate_tool_common_dir(tool_name, tool_version, base_dir=None):
    common_tool_map = make_tool_common_dir_map(tool_name, tool_version, base_dir=base_dir)
    validate_tool_content_from_map(common_tool_map, base_dir=base_dir)
    return


def validate_subtool_dir(tool_name, version_name, subtool_name=None, base_dir=None):
    subtool_dir_map = make_subtool_map(tool_name, version_name, subtool_name, base_dir=base_dir)
    validate_tool_content_from_map(subtool_dir_map, base_dir=base_dir)
    return


# Scripts stuff

def validate_script_content_from_map(script_map_dict, base_dir=None):
    if base_dir is None:
        base_dir = get_base_dir()
    for identifier, values in script_map_dict.items():
        # validate metadata
        script_path = base_dir / values['path']
        metadata_path = get_metadata_path(script_path)
        validate_script_metadata(metadata_path)

        # validate cwl
        cwl_status = values['cwlStatus']
        if cwl_status in ('Draft', 'Released'):
            validate_cwl_doc(script_path)
            validate_all_inputs_for_tool(script_path)
    return


def validate_scripts_dir(base_dir=None):
    script_map_temp_file = tempfile.NamedTemporaryFile(prefix='scripts_map', suffix='.yaml',
                                                       delete=True)  # Change to False if file doesn't persist long enough.
    make_script_maps(script_map_temp_file.name, base_dir=base_dir)
    with script_map_temp_file as script_map:
        script_map_dict = safe_load(script_map)
    validate_script_content_from_map(script_map_dict, base_dir)
    return


def validate_group_scripts_dir(group_name, base_dir=None):
    group_script_map = make_group_script_map(group_name, base_dir=base_dir)
    validate_script_content_from_map(group_script_map, base_dir=base_dir)
    return


def validate_project_scripts_dir(group_name, project_name, base_dir=None):
    project_script_map = make_project_script_map(group_name, project_name, base_dir=base_dir)
    validate_script_content_from_map(project_script_map, base_dir=base_dir)
    return


def validate_version_script_dir(group_name, project_name, version_name, base_dir=None):
    version_script_map = make_script_version_map(group_name, project_name, version_name, base_dir=base_dir)
    validate_script_content_from_map(version_script_map, base_dir=base_dir)
    return


def validate_script_dir(group_name, project_name, version_name, script_name, base_dir=None):
    script_map = make_script_map(group_name, project_name, version_name, script_name, base_dir=base_dir)
    validate_script_content_from_map(script_map, base_dir=base_dir)
    return

# ## Workflows stuff

def validate_workflows_from_map(workflow_map_dict, base_dir=None):
    if base_dir is None:
        base_dir = get_base_dir()
    for identifier, values in workflow_map_dict.items():
        workflow_metadata = base_dir / values['metadataPath']
        validate_workflow_metadata(workflow_metadata)

        wf_status = values['workflowStatus']
        if wf_status in ('Draft', 'Released'):
            wf_language = values['workflowLanguage']
            try:
                workflow_path = workflow_metadata.parent / values['workflowPath']
            except TypeError:
                print(values)
                raise
            if not workflow_path.exists():
                raise FileNotFoundError(f"{str(workflow_path)} does not exist.")
            logging.debug(
                f"Make sure you validate {workflow_path}")  # Todo. Think I have good way to validate somewhere. Need to port here (needs to be put in a temporary directory with the tools and workflows that it calls.)
    return


def validate_workflows_dir(base_dir=None):

    workflow_map_dict = make_workflow_maps_dict(base_dir=base_dir)
    validate_workflows_from_map(workflow_map_dict, base_dir)
    return

def validate_workflow_group_dir(group_name, base_dir=None):

    workflow_map_dict = make_group_workflow_map(group_name, base_dir)
    validate_workflows_from_map(workflow_map_dict, base_dir)
    return

def validate_workflow_project_dir(group_name, project_name, base_dir=None):
    workflow_map_dict = make_project_workflow_map(group_name, project_name, base_dir)
    validate_workflows_from_map(workflow_map_dict, base_dir)
    return

def validate_workflow_version_dir(group_name, project_name, version_name, base_dir=None):
    workflow_map_dict = make_version_workflow_map(group_name, project_name, version_name, base_dir)
    validate_workflows_from_map(workflow_map_dict, base_dir)
    return

# Whole repo

def validate_repo(base_dir=None):
    validate_tools_dir(base_dir=base_dir)
    validate_scripts_dir(base_dir=base_dir)
    validate_workflows_dir(base_dir=base_dir)
    return
