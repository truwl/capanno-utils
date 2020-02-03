import unittest
import logging
import os
import argparse
from unittest import defaultTestLoader, TestSuite
from tests.test_add_tool import TestAddTool
from tests.test_tool_metadata import TestMakeParentToolMetadata, TestMakeSubtoolMetadata
from tests.test_script_metadata import TestScriptMetadata
from tests.test_content_maps import TestToolMaps
from tests.test_workflow_metadata import TestWorkflowMetadata
from tests.test_validate import TestValidateMetadata
from tests.test_validate_all import TestValidateDirectories
from tests.test_validate_all_metadata_in_maps import TestValidateContent
from tests.test_validate_tool_inputs import TestValidateInputs



def suite_full():
    suite = TestSuite()
    suite.addTest((suite_add_tool()))
    suite.addTest(suite_content_maps())
    suite.addTest(suite_script_metadata())
    suite.addTest(suite_tool_metadata())
    suite.addTest(suite_validate())
    suite.addTest(suite_validate_all_metadata_in_maps())
    suite.addTest(suite_validate_directories())
    suite.addTest(suite_validate_tool_inputs())
    suite.addTest(suite_workflow_metadata())
    return suite


def suite_add_tool():
    suite = defaultTestLoader.loadTestsFromTestCase(TestAddTool)
    return suite

def suite_content_maps():
    suite = defaultTestLoader.loadTestsFromTestCase(TestToolMaps)
    return suite


def suite_script_metadata():
    suite = defaultTestLoader.loadTestsFromTestCase(TestScriptMetadata)
    return suite

def suite_tool_metadata():
    suite = defaultTestLoader.loadTestsFromTestCase(TestMakeParentToolMetadata)
    suite.addTest(defaultTestLoader.loadTestsFromTestCase(TestMakeSubtoolMetadata))
    return suite

def suite_validate():
    suite = defaultTestLoader.loadTestsFromTestCase(TestValidateMetadata)
    return suite

def suite_validate_directories():
    suite = defaultTestLoader.loadTestsFromTestCase(TestValidateDirectories)
    return suite

def suite_validate_all_metadata_in_maps():
    suite = defaultTestLoader.loadTestsFromTestCase(TestValidateContent)
    return suite

def suite_validate_tool_inputs():
    suite = defaultTestLoader.loadTestsFromTestCase(TestValidateInputs)
    return suite



def suite_workflow_metadata():
    suite = defaultTestLoader.loadTestsFromTestCase(TestWorkflowMetadata)
    return suite

def suite_dict():
    suite_dict = {'add_tool': suite_add_tool(),
                  'content_maps': suite_content_maps(),
                  'full': suite_full(),
                  'script_metadata': suite_script_metadata(),
                  'tool_metadata': suite_tool_metadata(),
                  'validate': suite_validate(),
                  'validate_all_metadata_in_maps': suite_validate_all_metadata_in_maps(),
                  'validate_directories': suite_validate_directories(),
                  'validate_tool_inputs': suite_validate_tool_inputs(),
                  'workflow_metadata': suite_workflow_metadata(),
                  }
    return suite_dict

parser = argparse.ArgumentParser(description="Run test suite")
parser.add_argument("module", nargs='?', default='full', choices= suite_dict().keys(),
                    help='Specify the test suite that you would like to run. All suites will run if not specified')
parser.add_argument("--log_level", help="Set logging level", choices=['debug', 'info', 'warning', 'error', 'critical'])
args = parser.parse_args()





def run_tests():
    # logging.basicConfig(level=logging.CRITICAL)
    if args.log_level:
        if args.log_level=='debug':
            log_level = logging.DEBUG
        elif args.log_level=='info':
            log_level = logging.INFO
        elif args.log_level=='warning':
            log_level = logging.WARNING
        elif args.log_level=='error':
            log_level = logging.ERROR
        elif args.log_level=='critical':
            log_level = logging.CRITICAL
        else:
            raise ValueError  # Should never hit this.
    else:
        log_level = logging.CRITICAL  # default level.

    logging.getLogger().setLevel(log_level)

    # update this dictionary when new suites are added.


    try:
        test_suite = suite_dict()[args.module]
    except KeyError:
        raise ValueError(f"Test suite {args.module} not recognized.")


    # Set temp directory

    os.environ['CONFIG_KEY'] = 'TEST'
    unittest.TextTestRunner().run(test_suite)
    return


if __name__ == '__main__':
    run_tests()
