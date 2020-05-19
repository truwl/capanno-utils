#!/usr/bin/env python3

import argparse
import sys
import logging
from pathlib import Path
from xd_cwl_utils.validate import validate_parent_tool_metadata, validate_subtool_metadata, validate_script_metadata, \
    validate_common_script_metadata, validate_workflow_metadata, validate_tools_dir, validate_scripts_dir, validate_workflows_dir, validate_repo


def get_parser():
    parser = argparse.ArgumentParser(description="Validate metadata files.")
    subparsers = parser.add_subparsers(description="Specify type of metadata to validate.", dest='command')
    parser.add_argument('-p', '--root_repo_path', dest='root_path', type=Path, default=Path.cwd(),
                        help="Specify the root path of your cwl content repo if it is not the current working directory.")

    validate_parent_tool = subparsers.add_parser('parent_tool', help="Validate parent tool metadata.")
    validate_parent_tool.add_argument('path', type=Path, help="Path to parent tool metadata file.")

    validate_subtool = subparsers.add_parser('subtool', help="Validate subtool metadata.")
    validate_subtool.add_argument('path', type=Path, help="Path to subtool metadata file.")

    validate_script = subparsers.add_parser('script', help="Validate script metadata")
    validate_script.add_argument('path', type=Path, help="Path to script metadata file.")

    validate_script_common = subparsers.add_parser('script_common', help="Validate common script metadata.")
    validate_script_common.add_argument('path', type=Path, help="Validate common script metadata")

    validate_workflow = subparsers.add_parser('workflow', help="Validate workflow metadata.")
    validate_workflow.add_argument('path', type=Path, help="Path to workflow metadata")

    validate_tool_dir = subparsers.add_parser('tool_dir', help='Validate an entire cwl-tools directory.')

    validate_script_dir = subparsers.add_parser('script_dir', help='Validate and entire cwl-scripts directory')

    validate_workflow_dir = subparsers.add_parser('workflow_dir', help="validate and entire cwl-workflows directory")

    validate_repo = subparsers.add_parser('repo', help='Validate entire cwl source repo.')

    return parser


def main(argsl=None):
    if not argsl:
        argsl = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(argsl)
    command = args.command
    try:
        if args.path.is_absolute():
            full_path = args.path
        else:
            full_path = args.root_path / args.path
    except AttributeError as e:
        if not command in ('tool_dir', 'script_dir', 'workflow_dir', 'repo'):
            raise
    if command == 'parent_tool':
        validate_parent_tool_metadata(full_path)
    elif command == 'subtool':
        validate_subtool_metadata(args.path)
    elif command == 'script':
        try:
            validate_script_metadata(args.path)
        except:
            logging.error(f"Problem with {args.path}")
            raise
    elif command == 'script_common':
        validate_common_script_metadata(args.path)
    elif command == 'workflow':
        validate_workflow_metadata(args.path)

    elif command == 'tool_dir':
        validate_tools_dir(base_dir=args.root_path)
    elif command == 'script_dir':
        validate_scripts_dir(base_dir=args.root_path)
    elif command == 'workflow_dir':
        validate_workflows_dir(base_dir=args.root_path)
    elif command == 'repo':
        validate_repo(base_dir=args.root_path)
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
