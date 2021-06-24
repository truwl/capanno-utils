#!/usr/bin/env python3

import argparse
import sys
import logging
from pathlib import Path
from capanno_utils.validate import *
from capanno_utils.validate_inputs import validate_inputs_for_instance
from capanno_utils.helpers.validate_cwl import validate_cwl_doc
from capanno_utils.helpers.validate_wdl import validate_wdl_doc
from capanno_utils.helpers.get_paths import get_types_from_path


def get_parser():
    parser = argparse.ArgumentParser(description="Validate metadata and workflow language files.")
    parser.add_argument('path', type=Path,
                        help='Provide the path to validate. If a directory is specified, all content in the directory will be validated. If a file is specified, only that file will be validated.')
    parser.add_argument('-p', '--root-repo-path', dest='root_path', type=Path, default=Path.cwd(),
                        help="Specify the root path of your content repo if it is not the current working directory.")
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help="Silence messages to stdout")

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

    base_type, specific_type = get_types_from_path(full_path, root_repo_name=args.root_path.name,
                                                   base_path=args.root_path)

    if not args.quiet:
        print(f"Validating {str(full_path)} \n")

    if base_type == 'tool':
        # Check for file types.
        if specific_type == 'common_metadata':
            validate_parent_tool_metadata(full_path)
        elif specific_type == 'cwl':  # Todo add validation for other files.
            validate_cwl_doc(full_path)
        elif specific_type == 'wdl':
            validate_wdl_doc(full_path)
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
            tool_name, version_name = full_path.parts[-2:]
            validate_tool_version_dir(tool_name, version_name, base_dir=args.root_path)
        elif specific_type == 'common_dir':
            tool_name, version_name = full_path.parts[-3:-1]
            validate_tool_common_dir(tool_name, version_name, base_dir=args.root_path)
        elif specific_type == 'subtool_dir':
            path_parts = full_path.parts
            tool_name, version_name = path_parts[-3:-1]
            subtool_name = path_parts[-1][len(tool_name) + 1:]
            if subtool_name == '':
                subtool_name = None
            validate_subtool_dir(tool_name, version_name, subtool_name, base_dir=args.root_path)
        elif specific_type == 'instance_dir':  # Must do the same as validating a subtool directory. Could skip validating subtool metadata, but won't. Don't see use for that.
            path_parts = full_path.parts
            tool_name, version_name = path_parts[-4:-2]
            subtool_name = path_parts[-2][len(tool_name) + 1:]
            if subtool_name == '':
                subtool_name = None
            validate_subtool_dir(tool_name, version_name, subtool_name=subtool_name, base_dir=args.root_path)
        else:
            raise ValueError(f"Cannot validate tool path {full_path}")
    elif base_type == 'script':
        if specific_type == 'cwl':  # Todo. Add support for other wf types.
            validate_cwl_doc(full_path)
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
            group_name = full_path.parts[-1]
            validate_group_scripts_dir(group_name, base_dir=args.root_path)
        elif specific_type == 'project_dir':
            group_name, project_name = full_path.parts[-2:]
            validate_project_scripts_dir(group_name, project_name, base_dir=args.root_path)
        elif specific_type == 'version_dir':
            group_name, project_name, version_name = full_path.parts[-3:]
            validate_version_script_dir(group_name, project_name, version_name, base_dir=args.root_path)
        elif specific_type == 'script_dir':
            group_name, project_name, version_name, script_name = full_path.parts[-4:]
            validate_script_dir(group_name, project_name, version_name, script_name, base_dir=args.root_path)
        elif specific_type == 'instance_dir':
            group_name, project_name, version_name, script_name = full_path.parts[-5:-1]
            validate_script_dir(group_name, project_name, version_name, script_name, base_dir=args.root_path)
        else:
            raise ValueError(f"Cannot validate script path {full_path}")

    elif base_type == 'workflow':
        if specific_type == 'base_dir':
            validate_workflows_dir(base_dir=args.root_path)
        elif specific_type == 'group_dir':
            group_name = full_path.parts[-1]
            validate_workflow_group_dir(group_name, base_dir=args.root_path)
        elif specific_type == 'project_dir':
            group_name, project_name = full_path.parts[-2:]
            validate_workflow_project_dir(group_name, project_name, base_dir=args.root_path)
        elif specific_type == 'version_dir':
            group_name, project_name, version_name = full_path.parts[-3:]
            validate_workflow_version_dir(group_name, project_name, version_name, base_dir=args.root_path)
        elif specific_type == 'cwl':  # Todo. Add other wf language types.
            raise NotImplementedError
        elif specific_type == 'metadata':
            validate_workflow_metadata(full_path)
        elif specific_type == 'instance':
            raise NotImplementedError
        elif specific_type == 'instance_metadata':
            raise NotImplementedError
        else:
            raise ValueError(f"Cannot validate workflow path {full_path}")
    elif base_type == 'repo_root':
        validate_repo(full_path)

    else:
        parser.print_help()

    if not args.quiet:
        print(f"{full_path} is valid.")
    return


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
