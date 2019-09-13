
from .helpers.get_paths import get_cwl_tool, get_tool_instance_path, get_tool_dir
from .classes.schema_salad.schema_salad import InputsSchema

def validate_inputs_for_instance(tool_name, tool_version, instance_hash, subtool_name=None):
    cwl_path = get_cwl_tool(tool_name, tool_version, subtool_name=subtool_name)
    inputs_schema = InputsSchema(cwl_path)
    document_path = get_tool_instance_path(tool_name, tool_version, instance_hash, subtool_name=subtool_name)
    inputs_schema.validate_inputs(document_path)  # Will raise error if not valid.
    return


def validate_all_inputs_for_tool_version(tool_name, tool_version, subtool_name=None):
    version_dir = get_tool_dir(tool_name, tool_version, subtool_name=subtool_name)

    raise NotImplementedError

def validate_all_instance_inputs():
    raise NotImplementedError