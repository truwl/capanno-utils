import logging
import os
from pathlib import Path
from urllib.parse import urlparse
from schema_salad.exceptions import ValidationException
from schema_salad.ref_resolver import file_uri
from cwltool.load_tool import resolve_and_validate_document, fetch_document
from cwltool.main import main as cwl_tool


def validate_cwl_doc_main(cwl_doc_path):
    """
    Not currently used. Calls the main function of cwltool with validation parameters. Does a lot of extra stuff.
    :param cwl_doc_path:
    :return:
    """
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    cwl_doc_path = str(cwl_doc_path)
    rv = cwl_tool(argsl=['--validate', '--disable-color', cwl_doc_path], logger_handler=stream_handler)
    if rv != 0:
        raise ValidationException(f"cwltool did not return a return value of 0 for {cwl_doc_path}")
    return


def validate_cwl_doc(cwl_doc):
    """
    This is adapted from cwltool.main.main and avoids the unnecessary stuff by using cwltool.main.main directly.
    :param cwl_doc_path:
    :return:
    """
    if isinstance(cwl_doc, (Path, str)):  # Can also be CWLObjectType
        cwl_doc = str(cwl_doc)
        if not (urlparse(cwl_doc)[0] and urlparse(cwl_doc)[0] in ['http', 'https', 'file']):
            cwl_doc = file_uri(os.path.abspath(cwl_doc))
    loading_context, workflow_object, uri = fetch_document(cwl_doc)
    resolve_and_validate_document(loading_context, workflow_object, uri)
    return
