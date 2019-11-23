#!/usr/bin/env python3

from pathlib import Path
from xd_cwl_utils.classes.metadata.tool_metadata import ParentToolMetadata
from xd_cwl_utils.helpers.get_paths import get_tool_common_dir, main_tool_subtool_name, get_tool_metadata


def add_tool(tool_name, tool_version, subtool_names=None, biotools_id=None, has_primary=False, root_repo_path=Path.cwd(), init_cwl=True):
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
    common_dir = get_tool_common_dir(tool_name, tool_version, base_dir=root_repo_path)
    common_dir.mkdir(parents=True, exist_ok=False)
    if has_primary:  # Need to append __main__ onto subtools.
        if subtool_names:
            subtool_names.append(main_tool_subtool_name)
        else:
            subtool_names = [main_tool_subtool_name]
    if biotools_id:
        # tool_name will be ignored.
        parent_metadata = ParentToolMetadata.create_from_biotools(biotools_id, tool_version, subtool_names)
    else:
        parent_metadata = ParentToolMetadata(name=tool_name, softwareVersion=tool_version, featureList=subtool_names)
    parent_file_path = common_dir / f"common-metadata.yaml"
    if parent_metadata.featureList:
        for subtool in parent_metadata.featureList:
            subtool_obj = parent_metadata.make_subtool_metadata(subtool_name=subtool, parent_metadata_path=parent_file_path)
            subtool_obj.mk_file()
    parent_metadata.mk_file(parent_file_path)
    return parent_file_path


def add_subtool(tool_name, tool_version, subtool_name, root_repo_path=Path.cwd(), update_featureList=False, init_cwl=True):
    """Add subtool to already existing ToolLibrary (ParentTool file already exists)"""
    parent_path = get_tool_metadata(tool_name, tool_version, parent=True, base_dir=root_repo_path)
    parent_meta = ParentToolMetadata.load_from_file(parent_path)
    if update_featureList:
        if parent_meta.featureList is None:
            parent_meta.featureList = [subtool_name]
        else:
            if not subtool_name in parent_meta.featureList:
                parent_meta.featureList.append(subtool_name)

    # new_subtool_dir = parent_path.parents[1] / f"{parent_meta.name}_{subtool_name}"
    # new_subtool_dir.mkdir()
    parent_meta.mk_file(parent_path)  # Might need to make update_file methods.
    subtool_meta = parent_meta.make_subtool_metadata(subtool_name, parent_path)
    # new_file_path = new_subtool_dir / f"{subtool_name}-metadata.yaml"
    subtool_meta.mk_file()
    return
