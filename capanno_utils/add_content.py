#!/usr/bin/env python3

# Module to call from command line.


import sys
import argparse
from pathlib import Path
from capanno_utils import repo_config
from capanno_utils.add.custom_actions import keyvalueparse
from capanno_utils.add.add_tools import add_tool, add_subtool, add_tool_instance
from capanno_utils.add.add_scripts import add_script, add_common_script_metadata
from capanno_utils.add.add_workflows import add_workflow
import logging

logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

def get_parser():
    parser = argparse.ArgumentParser(description='Initialize metadata and directories for a tool, script, or workflow.')
    parser.add_argument('-p','--root-repo-path', dest='root_path', type=Path, default=Path.cwd(), help="Specify the root path of your content repo if it is not the current working directory.")
    parser.add_argument('--no-refresh-index', dest='refresh_index', action='store_false', help="If specified, will use an already made index file that contains identifiers rather than assembling a new one.")
    subparsers = parser.add_subparsers(description='Specify the command to run.', dest='command')

    # add_tool parser
    addtool = subparsers.add_parser('tool', help='Add a new tool to the repository.')
    addtool.add_argument('tool_name', type=str, help="The name of the tool.")
    addtool.add_argument('version_name', type=str, help="The version name of the tool.")
    addtool.add_argument('subtool_names', nargs='*', type=str, help="The names of the subtools/subcommands for the tool. Directories and files will be initialized for the specified subtools.")
    addtool.add_argument('--biotoolsID', type=str, help='biotools id from https://bio.tools. Metadata fields will be populated with data from bio.tools if specified')
    addtool.add_argument('--has-primary', action='store_true', help='Specify if tool is callable without a subcommand.')
    addtool.add_argument('--init-cwl', nargs='*', action=keyvalueparse, help="If specified without arguments, CWL CommandLineTool files will be intiated from a template for the subtools and primary tool if it exists. url's to CWL files for individual subtools may also be provided in a series of arguments in the form subtoolName1=url1.")
    addtool.add_argument('--init-wdl', action='store_true', help="If specified, wdl task files will be intiated for the subtools and primary tool if it exists.")
    addtool.add_argument('--init-nf', action='store_true',
                         help="If specified, nextflow files will be intiated for the subtools and primary tool if it exists.")
    addtool.add_argument('--init-sm', action='store_true',
                         help="If specified, snakemake files will be intiated for the subtools and primary tool if it exists.")
    addtool.add_argument('--no-clobber', action='store_true', help="Do not overwrite the existing tool_name, version_name combination in the repository, if it already exists.", default=False)

    # add_subtool parser
    addsubtool = subparsers.add_parser('subtool', help='Add a subtool to a tool directory. An entry for the tool_name/tool_version must already exist.')
    addsubtool.add_argument('tool_name', help='The name of the tool.')
    addsubtool.add_argument('version_name', help='The version name of the tool.')
    addsubtool.add_argument('subtool_name', help="The name of the subtool to add. The subtool name must be present in the common-metadata featureList field. The featureList field can be updated automatically with the --update-featureList option.")
    addsubtool.add_argument('-u', '--update-featureList', action='store_true', help='Update the featureList of the Application Suite metadata to contain new subtool.')
    addsubtool.add_argument('--init-cwl', nargs='?', type=str, default=False, const=True,
                         help="If specified, CWL CommandLineTool files will be intiated. If a url is provided, the file will be intialized from the url.")
    addsubtool.add_argument('--init-wdl', nargs='?', type=str, default=False, const=True,
                            help="If specified, WDL task file will be intiated . If a url is provided, the file will be intialized from the url.")
    addsubtool.add_argument('--init-nf', nargs='?', type=str, default=False, const=True,
                            help="If specified, a nextflow file will be intiated . If a url is provided, the file will be intialized from the url.")
    addsubtool.add_argument('--init-sm', nargs='?', type=str, default=False, const=True,
                            help="If specified, a snakemake file will be intiated. If a url is provided, the file will be intialized from the url.")
    addsubtool.add_argument('--no-clobber', action='store_true', help="Do not overwrite the existing tool_name, version_name, subtool name combination in the repository, if it already exists.", default=False)

    # add_tool instance parser
    addtoolinstance = subparsers.add_parser('tool-instance', help='Add a tool instance.')
    addtoolinstance.add_argument('tool_name', type=str, help="The name of the tool.")
    addtoolinstance.add_argument('version_name', type=str, help="The version of the tool.")
    addtoolinstance.add_argument('subtool_name', type=str, nargs='?', default=repo_config.main_tool_subtool_name,
                                 help="The subtool name for the instance.")

    # add_common_script_parser
    addscriptcommon = subparsers.add_parser('common-script', help='add script metadata that other scripts can inherit from')
    addscriptcommon.add_argument('group_name', help='The name of the group directory that the script will go into.')
    addscriptcommon.add_argument('project_name', help='The name of the project directory that the script will go into.')
    addscriptcommon.add_argument('script_version', help='The version of the script.')
    addscriptcommon.add_argument('filename', help="The name of common metadata file. File extensions and '-metadata.yaml' postfix must be omitted.")

    # add_script parser
    addscript = subparsers.add_parser('script', help='add a new script to the repository.')
    addscript.add_argument('group_name', help='The name of the group directory that the script will go into.')
    addscript.add_argument('project_name', help='The name of the project directory that the script will go into.')
    addscript.add_argument('script_version', help='The version name of the script.')
    addscript.add_argument('script_name', help='The name of the script. File extensions should be omitted. Replace spaces with underscores')
    addscript.add_argument('--parent-metadata', '-p', nargs='+', help="path(s) to common script metadata that the script should inherit from.")
    addscript.add_argument('--init-cwl', action='store_true',
                         help="If specified, CWL CommandLineTool files will be intiated for the subtools and primary tool if it exists. ")
    # Could add flags for more kwargs here. Probably easiest to just add to file though.

    # add_script instance parser
    addscriptinstance = subparsers.add_parser('script-instance', help='Add a script instance.')
    addscriptinstance.add_argument('group_name', type=str, help="The name of the group directory for the script instance.")
    addscriptinstance.add_argument('project_name', type=str, help="The name of the project directory for the script instance.")
    addscriptinstance.add_argument('version_name', type=str, help="The version of the script.")
    addscriptinstance.add_argument('script_name',
                           help='The name of the script. File extensions should be omitted. Replace spaces with underscores')


    addworkflow = subparsers.add_parser('workflow', help='add a workflow')
    addworkflow.add_argument('group_name', help='The name of the group directory that the workflow will go into.')
    addworkflow.add_argument('workflow_name', help='The name of the workflow. Replace spaces with underscores.')
    addworkflow.add_argument('workflow_version', help='The version of the workflow.')

    return parser


def main(argsl=None):
    if not argsl:
        argsl = sys.argv[1:]
    parser = get_parser()
    args = parser.parse_args(argsl)
    logger.debug("command:{}".format(args.command))

    if args.command == 'tool':
        logger.debug("subtool names:{}".format(args.subtool_names))
        add_tool(args.tool_name, args.version_name, subtool_names=args.subtool_names, biotools_id=args.biotoolsID, has_primary=args.has_primary, init_cwl=args.init_cwl, init_wdl=args.init_wdl, init_sm=args.init_sm, init_nf=args.init_nf, root_repo_path=args.root_path, refresh_index=args.refresh_index, no_clobber=args.no_clobber)
    elif args.command == 'subtool':
        add_subtool(args.tool_name, args.version_name, args.subtool_name, update_featureList=args.update_featureList, init_cwl=args.init_cwl, init_wdl=args.init_wdl, init_sm=args.init_sm, init_nf=args.init_nf, root_repo_path=args.root_path, no_clobber=args.no_clobber)
    elif args.command == 'tool-instance':
        add_tool_instance(args.tool_name, args.version_name, args.subtool_name, root_repo_path=args.root_path)
    elif args.command == 'common-script':
        add_common_script_metadata(args.group_name, args.project_name, args.script_version, args.filename, root_repo_path=args.root_path)
    elif args.command == 'script':
        add_script(args.group_name, args.project_name, args.script_version, args.script_name, parentMetadata=args.parent_metadata, init_cwl=args.init_cwl, root_repo_path=args.root_path)
    elif args.command == 'script-instance':
        raise NotImplementedError
    elif args.command == 'workflow':
        add_workflow(args.group_name, args.workflow_name, args.workflow_version)
    else:
        parser.print_help()
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))