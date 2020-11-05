
import re
from urllib.parse import urlparse
from capanno_utils.repo_config import *

def get_shortened_id(input_uri):
    # return the part after the '#'
    url_parse = urlparse(input_uri)
    if url_parse.fragment:
        short_id =  url_parse.fragment
    else:
        short_id = url_parse.path.split("#")[-1]
    return short_id

def get_subtool_name_from_dir_name(tool_base_name, full_tool_name):
    pattern = re.compile(f"{tool_base_name}_")
    parts = pattern.split(full_tool_name)
    assert len(parts) == 2
    subtool_name = parts[1]
    return subtool_name

def get_type_from_identifier(identifier):
    """
    Can make this more sophisticated to handle parent tools/subtools, instances, etc. Maybe return classes rather than strings?
    :param identifier:
    :return:
    """
    if identifier.startswith(worklfow_identifier_prefix):
        identifier_type = 'workflow'
    elif identifier.startswith(tool_identifier_prefix):
        identifier_type = 'tool'
    elif identifier.startswith(script_identifier_prefix):
        identifier_type = 'script'
    else:
        raise ValueError(f"Identifier {identifier} is not recognized.")
    return identifier_type

