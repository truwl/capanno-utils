import argparse
import sys
from pathlib import Path
from capanno_utils.repo_config import content_repo_name
from capanno_utils.helpers.get_paths import get_dir_type_from_path
from capanno_utils.helpers.file_management import dump_dict_to_yaml_output
from capanno_utils.content_maps import *


def get_parser():
    parser = argparse.ArgumentParser(description=f"Make map of content in {content_repo_name}")
    parser.add_argument('path', type=Path,
                        help='Provide the directory path to make a map of.')
    parser.add_argument('output_path', type=Path, nargs='?', default=None,
                        help='Provide a file to output the map to.')
    parser.add_argument('-p', '--root-repo-path', dest='root_path', type=Path, default=Path.cwd(),
                        help="Specify the root path of your content repo if it is not the current working directory.")
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help="Silence messages to stdout")
    parser.add_argument('--include-exists', dest='exists', action='store_true',
                        help="Include whether workflow files exist for tools in the output. Currently for tools only.")

    return parser


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(argsl)
    base_dir = args.root_path.resolve()
    exists = args.exists
    if args.path.is_absolute():
        full_path = args.path
    else:
        full_path = base_dir / args.path

    if not full_path.is_dir():
        raise ValueError(f"{full_path} is not a directory")

    base_type, dir_type = get_dir_type_from_path(full_path, content_root_repo_name=base_dir.name)

    if base_type == 'base_dir':  # Content source root provided.
        # import pdb; pdb.set_trace()
        output_map = make_master_map_dict(base_dir=base_dir, specify_exists=exists)
    elif base_type == 'tool':
        if dir_type == 'base_dir':  # Base tools dir.
            output_map = make_tools_map_dict(base_dir=base_dir, specify_exists=exists)
        elif dir_type == 'tool_dir':
            output_map = make_main_tool_map(tool_name=full_path.name, base_dir=base_dir)
        elif dir_type == 'version_dir':
            print('version_dir')
            output_map = make_tool_version_dir_map(tool_name=full_path.parts[-2], tool_version=full_path.name,
                                                   base_dir=base_dir)
        elif dir_type == 'common_dir':
            output_map = make_tool_common_dir_map(tool_name=full_path.parts[-3], tool_version=full_path.parts[-2],
                                                  base_dir=base_dir)
        elif dir_type == 'subtool_dir':
            subtool_name = full_path.name.split('_')[-1]
            output_map = make_subtool_map(tool_name=full_path.parts[-3], tool_version=full_path.parts[-2],
                                          subtool_name=subtool_name, base_dir=base_dir)
        else:
            raise ValueError
    elif base_type == 'script':
        if dir_type == 'base_dir':
            output_map = make_scripts_map_dict(base_dir=base_dir)
        elif dir_type == 'group_dir':
            output_map = make_group_script_map(group_name=full_path.name, base_dir=base_dir)
        elif dir_type == 'project_dir':
            output_map = make_project_script_map(group_name=full_path.parts[-2], project_name=full_path.name,
                                                 base_dir=base_dir)
        elif dir_type == 'version_dir':
            output_map = make_script_version_map(group_name=full_path.parts[-3], project_name=full_path.parts[-2],
                                                 version_name=full_path.name, base_dir=base_dir)
        # elif dir_type == 'common_dir':  # Doesn't specify whole object item
        elif dir_type == 'scripts_dir':
            output_map = make_script_map(group_name=full_path.parts[-4], project_name=full_path.parts[-3],
                                         version_name=full_path.parts[-2], script_name=full_path.name,
                                         base_dir=base_dir)
        else:
            raise ValueError
    elif base_type == 'workflow':
        raise NotImplementedError
    else:
        raise ValueError
    return dump_dict_to_yaml_output(output_map, args.output_path)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
