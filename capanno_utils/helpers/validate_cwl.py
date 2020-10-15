
import logging
import sys
import coloredlogs
from cwltool.loghandler import _logger
from cwltool.main import main as cwl_tool
from ..classes.cwl.common_workflow_language import load_document

def validate_cwl_tool(cwl_doc_path):
    # Just load into CommandLineTool class and see if it works. Seems to be good.
    # It's not. Seems to check keys but not values; e.g type: String (instead of string) is not caught.
    coloredlogs.install(logger=_logger, stream=sys.stderr)  # logging in stuff is a hack to avoid raising error from loggin in cwltool.main. Calling main as module screws up logging handlers somehow.
    stream_handler = _logger.handlers[-1]
    cwl_doc_path = str(cwl_doc_path)
    cwl_tool(argsl=['--validate', cwl_doc_path], logger_handler=stream_handler)
    # command_line_tool = load_document(cwl_doc_path)
    return
