from pathlib import Path
from capanno_utils.classes.metadata.workflow_metadata import WorkflowMetadata
from capanno_utils.repo_config import workflows_dir_name


def _get_workflow_directory(group_name, workflow_name, workflow_version, root_repo_path):
    """
    Gets the workflow directory specified. Makes the directory if it doesn't exist.
    :param group_name:
    :param project_name:
    :param workflow_version:
    :return:
    """
    base_path = root_repo_path / workflows_dir_name / group_name / workflow_name / workflow_version
    if base_path.exists():
        if not base_path.is_dir():
            raise TypeError(f"{base_path} must be a directory")
    else:
        base_path.mkdir(parents=True)
    return base_path


def add_workflow(group_name, workflow_name, workflow_version, root_repo_path=None, **kwargs):
    if root_repo_path:
        root_repo_path = Path(root_repo_path)
    else:
        root_repo_path = Path.cwd()
    workflow_version = str(workflow_version)
    wf_path = _get_workflow_directory(group_name, workflow_name, workflow_version, root_repo_path)
    wf_metadata = WorkflowMetadata(name=workflow_name, softwareVersion={'versionName': workflow_version,
                                                                        'includedVersions': kwargs.pop(
                                                                            'includedVersions', None)}, **kwargs)
    filename = f"{workflow_name}-metadata.yaml"
    wf_metadata.mk_file(wf_path / filename)
    instances_dir = wf_path / 'instances'
    instances_dir.mkdir()
    return
