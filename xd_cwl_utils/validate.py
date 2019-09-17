import tempfile
import logging
from pathlib import Path
from ruamel.yaml import safe_load
from semantic_version import Version
from .content_maps import make_tools_map, make_script_maps
from .validate_metadata import main as validate_meta
from .helpers.get_paths import get_metadata_path
from .helpers.validate_cwl import validate_cwl_tool, validate_cwl_tool_2


def validate_tool_instances(cwl_file, instances_dir):
    raise NotImplementedError

def validate_tools_dir(cwl_tools_dir=None):
    """
    Validate all cwl files, metadata files, instances and instance metadata in a cwl-tools directory
    :return:
    """
    tool_map_temp_file = tempfile.NamedTemporaryFile(prefix='tools_map', suffix='.yaml', delete=True)  # Change to False if file doesn't persist long enough.
    make_tools_map(tool_map_temp_file.name, cwl_tools_dir=cwl_tools_dir)
    with tool_map_temp_file as tool_map:
        tool_map_dict = safe_load(tool_map)
    for identifier, values in tool_map_dict.items():
        tool_path = Path(values['path'])
        tool_type = values['type']
        file_version = Version(values['version'])


        if tool_type == 'parent':
            if not 'common' in tool_path.parts:
                raise ValueError  # an extra check.
            meta_type = 'parent_tool'  # correspond to command in validate_metadata
            validate_meta([meta_type, str(tool_path)])
            # assert no instances directory here?
        else:  # either a subtool or 'main' tool

            # validate metadata
            metadata_path = get_metadata_path(tool_path)
            meta_type = tool_type
            validate_meta([meta_type, str(metadata_path)])

            # validate cwl only if metadata specifies if it is version >= 1.0
            if file_version >= Version('1.0.0'):
                validate_cwl_tool_2(tool_path)

            # TODO: validate instances.  Work on this one.
    return


def validate_scripts_dir(cwl_scripts_dir=None):

    script_map_temp_file = tempfile.NamedTemporaryFile(prefix='scripts_map', suffix='.yaml', delete=True)  # Change to False if file doesn't persist long enough.
    make_script_maps(script_map_temp_file.name, cwl_scripts_dir=cwl_scripts_dir)
    with script_map_temp_file as script_map:
        script_map_dict = safe_load(script_map)
    for identifier, values in script_map_dict.items():
        # validate metadata
        metadata_path = get_metadata_path(values['path'])
        validate_meta(['script', str(metadata_path)])

        # validate cwl
        document_version = Version(values['version'])
        if document_version >= Version('1.0.0'):
            validate_cwl_tool_2(values['path'])

    return


def validate_repo():
    raise NotImplementedError