import argparse
import sys
from pathlib import Path
from capanno_utils.status import update_all_tools_to_released
from capanno_utils.content_maps import *


def get_parser():
    parser = argparse.ArgumentParser(description=f"Change the release status of content in {content_repo_name}")
    parser.add_argument('-p', '--root-repo-path', dest='root_path', type=Path, default=Path.cwd(),
                        help="Specify the root path of your content repo if it is not the current working directory.")
    # parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help="Silence messages to stdout")
    subparsers = parser.add_subparsers(description='', dest='source_type')

    release_tools = subparsers.add_parser('tools', help='Change the release status of tools')
    release_tools.add_argument('--release-all', action='store_true', help='Change the status of all unreleased tool to Released.')
    release_tools.add_argument('--release', action='store_true', help='NotImplemented')


    return parser


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(argsl)

    if args.source_type == 'tools':
        if args.release_all:
            update_all_tools_to_released(base_dir=args.root_path)
        elif args.release:
            raise NotImplementedError
    else:
        raise NotImplementedError

    return

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
