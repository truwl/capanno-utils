

from urllib import request
from pathlib import Path
from ruamel.yaml import YAML, tokens, error
from ruamel.yaml.comments import CommentedMap
from WDL.CLI import check as check_wdl
from capanno_utils.templates.tool_templates import wdl_templates, snakemake_templates, nextflow_templates
from capanno_utils.helpers.get_paths import get_tool_sources, get_cwl_script, main_tool_subtool_name
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
    cwl_path = Path(cwl_path)
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

def _initialize_empty_wdl_task(wdl_path):
    wdl_path = Path(wdl_path)
    wdl_path.write_text(wdl_templates.wdl_task_template)
    return

def _initialize_empty_sm_rule(sm_path):
    sm_path = Path(sm_path)
    sm_path.write_text(snakemake_templates.snakemake_rule)
    return

def _initialize_empty_nf_tool(nf_path):
    nf_path = Path(nf_path)
    nf_path.write_text(nextflow_templates.nextflow_tool_template)
    return

def _initialize_command_line_tool_from_url(url, cwl_path):

    # response = requests.get(url)
    logger.debug("loading cwl for new subtool {}".format(url))
    clt = load_document(url)
    clt.dump_cwl(cwl_path)
    return

def _initialize_wdl_task_from_url(url, wdl_path):
    logger.debug(f"loading wdl for new subtool/task {url}")
    request.urlretrieve(url, wdl_path)
    check_wdl(path=str(wdl_path)) # check after importing.
    return

def _initialize_sm_rule_from_url(url, sm_path):
    logger.debug(f"loading snakmake for new subtool/task {url}")
    request.urlretrieve(url, sm_path)
    # check_snakemake # Don't have anything to make sure bad things aren't being loaded here.
    return


def _initialize_nf_tool_from_url(url, nf_path):
    logger.debug(f"loading nextflow for new subtool/task {url}")
    request.urlretrieve(url, nf_path)
    # check_nf # Don't have anything to make sure bad things aren't being loaded here.
    return


def initialize_tool_wf_file_tool(tool_name, version_name, subtool_name, init_cwl, init_wdl, init_sm, init_nf, base_dir, ):
    tool_sources = get_tool_sources(tool_name, version_name, subtool_name=subtool_name, base_dir=base_dir)
    cwl_path, wdl_path, sm_path, nf_path = tuple(tool_sources.values())
    if not init_cwl:
        pass
    else:
        if init_cwl == True:
            base_command = f"{tool_name} {subtool_name}" if subtool_name != main_tool_subtool_name else tool_name
            _initialize_command_line_tool_file_yaml(base_command, cwl_path)
        else:
            try:
                assert isinstance(init_cwl, str)  # expect this to be a url.
            except AssertionError:
                print(f"init_cwl is {init_cwl}")
                raise
            _initialize_command_line_tool_from_url(init_cwl, cwl_path)
    if not init_wdl:
        pass
    else:
        if init_wdl == True:
            _initialize_empty_wdl_task(wdl_path)
        else:
            assert isinstance(init_wdl, str)
            _initialize_wdl_task_from_url(init_wdl, wdl_path)
    if not init_sm:
        pass
    else:
        if init_sm == True:
            _initialize_empty_sm_rule(sm_path)
        else:
            _initialize_sm_rule_from_url(init_sm, sm_path)
    if not init_nf:
        pass
    else:
        if init_nf == True:
            _initialize_empty_nf_tool(nf_path)
        else:
            _initialize_nf_tool_from_url(init_nf, nf_path)
    return

def initialize_command_line_tool_file_script(group_name, project_name, script_version, script_name, base_dir):
    cwl_script_path = get_cwl_script(group_name, project_name, script_version, script_name, base_dir)
    base_command = script_name
    _initialize_command_line_tool_file_yaml(base_command, cwl_script_path)
    return