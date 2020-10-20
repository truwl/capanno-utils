

from urllib import request
import requests
from ruamel.yaml import YAML, tokens, error
from ruamel.yaml.comments import CommentedMap
from capanno_utils.helpers.get_paths import get_cwl_tool, get_cwl_script, main_tool_subtool_name
from capanno_utils.classes.cwl.common_workflow_language import load_document
import logging, sys

logging.basicConfig(stream=sys.stderr)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

blank_line_tk = tokens.CommentToken('\n\n', error.CommentMark(0), None)


def _initialize_command_line_tool_file_yaml(base_command, cwl_path):
    """
    This is kind of dumb. Just make a template file to copy.
    """
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

def _initialize_command_line_tool_from_url(url, cwl_path):

    # response = requests.get(url)
    logger.debug("loading cwl for new subtool {}".format(url))
    clt = load_document(url)
    clt.dump_cwl(cwl_path)
    return


def initialize_command_line_tool_file_tool(tool_name, version_name, subtool_name, init_cwl, base_dir):
    if init_cwl == False:
        pass
    else:
        cwl_tool_path = get_cwl_tool(tool_name, version_name, subtool_name=subtool_name, base_dir=base_dir)
        if init_cwl == True:
            base_command = f"{tool_name} {subtool_name}" if subtool_name != main_tool_subtool_name else tool_name
            _initialize_command_line_tool_file_yaml(base_command, cwl_tool_path)
        else:
            assert isinstance(init_cwl, str)  # expect this to be a url.
            _initialize_command_line_tool_from_url(init_cwl, cwl_tool_path)
    return

def initialize_command_line_tool_file_script(group_name, project_name, script_version, script_name, base_dir):
    cwl_script_path = get_cwl_script(group_name, project_name, script_version, script_name, base_dir)
    base_command = script_name
    _initialize_command_line_tool_file_yaml(base_command, cwl_script_path)
    return