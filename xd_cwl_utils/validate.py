from pathlib import Path
from .helpers.string_tools import get_subtool_name_from_dir_name
from .validate_metadata import metadata_validator_factory
from .classes.metadata.tool_metadata import ParentToolMetadata
# from .helpers.get_paths import


def validate_tool_instances(cwl_file, instances_dir):
    raise NotImplementedError

def validate_tool_dir(cwl_tools_dir):
    """
    Validate all cwl files, metadata files, instances and instance metadata in a cwl-tools directory
    :return:
    """
    cwl_tools_dir = Path(cwl_tools_dir)
    for main_tool_dir in cwl_tools_dir.iterdir():
        tool_name = main_tool_dir.name
        for version_dir in main_tool_dir.iterdir():
            tool_version = version_dir.name
            for tool_subdir in version_dir.iterdir():
                subdir_name = tool_subdir.name
                if subdir_name == 'common':
                    # Have the common directory. Should only have to validate parent metadata.
                    common_metadata_path = tool_subdir / f"{tool_name}-metadata.yaml"
                    validate_file = metadata_validator_factory(ParentToolMetadata)
                    validate_file(common_metadata_path)
                elif subdir_name == tool_name:  # have the main tool. Might also have subtools.
                    # Validate metadata, cwl file, and instances/instance metadata
                    raise NotImplementedError
                else:
                    subtool_name = get_subtool_name_from_dir_name(tool_name, subdir_name)
                    raise NotImplementedError
    raise NotImplementedError


def validate_script_dir():
    raise NotImplementedError
