from pathlib import Path
from capanno_utils.make_content_maps import make_tools_map_dict
from capanno_utils.classes.metadata.tool_metadata import SubtoolMetadata
from capanno_utils.helpers.get_paths import *

unpublished_statuses = ('Draft', 'Incomplete')

def update_all_tools_to_released(base_dir=None, update_dir=None):
    tool_map = make_tools_map_dict(base_dir=base_dir, specify_exists=True)

    for identifier, values in tool_map.items():
        if values['type'] == 'subtool':
            update_existing_tool_wrapper_status(values, base_dir=base_dir, update_dir=update_dir)

    return


def update_existing_tool_wrapper_status(tool_map_values, base_dir=None, update_dir=None):
    base_dir = get_base_dir(base_dir=base_dir)
    metadata_path = Path(base_dir) / tool_map_values['metadataPath']
    subtool_metadata = SubtoolMetadata.load_from_file(metadata_path)
    if tool_map_values['cwlStatus'] in unpublished_statuses and tool_map_values['cwlExists'] == True:
        subtool_metadata.cwlStatus = 'Released'
    if tool_map_values['wdlStatus'] in unpublished_statuses and tool_map_values['wdlExists'] == True:
        subtool_metadata.wdlStatus = 'Released'
    if tool_map_values['nextflowStatus'] in unpublished_statuses and tool_map_values['nextflowExists'] == True:
        subtool_metadata.nextflowStatus = 'Released'
    if tool_map_values['snakemakeStatus'] in unpublished_statuses and tool_map_values['snakemakeExists'] == True:
        subtool_metadata.snakemakeStatus = 'Released'
    if update_dir == None or base_dir == update_dir:  # Need to overwrite the existing file.
        subtool_metadata.mk_file()
    else:
        # updated_path = Path(update_dir) / tool_map_values['metadataPath']
        subtool_metadata.root_repo_path = update_dir
        subtool_metadata.mk_file()

    return
