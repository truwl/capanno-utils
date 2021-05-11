

from WDL import load


def validate_wdl_doc(wdl_path):
    load(str(wdl_path))  # load works correctly for validation where parse_document and CLI.check do not.
    return