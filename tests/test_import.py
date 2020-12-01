# -*- coding: utf-8 -*-

"""Test the repo importer"""

import unittest

import cwl_utils.parser_v1_0 as parser
import os
import re
import sys
import glob
from abc import abstractmethod
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.compat import string_types, ordereddict
import logging, sys
import subprocess
from typing import Optional
from capanno_utils.add.add_tools import add_tool, add_subtool
from capanno_utils.helpers.get_paths import get_tool_common_dir, main_tool_subtool_name, get_tool_metadata, get_tool_dir

from capanno_utils.helpers.import_repo import bioCwl

class TestImport(unittest.TestCase):
    def test_import_noversion(self):
        mybio = bioCwl()
        lancetres=mybio.getCwlInfo('Lancet','Lancet.cwl')
        assert(lancetres['docker']=='truwl/lancet:latest')

    def test_import(self):
        mybio = bioCwl()
        allres=mybio.getCwlInfos()
