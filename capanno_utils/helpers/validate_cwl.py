
import logging
import cwltool.main
from ..classes.cwl.command_line_tool import load_document

def validate_cwl_tool(cwl_doc_path):
    # Just load into CommandLineTool class and see if it works. Seems to be good.
    cwl_doc_path = str(cwl_doc_path)
    command_line_tool = load_document(cwl_doc_path)
    return
