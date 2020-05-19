

# from cwlgen import CommandLineTool, CommandInputParameter, CommandOutputParameter, CommandOutputBinding
from ruamel.yaml import YAML, tokens, error
from ruamel.yaml.comments import CommentedMap
from xd_cwl_utils.helpers.get_paths import get_cwl_tool, get_cwl_script, main_tool_subtool_name

blank_line_tk = tokens.CommentToken('\n\n', error.CommentMark(0), None)

# def initialize_commmand_line_tool_file_cwl_gen(tool_name, version_name, subtool_name, base_dir):
#     cwl_tool_path = get_cwl_tool(tool_name, version_name, subtool_name=subtool_name, base_dir=base_dir)
#     base_command = f"{tool_name} {subtool_name}" if subtool_name != main_tool_subtool_name else tool_name
#     clt_obj = CommandLineTool(base_command=base_command, cwl_version="v1.0")
#     clt_obj.inputs.append(CommandInputParameter('input1', param_type='string'))
#     clt_obj.outputs.append(CommandOutputParameter('output1', param_type='File', doc="Add documentation here", output_binding=CommandOutputBinding()))
#     clt_obj.export(str(cwl_tool_path))



def _initialize_command_line_tool_file_yaml(base_command, cwl_path):
    cwl_map = CommentedMap()
    doc_placholder = 'Document here.'
    input_name = 'input1'
    output_name = 'output1'
    cwl_map['cwlVersion'] = 'v1.0'
    cwl_map['class'] = 'CommandLineTool'
    cwl_map['baseCommand'] = base_command
    cwl_map['stdout'] = None
    cwl_map['inputs'] = CommentedMap([(input_name, {'type': None, 'inputBinding': {'position': 1, 'prefix': None}, 'doc': doc_placholder})])
    cwl_map['outputs'] = CommentedMap([(output_name, {'type': None, 'outputBinding': {'glob': None}, 'doc': doc_placholder})])
    # insert some blank lines.
    cwl_map.ca.items['stdout'] = [None, None, blank_line_tk, None]
    cwl_map.ca.items['outputs'] = [None, [blank_line_tk], None, None]

    yaml = YAML(pure=True)
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)
    with cwl_path.open('w') as cwl_file:
        yaml.dump(cwl_map, cwl_file)
    return

def initialize_command_line_tool_file_tool(tool_name, version_name, subtool_name, base_dir):
    cwl_tool_path = get_cwl_tool(tool_name, version_name, subtool_name=subtool_name, base_dir=base_dir)
    base_command = f"{tool_name} {subtool_name}" if subtool_name != main_tool_subtool_name else tool_name
    _initialize_command_line_tool_file_yaml(base_command, cwl_tool_path)
    return

def initialize_command_line_tool_file_script(group_name, project_name, script_version, script_name, base_dir):
    cwl_script_path = get_cwl_script(group_name, project_name, script_version, script_name, base_dir)
    base_command = script_name
    _initialize_command_line_tool_file_yaml(base_command, cwl_script_path)
    return