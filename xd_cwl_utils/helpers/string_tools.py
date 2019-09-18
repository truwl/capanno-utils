
import re
from urllib.parse import urlparse

def uri_name(input_uri):
    # return the part after the '#'
    d = urlparse(input_uri)
    if d.fragment:
        return d.fragment
    return d.path.split("#")[-1]

def get_subtool_name_from_dir_name(tool_base_name, full_tool_name):
    pattern = re.compile(f"{tool_base_name}_")
    parts = pattern.split(full_tool_name)
    assert len(parts) == 2
    subtool_name = parts[1]
    return subtool_name
