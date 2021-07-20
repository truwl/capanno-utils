#!/usr/bin/env python3

from datetime import date
from capanno_utils.classes.metadata.tool_metadata import ParentToolMetadata, SubtoolMetadata
from capanno_utils.initialize_wf_files import initialize_tool_wf_file_tool
from capanno_utils.classes.schema_salad.schema_salad import InputsSchema
from capanno_utils.content_maps import make_tools_index
from capanno_utils.helpers.get_paths import *
import logging, sys

logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def add_tool(tool_name, version_name, subtool_names=None, biotools_id=None, has_primary=False, root_repo_path=Path.cwd(), init_cwl=False, init_wdl=False, init_sm=False, init_nf=False, no_clobber=False, refresh_index=True):
    """
    Make the correct directory structure for adding a new command line tool. Optionally, create initialized wf language
    and metadata files. Run from tools directory.
    :param tool_name(str): Name of the tool
    :param version_name(str): version of the tool
    :param subtool_names(list(str)): list of subtool names if the tool is broken into multiple subtools.
    :return: None
    """
    version_name = str(version_name) # In case ArgumentParser is bypassed.
    if subtool_names:
        if isinstance(subtool_names, str):
            subtool_names = [subtool_names]
    if has_primary:  # Need to append __main__ onto subtools.
        if subtool_names:
            subtool_names.append(main_tool_subtool_name)
        else: # __main__ is only subtool specified.
            subtool_names = [main_tool_subtool_name]
            if isinstance(init_cwl, str):
                init_cwl = {main_tool_subtool_name: init_cwl}

    if refresh_index:
        make_tools_index(base_dir=root_repo_path)
    common_dir = get_tool_common_dir(tool_name, version_name, base_dir=root_repo_path)
    if no_clobber and common_dir.exists():
        logger.debug("Skipping tool directory setup")
        return
    common_dir.mkdir(parents=True, exist_ok=not no_clobber)
    if biotools_id:
        # tool_name will be ignored.
        parent_metadata = ParentToolMetadata.create_from_biotools(biotools_id, version_name, subtool_names, name=tool_name, root_repo_path=root_repo_path)
        # can't find it in biotools
        if parent_metadata is None:
            parent_metadata = ParentToolMetadata(name=tool_name,
                                                 softwareVersion={'versionName': version_name, 'includedVersions': []},
                                                 featureList=subtool_names, check_index=True, _in_index=False)
    else:
        parent_metadata = ParentToolMetadata(name=tool_name, softwareVersion={'versionName': version_name, 'includedVersions': []}, featureList=subtool_names, root_repo_path=root_repo_path, check_index=True, _in_index=False)
    if parent_metadata.featureList:
        for subtool in parent_metadata.featureList:
            subtool_obj = parent_metadata.make_subtool_metadata(subtool_name=subtool, root_repo_path=root_repo_path, check_index=True)
            subtool_obj.mk_file()
            subtool_dir = get_tool_dir(tool_name, version_name, subtool, base_dir=root_repo_path)
            instances_dir = subtool_dir / 'instances'
            instances_dir.mkdir()
            git_keep_file = instances_dir / '.gitkeep'
            git_keep_file.touch()
            if isinstance(init_cwl, dict):
                init_cwl_ = init_cwl.get(subtool, False)  # Not initialized if not specified.
            else:
                init_cwl_ = init_cwl
            initialize_tool_wf_file_tool(tool_name, version_name, subtool, init_cwl=init_cwl_, init_wdl=init_wdl, init_sm=init_sm, init_nf=init_nf, base_dir=root_repo_path)
    parent_metadata.mk_file(root_repo_path)
    return


def add_subtool(tool_name, tool_version, subtool_name, root_repo_path=Path.cwd(), update_featureList=False, init_cwl=False, init_wdl=False, init_sm=False, init_nf=False, no_clobber=False, refresh_index=True):
    """
    Add subtool to already existing ToolLibrary (ParentTool file already exists)
    :param tool_name(str):
    :param version_name (str):
    :param subtool_name (str):
    :param root_repo_path (Path): The local directory under which this subtool should be added
    :param update_featureList (Bool): If True, subtool does not need to be in ParentTool featureList and ParentTool will be updated. Will throw error if False and subtool is not in ParentTool featureList.
    :param init_cwl:
    :return:
    """
    if refresh_index:
        make_tools_index(base_dir=root_repo_path)
    subtool_kwargs = {'extra': {}}  # initialize to add any additional information about the subtool.
    parent_path = get_tool_metadata(tool_name, tool_version, parent=True, base_dir=root_repo_path)
    parent_meta = ParentToolMetadata.load_from_file(parent_path, root_repo_path=root_repo_path, _in_index=True)  # When adding a subtool, the ParentTool should already be present and in the index.

    subtool_dir = get_tool_dir(tool_name, tool_version, subtool_name, base_dir=root_repo_path)
    if no_clobber and subtool_dir.exists():
        return
    if update_featureList:
        if parent_meta.featureList is None:
            parent_meta.featureList = [subtool_name]
        else:
            if not subtool_name in parent_meta.featureList:
                parent_meta.featureList.append(subtool_name)
        parent_meta.mk_file(base_dir=root_repo_path, update_index=False)  # Remake the file. Needs to be remade if updated. Identifier will already be in index. No place to update the identifier in this function.
    if not isinstance(init_cwl, bool):  # initialized from a url.
        subtool_kwargs['extra'].update({'cwlDocument': {'isBasedOn': init_cwl, 'dateCreated': str(date.today())}})
    if not isinstance(init_wdl, bool):  # initialized from a url.
        subtool_kwargs['extra'].update({'wdlDocument': {'isBasedOn': init_wdl, 'dateCreated': str(date.today())}})
    if not isinstance(init_sm, bool):  # initialized from a url.
        subtool_kwargs['extra'].update({'snakemakeDocument': {'isBasedOn': init_sm, 'dateCreated': str(date.today())}})
    if not isinstance(init_nf, bool):  # initialized from a url.
        subtool_kwargs['extra'].update({'nextflowDocument': {'isBasedOn': init_nf, 'dateCreated': str(date.today())}})
    subtool_meta = parent_meta.make_subtool_metadata(subtool_name, root_repo_path=root_repo_path, check_index=True, **subtool_kwargs)
    subtool_meta.mk_file()
    instances_dir = subtool_dir / 'instances'
    instances_dir.mkdir()
    git_keep_file = instances_dir / '.gitkeep'
    git_keep_file.touch()
    initialize_tool_wf_file_tool(tool_name, tool_version, subtool_name, init_cwl=init_cwl, init_wdl=init_wdl, init_sm=init_sm, init_nf=init_nf, base_dir=root_repo_path)
    return


def add_tool_instance(tool_name, tool_version, subtool_name, init_job_file=True, root_repo_path=Path.cwd()):
    subtool_path = get_tool_metadata(tool_name, tool_version, subtool_name, base_dir=root_repo_path)
    subtool_metadata = SubtoolMetadata.load_from_file(subtool_path, root_repo_path=root_repo_path, _in_index=False)
    instance_meta = subtool_metadata.mk_instance()
    instance_metadata_path = instance_meta.mk_file(base_dir=root_repo_path)
    input_hash = instance_meta.identifier[-4:]
    job_file_path = None
    if init_job_file:
        tool_sources = get_tool_sources(tool_name, tool_version, subtool_name, base_dir=root_repo_path)
        job_file_path = get_tool_instance_path(tool_name, tool_version, input_hash=input_hash, subtool_name=subtool_name, base_dir=root_repo_path)
        tool_inputs_schema = InputsSchema(tool_sources['cwl'])
        tool_inputs_schema.make_template_file(job_file_path)
    return instance_metadata_path, job_file_path
