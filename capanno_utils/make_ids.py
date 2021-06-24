
import argparse
import sys
from pathlib import Path
from capanno_utils.classes.metadata.workflow_metadata import WorkflowMetadata
import uuid

def get_parser():
    parser = argparse.ArgumentParser(description=f"Generate a tool, script or workflow identifier")
    parser.add_argument('type', type=str,
                        help='tool, script, workflow, workflowinstance')
    parser.add_argument('name', type=str,
                        help='Provide the name of the tool, script, or workflow')
    parser.add_argument('--identifier', type=str,
                        help='Provide the parent identifier of the workflow (for new instances)', required=False)
    parser.add_argument('version',type=str,
                        help='Provide the version of the tool, script, or workflow')
    parser.add_argument('-p', '--root-repo-path', dest='root_path', type=Path, default=Path.cwd(),
                        help="Specify the root path of your cwl content repo if it is not the current working directory.")
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', help="Silence messages to stdout")

    return parser


def main(argsl=None):
    if argsl is None:
        argsl = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(argsl)
    if args.type == 'workflow':
        kwargs = {"name": args.name, "softwareVersion": {"versionName": args.version, "includedVersions": args.version}, "cwlStatus": "Released"}
        wf = WorkflowMetadata(**kwargs)
        print(wf._mk_identifier())
    elif args.type == 'workflowinstance':
        if args.identifier:
            uuid_string = uuid.uuid4().hex[:4]
            print(f"{args.identifier}.{uuid_string}")
        else:
            kwargs = {"name": args.name, "softwareVersion": {"versionName": args.version, "includedVersions": args.version}, "cwlStatus": "Released"}
            wf = WorkflowMetadata(**kwargs)
            print(wf._make_workflow_inst_identifier())

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


