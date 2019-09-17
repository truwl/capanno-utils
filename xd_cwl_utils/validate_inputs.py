
from pathlib import Path
from xd_cwl_utils.helpers.get_paths import get_cwl_tool, get_tool_instance_path, get_tool_dir, get_tool_instances_dir_from_cwl_path
from xd_cwl_utils.classes.schema_salad.schema_salad import InputsSchema

def validate_inputs_for_instance(instance_path, inputs_schema=None, cwl_tool_path=None):
    if not inputs_schema:
        inputs_schema = InputsSchema(cwl_tool_path)
    inputs_schema.validate_inputs(instance_path)  # Will raise error if not valid.
    return

def validate_all_inputs_for_tool(cwl_tool_document_path):
    cwl_tool_document_path = Path(cwl_tool_document_path)
    inputs_schema = InputsSchema(cwl_tool_document_path)
    instances_path = get_tool_instances_dir_from_cwl_path(cwl_tool_document_path)
    for instance_file in instances_path.iterdir():
        if 'metadata' in instance_file.name:
            continue
        validate_inputs_for_instance(instance_file, inputs_schema=inputs_schema)
    return

