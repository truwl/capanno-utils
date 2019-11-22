#!/usr/bin/env python3

from pathlib import Path
from xd_cwl_utils.classes.metadata.tool_metadata import ParentToolMetadata
from xd_cwl_utils.helpers.get_paths import get_tool_common_dir


def add_tool(tool_name, tool_version, subtool_names=None, biotools_id=None, has_primary=False, init_cwl=True):
    """
    Make the correct directory structure for adding a new command line tool. Optionally, create initialized CWL
    and metadata files. Run from cwl-tools directory.
    :param tool_name(str): Name of the tool
    :param tool_version(str): version of the tool
    :param subtool_names(list(str)): list of subtool names if the tool is broken into multiple subtools.
    :param mk_meta_files(bool): Specify whether to make initial CWL and metadata files.
    :return: None
    """
    tool_version = str(tool_version) # In case ArgumentParser is bypassed.
    if subtool_names:
        if isinstance(subtool_names, str):
            subtool_names = [subtool_names]
    common_dir = get_tool_common_dir(tool_name, tool_version, base_dir=Path.cwd())
    common_dir.mkdir(parents=True, exist_ok=False)
    if has_primary:  # Need to append __main__ onto subtools.
        if subtool_names:
            subtool_names.append('__main__')
        else:
            subtool_names = ['__main__']
    if biotools_id:
        # tool_name will be ignored.
        parent_metadata = ParentToolMetadata.create_from_biotools(biotools_id, tool_version, subtool_names)
    else:
        parent_metadata = ParentToolMetadata(name=tool_name, softwareVersion=tool_version, featureList=subtool_names)
    parent_file_path = common_dir / f"common-metadata.yaml"
    for subtool in parent_metadata.featureList:
        subtool_obj = parent_metadata.make_subtool_metadata(subtool_name=subtool, parent_metadata_path=parent_file_path)
        subtool_obj.mk_file()
    parent_metadata.mk_file(parent_file_path)
    return parent_file_path


def add_subtool(parent_rel_path, subtool_name, init_cwl=True):
    parent_path = Path(parent_rel_path) # Should be in /common
    parent_meta = ParentToolMetadata.load_from_file(parent_path)
    new_subtool_dir = parent_path.parents[1] / f"{parent_meta.name}_{subtool_name}"
    new_subtool_dir.mkdir()
    subtool_meta = parent_meta.make_subtool_metadata(subtool_name, parent_path)
    new_file_path = new_subtool_dir / f"{subtool_name}-metadata.yaml"
    subtool_meta.mk_file(new_file_path)
    return new_file_path
