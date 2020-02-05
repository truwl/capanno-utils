#!/usr/bin/env python3

from pathlib import Path
from xd_cwl_utils.classes.metadata.tool_metadata import ParentToolMetadata
from xd_cwl_utils.helpers.get_paths import get_tool_common_dir, main_tool_subtool_name, get_tool_metadata, get_tool_dir


def add_tool(tool_name, version_name, subtool_names=None, biotools_id=None, has_primary=False, root_repo_path=Path.cwd(), init_cwl=True):
    """
    Make the correct directory structure for adding a new command line tool. Optionally, create initialized CWL
    and metadata files. Run from cwl-tools directory.
    :param tool_name(str): Name of the tool
    :param version_name(str): version of the tool
    :param subtool_names(list(str)): list of subtool names if the tool is broken into multiple subtools.
    :param mk_meta_files(bool): Specify whether to make initial CWL and metadata files.
    :return: None
    """
    version_name = str(version_name) # In case ArgumentParser is bypassed.
    if subtool_names:
        if isinstance(subtool_names, str):
            subtool_names = [subtool_names]
    common_dir = get_tool_common_dir(tool_name, version_name, base_dir=root_repo_path)
    common_dir.mkdir(parents=True, exist_ok=False)
    if has_primary:  # Need to append __main__ onto subtools.
        if subtool_names:
            subtool_names.append(main_tool_subtool_name)
        else:
            subtool_names = [main_tool_subtool_name]
    if biotools_id:
        # tool_name will be ignored.
        parent_metadata = ParentToolMetadata.create_from_biotools(biotools_id, version_name, subtool_names, tool_name=tool_name)
    else:
        parent_metadata = ParentToolMetadata(name=tool_name, softwareVersion={'versionName': version_name, 'includedVersions': []}, featureList=subtool_names)
    if parent_metadata.featureList:
        for subtool in parent_metadata.featureList:
            subtool_obj = parent_metadata.make_subtool_metadata(subtool_name=subtool)
            subtool_obj.mk_file(base_dir=root_repo_path)
            subtool_dir = get_tool_dir(tool_name, version_name, subtool, base_dir=root_repo_path)
            instances_dir = subtool_dir / 'instances'
            instances_dir.mkdir()
            git_keep_file = instances_dir / '.gitkeep'
            git_keep_file.touch()
    parent_metadata.mk_file(root_repo_path)
    return


def add_subtool(tool_name, tool_version, subtool_name, root_repo_path=Path.cwd(), update_featureList=False, init_cwl=True):
    """
    Add subtool to already existing ToolLibrary (ParentTool file already exists)
    :param tool_name(str):
    :param version_name (str):
    :param subtool_name (str):
    :param root_repo_path (Path):
    :param update_featureList (Bool): If True, subtool does not need to be in ParentTool featureList and ParentTool will be updated. Will throw error if False and subtool is not in ParentTool featureList.
    :param init_cwl:
    :return:
    """
    parent_path = get_tool_metadata(tool_name, tool_version, parent=True, base_dir=root_repo_path)
    parent_meta = ParentToolMetadata.load_from_file(parent_path)
    if update_featureList:
        if parent_meta.featureList is None:
            parent_meta.featureList = [subtool_name]
        else:
            if not subtool_name in parent_meta.featureList:
                parent_meta.featureList.append(subtool_name)
        parent_meta.mk_file(base_dir=root_repo_path)  # Remake the file. Needs to be remade if updated.

    subtool_meta = parent_meta.make_subtool_metadata(subtool_name)
    subtool_meta.mk_file(base_dir=root_repo_path)
    subtool_dir = get_tool_dir(tool_name, tool_version, subtool_name, base_dir=root_repo_path)
    instances_dir = subtool_dir / 'instances'
    instances_dir.mkdir()
    git_keep_file = instances_dir / '.gitkeep'
    git_keep_file.touch()
    return
