
import logging
import cwltool.main


def validate_cwl_tool(cwl_tool_path):

    cwl_path = str(cwl_tool_path)  # in case it is a Path object.
    logger_handler = logging.StreamHandler()
    logger_handler.setLevel(logging.CRITICAL)
    return_code = cwltool.main.main(argsl=["--validate", cwl_path], logger_handler=logging.StreamHandler())
    if return_code == 0:
        return
    else:
        raise ValueError(f"Validation of cwl file {cwl_path} returned non-zero return code.")