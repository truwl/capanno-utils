#!/usr/bin/env python3

import argparse
import sys
import logging
from pathlib import Path
from xd_cwl_utils.validate import validate_parent_tool_metadata, validate_subtool_metadata, validate_script_metadata, \
    validate_common_script_metadata, validate_workflow_metadata, validate_tools_dir, validate_scripts_dir, validate_workflows_dir, validate_repo
from xd_cwl_utils.validate_inputs import validate_inputs_for_instance
from xd_cwl_utils.helpers.validate_cwl import validate_cwl_tool
from xd_cwl_utils.helpers.get_paths import get_types_from_path


def get_parser():
    parser = argparse.ArgumentParser(description="Validate metadata and cwl files.")
    parser.add_argument('path', type=Path, help='Provide the path to validate. If a directory is specified, all content in the directory will be validated. If a file is specified, only that file will be validated.')
    parser.add_argument('-p', '--root_repo_path', dest='root_path', type=Path, default=Path.cwd(),
                        help="Specify the root path of your cwl content repo if it is not the current working directory.")

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

    base_type, specific_type = get_types_from_path(full_path, base_path=args.root_path)

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
            raise NotImplementedError
        elif specific_type == 'version_dir':
            raise NotImplementedError
        elif specific_type == 'common_dir':
            raise NotImplementedError
        elif specific_type == 'subtool_dir':
            raise NotImplementedError
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
    return


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
