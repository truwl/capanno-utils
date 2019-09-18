import re
import logging
from pathlib import Path
from schema_salad.validate import ValidationException
from xd_cwl_utils.helpers.get_paths import get_cwl_tool, get_tool_instance_path, get_tool_dir, get_tool_instances_dir_from_cwl_path
from xd_cwl_utils.classes.schema_salad.schema_salad import InputsSchema

def validate_inputs_for_instance(instance_path, inputs_schema=None, cwl_tool_path=None):
    if not inputs_schema:
        inputs_schema = InputsSchema(cwl_tool_path)
    inputs_schema.validate_inputs(instance_path)  # Will raise error if not valid.
    return

def validate_all_inputs_for_tool(cwl_tool_document_path):
    instance_file_pattern = re.compile(r'[0-9a-f]{4}\.ya?ml')

    cwl_tool_document_path = Path(cwl_tool_document_path)
    inputs_schema = InputsSchema(cwl_tool_document_path)
    instances_path = get_tool_instances_dir_from_cwl_path(cwl_tool_document_path)
    for instance_file in instances_path.iterdir():
        if  instance_file_pattern.match(instance_file.name):
            try:
                validate_inputs_for_instance(instance_file, inputs_schema=inputs_schema)
            except ValidationException:
                print(f"{instance_file} failed validation")
                raise
    return

