import logging
import os
from argparse import Namespace
from pathlib import Path
from urllib.parse import urlparse
from ruamel.yaml import YAML
from schema_salad.exceptions import ValidationException
from cwltool.load_tool import resolve_and_validate_document, fetch_document
from cwltool.context import RuntimeContext
from cwltool.main import setup_loadingContext
from cwltool.main import main as cwl_tool
from ..classes.cwl.common_workflow_language import load_document


def validate_cwl_doc_main(cwl_doc_path):
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.ERROR)
    cwl_doc_path = str(cwl_doc_path)
    rv = cwl_tool(argsl=['--validate', '--disable-color', cwl_doc_path], logger_handler=stream_handler)
    if rv != 0:
        raise ValidationException(f"cwltool did not return a return value of 0 for {cwl_doc_path}")
    # command_line_tool = load_document(cwl_doc_path)
    return


def validate_cwl_doc(cwl_doc):
    """
    This is adapted from cwltool.main.main and avoids the unnecessary stuff by using cwltool.main.main directly.
    :param cwl_doc_path:
    :return:
    """
    if isinstance(cwl_doc, (Path, str)): # Can also be CWLObjectType
        cwl_doc = str(cwl_doc)
        if not urlparse(cwl_doc)[0]:
            cwl_doc = f"file://{os.path.abspath(cwl_doc)}"
    loading_context, workflow_object, uri = fetch_document(cwl_doc)
    resolve_and_validate_document(loading_context, workflow_object, uri)
    return
#
#
# def _get_loading_context():
#     # Can probably deprecate. fetch_document() takes care of getting a loading context.
#     runtime_context = RuntimeContext()
#     namespace_dict = {
#         'enable_dev': False,
#         'doc_cache': False,
#         'disable_js_validation': False,
#         'do_validate': True,
#         'pack': False,
#         'print_subgraph': False,
#
#     }
#     args = Namespace(**namespace_dict)
#     loading_context = setup_loadingContext(loadingContext=None, runtimeContext=runtime_context, args=args)
#     return loading_context
