import tempfile
import logging
from pathlib import Path
from ruamel.yaml import safe_load
from semantic_version import Version
from .content_maps import make_tools_map, make_script_maps, make_workflow_maps
from .validate_metadata import main as validate_meta
from .helpers.get_paths import get_metadata_path
from .helpers.validate_cwl import validate_cwl_tool
from .validate_inputs import validate_all_inputs_for_tool
from .classes.cwl.command_line_tool import ValidationException


def validate_tools_dir(base_dir=None):
    """
    Validate all cwl files, metadata files, instances and instance metadata in a cwl-tools directory
    :return:
    """
    tool_map_temp_file = tempfile.NamedTemporaryFile(prefix='tools_map', suffix='.yaml', delete=True)  # Change to False if file doesn't persist long enough.
    make_tools_map(tool_map_temp_file.name, base_dir=base_dir)
    with tool_map_temp_file as tool_map:
        tool_map_dict = safe_load(tool_map)
    for identifier, values in tool_map_dict.items():
        tool_path = base_dir / values['path']
        tool_type = values['type']
        metadata_status = values['metadataStatus']


        if tool_type == 'parent':
            if not 'common' in tool_path.parts:
                raise ValueError  # an extra check.
            meta_type = 'parent_tool'  # correspond to command in validate_metadata
            validate_meta([meta_type, str(tool_path)])
            # assert no instances directory here?
        else:  # either a subtool or 'main' tool
            cwl_status = values['cwlStatus']
            # validate metadata
            metadata_path = get_metadata_path(tool_path)
            meta_type = tool_type
            validate_meta([meta_type, str(metadata_path)])

            # validate cwl only if metadata specifies if it is version Released
            if cwl_status in ('Released',):
                validate_cwl_tool(tool_path)

                # validate instances
                validate_all_inputs_for_tool(tool_path)

    return


def validate_scripts_dir(base_dir=None):

    script_map_temp_file = tempfile.NamedTemporaryFile(prefix='scripts_map', suffix='.yaml', delete=True)  # Change to False if file doesn't persist long enough.
    make_script_maps(script_map_temp_file.name, base_dir=base_dir)
    with script_map_temp_file as script_map:
        script_map_dict = safe_load(script_map)
    for identifier, values in script_map_dict.items():
        # validate metadata
        script_path = base_dir / values['path']
        metadata_path = get_metadata_path(script_path)
        validate_meta(['script', str(metadata_path)])

        # validate cwl
        cwl_status = values['cwlStatus']
        if cwl_status in ('Draft', 'Released'):
            validate_cwl_tool(script_path)
            validate_all_inputs_for_tool(script_path)
    return


def validate_workflows_dir(base_dir=None):
    workflow_map_temp_file = tempfile.NamedTemporaryFile(prefix='workflows_map', suffix='.yaml', delete=True)
    make_workflow_maps(workflow_map_temp_file.name, base_dir=base_dir)
    with workflow_map_temp_file as workflow_map:
        workflow_map_dict = safe_load(workflow_map)
    for identifier, values in workflow_map_dict.items():
        workflow_path = base_dir / values['path']
        workflow_metadata = get_metadata_path(workflow_path)
        validate_meta(['workflow', str(workflow_metadata)])

        cwl_status = values['cwlStatus']
        if cwl_status in ('Draft', 'Released'):
            print(f"Make sure you validate {workflow_path}")  # Todo. Think I have good way to validate somewhere in biodrafter. Need to port here (needs to be put in a temporary directory with the tools and workflows that it calls.)
    return

def validate_repo(base_dir=None):
    validate_tools_dir(base_dir=base_dir)
    validate_scripts_dir(base_dir=base_dir)
    validate_workflows_dir(base_dir=base_dir)
    return
