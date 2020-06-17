#!/usr/bin/env python3

import argparse
import sys
import logging
from pathlib import Path
from xd_cwl_utils.validate import validate_parent_tool_metadata, validate_subtool_metadata, validate_script_metadata, \
    validate_common_script_metadata, validate_workflow_metadata, validate_tools_dir, validate_main_tool_directory, validate_tool_version_dir, validate_tool_comomon_dir, validate_subtool_dir, validate_scripts_dir, validate_workflows_dir, validate_repo
from xd_cwl_utils.validate_inputs import validate_inputs_for_instance
from xd_cwl_utils.helpers.validate_cwl import validate_cwl_tool
from xd_cwl_utils.helpers.get_paths import get_types_from_path


def get_parser():
    parser = argparse.ArgumentParser(description="Validate metadata and cwl files.")
    parser.add_argument('path', type=Path, help='Provide the path to validate. If a directory is specified, all content in the directory will be validated. If a file is specified, only that file will be validated.')
    parser.add_argument('-p', '--root_repo_path', dest='root_path', type=Path, default=Path.cwd(),
                        help="Specify the root path of your cwl content repo if it is not the current working directory.")
    # parser.add_argument('--root-repo-name', dest='repo_name', type=str, default='cwl-source', help="Provide the name of your repo if it is something other than 'cwl-source'. This is used to make sure paths are properly formatted")

    return parser


def main(argsl=None):
    if not argsl:
        argsl = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(argsl)

    # from pdb import set_trace; set_trace()
    if args.path.is_absolute():
        full_path = args.path
    else:
        full_path = args.root_path / args.path

    base_type, specific_type = get_types_from_path(full_path, cwl_root_repo_name=args.root_path.name, base_path=args.root_path)

    if base_type == 'tool':
        # Check for file types.
        if specific_type == 'common_metadata':
            validate_parent_tool_metadata(full_path)
        elif specific_type == 'cwl':
            validate_cwl_tool(full_path)
        elif specific_type == 'metadata':
            validate_subtool_metadata(full_path)
        elif specific_type == 'instance':
            validate_inputs_for_instance(full_path)
        elif specific_type == 'instance_metadata':
            raise NotImplementedError
        # Check for directory types.
        elif specific_type == 'base_dir':
            validate_tools_dir(base_dir=args.root_path)
        elif specific_type == 'tool_dir':
            tool_name = full_path.parts[-1]
            validate_main_tool_directory(tool_name, base_dir=args.root_path)
        elif specific_type == 'version_dir':
            tool_name = full_path.parts[-2]
            version_name = full_path.parts[-1]
            # print("Validating tool version directory.")
            validate_tool_version_dir(tool_name, version_name, base_dir=args.root_path)
        elif specific_type == 'common_dir':
            tool_name = full_path.parts[-3]
            tool_version = full_path.parts[-2]
            validate_tool_comomon_dir(tool_name, tool_version, base_dir=args.root_path)
        elif specific_type == 'subtool_dir':
            path_parts = full_path.parts
            tool_name = path_parts[-3]
            version_name = path_parts[-2]
            subtool_name = path_parts[-1][len(tool_name)+1:]
            if subtool_name == '':
                subtool_name = None
            validate_subtool_dir(tool_name, version_name, subtool_name, base_dir=args.root_path)
        elif specific_type == 'instance_dir':
            raise NotImplementedError
        else:
            raise ValueError(f"")
    elif base_type == 'script':
        if specific_type == 'cwl':
            validate_cwl_tool(full_path)
        elif specific_type == 'metadata':
            validate_script_metadata(full_path)
        elif specific_type == 'instance':
            validate_inputs_for_instance(full_path)
        elif specific_type == 'instance_metadata':
            raise NotImplementedError
        # Check for directory types.
        elif specific_type == 'base_dir':
            validate_scripts_dir(base_dir=args.root_path)
        elif specific_type == 'group_dir':
            raise NotImplementedError
        elif specific_type == 'project_dir':
            raise NotImplementedError
        elif specific_type == 'version_dir':
            raise NotImplementedError
        elif specific_type == 'script_dir':
            raise NotImplementedError
        elif specific_type == 'instance_dir':
            raise NotImplementedError
        else:
            raise ValueError(f"")

    elif base_type == 'workflow':
        if specific_type == 'cwl':
            raise NotImplementedError
        elif specific_type == 'metadata':
            validate_workflow_metadata(full_path)
        elif specific_type == 'instance':
            raise NotImplementedError
        elif specific_type == 'instance_metadata':
            raise NotImplementedError
        else:
            raise ValueError(f"")
    elif base_type == 'repo_root':
        validate_repo(full_path)

    else:
        parser.print_help()

    # print(f"{full_path} is valid.")
    return


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
