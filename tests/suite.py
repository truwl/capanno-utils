import unittest
import logging
import os
import argparse
from unittest import defaultTestLoader, TestSuite
from tests.test_add_content import TestAddToolMain, TestAddScriptMain
from tests.test_add_tool import TestAddTool
from tests.test_add_tool_instance import TestAddToolInstance
from tests.test_add_workflows import TestAddWorkflow
from tests.test_change_status import TestChangeStatus
from tests.test_dict_tools import TestDictTools
from tests.test_dump_cwl import TestDumpCwlTool
from tests.test_input_templates import TestMakeCommandLineToolInputsTemplate
from tests.test_tool_instance_metadata import TestMakeToolInstanceMetadata
from tests.test_tool_metadata import TestMakeParentToolMetadata, TestMakeSubtoolMetadata
from tests.test_script_metadata import TestScriptMetadata
from tests.test_content_maps import TestToolMaps
from tests.test_modify_yaml_files import TestModifyYamlFiles
from tests.test_path_tools import TestGetTypesFromPath
from tests.test_workflow_metadata import TestWorkflowMetadata
from tests.test_validate import TestValidateMetadata
from tests.test_validate_all import TestValidateDirectories
from tests.test_validate_all_metadata_in_maps import TestValidateContent
import tests.test_validate_content
from tests.test_validate_tool_inputs import TestValidateInputs


def suite_full():
    suite = TestSuite()
    suite.addTest(suite_add_content())
    suite.addTest(suite_add_tool())
    suite.addTest(suite_add_workflow())
    suite.addTest(suite_add_tool_instance())
    suite.addTest(suite_content_maps())
    suite.addTest(suite_dict_tools()),
    suite.addTest(suite_dump_cwl()),
    suite.addTest(suite_input_templates())
    suite.addTest(suite_script_metadata())
    suite.addTest(suite_tool_metadata())
    suite.addTest(suite_tool_instance_metadata())
    suite.addTest(suite_validate())
    suite.addTest(suite_validate_all_metadata_in_maps())
    suite.addTest(suite_validate_content())
    suite.addTest(suite_validate_directories())
    suite.addTest(suite_validate_tool_inputs())
    suite.addTest(suite_workflow_metadata())
    return suite


def suite_add_content():
    suite = defaultTestLoader.loadTestsFromTestCase(TestAddToolMain)
    suite.addTest(defaultTestLoader.loadTestsFromTestCase(TestAddScriptMain))
    return suite


def suite_add_tool():
    suite = defaultTestLoader.loadTestsFromTestCase(TestAddTool)
    return suite


def suite_add_tool_instance():
    suite = defaultTestLoader.loadTestsFromTestCase(TestAddToolInstance)
    return suite

def suite_add_workflow():
    suite = defaultTestLoader.loadTestsFromTestCase(TestAddWorkflow)
    return suite

def suite_change_status():
    """
    Keep this test out of suite_full!! It is very long and should be used in isolation if needed.
    """
    suite = defaultTestLoader.loadTestsFromTestCase(TestChangeStatus)
    return suite

def suite_content_maps():
    suite = defaultTestLoader.loadTestsFromTestCase(TestToolMaps)
    return suite


def suite_dict_tools():
    suite = defaultTestLoader.loadTestsFromTestCase(TestDictTools)
    return suite


def suite_dump_cwl():
    suite = defaultTestLoader.loadTestsFromTestCase(TestDumpCwlTool)
    return suite


def suite_input_templates():
    suite = defaultTestLoader.loadTestsFromTestCase(TestMakeCommandLineToolInputsTemplate)
    return suite

def suite_modify_yaml_files():
    suite = defaultTestLoader.loadTestsFromTestCase(TestModifyYamlFiles)
    return suite

def suite_path_tools():
    suite = defaultTestLoader.loadTestsFromTestCase(TestGetTypesFromPath)
    return suite


def suite_script_metadata():
    suite = defaultTestLoader.loadTestsFromTestCase(TestScriptMetadata)
    return suite


def suite_tool_instance_metadata():
    suite = defaultTestLoader.loadTestsFromTestCase(TestMakeToolInstanceMetadata)
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


def suite_validate_content():
    suite = defaultTestLoader.loadTestsFromTestCase(tests.test_validate_content.TestValidateTools)
    suite.addTest(defaultTestLoader.loadTestsFromTestCase(tests.test_validate_content.TestValidateScripts))
    return suite


def suite_validate_tool_inputs():
    suite = defaultTestLoader.loadTestsFromTestCase(TestValidateInputs)
    return suite


def suite_workflow_metadata():
    suite = defaultTestLoader.loadTestsFromTestCase(TestWorkflowMetadata)
    return suite


def suite_dict():
    suite_dict = {'add_content': suite_add_content(),
                  'add_tool': suite_add_tool(),
                  'add_workflow': suite_add_workflow(),
                  'add_tool_instance': suite_add_tool_instance(),
                  'change_status': suite_change_status(),
                  'content_maps': suite_content_maps(),
                  'dict_tools': suite_dict_tools(),
                  'dump_cwl': suite_dump_cwl(),
                  'full': suite_full(),
                  'input_templates': suite_input_templates(),
                  'modify_yaml': suite_modify_yaml_files(),
                  'path_tools': suite_path_tools(),
                  'script_metadata': suite_script_metadata(),
                  'tool_instance_metadata': suite_tool_instance_metadata(),
                  'tool_metadata': suite_tool_metadata(),
                  'validate': suite_validate(),
                  'validate_all_metadata_in_maps': suite_validate_all_metadata_in_maps(),
                  'validate_content': suite_validate_content(),
                  'validate_directories': suite_validate_directories(),
                  'validate_tool_inputs': suite_validate_tool_inputs(),
                  'workflow_metadata': suite_workflow_metadata(),
                  }
    return suite_dict


parser = argparse.ArgumentParser(description="Run test suite")
parser.add_argument("module", nargs='?', default='full', choices=suite_dict().keys(),
                    help='Specify the test suite that you would like to run. All suites will run if not specified')
parser.add_argument("--log_level", help="Set logging level", choices=['debug', 'info', 'warning', 'error', 'critical'])
args = parser.parse_args()


def run_tests():
    # logging.basicConfig(level=logging.CRITICAL)
    if args.log_level:
        if args.log_level == 'debug':
            log_level = logging.DEBUG
        elif args.log_level == 'info':
            log_level = logging.INFO
        elif args.log_level == 'warning':
            log_level = logging.WARNING
        elif args.log_level == 'error':
            log_level = logging.ERROR
        elif args.log_level == 'critical':
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
