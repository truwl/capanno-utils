
import sys
import shutil
from pathlib import Path
from ruamel.yaml import safe_load, dump
from tests.test_base import TestBase
from capanno_utils.content_maps import make_tools_index
from capanno_utils.helpers.get_paths import get_tool_version_dir, get_root_tools_dir, get_tool_common_dir, get_script_version_dir, get_root_scripts_dir


tool_args_list = [('cat', '8.x'), ('samtools', '1.x'), ('gawk', '4.1.x'), ('sort', '8.x'), ('STAR', '2.5'), ('STAR', '2.7.x'), ('md5sum', '8.x')]

script_args_list = [
    ('ENCODE-DCC', 'atac-seq-pipeline', '1.1.x'),
    ]

workflow_args = [
    ('example_workflows', 'cat_sort', 'master'),
    ]

src_content_dir = TestBase.src_content_dir
test_content_dir = TestBase.test_content_dir
invalid_content_dir = TestBase.invalid_content_dir


def teardown_tools():
    """Just delete whole tools directory. Removes anything that was manually copied too."""
    test_tools_dir = get_root_tools_dir(base_dir=test_content_dir)
    invalid_tools_dir = get_root_tools_dir(base_dir=invalid_content_dir)
    if test_tools_dir.exists():
        print(f"Removing {test_tools_dir}")
        shutil.rmtree(str(test_tools_dir))
    if invalid_tools_dir.exists():
        print(f"Removing {invalid_tools_dir}")
        shutil.rmtree(str(invalid_tools_dir))
    return

def copy_tools():
    for tool_args in tool_args_list:
        src_tool_dir = get_tool_version_dir(*tool_args, base_dir=src_content_dir)
        dest_tool_dir = get_tool_version_dir(*tool_args, base_dir=test_content_dir)
        shutil.copytree(src_tool_dir, dest_tool_dir)
    make_tools_index(base_dir=test_content_dir)
    return

def copy_to_invalid_tools():
    for tool_args in tool_args_list:
        src_tool_dir = get_tool_version_dir(*tool_args, base_dir=src_content_dir)
        invalid_tool_dir = get_tool_version_dir(*tool_args, base_dir=invalid_content_dir)
        shutil.copytree(src_tool_dir, invalid_tool_dir)
    make_tools_index(base_dir=invalid_content_dir)
    return


def update_invalid_tools():
    cat_common_dir = get_tool_common_dir(*tool_args_list[0], base_dir=invalid_content_dir)
    cat_common_metadata_path = cat_common_dir / 'common-metadata.yaml'
    with cat_common_metadata_path.open('r') as metadata_file:
        metadata_dict = safe_load(metadata_file)
    cat_common_metadata_path.unlink()  # Delete the original.
    metadata_dict['featurList'] = metadata_dict.pop('featureList')
    with cat_common_metadata_path.open('w') as metadata_file:
        dump(metadata_dict, metadata_file)


    samtools_common_dir = get_tool_common_dir(*tool_args_list[1], base_dir=invalid_content_dir)
    samtools_subtool = 'view'
    samtools_common_metadata_path = samtools_common_dir / 'common-metadata.yaml'
    with samtools_common_metadata_path.open('r') as metadata_file:
        samtools_meta_dict = safe_load(metadata_file)
    samtools_common_metadata_path.unlink()
    samtools_meta_dict['featureList'].remove(samtools_subtool)
    with samtools_common_metadata_path.open('w') as metadata_file:
        dump(samtools_meta_dict, metadata_file)
    return

def populate_invalid_tools():
    copy_to_invalid_tools()
    update_invalid_tools()
    return


def teardown_scripts():
    test_scripts_dir = get_root_scripts_dir(base_dir=test_content_dir)
    if test_scripts_dir.exists():
        shutil.rmtree(test_scripts_dir)
    return

def copy_scripts():
    for script_args in script_args_list:
        src_script_dir = get_script_version_dir(*script_args, base_dir=src_content_dir)
        dest_script_dir = get_script_version_dir(*script_args, base_dir=test_content_dir)
        shutil.copytree(src_script_dir, dest_script_dir)
    return

def populate_scripts():
    teardown_scripts()
    copy_scripts()

def make_content_maps():
    raise NotImplementedError



def main():
    teardown_tools()
    copy_tools()
    populate_invalid_tools()
    populate_scripts()

if  __name__ == "__main__":
    print(f"Updating {test_content_dir}")
    sys.exit(main())