

from cwlgen import CommandLineTool
from xd_cwl_utils.helpers.get_paths import get_cwl_tool, main_tool_subtool_name

def initialize_commmand_line_tool_file(tool_name, version_name, subtool_name, base_dir):
    cwl_tool_path = get_cwl_tool(tool_name, version_name, subtool_name=subtool_name, base_dir=base_dir)
    base_command = f"{tool_name} {subtool_name}" if subtool_name != main_tool_subtool_name else tool_name
    clt = CommandLineTool(base_command=base_command, cwl_version="v1.0", stdout=None, doc=None)
    clt.export(str(cwl_tool_path))
