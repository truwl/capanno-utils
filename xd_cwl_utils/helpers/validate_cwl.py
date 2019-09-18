
import logging
import cwltool.main


def validate_cwl_tool(cwl_tool_path):
    """
    Wrapper to call cwltool --validate cwl_tool_path
    :param cwl_tool_path:
    :return:
    """
    # works, but I can't get logger to shut up.
    cwl_path = str(cwl_tool_path)  # in case it is a Path object.
    logger_handler = logging.NullHandler()
    logger_handler.setLevel(logging.CRITICAL)
    return_code = cwltool.main.main(argsl=["--validate", "--quiet", cwl_path], logger_handler=logger_handler)
    if return_code == 0:
        return
    else:
        raise ValueError(f"Validation of cwl file {cwl_path} returned non-zero return code.")


from ..classes.cwl.command_line_tool import load_document

def validate_cwl_tool_2(cwl_doc_path):
    # Just load into CommandLineTool class and see if it works. Seems to be good.
    cwl_doc_path = str(cwl_doc_path)
    command_line_tool = load_document(cwl_doc_path)
    return
