import os
from pathlib import Path
from xd_cwl_utils.config import config

# IDEA: Using Path class, it might be better to generate the get methods by getting longest path, then using Path.parents
# for parent directories. More maintainable if we change path structure. Maybe not.

# Misc

def get_inputs_schema_template():

    schema_template_path = Path.cwd() / 'tests/test_files/schema_salad/inputs_schema_template.yml'

    return schema_template_path

def get_base_dir(base_dir=None):
    if not base_dir:
        base_dir = config[os.environ['CONFIG_KEY']]['base_path']
    return Path(base_dir)

# cwl-tools

def get_root_tools_dir(base_dir=None):
    if not base_dir:
        base_dir = get_base_dir()
    else:
        base_dir = Path(base_dir)
    tool_dir = base_dir / 'cwl-tools'
    return tool_dir

def get_main_tool_dir(tool_name, base_dir=None):
    root_tools_dir = get_root_tools_dir(base_dir)
    main_tool_dir = root_tools_dir / tool_name
    return main_tool_dir

def get_tool_version_dir(tool_name, tool_version, base_dir=None):

    version_dir = get_main_tool_dir(tool_name, base_dir=base_dir) / tool_version
    return version_dir

def get_tool_dir(tool_name, tool_version, subtool_name=None, base_dir=None):
    tool_version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=base_dir)
    if subtool_name:
        tool_dir = tool_version_dir / f"{tool_name}_{subtool_name}"
    else:
        tool_dir = tool_version_dir / tool_name
    return tool_dir

def get_cwl_tool(tool_name, tool_version, subtool_name=None, base_dir=None):
    tool_dir = get_tool_dir(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)

    if subtool_name:
        cwl_tool_path = tool_dir / f"{tool_name}-{subtool_name}.cwl"
    else:
        cwl_tool_path = tool_dir / f"{tool_name}.cwl"
    return cwl_tool_path


def get_cwl_tool_metadata(tool_name, tool_version, subtool_name=None, parent=False, base_dir=None):
    version_dir = get_tool_version_dir(tool_name, tool_version, base_dir=base_dir)

    if parent:
        cwl_tool_metadata_path = version_dir / 'common' / f"{tool_name}-metadata.yaml"
    else:
        cwl_tool_metadata_path = get_metadata_path(get_cwl_tool(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir))
    return cwl_tool_metadata_path


def get_tool_inputs_dir(tool_name, tool_version, subtool_name=None, base_dir=None):
    cwl_tool_dir = get_tool_dir(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)
    instances_dir = cwl_tool_dir / 'instances'
    return instances_dir

def get_tool_instances_dir_from_cwl_path(cwl_path):
    cwl_path = Path(cwl_path)
    instances_dir = cwl_path.parent / 'instances'
    return instances_dir


def get_tool_instance_path(tool_name, tool_version, input_hash, subtool_name=None, base_dir=None):

    cwl_tool_inst_dir = get_tool_inputs_dir(tool_name, tool_version, subtool_name=subtool_name, base_dir=base_dir)
    inputs_path = cwl_tool_inst_dir / f"{input_hash}.yaml"

    return inputs_path

def get_tool_args_from_path(cwl_tool_path):
    cwl_tool_path = Path(cwl_tool_path)
    tool_type = get_tool_type_from_path(cwl_tool_path)
    path_parts = cwl_tool_path.parts

    tool_name = path_parts[-4]
    tool_version = path_parts[-3]
    subtool_name = path_parts[-2].split('_')[-1] if tool_type=='subtool' else None

    return tool_name, tool_version, subtool_name

def get_tool_type_from_path(tool_path):
    tool_path = Path(tool_path)
    if tool_path.suffix == '.yaml':
        if not tool_path.parent.parts[-1] == 'common':
            raise ValueError(f"Provided a .yaml file {tool_path} for file that is not in a 'common' directory")
        tool_type = "parent"
    elif tool_path.suffix == '.cwl':
        common_dir = tool_path.parents[1] / 'common'
        if common_dir.exists():
            tool_type = 'subtool'
        else:
            tool_type = 'tool'
    else:
        raise ValueError(f"Do not recognize {tool_path} as a path to a tool.")

    return tool_type


# cwl-scripts

def get_root_scripts_dir(base_dir=None):
    if not base_dir:
        base_dir = get_base_dir()
    else:
        base_dir = Path(base_dir)
    scripts_dir = base_dir / 'cwl-scripts'
    return scripts_dir

def get_script_version_dir(group_name, project_name, version, base_dir=None):
    script_ver_dir = get_root_scripts_dir(base_dir=base_dir) / group_name / project_name / version
    return script_ver_dir

def get_cwl_script(group_name, project_name, version, script_name, base_dir=None):
    script_ver_dir = get_script_version_dir(group_name, project_name, version, base_dir=base_dir)
    script_path = script_ver_dir / script_name / f"{script_name}.cwl"
    return script_path

def get_script_metadata(group_name, project_name, version, script_name, base_dir=None):
    script_ver_dir = get_script_version_dir(group_name, project_name, version, base_dir=base_dir)
    script_metadata_path = script_ver_dir / script_name / f"{script_name}-metadata.cwl"
    return script_metadata_path


def get_script_instance_dir(group_name, project_name, version, script_name, base_dir=None):
    script_version_dir = get_script_version_dir(group_name, project_name, version, base_dir=base_dir)
    instances_dir = script_version_dir / script_name / 'instances'
    return instances_dir

def get_script_args_from_path(cwl_script_path):
    cwl_script_path = Path(cwl_script_path)
    script_name = cwl_script_path.stem
    path_parts = cwl_script_path.parts
    assert script_name == path_parts[-2]
    script_version = path_parts[-3]
    project_name = path_parts[-4]
    group_name = path_parts[-5]
    return group_name, project_name, script_version, script_name


def get_script_instance_path(group_name, project_name, version, script_name, instance_hash, base_dir=None):
    script_instance_dir = get_script_instance_dir(group_name, project_name, version, script_name, base_dir=base_dir)
    instance_path = script_instance_dir / f"{instance_hash}.yaml"
    return instance_path

# cwl-workflows

def get_workflows_root_dir(base_dir=None):
    if not base_dir:
        base_dir = get_base_dir()
    else:
        base_dir = Path(base_dir)
    workflows_dir = base_dir / 'cwl-workflows'
    return workflows_dir

def get_workflow_version_dir(group_name, project_name, version, base_dir=None):
    workflow_ver_dir = get_workflows_root_dir(base_dir=base_dir) / group_name / project_name / version
    return workflow_ver_dir

def get_cwl_workflow(group_name, project_name, version, workflow_name, base_dir=None):
    workflow_ver_dir = get_workflow_version_dir(group_name, project_name, version, base_dir=base_dir)
    workflow_path = workflow_ver_dir / f"{workflow_name}.cwl"
    return workflow_path

def get_workflow_metadata(group_name, project_name, version, workflow_name, base_dir=None):
    workflow_ver_dir = get_workflow_version_dir(group_name, project_name, version, base_dir=base_dir)
    workflow_metadata_path = workflow_ver_dir / f"{workflow_name}-metadata.yaml"
    return workflow_metadata_path

def get_workflow_inputs_dir(group_name, project_name, version, base_dir=None):
    cwl_workflow_dir = get_workflow_version_dir(group_name, project_name, version, base_dir=base_dir)
    instances_dir = cwl_workflow_dir / 'instances'
    return instances_dir

def get_workflow_instance_dir_from_cwl_path(cwl_path):
    cwl_path = Path(cwl_path)
    instances_dir = cwl_path.parent / 'instances'
    return instances_dir

def get_workflow_instance_path(group_name, project_name, version, instance_hash, base_dir=None):
    workflow_instances_dir = get_workflow_inputs_dir(group_name, project_name, version, base_dir=base_dir)
    instance_path = workflow_instances_dir / f"{instance_hash}.yaml"
    return instance_path


def get_workflow_args_from_path(cwl_workflows_path):
    cwl_workflows_path = Path(cwl_workflows_path)
    path_parts = cwl_workflows_path.parts
    file_name = path_parts[-1]
    workflow_name = cwl_workflows_path.stem
    workflow_version = path_parts[-2]
    project_name = path_parts[-3]
    group_name = path_parts[-4]
    return group_name, project_name, workflow_version, workflow_name




# helpers

def get_relative_path(full_path, base_path=None):
    base_path = get_base_dir(base_dir=base_path)
    return full_path.relative_to(base_path)

def get_metadata_path(cwl_path):
    cwl_path = Path(cwl_path)
    path_dir = cwl_path.parent
    metafile_name = f"{cwl_path.stem}-metadata.yaml"
    metadata_path = path_dir / metafile_name
    return metadata_path
