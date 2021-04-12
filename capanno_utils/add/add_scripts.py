
from pathlib import Path
from capanno_utils.repo_config import scripts_dir_name
from capanno_utils.classes.metadata.script_metadata import ScriptMetadata, CommonScriptMetadata
from capanno_utils.initialize_wf_files import initialize_command_line_tool_file_script

def _get_script_directory(group_name, project_name, script_version, root_repo_path):
    """
    Gets the script directory specified. Makes the directory if it doesn't exist.
    :param group_name:
    :param project_name:
    :param script_version:
    :return:
    """
    base_path = Path(root_repo_path) / scripts_dir_name / group_name / project_name / script_version
    if base_path.exists():
        if not base_path.is_dir():
            raise TypeError(f"{base_path} must be a directory")
    else:
        base_path.mkdir(parents=True)
    return base_path


def add_common_script_metadata(group_name, project_name, script_version, filename, root_repo_path=Path.cwd(), **kwargs):
    path = _get_script_directory(group_name, project_name, script_version, root_repo_path=root_repo_path) / 'common'
    path.mkdir(exist_ok=True)
    filename = f"{filename}-metadata.yaml"
    file_path = path / filename
    script_metadata = CommonScriptMetadata(**kwargs)
    script_metadata.mk_file(file_path)
    return


def add_script(group_name, project_name, script_version, script_name, root_repo_path=Path.cwd(), init_cwl=False, **kwargs):
    script_version = str(script_version)
    script_dir = _get_script_directory(group_name, project_name, script_version, root_repo_path) / script_name
    script_dir.mkdir()
    script_metadata = ScriptMetadata(name=script_name, softwareVersion={'versionName': script_version}, **kwargs)
    filename = f"{script_name}-metadata.yaml"
    script_metadata.mk_file(script_dir / filename)
    instances_dir = script_dir / 'instances'
    instances_dir.mkdir()
    git_keep_file = instances_dir / '.gitkeep'
    git_keep_file.touch()
    if init_cwl:
        initialize_command_line_tool_file_script(group_name, project_name, script_version, script_name, base_dir=root_repo_path)
    return

def add_script_instance(group_name, project_name, script_version, script_name, init_job_file=True, base_dir=Path.cwd()):
    raise NotImplementedError(f"Need to make script instance metadata classes first")


