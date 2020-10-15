
import logging
import cwltool.main
from ..classes.cwl.common_workflow_language import load_document

def validate_cwl_tool(cwl_doc_path):
    # Just load into CommandLineTool class and see if it works. Seems to be good.
    # It's not. Seems to check keys but not values; e.g type: String (instead of string) is not caught.
    cwl_doc_path = str(cwl_doc_path)
    if 'cwl-tools' in cwl_doc_path:
        assert True
        if 'genomeGenerate' in cwl_doc_path:
            assert True
    command_line_tool = load_document(cwl_doc_path)
    return
